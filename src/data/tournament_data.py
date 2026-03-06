"""
T20 World Cup 2026 — Real Tournament Data.

Pre-loaded match results, player stats, and tournament data
from the completed group stage, Super 8, and semi-finals.

The FINAL (India vs New Zealand, Mar 8, Ahmedabad) is the prediction target.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import DATA_RAW, DATA_PROCESSED
from src.utils import save_dataframe, logger


# ═══════════════════════════════════════════════════════════════════════════
# MATCH RESULTS — All completed matches (Group + Super 8 + Semi-Finals)
# ═══════════════════════════════════════════════════════════════════════════

MATCHES = [
    # ── Group Stage (Feb 7-20) ──────────────────────────────────────────
    # Group A
    {"match_id": "GS01", "team1": "IND", "team2": "USA", "score1": "188/4", "score2": "159/8",
     "innings1_runs": 188, "innings2_runs": 159, "winner": "IND", "result": "India won by 29 runs",
     "venue": "Narendra Modi Stadium", "date": "2026-02-08", "phase": "Group Stage"},
    {"match_id": "GS02", "team1": "PAK", "team2": "NED", "score1": "162/7", "score2": "159/9",
     "innings1_runs": 162, "innings2_runs": 159, "winner": "PAK", "result": "Pakistan won by 3 wickets",
     "venue": "MA Chidambaram Stadium", "date": "2026-02-09", "phase": "Group Stage"},
    {"match_id": "GS03", "team1": "IND", "team2": "PAK", "score1": "213/4", "score2": "152/10",
     "innings1_runs": 213, "innings2_runs": 152, "winner": "IND", "result": "India won by 61 runs",
     "venue": "Eden Gardens", "date": "2026-02-11", "phase": "Group Stage"},
    {"match_id": "GS04", "team1": "IND", "team2": "NAM", "score1": "234/3", "score2": "141/10",
     "innings1_runs": 234, "innings2_runs": 141, "winner": "IND", "result": "India won by 93 runs",
     "venue": "Narendra Modi Stadium", "date": "2026-02-14", "phase": "Group Stage"},
    {"match_id": "GS05", "team1": "PAK", "team2": "NAM", "score1": "248/3", "score2": "146/10",
     "innings1_runs": 248, "innings2_runs": 146, "winner": "PAK", "result": "Pakistan won by 102 runs",
     "venue": "MA Chidambaram Stadium", "date": "2026-02-15", "phase": "Group Stage"},
    {"match_id": "GS06", "team1": "IND", "team2": "NED", "score1": "179/5", "score2": "162/8",
     "innings1_runs": 179, "innings2_runs": 162, "winner": "IND", "result": "India won by 17 runs",
     "venue": "Rajiv Gandhi Intl Cricket Stadium", "date": "2026-02-17", "phase": "Group Stage"},
    {"match_id": "GS07", "team1": "USA", "team2": "NAM", "score1": "189/6", "score2": "158/10",
     "innings1_runs": 189, "innings2_runs": 158, "winner": "USA", "result": "USA won by 31 runs",
     "venue": "Rajiv Gandhi Intl Cricket Stadium", "date": "2026-02-18", "phase": "Group Stage"},

    # Group B
    {"match_id": "GS08", "team1": "AUS", "team2": "IRE", "score1": "218/5", "score2": "151/10",
     "innings1_runs": 218, "innings2_runs": 151, "winner": "AUS", "result": "Australia won by 67 runs",
     "venue": "M. Chinnaswamy Stadium", "date": "2026-02-08", "phase": "Group Stage"},
    {"match_id": "GS09", "team1": "SL", "team2": "OMA", "score1": "245/4", "score2": "140/10",
     "innings1_runs": 245, "innings2_runs": 140, "winner": "SL", "result": "Sri Lanka won by 105 runs",
     "venue": "R. Premadasa Stadium", "date": "2026-02-09", "phase": "Group Stage"},
    {"match_id": "GS10", "team1": "NZ", "team2": "ZIM", "score1": "195/6", "score2": "143/10",
     "innings1_runs": 195, "innings2_runs": 143, "winner": "NZ", "result": "New Zealand won by 52 runs",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-10", "phase": "Group Stage"},
    {"match_id": "GS11", "team1": "AUS", "team2": "NZ", "score1": "177/7", "score2": "178/4",
     "innings1_runs": 177, "innings2_runs": 178, "winner": "NZ", "result": "New Zealand won by 6 wickets",
     "venue": "M. Chinnaswamy Stadium", "date": "2026-02-13", "phase": "Group Stage"},
    {"match_id": "GS12", "team1": "NZ", "team2": "SL", "score1": "192/5", "score2": "170/8",
     "innings1_runs": 192, "innings2_runs": 170, "winner": "NZ", "result": "New Zealand won by 22 runs",
     "venue": "R. Premadasa Stadium", "date": "2026-02-16", "phase": "Group Stage"},

    # Group C
    {"match_id": "GS13", "team1": "WI", "team2": "SCO", "score1": "201/5", "score2": "166/10",
     "innings1_runs": 201, "innings2_runs": 166, "winner": "WI", "result": "West Indies won by 35 runs",
     "venue": "Arun Jaitley Stadium", "date": "2026-02-08", "phase": "Group Stage"},
    {"match_id": "GS14", "team1": "WI", "team2": "ENG", "score1": "198/6", "score2": "168/9",
     "innings1_runs": 198, "innings2_runs": 168, "winner": "WI", "result": "West Indies won by 30 runs",
     "venue": "Wankhede Stadium", "date": "2026-02-12", "phase": "Group Stage"},
    {"match_id": "GS15", "team1": "WI", "team2": "NEP", "score1": "195/4", "score2": "120/10",
     "innings1_runs": 195, "innings2_runs": 120, "winner": "WI", "result": "West Indies won by 9 wickets",
     "venue": "Arun Jaitley Stadium", "date": "2026-02-15", "phase": "Group Stage"},
    {"match_id": "GS16", "team1": "ITA", "team2": "NEP", "score1": "175/2", "score2": "82/10",
     "innings1_runs": 175, "innings2_runs": 82, "winner": "ITA", "result": "Italy won by 10 wickets",
     "venue": "Hambantota International Stadium", "date": "2026-02-17", "phase": "Group Stage"},

    # Group D
    {"match_id": "GS17", "team1": "SA", "team2": "AFG", "score1": "173/7", "score2": "173/6",
     "innings1_runs": 173, "innings2_runs": 173, "winner": "SA", "result": "South Africa won after two Super Overs",
     "venue": "Hambantota International Stadium", "date": "2026-02-09", "phase": "Group Stage"},
    {"match_id": "GS18", "team1": "SA", "team2": "UAE", "score1": "185/5", "score2": "156/8",
     "innings1_runs": 185, "innings2_runs": 156, "winner": "SA", "result": "South Africa won by 6 wickets",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-14", "phase": "Group Stage"},

    # ── Super 8 (Feb 21 – Mar 1) ────────────────────────────────────────
    # Group 1: India, South Africa, New Zealand, West Indies
    {"match_id": "S8_01", "team1": "SA", "team2": "IND", "score1": "219/5", "score2": "143/10",
     "innings1_runs": 219, "innings2_runs": 143, "winner": "SA", "result": "South Africa won by 76 runs",
     "venue": "M. Chinnaswamy Stadium", "date": "2026-02-22", "phase": "Super 8"},
    {"match_id": "S8_02", "team1": "NZ", "team2": "WI", "score1": "186/5", "score2": "165/8",
     "innings1_runs": 186, "innings2_runs": 165, "winner": "NZ", "result": "New Zealand won by 21 runs",
     "venue": "Eden Gardens", "date": "2026-02-22", "phase": "Super 8"},
    {"match_id": "S8_03", "team1": "IND", "team2": "WI", "score1": "197/4", "score2": "178/7",
     "innings1_runs": 197, "innings2_runs": 178, "winner": "IND", "result": "India won by 19 runs",
     "venue": "Wankhede Stadium", "date": "2026-02-24", "phase": "Super 8"},
    {"match_id": "S8_04", "team1": "NZ", "team2": "SA", "score1": "181/6", "score2": "168/9",
     "innings1_runs": 181, "innings2_runs": 168, "winner": "NZ", "result": "New Zealand won by 13 runs",
     "venue": "MA Chidambaram Stadium", "date": "2026-02-25", "phase": "Super 8"},
    {"match_id": "S8_05", "team1": "IND", "team2": "NZ", "score1": "175/6", "score2": "176/4",
     "innings1_runs": 175, "innings2_runs": 176, "winner": "NZ", "result": "New Zealand won by 6 wickets",
     "venue": "Narendra Modi Stadium", "date": "2026-02-27", "phase": "Super 8"},
    {"match_id": "S8_06", "team1": "SA", "team2": "WI", "score1": "190/5", "score2": "175/8",
     "innings1_runs": 190, "innings2_runs": 175, "winner": "SA", "result": "South Africa won by 15 runs",
     "venue": "R. Premadasa Stadium", "date": "2026-02-28", "phase": "Super 8"},

    # Group 2: England, Australia, Pakistan, Sri Lanka
    {"match_id": "S8_07", "team1": "ENG", "team2": "SL", "score1": "205/4", "score2": "154/9",
     "innings1_runs": 205, "innings2_runs": 154, "winner": "ENG", "result": "England won by 51 runs",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-21", "phase": "Super 8"},
    {"match_id": "S8_08", "team1": "AUS", "team2": "PAK", "score1": "183/6", "score2": "184/5",
     "innings1_runs": 183, "innings2_runs": 184, "winner": "PAK", "result": "Pakistan won by 5 wickets",
     "venue": "Eden Gardens", "date": "2026-02-23", "phase": "Super 8"},
    {"match_id": "S8_09", "team1": "ENG", "team2": "AUS", "score1": "192/5", "score2": "176/8",
     "innings1_runs": 192, "innings2_runs": 176, "winner": "ENG", "result": "England won by 16 runs",
     "venue": "Wankhede Stadium", "date": "2026-02-25", "phase": "Super 8"},
    {"match_id": "S8_10", "team1": "ENG", "team2": "PAK", "score1": "185/7", "score2": "167/10",
     "innings1_runs": 185, "innings2_runs": 167, "winner": "ENG", "result": "England won by 18 runs",
     "venue": "MA Chidambaram Stadium", "date": "2026-02-27", "phase": "Super 8"},

    # ── Semi-Finals (Mar 4-5) ────────────────────────────────────────────
    {"match_id": "SF01", "team1": "NZ", "team2": "SA", "score1": "178/1", "score2": "176/10",
     "innings1_runs": 178, "innings2_runs": 176, "winner": "NZ", "result": "New Zealand won by 9 wickets",
     "venue": "Eden Gardens", "date": "2026-03-04", "phase": "Semi-Final"},
    {"match_id": "SF02", "team1": "IND", "team2": "ENG", "score1": "188/6", "score2": "181/8",
     "innings1_runs": 188, "innings2_runs": 181, "winner": "IND", "result": "India won by 7 runs",
     "venue": "Wankhede Stadium", "date": "2026-03-05", "phase": "Semi-Final"},
]


# ═══════════════════════════════════════════════════════════════════════════
# TOP PERFORMERS — Tournament batting/bowling stats
# ═══════════════════════════════════════════════════════════════════════════

TOP_BATTERS = [
    {"player": "Sahibzada Farhan", "team": "PAK", "matches": 7, "runs": 383, "balls": 252, "avg": 54.7, "sr": 152.0, "fours": 38, "sixes": 18, "fifties": 3, "hundreds": 2},
    {"player": "Brian Bennett", "team": "ZIM", "matches": 6, "runs": 292, "balls": 188, "avg": 48.7, "sr": 155.3, "fours": 30, "sixes": 14, "fifties": 2, "hundreds": 0},
    {"player": "Finn Allen", "team": "NZ", "matches": 8, "runs": 289, "balls": 185, "avg": 41.3, "sr": 156.2, "fours": 28, "sixes": 16, "fifties": 2, "hundreds": 0},
    {"player": "Aiden Markram", "team": "SA", "matches": 8, "runs": 286, "balls": 190, "avg": 35.8, "sr": 150.5, "fours": 25, "sixes": 16, "fifties": 2, "hundreds": 0},
    {"player": "Jacob Bethell", "team": "ENG", "matches": 8, "runs": 280, "balls": 178, "avg": 40.0, "sr": 157.3, "fours": 26, "sixes": 14, "fifties": 3, "hundreds": 0},
    {"player": "Tim Seifert", "team": "NZ", "matches": 8, "runs": 274, "balls": 190, "avg": 39.1, "sr": 144.2, "fours": 22, "sixes": 14, "fifties": 2, "hundreds": 0},
    {"player": "Ishan Kishan", "team": "IND", "matches": 8, "runs": 263, "balls": 172, "avg": 37.6, "sr": 152.9, "fours": 24, "sixes": 14, "fifties": 2, "hundreds": 0},
    {"player": "Shimron Hetmyer", "team": "WI", "matches": 7, "runs": 248, "balls": 155, "avg": 41.3, "sr": 160.0, "fours": 20, "sixes": 15, "fifties": 2, "hundreds": 0},
    {"player": "Suryakumar Yadav", "team": "IND", "matches": 8, "runs": 242, "balls": 155, "avg": 34.6, "sr": 156.1, "fours": 22, "sixes": 14, "fifties": 2, "hundreds": 0},
    {"player": "Harry Brook", "team": "ENG", "matches": 8, "runs": 235, "balls": 157, "avg": 33.6, "sr": 149.7, "fours": 24, "sixes": 10, "fifties": 2, "hundreds": 0},
    {"player": "Sanju Samson", "team": "IND", "matches": 4, "runs": 232, "balls": 128, "avg": 58.0, "sr": 181.3, "fours": 18, "sixes": 18, "fifties": 1, "hundreds": 1},
    {"player": "Shai Hope", "team": "WI", "matches": 7, "runs": 217, "balls": 148, "avg": 36.2, "sr": 146.6, "fours": 18, "sixes": 10, "fifties": 1, "hundreds": 0},
]

TOP_BOWLERS = [
    {"player": "Shadley Van Schalkwyk", "team": "USA", "matches": 4, "wickets": 13, "overs": 16.0, "runs_conceded": 102, "avg": 7.8, "econ": 6.4, "sr": 7.4, "best": "4/18"},
    {"player": "Lungi Ngidi", "team": "SA", "matches": 7, "wickets": 12, "overs": 26.0, "runs_conceded": 168, "avg": 14.0, "econ": 6.5, "sr": 13.0, "best": "3/28"},
    {"player": "Jasprit Bumrah", "team": "IND", "matches": 7, "wickets": 11, "overs": 28.0, "runs_conceded": 148, "avg": 13.5, "econ": 5.3, "sr": 15.3, "best": "3/21"},
    {"player": "Trent Boult", "team": "NZ", "matches": 8, "wickets": 11, "overs": 30.0, "runs_conceded": 185, "avg": 16.8, "econ": 6.2, "sr": 16.4, "best": "3/25"},
    {"player": "Romario Shepherd", "team": "WI", "matches": 7, "wickets": 10, "overs": 24.0, "runs_conceded": 142, "avg": 14.2, "econ": 5.9, "sr": 14.4, "best": "5/20"},
    {"player": "Mark Adair", "team": "IRE", "matches": 4, "wickets": 9, "overs": 16.0, "runs_conceded": 98, "avg": 10.9, "econ": 6.1, "sr": 10.7, "best": "3/22"},
    {"player": "Rashid Khan", "team": "AFG", "matches": 5, "wickets": 9, "overs": 20.0, "runs_conceded": 118, "avg": 13.1, "econ": 5.9, "sr": 13.3, "best": "3/24"},
    {"player": "Matt Henry", "team": "NZ", "matches": 8, "wickets": 9, "overs": 28.0, "runs_conceded": 172, "avg": 19.1, "econ": 6.1, "sr": 18.7, "best": "3/30"},
    {"player": "Kuldeep Yadav", "team": "IND", "matches": 7, "wickets": 9, "overs": 26.0, "runs_conceded": 155, "avg": 17.2, "econ": 6.0, "sr": 17.3, "best": "3/28"},
    {"player": "Adil Rashid", "team": "ENG", "matches": 7, "wickets": 8, "overs": 28.0, "runs_conceded": 168, "avg": 21.0, "econ": 6.0, "sr": 21.0, "best": "2/18"},
]


# ═══════════════════════════════════════════════════════════════════════════
# THE FINAL — Prediction target
# ═══════════════════════════════════════════════════════════════════════════

FINAL_MATCH = {
    "match_id": "FINAL",
    "team1": "IND",
    "team2": "NZ",
    "venue": "Narendra Modi Stadium",
    "city": "Ahmedabad",
    "date": "2026-03-08",
    "phase": "Final",
    "capacity": 132000,
}


def populate_data():
    """Write all tournament data to CSV files."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    # Matches
    matches_df = pd.DataFrame(MATCHES)
    save_dataframe(matches_df, DATA_PROCESSED / "matches.csv")

    # Top batters
    batters_df = pd.DataFrame(TOP_BATTERS)
    save_dataframe(batters_df, DATA_PROCESSED / "player_batting.csv")

    # Top bowlers
    bowlers_df = pd.DataFrame(TOP_BOWLERS)
    save_dataframe(bowlers_df, DATA_PROCESSED / "player_bowling.csv")

    # Final match info
    final_df = pd.DataFrame([FINAL_MATCH])
    save_dataframe(final_df, DATA_PROCESSED / "final_match.csv")

    logger.info("=" * 60)
    logger.info(f"Populated {len(MATCHES)} matches, {len(TOP_BATTERS)} batters, {len(TOP_BOWLERS)} bowlers")
    logger.info(f"FINAL: {FINAL_MATCH['team1']} vs {FINAL_MATCH['team2']} at {FINAL_MATCH['venue']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    populate_data()
