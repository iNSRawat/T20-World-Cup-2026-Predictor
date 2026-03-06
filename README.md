# 🏏 T20 World Cup 2026 — Match Prediction & Analytics

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-006400?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

**AI-powered pre-match win predictions for the ICC Men's T20 World Cup 2026**  
*Using real-world data from ESPNcricinfo, Cricbuzz & ICC*

[View Demo](#-streamlit-dashboard) · [Run Locally](#-quick-start) · [Data Sources](#-data-sources)

</div>

---

## 📝 Problem Statement

Given two teams, a venue, toss outcome, and recent form data, **predict the probability of each team winning a T20 World Cup 2026 match**. This project simulates a production-grade analytics tool that could serve broadcasters, fantasy platforms, or team analysts with real-time predictive insights.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA INGESTION                            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                │
│  │  ESPN     │   │ Cricbuzz │   │   ICC    │                │
│  │ Scraper  │   │ Scraper  │   │ Scraper  │                │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘                │
│       └───────────┬───┴──────────────┘                      │
│              data_raw/ (HTML, CSV)                           │
├─────────────────────────────────────────────────────────────┤
│                 DATA PROCESSING                              │
│  ┌──────────────────┐   ┌──────────────────┐                │
│  │  cleaner.py       │──▶│  features.py     │               │
│  │  Multi-source     │   │  Team strength   │               │
│  │  merge & dedup    │   │  Venue profile   │               │
│  └──────────────────┘   │  Form metrics    │               │
│                          │  Toss features   │               │
│                          └────────┬─────────┘               │
│                          data_processed/                     │
├─────────────────────────────────────────────────────────────┤
│                    MODELING                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Logistic   │  │  Random     │  │  XGBoost /  │         │
│  │  Regression │  │  Forest     │  │  LightGBM   │         │
│  └─────────────┘  └─────────────┘  └──────┬──────┘         │
│                                      Best Model              │
├─────────────────────────────────────────────────────────────┤
│                 STREAMLIT DASHBOARD                           │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Match Predictor  │  │ Tournament       │                 │
│  │ Win Probability  │  │ Insights         │                 │
│  │ Key Drivers      │  │ Points Table     │                 │
│  │ Venue Insights   │  │ Top Performers   │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
T20 World Cup 2026 data science project/
├── app/
│   └── app.py                 # Streamlit dashboard
├── data_raw/                  # Raw scraped data
│   ├── espn/                  #   ESPNcricinfo outputs
│   ├── cricbuzz/              #   Cricbuzz outputs
│   └── icc/                   #   ICC portal outputs
├── data_processed/            # Clean analytical tables
├── models/                    # Saved model artifacts (.pkl)
├── notebooks/                 # Jupyter notebooks (EDA)
│   └── 01_eda.ipynb
├── src/
│   ├── config.py              # URLs, team mappings, venues
│   ├── utils.py               # Shared helpers
│   ├── scrapers/
│   │   ├── espn_scraper.py    # ESPNcricinfo scraper
│   │   ├── cricbuzz_scraper.py# Cricbuzz scraper
│   │   └── icc_scraper.py     # ICC portal scraper
│   ├── processing/
│   │   ├── cleaner.py         # Multi-source data cleaning
│   │   └── features.py        # Feature engineering
│   └── models/
│       └── win_predictor.py   # ML models & evaluation
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/iNSRawat/T20-World-Cup-2026-Predictor.git
cd T20-World-Cup-2026-Predictor

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Populate tournament data (28 completed matches + stats)
python src/data/tournament_data.py

# Run the full pipeline
python src/processing/cleaner.py        # 1. Clean & integrate
python src/processing/features.py       # 2. Engineer features
python src/models/win_predictor.py      # 3. Train models

# Launch the dashboard
streamlit run app/app.py
```

## 📡 Data Sources

| Source | What We Scrape | Purpose |
|--------|---------------|---------|
| **[ESPNcricinfo](https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2025-26-1502138)** | Fixtures, scorecards, batting/bowling stats | Primary data source |
| **[Cricbuzz](https://www.cricbuzz.com/cricket-series/11253/icc-mens-t20-world-cup-2026)** | Match results, scorecards | Cross-validation |
| **[ICC Portal](https://www.icc-cricket.com/tournaments/mens-t20-world-cup-2026/stats)** | Official results, tournament stats | Ground truth |

## 🤖 ML Models

### Features Used
- **Team Strength** — Batting/bowling indices computed from average scores & conceded runs
- **Venue Profile** — Average 1st innings score, chase vs defend win rates
- **Form Metrics** — Win/loss streak, recent win rate (last 5 matches)
- **Toss** — Winner and bat/field decision
- **Match Context** — Group stage vs knockout, tournament progress
- **Differential Features** — Strength gaps between opposing teams

### Models Implemented
| Model | Description |
|-------|------------|
| Logistic Regression | Interpretable baseline with L2 regularization |
| Random Forest | Ensemble of 100 decision trees (max_depth=6) |
| XGBoost | Gradient boosted trees (100 estimators, lr=0.1) |
| LightGBM | Fast gradient boosting (100 estimators, lr=0.1) |

### Evaluation
- **Accuracy** — Correct prediction rate
- **AUC-ROC** — Ability to rank probabilities correctly
- **Brier Score** — Calibration of probability estimates
- **Calibration Plot** — Visual check on predicted vs actual frequencies

## 📊 Streamlit Dashboard

### Match Predictor
- Select Team 1 vs Team 2, venue, and toss outcome
- View win probabilities with interactive donut chart
- See key match factors and venue insights

### Tournament Insights
- Team standings (points table with NRR)
- Top run scorers and wicket takers
- Venue performance analysis with bar charts

## 💼 Business Framing

This project demonstrates capabilities applicable to:
- **Broadcasters** — Real-time predictive overlays during live matches
- **Fantasy Platforms** — Player impact scoring for daily fantasy contests
- **Team Analysts** — Pre-match matchup analysis and venue strategy
- **Betting/Odds** — Data-driven probability estimation

## 🛠️ Tech Stack

- **Python 3.9+** — Core language
- **pandas / NumPy** — Data manipulation
- **BeautifulSoup / requests** — Web scraping
- **scikit-learn** — ML framework
- **XGBoost / LightGBM** — Advanced models
- **Streamlit** — Interactive dashboard
- **Plotly** — Data visualization
- **SHAP** — Model interpretability

## 📄 License

This project is for educational and portfolio purposes. All cricket data is sourced from publicly available pages.

---

<div align="center">
  <strong>Built with ❤️ for cricket analytics</strong>
</div>
