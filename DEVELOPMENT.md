# Development Guide

This document outlines the setup, architecture, and development workflow for the **T20 World Cup 2026 Predictor** project.

## 🛠️ Local Setup

### Prerequisites
- Python 3.9+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iNSRawat/T20-World-Cup-2026-Predictor.git
   cd T20-World-Cup-2026-Predictor
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📂 Project Architecture

The codebase is organized entirely modularly to separate data ingestion, feature engineering, modeling, and presentation.

```
T20-World-Cup-2026-Predictor/
├── app/                  # Streamlit Dashboard UI
│   └── app.py            # Main entry point for the web app
├── data_raw/             # Raw scraped data (HTML, JSON, CSV) 
├── data_processed/       # Cleaned, analytical data ready for ML
├── models/               # Serialized model artifacts (.pkl files)
├── notebooks/            # Jupyter notebooks for EDA and prototyping
├── src/                  # Core source code
│   ├── config.py         # Global variables, paths, and configurations
│   ├── utils.py          # Shared utility functions (logging, file I/O)
│   ├── data/
│   │   └── tournament_data.py # Real 2026 tournament stats and match data
│   ├── processing/
│   │   ├── cleaner.py    # Merges and cleans multi-source scraped data
│   │   └── features.py   # Engineers advanced ML features (form, strength)
│   └── models/
│       └── win_predictor.py  # Model training, evaluation, and prediction pipeline
```

## ⚙️ Running the Data Pipeline

The project supports a full end-to-end data pipeline.

1. **Populate Base Data:**
   Generates necessary CSVs for top performers and completed tournament matches.
   ```bash
   python src/data/tournament_data.py
   ```

2. **Feature Engineering:**
   Calculates team strengths, venue profiles, and constructs the training dataset.
   ```bash
   python src/processing/features.py
   ```

3. **Train Models:**
   Trains Logistic Regression, Random Forest, XGBoost, and LightGBM models.
   ```bash
   python src/models/win_predictor.py --train
   ```

## 🖥️ Running the Application

To launch the Streamlit frontend with the trained models and latest data:

```bash
streamlit run app/app.py
```

The app will become available at `http://localhost:8501`.

## 🧑‍💻 Contribution Guidelines

1. **Branching:** Create a feature branch (`feature/your-feature-name`) from `main`.
2. **Code Style:** Ensure Python code adheres to PEP-8 standards.
3. **Commit Messages:** Write clear, concise commit messages describing *what* was changed and *why*.
4. **Pull Requests:** Submit PRs against the `main` branch with a thorough description of the changes.
