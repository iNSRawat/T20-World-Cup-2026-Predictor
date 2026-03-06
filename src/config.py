"""
Central configuration for the T20 World Cup 2026 Data Science Project.
All paths, URLs, constants, and mappings in one place.
"""

import os
from pathlib import Path

# ─── Project Paths ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data_raw"
DATA_PROCESSED = PROJECT_ROOT / "data_processed"
MODELS_DIR = PROJECT_ROOT / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Raw data sub-directories
RAW_ESPN = DATA_RAW / "espn"
RAW_CRICBUZZ = DATA_RAW / "cricbuzz"
RAW_ICC = DATA_RAW / "icc"

# ─── ESPN Cricinfo ───────────────────────────────────────────────────────────
ESPN_SERIES_ID = "1502138"
ESPN_BASE_URL = "https://www.espncricinfo.com"
ESPN_SERIES_URL = f"{ESPN_BASE_URL}/series/icc-men-s-t20-world-cup-2025-26-{ESPN_SERIES_ID}"
ESPN_FIXTURES_URL = f"{ESPN_SERIES_URL}/match-schedule-fixtures-and-results"
ESPN_STATS_URL = f"{ESPN_SERIES_URL}/stats"
ESPN_SCORECARD_BASE = f"{ESPN_BASE_URL}/series/icc-men-s-t20-world-cup-2025-26-{ESPN_SERIES_ID}"

# ─── Cricbuzz ────────────────────────────────────────────────────────────────
CRICBUZZ_SERIES_ID = "11253"
CRICBUZZ_BASE_URL = "https://www.cricbuzz.com"
CRICBUZZ_SERIES_URL = f"{CRICBUZZ_BASE_URL}/cricket-series/{CRICBUZZ_SERIES_ID}/icc-mens-t20-world-cup-2026"
CRICBUZZ_MATCHES_URL = f"{CRICBUZZ_SERIES_URL}/matches"

# ─── ICC ─────────────────────────────────────────────────────────────────────
ICC_BASE_URL = "https://www.icc-cricket.com"
ICC_TOURNAMENT_URL = f"{ICC_BASE_URL}/tournaments/mens-t20-world-cup-2026"
ICC_STATS_URL = f"{ICC_TOURNAMENT_URL}/stats"
ICC_STATS_TRACKER_URL = f"{ICC_TOURNAMENT_URL}/stats-tracker"

# ─── Request Settings ────────────────────────────────────────────────────────
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2.0   # seconds between requests (be respectful)

# ─── Team Mappings ───────────────────────────────────────────────────────────
# Standardized team codes → full names
TEAM_CODES = {
    "IND": "India",
    "AUS": "Australia",
    "ENG": "England",
    "PAK": "Pakistan",
    "SA":  "South Africa",
    "NZ":  "New Zealand",
    "WI":  "West Indies",
    "SL":  "Sri Lanka",
    "BAN": "Bangladesh",
    "AFG": "Afghanistan",
    "IRE": "Ireland",
    "SCO": "Scotland",
    "NAM": "Namibia",
    "NEP": "Nepal",
    "NED": "Netherlands",
    "ZIM": "Zimbabwe",
    "OMA": "Oman",
    "USA": "United States",
    "ITA": "Italy",
    "UAE": "United Arab Emirates",
    "CAN": "Canada",
}

# Reverse mapping: name → code
TEAM_NAMES_TO_CODES = {v: k for k, v in TEAM_CODES.items()}

# Name aliases found across ESPN / Cricbuzz / ICC
TEAM_ALIASES = {
    "SA": ["South Africa", "S Africa", "RSA", "S.Africa"],
    "NZ": ["New Zealand", "N Zealand", "NZL"],
    "WI": ["West Indies", "W Indies", "Windies", "WIndies"],
    "SL": ["Sri Lanka", "S Lanka", "SRI"],
    "BAN": ["Bangladesh", "BDESH"],
    "AFG": ["Afghanistan", "AFGH"],
    "PNG": ["Papua New Guinea", "P.N.Guinea", "P N Guinea"],
    "USA": ["United States", "United States of America", "U.S.A"],
    "NED": ["Netherlands", "Holland", "NETH"],
    "NAM": ["Namibia", "NAM"],
    "UGA": ["Uganda", "UGA"],
    "OMA": ["Oman", "OMAN"],
    "NEP": ["Nepal", "NEP"],
    "SCO": ["Scotland", "SCOT"],
    "ZIM": ["Zimbabwe", "ZIMB"],
    "IRE": ["Ireland", "IRE"],
}

# ─── Venue Information ───────────────────────────────────────────────────────
# 2026 T20 WC venues in India & Sri Lanka
VENUES = {
    "Wankhede Stadium": {"city": "Mumbai", "country": "India", "capacity": 33000},
    "Eden Gardens": {"city": "Kolkata", "country": "India", "capacity": 68000},
    "M. Chinnaswamy Stadium": {"city": "Bengaluru", "country": "India", "capacity": 40000},
    "Narendra Modi Stadium": {"city": "Ahmedabad", "country": "India", "capacity": 132000},
    "MA Chidambaram Stadium": {"city": "Chennai", "country": "India", "capacity": 50000},
    "Arun Jaitley Stadium": {"city": "New Delhi", "country": "India", "capacity": 41000},
    "Rajiv Gandhi Intl Cricket Stadium": {"city": "Hyderabad", "country": "India", "capacity": 55000},
    "Punjab Cricket Association Stadium": {"city": "Mullanpur", "country": "India", "capacity": 35000},
    "HPCA Stadium": {"city": "Dharamsala", "country": "India", "capacity": 23000},
    "Sawai Mansingh Stadium": {"city": "Jaipur", "country": "India", "capacity": 30000},
    "Barabati Stadium": {"city": "Cuttack", "country": "India", "capacity": 45000},
    "Greenfield International Stadium": {"city": "Thiruvananthapuram", "country": "India", "capacity": 50000},
    "Barsapara Cricket Stadium": {"city": "Guwahati", "country": "India", "capacity": 40000},
    "R. Premadasa Stadium": {"city": "Colombo", "country": "Sri Lanka", "capacity": 35000},
    "Pallekele International Cricket Stadium": {"city": "Kandy", "country": "Sri Lanka", "capacity": 35000},
    "Hambantota International Stadium": {"city": "Hambantota", "country": "Sri Lanka", "capacity": 35000},
}

# ─── Tournament Phases ───────────────────────────────────────────────────────
PHASES = ["Group Stage", "Super 8", "Semi-Final", "Final"]

# ─── Feature Engineering Constants ───────────────────────────────────────────
POWERPLAY_OVERS = 6
MIDDLE_OVERS = (7, 15)
DEATH_OVERS = (16, 20)
FORM_WINDOW = 5  # last N matches for form calculation


def ensure_dirs():
    """Create all required data directories if they don't exist."""
    for d in [DATA_RAW, DATA_PROCESSED, MODELS_DIR, RAW_ESPN, RAW_CRICBUZZ, RAW_ICC]:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data dirs created: {DATA_RAW}, {DATA_PROCESSED}, {MODELS_DIR}")
