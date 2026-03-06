"""
ICC Portal Scraper for T20 World Cup 2026.

Scrapes:
  - Official fixtures, groups, and venues
  - Tournament-level stat aggregates (most runs, wickets, averages)

Outputs CSVs to data_raw/icc/
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    ICC_BASE_URL, ICC_TOURNAMENT_URL, ICC_STATS_URL,
    ICC_STATS_TRACKER_URL, RAW_ICC
)
from src.utils import (
    fetch_page, standardize_team_name, safe_float, safe_int,
    save_dataframe, logger
)


class ICCScraper:
    """Scraper for ICC Cricket T20 World Cup 2026 data."""

    def __init__(self):
        self.base_url = ICC_BASE_URL
        self.output_dir = RAW_ICC
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ─── Tournament Stats ────────────────────────────────────────────────

    def scrape_stats(self) -> Dict[str, pd.DataFrame]:
        """
        Scrape tournament stats from ICC portal.
        Covers: most runs, most wickets, best batting avg, best bowling avg, etc.
        """
        logger.info("Scraping ICC tournament stats...")

        stats = {}

        # ICC stats page — main table
        soup = fetch_page(ICC_STATS_URL)
        if soup:
            stats["main"] = self._parse_stats_page(soup)
            if not stats["main"].empty:
                save_dataframe(stats["main"], self.output_dir / "tournament_stats.csv")

        # Stats tracker for more detailed views
        soup = fetch_page(ICC_STATS_TRACKER_URL)
        if soup:
            stats["tracker"] = self._parse_stats_page(soup)
            if not stats["tracker"].empty:
                save_dataframe(stats["tracker"], self.output_dir / "stats_tracker.csv")

        # Try specific stat category URLs
        stat_categories = [
            ("most-runs", "batting_runs"),
            ("most-wickets", "bowling_wickets"),
            ("best-batting-strike-rate", "batting_sr"),
            ("best-bowling-economy", "bowling_econ"),
            ("most-sixes", "batting_sixes"),
            ("most-fours", "batting_fours"),
        ]

        for cat_slug, cat_name in stat_categories:
            url = f"{ICC_STATS_URL}/{cat_slug}"
            soup = fetch_page(url)
            if soup:
                df = self._parse_stats_page(soup)
                if not df.empty:
                    df["category"] = cat_name
                    stats[cat_name] = df
                    save_dataframe(df, self.output_dir / f"{cat_name}.csv")

        return stats

    def _parse_stats_page(self, soup) -> pd.DataFrame:
        """Parse a stats table from ICC page."""
        # Try common table selectors
        tables = soup.select("table")
        if not tables:
            # ICC sometimes uses div-based layouts
            return self._parse_div_stats(soup)

        # Use the largest table
        best_table = max(tables, key=lambda t: len(t.select("tr")))

        headers = [th.get_text(strip=True) for th in best_table.select("thead th, tr:first-child th")]
        if not headers:
            # Try first row as header
            first_row = best_table.select_one("tr")
            if first_row:
                headers = [td.get_text(strip=True) for td in first_row.select("td, th")]

        rows = []
        for tr in best_table.select("tbody tr, tr")[1:]:  # Skip header row
            cells = [td.get_text(strip=True) for td in tr.select("td")]
            if cells and any(c.strip() for c in cells):
                rows.append(cells)

        if headers and rows:
            # Align column count
            max_cols = max(len(headers), max(len(r) for r in rows) if rows else 0)
            headers = headers + [f"col_{i}" for i in range(len(headers), max_cols)]
            rows = [r + [""] * (max_cols - len(r)) for r in rows]
            return pd.DataFrame(rows, columns=headers[:max_cols])

        return pd.DataFrame()

    def _parse_div_stats(self, soup) -> pd.DataFrame:
        """Parse div-based stat layouts (ICC sometimes avoids tables)."""
        records = []

        # Look for stat cards / player stat rows
        stat_items = soup.select("div[class*='stat'], div[class*='player'], div[class*='ranking']")

        for item in stat_items:
            try:
                name_el = item.select_one("span[class*='name'], div[class*='name'], a")
                if not name_el:
                    continue

                record = {"player": name_el.get_text(strip=True)}

                # Extract all number-like spans as potential stat values
                numbers = item.select("span[class*='value'], div[class*='value'], span[class*='stat']")
                for i, num in enumerate(numbers):
                    val = num.get_text(strip=True)
                    if val:
                        record[f"stat_{i}"] = val

                if len(record) > 1:
                    records.append(record)
            except Exception:
                continue

        return pd.DataFrame(records) if records else pd.DataFrame()

    # ─── Fixtures / Schedule ─────────────────────────────────────────────

    def scrape_fixtures(self) -> pd.DataFrame:
        """Scrape official ICC fixtures."""
        logger.info("Scraping ICC fixtures...")
        url = f"{ICC_TOURNAMENT_URL}/matches"
        soup = fetch_page(url)
        if not soup:
            logger.error("Failed to fetch ICC fixtures")
            return pd.DataFrame()

        matches = []
        match_cards = soup.select("div[class*='match'], div[class*='fixture'], a[class*='match']")

        for card in match_cards:
            try:
                teams = card.select("span[class*='team'], div[class*='team']")
                if len(teams) >= 2:
                    match = {
                        "team1": standardize_team_name(teams[0].get_text(strip=True)),
                        "team2": standardize_team_name(teams[1].get_text(strip=True)),
                    }

                    # Score
                    scores = card.select("span[class*='score']")
                    match["score1"] = scores[0].get_text(strip=True) if scores else ""
                    match["score2"] = scores[1].get_text(strip=True) if len(scores) > 1 else ""

                    # Venue and date
                    venue_el = card.select_one("span[class*='venue'], div[class*='venue']")
                    date_el = card.select_one("span[class*='date'], div[class*='date']")
                    match["venue"] = venue_el.get_text(strip=True) if venue_el else ""
                    match["date"] = date_el.get_text(strip=True) if date_el else ""

                    # Result
                    result_el = card.select_one("span[class*='result'], div[class*='status']")
                    match["result"] = result_el.get_text(strip=True) if result_el else ""
                    match["source"] = "icc"

                    matches.append(match)
            except Exception as e:
                logger.debug(f"Skipping ICC card: {e}")

        df = pd.DataFrame(matches)
        if not df.empty:
            save_dataframe(df, self.output_dir / "fixtures.csv")
        else:
            logger.warning("No ICC fixtures extracted")
            if soup:
                (self.output_dir / "fixtures_raw.html").write_text(
                    str(soup), encoding="utf-8"
                )
        return df

    # ─── Orchestrator ────────────────────────────────────────────────────

    def scrape_all(self):
        """Run full ICC scraping pipeline."""
        logger.info("=" * 60)
        logger.info("Starting full ICC scrape")
        logger.info("=" * 60)

        self.scrape_fixtures()
        self.scrape_stats()

        logger.info("ICC scrape complete!")


if __name__ == "__main__":
    scraper = ICCScraper()
    scraper.scrape_all()
