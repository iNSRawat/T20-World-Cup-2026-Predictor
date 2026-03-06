"""
Feature Engineering for T20 World Cup 2026 Win Prediction.

Creates match-level features from clean data:
  - Team strength (batting + bowling indices)
  - Venue profile (avg score, chase/defend bias)
  - Toss features
  - Form metrics (win/loss streak, NRR trend)
  - Match context (group vs knockout, day/night)

Outputs: data_processed/match_features.csv
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import (
    DATA_PROCESSED, POWERPLAY_OVERS, MIDDLE_OVERS,
    DEATH_OVERS, FORM_WINDOW, PHASES, VENUES
)
from src.utils import (
    safe_float, safe_int, save_dataframe, load_dataframe, logger
)


class FeatureEngineer:
    """Creates ML-ready features for match prediction."""

    def __init__(self):
        self.output_dir = DATA_PROCESSED
        self.matches = None
        self.batting = None
        self.bowling = None

    def load_data(self):
        """Load cleaned data."""
        self.matches = load_dataframe(self.output_dir / "matches.csv")
        self.batting = load_dataframe(self.output_dir / "player_batting.csv")
        self.bowling = load_dataframe(self.output_dir / "player_bowling.csv")

        if self.matches is None or self.matches.empty:
            logger.error("No match data found — run cleaner first")
            return False
        return True

    # ─── Team Strength Features ──────────────────────────────────────────

    def compute_team_strength(self, team: str, before_date: str = None) -> dict:
        """
        Compute batting and bowling strength indices for a team
        based on match-level data (optionally filtered to before a date).
        """
        df = self.matches.copy()
        if before_date:
            df = df[df["date"] < before_date]

        # Matches involving this team
        team_matches = df[(df["team1"] == team) | (df["team2"] == team)]

        if team_matches.empty:
            return {
                "bat_strength": 0.5,
                "bowl_strength": 0.5,
                "win_rate": 0.5,
                "avg_score": 150,
                "avg_conceded": 150,
            }

        wins = len(team_matches[team_matches["winner"] == team])
        total = len(team_matches)

        # Compute average runs scored and conceded
        scores = []
        conceded = []
        for _, row in team_matches.iterrows():
            if row["team1"] == team:
                scores.append(safe_int(row.get("innings1_runs", 0)))
                conceded.append(safe_int(row.get("innings2_runs", 0)))
            else:
                scores.append(safe_int(row.get("innings2_runs", 0)))
                conceded.append(safe_int(row.get("innings1_runs", 0)))

        avg_score = np.mean(scores) if scores else 150
        avg_conceded = np.mean(conceded) if conceded else 150

        # Normalize strength to [0, 1]
        bat_strength = min(1.0, avg_score / 200)  # 200 is ~max T20 score
        bowl_strength = min(1.0, 1 - (avg_conceded / 200))

        return {
            "bat_strength": round(bat_strength, 3),
            "bowl_strength": round(bowl_strength, 3),
            "win_rate": round(wins / total, 3) if total > 0 else 0.5,
            "avg_score": round(avg_score, 1),
            "avg_conceded": round(avg_conceded, 1),
        }

    # ─── Venue Features ──────────────────────────────────────────────────

    def compute_venue_features(self, venue: str) -> dict:
        """
        Compute venue-specific features:
        - Average first innings score
        - Win % for batting first vs chasing
        - Pace/spin friendliness (proxy)
        """
        df = self.matches.copy()
        venue_matches = df[df["venue"].str.contains(venue, case=False, na=False)]

        if venue_matches.empty:
            # Use defaults based on known venue data
            venue_info = VENUES.get(venue, {})
            return {
                "venue_avg_first_innings": 165,
                "venue_chase_win_pct": 0.50,
                "venue_matches_played": 0,
                "venue_capacity": venue_info.get("capacity", 0),
                "venue_country": venue_info.get("country", ""),
            }

        avg_first = venue_matches["innings1_runs"].mean()

        # Chase success: team2 (chaser) won
        chasers_won = len(venue_matches[venue_matches.apply(
            lambda r: r["winner"] == r["team2"], axis=1
        )])
        total = len(venue_matches)
        chase_pct = chasers_won / total if total > 0 else 0.5

        return {
            "venue_avg_first_innings": round(avg_first, 1),
            "venue_chase_win_pct": round(chase_pct, 3),
            "venue_matches_played": total,
            "venue_capacity": VENUES.get(venue, {}).get("capacity", 0),
            "venue_country": VENUES.get(venue, {}).get("country", ""),
        }

    # ─── Form Features ───────────────────────────────────────────────────

    def compute_form(self, team: str, before_date: str = None, window: int = FORM_WINDOW) -> dict:
        """
        Compute recent form metrics:
        - Win/loss in last N matches
        - Win streak
        - Trend (improving/declining)
        """
        df = self.matches.copy()
        if before_date:
            df = df[df["date"] < before_date]

        team_matches = df[(df["team1"] == team) | (df["team2"] == team)]
        team_matches = team_matches.sort_values("date", ascending=False).head(window)

        if team_matches.empty:
            return {
                "form_wins": 0,
                "form_losses": 0,
                "form_win_rate": 0.5,
                "form_streak": 0,
            }

        wins = len(team_matches[team_matches["winner"] == team])
        losses = len(team_matches) - wins

        # Win streak (consecutive wins from most recent)
        streak = 0
        for _, row in team_matches.iterrows():
            if row["winner"] == team:
                streak += 1
            else:
                break

        return {
            "form_wins": wins,
            "form_losses": losses,
            "form_win_rate": round(wins / len(team_matches), 3),
            "form_streak": streak,
        }

    # ─── Toss Features ───────────────────────────────────────────────────

    def extract_toss_features(self, row: pd.Series) -> dict:
        """Extract toss-related features from a match row."""
        result_text = str(row.get("result", "")).lower()

        toss_winner = ""
        toss_decision = ""

        # Try to parse from result or dedicated columns
        if "toss" in result_text:
            # Common pattern: "X won the toss and elected to bat/field"
            for team in [row.get("team1", ""), row.get("team2", "")]:
                if str(team).lower() in result_text:
                    toss_winner = team
                    break

            if "bat" in result_text:
                toss_decision = "bat"
            elif "field" in result_text or "bowl" in result_text:
                toss_decision = "field"

        return {
            "toss_winner": toss_winner,
            "toss_decision": toss_decision,
            "toss_winner_is_team1": 1 if toss_winner == row.get("team1") else 0,
        }

    # ─── Match Context Features ──────────────────────────────────────────

    def compute_match_context(self, row: pd.Series, match_idx: int, total_matches: int) -> dict:
        """Compute match context features."""
        # Determine phase based on match number (approximate)
        progress = match_idx / max(total_matches, 1)
        if progress < 0.6:
            phase = "Group Stage"
        elif progress < 0.85:
            phase = "Super 8"
        elif progress < 0.95:
            phase = "Semi-Final"
        else:
            phase = "Final"

        return {
            "phase": phase,
            "is_knockout": 1 if phase in ("Semi-Final", "Final") else 0,
            "match_number": match_idx + 1,
            "tournament_progress": round(progress, 3),
        }

    # ─── Build Full Feature Matrix ───────────────────────────────────────

    def build_features(self) -> pd.DataFrame:
        """
        Build the full match-level feature matrix for ML.
        Each row = one match with features for both teams.
        """
        if not self.load_data():
            return pd.DataFrame()

        logger.info("Building feature matrix...")

        features = []
        total = len(self.matches)

        for idx, row in self.matches.iterrows():
            team1 = row["team1"]
            team2 = row["team2"]
            date = row.get("date", "")
            venue = row.get("venue", "")

            # Team strength
            t1_strength = self.compute_team_strength(team1, before_date=date)
            t2_strength = self.compute_team_strength(team2, before_date=date)

            # Venue
            venue_feats = self.compute_venue_features(venue)

            # Form
            t1_form = self.compute_form(team1, before_date=date)
            t2_form = self.compute_form(team2, before_date=date)

            # Toss
            toss_feats = self.extract_toss_features(row)

            # Context
            ctx = self.compute_match_context(row, idx, total)

            # Target variable
            winner = row.get("winner", "")
            target = 1 if winner == team1 else (0 if winner == team2 else -1)

            feature_row = {
                "match_id": row.get("match_id", ""),
                "team1": team1,
                "team2": team2,
                "date": date,
                "venue": venue,

                # Team 1 features
                "t1_bat_strength": t1_strength["bat_strength"],
                "t1_bowl_strength": t1_strength["bowl_strength"],
                "t1_win_rate": t1_strength["win_rate"],
                "t1_avg_score": t1_strength["avg_score"],
                "t1_avg_conceded": t1_strength["avg_conceded"],
                "t1_form_win_rate": t1_form["form_win_rate"],
                "t1_form_streak": t1_form["form_streak"],

                # Team 2 features
                "t2_bat_strength": t2_strength["bat_strength"],
                "t2_bowl_strength": t2_strength["bowl_strength"],
                "t2_win_rate": t2_strength["win_rate"],
                "t2_avg_score": t2_strength["avg_score"],
                "t2_avg_conceded": t2_strength["avg_conceded"],
                "t2_form_win_rate": t2_form["form_win_rate"],
                "t2_form_streak": t2_form["form_streak"],

                # Differential features (more powerful for models)
                "strength_diff_bat": t1_strength["bat_strength"] - t2_strength["bat_strength"],
                "strength_diff_bowl": t1_strength["bowl_strength"] - t2_strength["bowl_strength"],
                "win_rate_diff": t1_strength["win_rate"] - t2_strength["win_rate"],
                "form_diff": t1_form["form_win_rate"] - t2_form["form_win_rate"],

                # Venue
                **venue_feats,

                # Toss
                **toss_feats,

                # Context
                **ctx,

                # Target
                "team1_won": target,
            }

            features.append(feature_row)

        df = pd.DataFrame(features)

        # Drop matches with unknown winner
        df = df[df["team1_won"] != -1].reset_index(drop=True)

        save_dataframe(df, self.output_dir / "match_features.csv")
        logger.info(f"Built feature matrix: {df.shape[0]} matches × {df.shape[1]} features")
        return df

    # ─── Orchestrator ────────────────────────────────────────────────────

    def engineer_all(self):
        """Run full feature engineering pipeline."""
        logger.info("=" * 60)
        logger.info("Starting feature engineering pipeline")
        logger.info("=" * 60)

        self.build_features()

        logger.info("Feature engineering complete!")


if __name__ == "__main__":
    engineer = FeatureEngineer()
    engineer.engineer_all()
