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
     "innings1_runs": 162, "innings2_runs": 159, "winner": "PAK", "result": "Pakistan won by 3 runs",
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
     "innings1_runs": 195, "innings2_runs": 120, "winner": "WI", "result": "West Indies won by 75 runs",
     "venue": "Arun Jaitley Stadium", "date": "2026-02-15", "phase": "Group Stage"},
    {"match_id": "GS16", "team1": "ITA", "team2": "NEP", "score1": "175/2", "score2": "82/10",
     "innings1_runs": 175, "innings2_runs": 82, "winner": "ITA", "result": "Italy won by 93 runs",
     "venue": "Hambantota International Stadium", "date": "2026-02-17", "phase": "Group Stage"},

    # Group D
    {"match_id": "GS17", "team1": "SA", "team2": "AFG", "score1": "173/7", "score2": "173/6",
     "innings1_runs": 173, "innings2_runs": 173, "winner": "SA", "result": "South Africa won after two Super Overs",
     "venue": "Hambantota International Stadium", "date": "2026-02-09", "phase": "Group Stage"},
    {"match_id": "GS18", "team1": "SA", "team2": "UAE", "score1": "185/5", "score2": "156/8",
     "innings1_runs": 185, "innings2_runs": 156, "winner": "SA", "result": "South Africa won by 29 runs",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-14", "phase": "Group Stage"},

    # ── Super 8 (Feb 21 – Mar 1) ────────────────────────────────────────
    # Group 1: India, South Africa, Zimbabwe, West Indies
    {"match_id": "S8_01", "team1": "SA", "team2": "IND", "score1": "187/7", "score2": "111/10",
     "innings1_runs": 187, "innings2_runs": 111, "winner": "SA", "result": "South Africa won by 76 runs",
     "venue": "Narendra Modi Stadium", "date": "2026-02-22", "phase": "Super 8"},
    {"match_id": "S8_02", "team1": "WI", "team2": "ZIM", "score1": "254/6", "score2": "147/10",
     "innings1_runs": 254, "innings2_runs": 147, "winner": "WI", "result": "West Indies won by 107 runs",
     "venue": "Wankhede Stadium", "date": "2026-02-23", "phase": "Super 8"},
    {"match_id": "S8_03", "team1": "IND", "team2": "ZIM", "score1": "256/4", "score2": "184/6",
     "innings1_runs": 256, "innings2_runs": 184, "winner": "IND", "result": "India won by 72 runs",
     "venue": "MA Chidambaram Stadium", "date": "2026-02-26", "phase": "Super 8"},
    {"match_id": "S8_04", "team1": "WI", "team2": "SA", "score1": "176/8", "score2": "177/1",
     "innings1_runs": 176, "innings2_runs": 177, "winner": "SA", "result": "South Africa won by 9 wickets",
     "venue": "Narendra Modi Stadium", "date": "2026-02-26", "phase": "Super 8"},
    {"match_id": "S8_05", "team1": "ZIM", "team2": "SA", "score1": "153/7", "score2": "154/5",
     "innings1_runs": 153, "innings2_runs": 154, "winner": "SA", "result": "South Africa won by 5 wickets",
     "venue": "Arun Jaitley Stadium", "date": "2026-03-01", "phase": "Super 8"},
    {"match_id": "S8_06", "team1": "IND", "team2": "WI", "score1": "199/5", "score2": "195/4",
     "innings1_runs": 199, "innings2_runs": 195, "winner": "IND", "result": "India won by 5 wickets",
     "venue": "Eden Gardens", "date": "2026-03-02", "phase": "Super 8"},

    # Group 2: England, New Zealand, Pakistan, Sri Lanka
    {"match_id": "S8_07", "team1": "PAK", "team2": "NZ", "score1": "-", "score2": "-",
     "innings1_runs": 0, "innings2_runs": 0, "winner": "No Result", "result": "Match Abandoned",
     "venue": "R. Premadasa Stadium", "date": "2026-02-21", "phase": "Super 8"},
    {"match_id": "S8_08", "team1": "ENG", "team2": "SL", "score1": "146/9", "score2": "95/10",
     "innings1_runs": 146, "innings2_runs": 95, "winner": "ENG", "result": "England won by 51 runs",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-22", "phase": "Super 8"},
    {"match_id": "S8_09", "team1": "PAK", "team2": "ENG", "score1": "164/9", "score2": "166/8",
     "innings1_runs": 164, "innings2_runs": 166, "winner": "ENG", "result": "England won by 2 wickets",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-24", "phase": "Super 8"},
    {"match_id": "S8_10", "team1": "NZ", "team2": "SL", "score1": "168/7", "score2": "107/8",
     "innings1_runs": 168, "innings2_runs": 107, "winner": "NZ", "result": "New Zealand won by 61 runs",
     "venue": "R. Premadasa Stadium", "date": "2026-02-25", "phase": "Super 8"},
    {"match_id": "S8_11", "team1": "NZ", "team2": "ENG", "score1": "159/7", "score2": "161/6",
     "innings1_runs": 159, "innings2_runs": 161, "winner": "ENG", "result": "England won by 4 wickets",
     "venue": "R. Premadasa Stadium", "date": "2026-02-27", "phase": "Super 8"},
    {"match_id": "S8_12", "team1": "PAK", "team2": "SL", "score1": "212/8", "score2": "207/6",
     "innings1_runs": 212, "innings2_runs": 207, "winner": "PAK", "result": "Pakistan won by 5 runs",
     "venue": "Pallekele International Cricket Stadium", "date": "2026-02-28", "phase": "Super 8"},

    # ── Semi-Finals (Mar 4-5) ────────────────────────────────────────────
    {"match_id": "SF01", "team1": "SA", "team2": "NZ", "score1": "169/8", "score2": "173/1",
     "innings1_runs": 169, "innings2_runs": 173, "winner": "NZ", "result": "New Zealand won by 9 wickets",
     "venue": "Eden Gardens", "date": "2026-03-04", "phase": "Semi-Final"},
    {"match_id": "SF02", "team1": "IND", "team2": "ENG", "score1": "253/7", "score2": "246/7",
     "innings1_runs": 253, "innings2_runs": 246, "winner": "IND", "result": "India won by 7 runs",
     "venue": "Wankhede Stadium", "date": "2026-03-05", "phase": "Semi-Final"},
]


# ═══════════════════════════════════════════════════════════════════════════
# TOP PERFORMERS — Tournament batting/bowling stats
# ═══════════════════════════════════════════════════════════════════════════

TOP_BATTERS = [
    {'player': 'Sahibzada Farhan', 'team': 'PAK', 'matches': 6, 'runs': 383, 'balls': 239, 'avg': 76.6, 'sr': 160.25, 'fours': 37, 'sixes': 18, 'fifties': 2, 'hundreds': 2},
    {'player': 'Brian Bennett', 'team': 'ZIM', 'matches': 6, 'runs': 292, 'balls': 217, 'avg': 146.0, 'sr': 134.56, 'fours': 32, 'sixes': 7, 'fifties': 3, 'hundreds': 0},
    {'player': 'Finn Allen', 'team': 'NZ', 'matches': 7, 'runs': 289, 'balls': 142, 'avg': 57.8, 'sr': 203.52, 'fours': 24, 'sixes': 20, 'fifties': 0, 'hundreds': 1},
    {'player': 'Aiden Markram', 'team': 'SA', 'matches': 8, 'runs': 286, 'balls': 172, 'avg': 47.67, 'sr': 165.32, 'fours': 32, 'sixes': 11, 'fifties': 3, 'hundreds': 0},
    {'player': 'Jacob Bethell', 'team': 'ENG', 'matches': 8, 'runs': 280, 'balls': 184, 'avg': 35.0, 'sr': 152.17, 'fours': 25, 'sixes': 14, 'fifties': 0, 'hundreds': 1},
    {'player': 'Tim Seifert', 'team': 'NZ', 'matches': 7, 'runs': 274, 'balls': 169, 'avg': 45.67, 'sr': 161.18, 'fours': 32, 'sixes': 11, 'fifties': 3, 'hundreds': 0},
    {'player': 'Ishan Kishan', 'team': 'IND', 'matches': 8, 'runs': 263, 'balls': 138, 'avg': 32.88, 'sr': 189.21, 'fours': 29, 'sixes': 14, 'fifties': 2, 'hundreds': 0},
    {'player': 'Shimron Hetmyer', 'team': 'WI', 'matches': 7, 'runs': 248, 'balls': 132, 'avg': 41.33, 'sr': 186.47, 'fours': 16, 'sixes': 19, 'fifties': 2, 'hundreds': 0},
    {'player': 'Suryakumar Yadav', 'team': 'IND', 'matches': 8, 'runs': 242, 'balls': 176, 'avg': 34.57, 'sr': 137.5, 'fours': 21, 'sixes': 10, 'fifties': 1, 'hundreds': 0},
    {'player': 'Harry Brook', 'team': 'ENG', 'matches': 8, 'runs': 235, 'balls': 147, 'avg': 29.38, 'sr': 159.86, 'fours': 21, 'sixes': 9, 'fifties': 0, 'hundreds': 1},
    {'player': 'Sanju Samson', 'team': 'IND', 'matches': 4, 'runs': 232, 'balls': 114, 'avg': 77.33, 'sr': 201.74, 'fours': 22, 'sixes': 16, 'fifties': 2, 'hundreds': 0},
    {'player': 'Ryan Rickelton', 'team': 'SA', 'matches': 8, 'runs': 228, 'balls': 133, 'avg': 32.57, 'sr': 170.15, 'fours': 17, 'sixes': 15, 'fifties': 1, 'hundreds': 0},
]

TOP_BOWLERS = [
    {'player': 'Shadley van Schalkwyk', 'team': 'USA', 'matches': 4, 'wickets': 13, 'overs': 14.5, 'runs_conceded': 101, 'avg': 7.77, 'econ': 6.81, 'sr': 6.85, 'best': '4/25'},
    {'player': 'Blessing Muzarabani', 'team': 'ZIM', 'matches': 6, 'wickets': 13, 'overs': 23.5, 'runs_conceded': 188, 'avg': 14.46, 'econ': 7.89, 'sr': 11.0, 'best': '4/17'},
    {'player': 'Adil Rashid', 'team': 'ENG', 'matches': 8, 'wickets': 13, 'overs': 30.4, 'runs_conceded': 250, 'avg': 19.23, 'econ': 8.15, 'sr': 14.15, 'best': '3/19'},
    {'player': 'Varun Chakaravarthy', 'team': 'IND', 'matches': 8, 'wickets': 13, 'overs': 28.0, 'runs_conceded': 248, 'avg': 19.08, 'econ': 8.86, 'sr': 12.92, 'best': '3/24'},
    {'player': 'Lungi Ngidi', 'team': 'SA', 'matches': 7, 'wickets': 12, 'overs': 26.0, 'runs_conceded': 187, 'avg': 15.58, 'econ': 7.19, 'sr': 13.0, 'best': '4/28'},
    {'player': 'Marco Jansen', 'team': 'SA', 'matches': 6, 'wickets': 11, 'overs': 22.4, 'runs_conceded': 237, 'avg': 21.55, 'econ': 10.45, 'sr': 12.36, 'best': '4/22'},
    {'player': 'Rachin Ravindra', 'team': 'NZ', 'matches': 7, 'wickets': 11, 'overs': 17.0, 'runs_conceded': 117, 'avg': 10.64, 'econ': 6.88, 'sr': 9.27, 'best': '4/20'},
    {'player': 'Maheesh Theekshana', 'team': 'SL', 'matches': 7, 'wickets': 11, 'overs': 27.3, 'runs_conceded': 204, 'avg': 18.55, 'econ': 7.42, 'sr': 15.0, 'best': '3/18'},
    {'player': 'Corbin Bosch', 'team': 'SA', 'matches': 7, 'wickets': 11, 'overs': 25.0, 'runs_conceded': 191, 'avg': 17.36, 'econ': 7.64, 'sr': 13.64, 'best': '3/21'},
    {'player': 'Jofra Archer', 'team': 'ENG', 'matches': 8, 'wickets': 11, 'overs': 30.0, 'runs_conceded': 286, 'avg': 26.0, 'econ': 9.53, 'sr': 16.36, 'best': '3/25'},
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
