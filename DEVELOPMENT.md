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

## 🚀 Free Deployment Platforms

This app is built with Streamlit, making it incredibly easy to deploy for free. Here are the best free platforms with quick-start guides:

### 1. Streamlit Community Cloud (Recommended)
The absolute easiest way to deploy Streamlit apps.
1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. Click **New app**.
3. Select your repository: `iNSRawat/T20-World-Cup-2026-Predictor`.
4. Branch: `main`.
5. Main file path: `app/app.py`.
6. Click **Deploy!**

### 2. Hugging Face Spaces
Great for machine learning portfolios.
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Name your space and select **Streamlit** as the Space SDK.
3. Keep the space Public and click **Create Space**.
4. Clone the space, add your files, or directly link your GitHub repo to the space settings.
5. Hugging Face will automatically build and host the app based on your `requirements.txt`.

### 3. Render
A great platform for general web apps (spins down after inactivity).
1. Go to [Render](https://render.com/) and sign up.
2. Click **New +** and select **Web Service**.
3. Connect your GitHub and select the repository.
4. Name the service, select **Python** runtime.
5. Build Command: `pip install -r requirements.txt`.
6. Start Command: `streamlit run app/app.py --server.port $PORT`.
7. Select the **Free** tier and click **Create Web Service**.

## 🧑‍💻 Contribution Guidelines

1. **Branching:** Create a feature branch (`feature/your-feature-name`) from `main`.
2. **Code Style:** Ensure Python code adheres to PEP-8 standards.
3. **Commit Messages:** Write clear, concise commit messages describing *what* was changed and *why*.
4. **Pull Requests:** Submit PRs against the `main` branch with a thorough description of the changes.
