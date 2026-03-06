"""
ESPNcricinfo Scraper for T20 World Cup 2026.

Scrapes:
  - Fixtures & results (match list with scores, venues, dates)
  - Individual match scorecards (batting, bowling, toss, MoM)
  - Tournament aggregate stats (player-level batting/bowling)

Outputs CSVs to data_raw/espn/
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    ESPN_SERIES_URL, ESPN_FIXTURES_URL, ESPN_STATS_URL,
    ESPN_BASE_URL, RAW_ESPN, ESPN_SERIES_ID
)
from src.utils import (
    fetch_page, standardize_team_name, safe_float, safe_int,
    save_dataframe, generate_match_id, logger
)


class ESPNScraper:
    """Scraper for ESPNcricinfo T20 World Cup 2026 data."""

    def __init__(self):
        self.base_url = ESPN_BASE_URL
        self.series_url = ESPN_SERIES_URL
        self.output_dir = RAW_ESPN
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ─── Fixtures & Results ──────────────────────────────────────────────

    def scrape_fixtures(self) -> pd.DataFrame:
        """
        Scrape the fixtures/results page to get all matches with
        basic info: teams, venue, date, result, scores.
        """
        logger.info("Scraping ESPN fixtures & results...")
        soup = fetch_page(ESPN_FIXTURES_URL)
        if not soup:
            logger.error("Failed to fetch fixtures page")
            return pd.DataFrame()

        matches = []
        # ESPN renders match cards with data in structured divs
        match_cards = soup.select("div.ds-border-b, div.ds-border-line")

        for card in match_cards:
            try:
                match = self._parse_match_card(card)
                if match:
                    matches.append(match)
            except Exception as e:
                logger.warning(f"Skipping match card: {e}")
                continue

        # If structured parsing yields nothing, try alternative selectors
        if not matches:
            matches = self._parse_fixtures_alternative(soup)

        df = pd.DataFrame(matches)
        if not df.empty:
            save_dataframe(df, self.output_dir / "fixtures.csv")
        else:
            logger.warning("No fixtures extracted — page structure may have changed.")
            # Save raw HTML for manual inspection
            (self.output_dir / "fixtures_raw.html").write_text(
                str(soup), encoding="utf-8"
            )

        return df

    def _parse_match_card(self, card) -> Optional[Dict]:
        """Parse a single match card element."""
        # Extract team names
        teams = card.select("p.ds-text-tight-m, span.ds-text-tight-m")
        if len(teams) < 2:
            return None

        team1 = standardize_team_name(teams[0].get_text(strip=True))
        team2 = standardize_team_name(teams[1].get_text(strip=True))

        # Extract scores
        scores = card.select("strong, span.ds-text-compact-s")
        score1 = scores[0].get_text(strip=True) if scores else ""
        score2 = scores[1].get_text(strip=True) if len(scores) > 1 else ""

        # Extract result text
        result_el = card.select_one("p.ds-text-tight-s, span.ds-text-tight-s")
        result = result_el.get_text(strip=True) if result_el else ""

        # Extract match link
        link_el = card.select_one("a[href*='/full-scorecard']") or card.select_one("a[href*='live-cricket-score']")
        match_url = f"{self.base_url}{link_el['href']}" if link_el else ""

        # Extract venue and date
        info = card.select("span.ds-text-tight-xs")
        venue = info[0].get_text(strip=True) if info else ""
        date = info[1].get_text(strip=True) if len(info) > 1 else ""

        return {
            "team1": team1,
            "team2": team2,
            "score1": score1,
            "score2": score2,
            "result": result,
            "venue": venue,
            "date": date,
            "match_url": match_url,
            "source": "espn",
        }

    def _parse_fixtures_alternative(self, soup) -> List[Dict]:
        """Alternative parser if primary selectors fail."""
        matches = []
        # Look for script tags with JSON data (ESPN embeds match data)
        scripts = soup.find_all("script", {"id": "__NEXT_DATA__"})
        if scripts:
            try:
                data = json.loads(scripts[0].string)
                # Navigate the JSON structure to find match data
                page_props = data.get("props", {}).get("pageProps", {})
                content = page_props.get("data", {})

                # Try multiple potential keys
                for key in ["content", "matchSchedule", "matches"]:
                    if key in content:
                        match_list = content[key]
                        if isinstance(match_list, list):
                            for m in match_list:
                                matches.append(self._extract_from_json(m))
                        break
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"JSON parsing failed: {e}")

        return [m for m in matches if m]

    def _extract_from_json(self, match_data: Dict) -> Optional[Dict]:
        """Extract match info from ESPN JSON data structure."""
        try:
            teams = match_data.get("teams", [])
            if len(teams) < 2:
                return None
            return {
                "team1": standardize_team_name(teams[0].get("team", {}).get("name", "")),
                "team2": standardize_team_name(teams[1].get("team", {}).get("name", "")),
                "score1": teams[0].get("score", ""),
                "score2": teams[1].get("score", ""),
                "result": match_data.get("statusText", ""),
                "venue": match_data.get("ground", {}).get("name", ""),
                "date": match_data.get("startDate", ""),
                "match_url": f"{self.base_url}/series/{ESPN_SERIES_ID}/{match_data.get('slug', '')}",
                "source": "espn",
            }
        except Exception:
            return None

    # ─── Scorecard Parsing ───────────────────────────────────────────────

    def scrape_scorecard(self, match_url: str) -> Dict:
        """
        Scrape a full scorecard from an ESPN match page.
        Returns batting, bowling, toss, and match summary.
        """
        logger.info(f"Scraping scorecard: {match_url}")
        soup = fetch_page(match_url)
        if not soup:
            return {}

        scorecard = {
            "batting": [],
            "bowling": [],
            "toss": "",
            "mom": "",
            "match_info": {},
        }

        # Extract match info
        info_items = soup.select("div.ds-border-line tr, table.ds-table tr")
        for item in info_items:
            try:
                cells = item.select("td, th")
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    val = cells[1].get_text(strip=True)
                    if "toss" in key:
                        scorecard["toss"] = val
                    elif "player of the match" in key or "mom" in key:
                        scorecard["mom"] = val
            except Exception:
                continue

        # Extract batting tables
        batting_tables = soup.select("table.ds-table")
        for table in batting_tables:
            headers = [th.get_text(strip=True) for th in table.select("thead th")]
            if not headers:
                continue

            # Identify batting tables (have 'R', 'B', '4s', '6s', 'SR')
            header_lower = [h.lower() for h in headers]
            if "r" in header_lower and "b" in header_lower:
                rows = table.select("tbody tr")
                for row in rows:
                    cells = row.select("td")
                    if len(cells) >= 7:
                        scorecard["batting"].append({
                            "player": cells[0].get_text(strip=True),
                            "dismissal": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                            "runs": safe_int(cells[2].get_text(strip=True)),
                            "balls": safe_int(cells[3].get_text(strip=True)),
                            "fours": safe_int(cells[4].get_text(strip=True)),
                            "sixes": safe_int(cells[5].get_text(strip=True)),
                            "strike_rate": safe_float(cells[6].get_text(strip=True)),
                        })

            # Identify bowling tables ('O', 'M', 'R', 'W', 'Econ')
            elif "o" in header_lower and "econ" in header_lower:
                rows = table.select("tbody tr")
                for row in rows:
                    cells = row.select("td")
                    if len(cells) >= 6:
                        scorecard["bowling"].append({
                            "player": cells[0].get_text(strip=True),
                            "overs": safe_float(cells[1].get_text(strip=True)),
                            "maidens": safe_int(cells[2].get_text(strip=True)),
                            "runs": safe_int(cells[3].get_text(strip=True)),
                            "wickets": safe_int(cells[4].get_text(strip=True)),
                            "economy": safe_float(cells[5].get_text(strip=True)),
                        })

        return scorecard

    # ─── Tournament Stats ────────────────────────────────────────────────

    def scrape_tournament_stats(self) -> Dict[str, pd.DataFrame]:
        """
        Scrape tournament-level aggregate stats from the ESPN stats page.
        Returns dict with keys: 'batting', 'bowling'.
        """
        logger.info("Scraping ESPN tournament stats...")
        result = {"batting": pd.DataFrame(), "bowling": pd.DataFrame()}

        # Batting stats
        batting_url = f"{ESPN_STATS_URL}"
        soup = fetch_page(batting_url)
        if soup:
            result["batting"] = self._parse_stats_table(soup, "batting")
            save_dataframe(result["batting"], self.output_dir / "tournament_batting.csv")

        # Bowling stats (ESPN uses filter params)
        bowling_url = f"{ESPN_STATS_URL}?type=bowling"
        soup = fetch_page(bowling_url)
        if soup:
            result["bowling"] = self._parse_stats_table(soup, "bowling")
            save_dataframe(result["bowling"], self.output_dir / "tournament_bowling.csv")

        return result

    def _parse_stats_table(self, soup, stat_type: str) -> pd.DataFrame:
        """Parse a stats table from ESPN stats page."""
        table = soup.select_one("table.ds-table, table.ds-w-full")
        if not table:
            logger.warning(f"No {stat_type} stats table found")
            return pd.DataFrame()

        # Headers
        headers = [th.get_text(strip=True) for th in table.select("thead th")]

        # Rows
        rows = []
        for tr in table.select("tbody tr"):
            cells = [td.get_text(strip=True) for td in tr.select("td")]
            if cells:
                rows.append(cells)

        if headers and rows:
            df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
            df["stat_type"] = stat_type
            return df

        return pd.DataFrame()

    # ─── Orchestrator ────────────────────────────────────────────────────

    def scrape_all(self):
        """Run full ESPN scraping pipeline."""
        logger.info("=" * 60)
        logger.info("Starting full ESPN scrape")
        logger.info("=" * 60)

        # 1. Fixtures
        fixtures_df = self.scrape_fixtures()

        # 2. Scorecards for each match with a URL
        if not fixtures_df.empty and "match_url" in fixtures_df.columns:
            all_batting = []
            all_bowling = []

            for _, row in fixtures_df.iterrows():
                if row.get("match_url"):
                    card = self.scrape_scorecard(row["match_url"])
                    if card.get("batting"):
                        for b in card["batting"]:
                            b["team1"] = row["team1"]
                            b["team2"] = row["team2"]
                            b["date"] = row["date"]
                        all_batting.extend(card["batting"])
                    if card.get("bowling"):
                        for b in card["bowling"]:
                            b["team1"] = row["team1"]
                            b["team2"] = row["team2"]
                            b["date"] = row["date"]
                        all_bowling.extend(card["bowling"])

            if all_batting:
                save_dataframe(pd.DataFrame(all_batting), self.output_dir / "match_batting.csv")
            if all_bowling:
                save_dataframe(pd.DataFrame(all_bowling), self.output_dir / "match_bowling.csv")

        # 3. Tournament stats
        self.scrape_tournament_stats()

        logger.info("ESPN scrape complete!")


if __name__ == "__main__":
    scraper = ESPNScraper()
    scraper.scrape_all()
