"""
Data Cleaning Pipeline for T20 World Cup 2026.

Merges and standardizes data from ESPN, Cricbuzz, and ICC into
unified analytical tables: matches, innings_summary, player_match_stats.
"""

import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    RAW_ESPN, RAW_CRICBUZZ, RAW_ICC,
    DATA_PROCESSED, TEAM_CODES
)
from src.utils import (
    standardize_team_name, standardize_player_name,
    safe_float, safe_int, save_dataframe, load_dataframe,
    generate_match_id, logger
)


class DataCleaner:
    """Cleans and integrates multi-source cricket data."""

    def __init__(self):
        self.output_dir = DATA_PROCESSED
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ─── Load Raw Data ───────────────────────────────────────────────────

    def _load_source(self, source_dir: Path, filename: str) -> pd.DataFrame:
        """Safely load a CSV from a source directory."""
        filepath = source_dir / filename
        if filepath.exists():
            return load_dataframe(filepath) or pd.DataFrame()
        logger.warning(f"File not found: {filepath}")
        return pd.DataFrame()

    # ─── Merge Fixtures ──────────────────────────────────────────────────

    def merge_fixtures(self) -> pd.DataFrame:
        """
        Merge fixtures from ESPN, Cricbuzz, and ICC into a single
        unified matches table. ESPN is primary; others fill gaps.
        """
        logger.info("Merging fixtures from all sources...")

        espn = self._load_source(RAW_ESPN, "fixtures.csv")
        cricbuzz = self._load_source(RAW_CRICBUZZ, "matches.csv")
        icc = self._load_source(RAW_ICC, "fixtures.csv")

        # Standardize columns across sources
        dfs = []
        for df, source in [(espn, "espn"), (cricbuzz, "cricbuzz"), (icc, "icc")]:
            if df.empty:
                continue
            df = df.copy()
            df["source"] = source

            # Ensure common columns exist
            for col in ["team1", "team2", "score1", "score2", "result", "venue", "date"]:
                if col not in df.columns:
                    df[col] = ""

            # Standardize team names
            df["team1"] = df["team1"].apply(standardize_team_name)
            df["team2"] = df["team2"].apply(standardize_team_name)

            dfs.append(df[["team1", "team2", "score1", "score2", "result", "venue", "date", "source"]])

        if not dfs:
            logger.warning("No fixture data available from any source")
            return pd.DataFrame()

        combined = pd.concat(dfs, ignore_index=True)

        # Deduplicate: keep ESPN version if available, else Cricbuzz, else ICC
        source_priority = {"espn": 0, "cricbuzz": 1, "icc": 2}
        combined["priority"] = combined["source"].map(source_priority)
        combined = combined.sort_values("priority")

        # Create match key for dedup
        combined["match_key"] = combined.apply(
            lambda r: "_".join(sorted([str(r["team1"]), str(r["team2"])])) + "_" + str(r["date"]),
            axis=1,
        )
        matches = combined.drop_duplicates(subset="match_key", keep="first").copy()
        matches = matches.drop(columns=["priority", "match_key"])

        # Generate match IDs
        matches["match_id"] = matches.apply(
            lambda r: generate_match_id(r["team1"], r["team2"], r["date"]), axis=1
        )

        # Parse scores into components
        matches = self._parse_scores(matches)

        # Determine winner
        matches["winner"] = matches.apply(self._determine_winner, axis=1)

        # Reorder columns
        col_order = [
            "match_id", "team1", "team2", "score1", "score2",
            "innings1_runs", "innings1_wickets", "innings1_overs",
            "innings2_runs", "innings2_wickets", "innings2_overs",
            "winner", "result", "venue", "date", "source",
        ]
        for c in col_order:
            if c not in matches.columns:
                matches[c] = ""

        matches = matches[col_order].reset_index(drop=True)

        save_dataframe(matches, self.output_dir / "matches.csv")
        logger.info(f"Merged {len(matches)} unique matches")
        return matches

    def _parse_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse score strings like '180/5 (20)' into runs, wickets, overs."""
        import re

        for innings_num, score_col in [(1, "score1"), (2, "score2")]:
            runs_col = f"innings{innings_num}_runs"
            wkts_col = f"innings{innings_num}_wickets"
            overs_col = f"innings{innings_num}_overs"

            df[runs_col] = 0
            df[wkts_col] = 0
            df[overs_col] = 0.0

            for idx, val in df[score_col].items():
                if pd.isna(val) or not str(val).strip():
                    continue
                score_str = str(val).strip()

                # Match patterns: "180/5 (20)", "180/5", "180"
                m = re.match(r"(\d+)(?:/(\d+))?(?:\s*\((\d+(?:\.\d+)?)\))?", score_str)
                if m:
                    df.at[idx, runs_col] = int(m.group(1))
                    df.at[idx, wkts_col] = int(m.group(2)) if m.group(2) else 10
                    df.at[idx, overs_col] = float(m.group(3)) if m.group(3) else 20.0

        return df

    def _determine_winner(self, row) -> str:
        """Determine match winner from result text or scores."""
        result = str(row.get("result", "")).lower()

        # Check if result text contains team name
        for team_col in ["team1", "team2"]:
            team = str(row.get(team_col, ""))
            team_name = TEAM_CODES.get(team, team)
            if team.lower() in result or team_name.lower() in result:
                if "won" in result:
                    return team

        # Fallback: compare runs
        r1 = safe_int(row.get("innings1_runs", 0))
        r2 = safe_int(row.get("innings2_runs", 0))
        if r1 > r2 and r1 > 0:
            return str(row.get("team1", ""))
        elif r2 > r1 and r2 > 0:
            return str(row.get("team2", ""))

        return ""

    # ─── Player Stats ────────────────────────────────────────────────────

    def clean_player_stats(self) -> pd.DataFrame:
        """
        Clean and merge player match stats (batting + bowling) from ESPN and Cricbuzz.
        """
        logger.info("Cleaning player match stats...")

        # Load batting data
        espn_bat = self._load_source(RAW_ESPN, "match_batting.csv")
        cb_bat = self._load_source(RAW_CRICBUZZ, "match_batting.csv")

        batting = pd.concat([espn_bat, cb_bat], ignore_index=True) if not espn_bat.empty or not cb_bat.empty else pd.DataFrame()

        if not batting.empty:
            batting["player"] = batting["player"].apply(standardize_player_name)
            batting = batting.drop_duplicates(subset=["player", "team1", "team2", "runs", "balls"], keep="first")
            save_dataframe(batting, self.output_dir / "player_batting.csv")

        # Load bowling data
        espn_bowl = self._load_source(RAW_ESPN, "match_bowling.csv")
        cb_bowl = self._load_source(RAW_CRICBUZZ, "match_bowling.csv")

        bowling = pd.concat([espn_bowl, cb_bowl], ignore_index=True) if not espn_bowl.empty or not cb_bowl.empty else pd.DataFrame()

        if not bowling.empty:
            bowling["player"] = bowling["player"].apply(standardize_player_name)
            bowling = bowling.drop_duplicates(subset=["player", "team1", "team2", "overs", "wickets"], keep="first")
            save_dataframe(bowling, self.output_dir / "player_bowling.csv")

        logger.info(f"Cleaned {len(batting)} batting + {len(bowling)} bowling records")
        return batting

    # ─── Tournament Aggregates ───────────────────────────────────────────

    def clean_tournament_stats(self) -> pd.DataFrame:
        """Clean tournament-level stats from ESPN and ICC."""
        logger.info("Cleaning tournament aggregate stats...")

        espn_bat = self._load_source(RAW_ESPN, "tournament_batting.csv")
        espn_bowl = self._load_source(RAW_ESPN, "tournament_bowling.csv")
        icc_stats = self._load_source(RAW_ICC, "tournament_stats.csv")

        dfs = []
        for df, label in [(espn_bat, "espn_batting"), (espn_bowl, "espn_bowling"), (icc_stats, "icc_stats")]:
            if not df.empty:
                df = df.copy()
                df["stat_source"] = label
                dfs.append(df)

        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            save_dataframe(combined, self.output_dir / "player_tournament_stats.csv")
            return combined

        return pd.DataFrame()

    # ─── Orchestrator ────────────────────────────────────────────────────

    def clean_all(self):
        """Run full cleaning pipeline."""
        logger.info("=" * 60)
        logger.info("Starting data cleaning pipeline")
        logger.info("=" * 60)

        self.merge_fixtures()
        self.clean_player_stats()
        self.clean_tournament_stats()

        logger.info("Data cleaning complete!")


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.clean_all()
