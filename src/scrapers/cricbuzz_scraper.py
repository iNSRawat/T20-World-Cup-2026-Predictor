"""
Cricbuzz Scraper for T20 World Cup 2026.

Scrapes:
  - Match schedule with results and basic scores
  - Individual match scorecards for cross-validation

Outputs CSVs to data_raw/cricbuzz/
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    CRICBUZZ_BASE_URL, CRICBUZZ_SERIES_URL, CRICBUZZ_MATCHES_URL,
    RAW_CRICBUZZ, CRICBUZZ_SERIES_ID
)
from src.utils import (
    fetch_page, standardize_team_name, safe_float, safe_int,
    save_dataframe, logger
)


class CricbuzzScraper:
    """Scraper for Cricbuzz T20 World Cup 2026 data."""

    def __init__(self):
        self.base_url = CRICBUZZ_BASE_URL
        self.series_url = CRICBUZZ_SERIES_URL
        self.output_dir = RAW_CRICBUZZ
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ─── Match Schedule & Results ────────────────────────────────────────

    def scrape_matches(self) -> pd.DataFrame:
        """
        Scrape match schedule/results from Cricbuzz series matches page.
        """
        logger.info("Scraping Cricbuzz matches...")
        soup = fetch_page(CRICBUZZ_MATCHES_URL)
        if not soup:
            logger.error("Failed to fetch Cricbuzz matches page")
            return pd.DataFrame()

        matches = []

        # Cricbuzz uses div-based match cards
        match_cards = soup.select("div.cb-series-matches, div.cb-col-100")

        for card in match_cards:
            try:
                match = self._parse_match_card(card)
                if match:
                    matches.append(match)
            except Exception as e:
                logger.debug(f"Skipping Cricbuzz card: {e}")
                continue

        # Fallback: try anchor-based parsing
        if not matches:
            matches = self._parse_matches_fallback(soup)

        df = pd.DataFrame(matches)
        if not df.empty:
            save_dataframe(df, self.output_dir / "matches.csv")
        else:
            logger.warning("No Cricbuzz matches extracted")
            (self.output_dir / "matches_raw.html").write_text(
                str(soup), encoding="utf-8"
            )

        return df

    def _parse_match_card(self, card) -> Optional[Dict]:
        """Parse a Cricbuzz match card."""
        # Team names
        teams = card.select("div.cb-ovr-flo, a.cb-text-link")
        if len(teams) < 2:
            return None

        team_texts = [t.get_text(strip=True) for t in teams if t.get_text(strip=True)]
        if len(team_texts) < 2:
            return None

        # Extract scores from team text (e.g., "India 180/5 (20)")
        team1_info = self._parse_team_score(team_texts[0])
        team2_info = self._parse_team_score(team_texts[1])

        # Result
        result_el = card.select_one("div.cb-text-complete, a.cb-text-complete")
        result = result_el.get_text(strip=True) if result_el else ""

        # Match link
        link = card.select_one("a[href*='cricket-scores']") or card.select_one("a[href*='live-cricket-scorecard']")
        match_url = f"{self.base_url}{link['href']}" if link else ""

        # Venue/date info
        info_el = card.select_one("div.text-gray, span.text-gray")
        info_text = info_el.get_text(strip=True) if info_el else ""

        return {
            "team1": standardize_team_name(team1_info["team"]),
            "team2": standardize_team_name(team2_info["team"]),
            "score1": team1_info["score"],
            "score2": team2_info["score"],
            "result": result,
            "info": info_text,
            "match_url": match_url,
            "source": "cricbuzz",
        }

    def _parse_team_score(self, text: str) -> Dict:
        """Parse team name and score from combined text like 'India 180/5 (20)'."""
        import re
        # Try to split name from score
        match = re.match(r"^(.+?)\s+(\d+/\d+.*?)$", text.strip())
        if match:
            return {"team": match.group(1).strip(), "score": match.group(2).strip()}
        return {"team": text.strip(), "score": ""}

    def _parse_matches_fallback(self, soup) -> List[Dict]:
        """Fallback parsing for Cricbuzz matches."""
        matches = []
        # Try to find match links directly
        links = soup.select("a[href*='/live-cricket-scorecard/'], a[href*='/cricket-scores/']")
        for link in links:
            text = link.get_text(strip=True)
            if " vs " in text.lower() or " v " in text.lower():
                parts = text.lower().replace(" v ", " vs ").split(" vs ")
                if len(parts) == 2:
                    matches.append({
                        "team1": standardize_team_name(parts[0].strip()),
                        "team2": standardize_team_name(parts[1].strip()),
                        "score1": "",
                        "score2": "",
                        "result": "",
                        "info": "",
                        "match_url": f"{self.base_url}{link.get('href', '')}",
                        "source": "cricbuzz",
                    })
        return matches

    # ─── Scorecard ───────────────────────────────────────────────────────

    def scrape_scorecard(self, match_url: str) -> Dict:
        """Scrape a Cricbuzz scorecard page."""
        logger.info(f"Scraping Cricbuzz scorecard: {match_url}")
        soup = fetch_page(match_url)
        if not soup:
            return {}

        scorecard = {"batting": [], "bowling": [], "match_info": {}}

        # Cricbuzz batting table rows
        bat_rows = soup.select("div.cb-col.cb-col-100.cb-scrd-itms")
        for row in bat_rows:
            cells = row.select("div.cb-col")
            if len(cells) >= 7:
                name = cells[0].get_text(strip=True)
                if name and name not in ("Extras", "Total", "Did not bat", "Yet to bat"):
                    scorecard["batting"].append({
                        "player": name,
                        "dismissal": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        "runs": safe_int(cells[2].get_text(strip=True)),
                        "balls": safe_int(cells[3].get_text(strip=True)),
                        "fours": safe_int(cells[4].get_text(strip=True)),
                        "sixes": safe_int(cells[5].get_text(strip=True)),
                        "strike_rate": safe_float(cells[6].get_text(strip=True)),
                    })

        # Bowling table
        bowl_rows = soup.select("div.cb-col.cb-col-100.cb-scrd-itms")
        for row in bowl_rows:
            cells = row.select("div.cb-col")
            if len(cells) >= 6:
                name = cells[0].get_text(strip=True)
                # Check if this looks like bowling data (overs format)
                overs_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                if "." in overs_text and name not in ("Extras", "Total"):
                    scorecard["bowling"].append({
                        "player": name,
                        "overs": safe_float(overs_text),
                        "maidens": safe_int(cells[2].get_text(strip=True)),
                        "runs": safe_int(cells[3].get_text(strip=True)),
                        "wickets": safe_int(cells[4].get_text(strip=True)),
                        "economy": safe_float(cells[5].get_text(strip=True)),
                    })

        return scorecard

    # ─── Orchestrator ────────────────────────────────────────────────────

    def scrape_all(self):
        """Run full Cricbuzz scraping pipeline."""
        logger.info("=" * 60)
        logger.info("Starting full Cricbuzz scrape")
        logger.info("=" * 60)

        # 1. Get matches
        matches_df = self.scrape_matches()

        # 2. Scrape scorecards for completed matches
        if not matches_df.empty and "match_url" in matches_df.columns:
            all_batting = []
            all_bowling = []

            for _, row in matches_df.iterrows():
                if row.get("match_url"):
                    card = self.scrape_scorecard(row["match_url"])
                    if card.get("batting"):
                        for b in card["batting"]:
                            b["team1"] = row["team1"]
                            b["team2"] = row["team2"]
                        all_batting.extend(card["batting"])
                    if card.get("bowling"):
                        for b in card["bowling"]:
                            b["team1"] = row["team1"]
                            b["team2"] = row["team2"]
                        all_bowling.extend(card["bowling"])

            if all_batting:
                save_dataframe(pd.DataFrame(all_batting), self.output_dir / "match_batting.csv")
            if all_bowling:
                save_dataframe(pd.DataFrame(all_bowling), self.output_dir / "match_bowling.csv")

        logger.info("Cricbuzz scrape complete!")


if __name__ == "__main__":
    scraper = CricbuzzScraper()
    scraper.scrape_all()
