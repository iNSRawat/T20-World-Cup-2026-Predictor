"""
Shared utility functions for scraping, data processing, and modeling.
"""

import time
import logging
import hashlib
from pathlib import Path
from typing import Optional

import requests
import pandas as pd
from bs4 import BeautifulSoup

from src.config import REQUEST_HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY, TEAM_ALIASES, TEAM_NAMES_TO_CODES

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-18s │ %(levelname)-7s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("t20wc2026")


# ─── HTTP Helpers ────────────────────────────────────────────────────────────
def fetch_page(url: str, delay: float = REQUEST_DELAY, headers: dict = None) -> Optional[BeautifulSoup]:
    """
    Fetch a page and return parsed BeautifulSoup object.
    Includes polite delay between requests.
    """
    headers = headers or REQUEST_HEADERS
    try:
        time.sleep(delay)
        logger.info(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def fetch_json(url: str, delay: float = REQUEST_DELAY, headers: dict = None) -> Optional[dict]:
    """Fetch JSON data from a URL."""
    headers = headers or REQUEST_HEADERS
    try:
        time.sleep(delay)
        logger.info(f"Fetching JSON: {url}")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        logger.error(f"Failed to fetch JSON from {url}: {e}")
        return None


def save_html(content: str, filepath: Path):
    """Save raw HTML content to a file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    logger.info(f"Saved HTML: {filepath}")


# ─── Name Standardization ───────────────────────────────────────────────────
def standardize_team_name(raw_name: str) -> str:
    """
    Convert any team name variant to the standard code (e.g., 'S Africa' → 'SA').
    Falls back to the raw name if no mapping is found.
    """
    cleaned = raw_name.strip()

    # Direct lookup
    if cleaned in TEAM_NAMES_TO_CODES:
        return TEAM_NAMES_TO_CODES[cleaned]

    # Check aliases
    for code, aliases in TEAM_ALIASES.items():
        if cleaned in aliases or cleaned.upper() == code:
            return code

    # Fallback: return as-is
    logger.warning(f"Unknown team name: '{raw_name}', returning as-is")
    return cleaned


def standardize_player_name(name: str) -> str:
    """
    Basic player name standardization:
    - Strip whitespace, normalize unicode
    - Title case
    """
    return " ".join(name.strip().split()).title()


# ─── Data Helpers ────────────────────────────────────────────────────────────
def safe_float(value, default=0.0) -> float:
    """Convert to float safely, returning default on failure."""
    try:
        return float(str(value).replace("*", "").replace("-", "0").strip())
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0) -> int:
    """Convert to int safely, returning default on failure."""
    try:
        return int(safe_float(value, default))
    except (ValueError, TypeError):
        return default


def generate_match_id(team1: str, team2: str, date: str) -> str:
    """Generate a deterministic match ID from teams and date."""
    key = f"{sorted([team1, team2])[0]}_{sorted([team1, team2])[1]}_{date}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def save_dataframe(df: pd.DataFrame, filepath: Path, index: bool = False):
    """Save DataFrame to CSV with logging."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=index)
    logger.info(f"Saved {len(df)} rows → {filepath}")


def load_dataframe(filepath: Path) -> Optional[pd.DataFrame]:
    """Load CSV into DataFrame with error handling."""
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} rows ← {filepath}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return None


# ─── Display Helpers ─────────────────────────────────────────────────────────
def format_probability(prob: float) -> str:
    """Format probability as percentage string."""
    return f"{prob * 100:.1f}%"


def overs_to_balls(overs: float) -> int:
    """Convert overs (e.g., 4.3) to total balls (e.g., 27)."""
    full_overs = int(overs)
    balls = round((overs - full_overs) * 10)
    return full_overs * 6 + balls


def balls_to_overs(balls: int) -> float:
    """Convert total balls to overs notation (e.g., 27 → 4.3)."""
    return int(balls / 6) + (balls % 6) / 10
