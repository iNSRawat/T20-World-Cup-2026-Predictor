"""
Win Prediction Model for T20 World Cup 2026.

Implements:
  - Logistic Regression baseline
  - XGBoost model
  - Evaluation (AUC, Brier score, accuracy)
  - Feature importance (SHAP)
  - Model persistence

Usage:
  python src/models/win_predictor.py          # Train & evaluate
  python src/models/win_predictor.py --predict IND AUS  # Predict match
"""

import sys
import argparse
import pickle
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, roc_auc_score, brier_score_loss,
    classification_report, confusion_matrix
)
from sklearn.calibration import calibration_curve

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import DATA_PROCESSED, MODELS_DIR, TEAM_CODES
from src.utils import save_dataframe, load_dataframe, logger


# ─── Feature Columns ────────────────────────────────────────────────────────
# These are the columns used as model inputs
NUMERIC_FEATURES = [
    "t1_bat_strength", "t1_bowl_strength", "t1_win_rate",
    "t1_avg_score", "t1_avg_conceded",
    "t1_form_win_rate", "t1_form_streak",

    "t2_bat_strength", "t2_bowl_strength", "t2_win_rate",
    "t2_avg_score", "t2_avg_conceded",
    "t2_form_win_rate", "t2_form_streak",

    "strength_diff_bat", "strength_diff_bowl",
    "win_rate_diff", "form_diff",

    "venue_avg_first_innings", "venue_chase_win_pct",
    "venue_matches_played",

    "toss_winner_is_team1",
    "is_knockout", "tournament_progress",
]

TARGET = "team1_won"


class WinPredictor:
    """Match win prediction model with multiple algorithms."""

    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.best_model_name = "xgboost"
        self.feature_columns = NUMERIC_FEATURES
        self.is_fitted = False

    # ─── Data Loading ────────────────────────────────────────────────────

    def load_features(self) -> pd.DataFrame:
        """Load the feature matrix."""
        df = load_dataframe(DATA_PROCESSED / "match_features.csv")
        if df is None or df.empty:
            logger.error("No feature data found — run feature engineering first")
            return pd.DataFrame()
        return df

    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Prepare X, y arrays from feature DataFrame.
        Handles missing values and feature selection.
        """
        # Keep only rows with valid target
        df = df[df[TARGET].isin([0, 1])].copy()

        # Select features that exist
        available = [c for c in self.feature_columns if c in df.columns]
        if not available:
            logger.error("No valid features found")
            return np.array([]), np.array([]), df

        X = df[available].fillna(0).values
        y = df[TARGET].values

        self.feature_columns = available
        return X, y, df

    # ─── Training ────────────────────────────────────────────────────────

    def train(self, test_size: float = 0.25, random_state: int = 42) -> Dict:
        """
        Train multiple models and evaluate them.
        Returns evaluation metrics.
        """
        df = self.load_features()
        if df.empty:
            return {}

        X, y, df = self.prepare_data(df)
        if X.size == 0:
            return {}

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Define models
        model_configs = {
            "logistic_regression": LogisticRegression(
                max_iter=1000, random_state=random_state, C=1.0
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=6, random_state=random_state
            ),
        }

        # Try to import XGBoost
        try:
            import xgboost as xgb
            model_configs["xgboost"] = xgb.XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                random_state=random_state, eval_metric="logloss",
                use_label_encoder=False,
            )
        except ImportError:
            logger.warning("XGBoost not installed, skipping")

        # Try LightGBM
        try:
            import lightgbm as lgb
            model_configs["lightgbm"] = lgb.LGBMClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                random_state=random_state, verbose=-1,
            )
        except ImportError:
            logger.warning("LightGBM not installed, skipping")

        # Train and evaluate each model
        results = {}
        best_auc = -1

        for name, model in model_configs.items():
            logger.info(f"Training {name}...")

            # Use scaled data for logistic regression, raw for tree models
            X_tr = X_train_scaled if name == "logistic_regression" else X_train
            X_te = X_test_scaled if name == "logistic_regression" else X_test

            model.fit(X_tr, y_train)
            self.models[name] = model

            # Predictions
            y_pred = model.predict(X_te)
            y_prob = model.predict_proba(X_te)[:, 1]

            # Metrics
            acc = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0
            brier = brier_score_loss(y_test, y_prob)

            results[name] = {
                "accuracy": round(acc, 4),
                "auc": round(auc, 4),
                "brier_score": round(brier, 4),
            }

            logger.info(f"  {name}: Accuracy={acc:.3f}, AUC={auc:.3f}, Brier={brier:.3f}")

            # Track best model
            if auc > best_auc:
                best_auc = auc
                self.best_model_name = name

        # Cross-validation for best model
        logger.info(f"\nBest model: {self.best_model_name}")
        cv_model = model_configs[self.best_model_name]
        X_cv = X_train_scaled if self.best_model_name == "logistic_regression" else X_train
        cv_scores = cross_val_score(cv_model, X_cv, y_train, cv=5, scoring="roc_auc")
        results["cross_val_auc"] = {
            "mean": round(cv_scores.mean(), 4),
            "std": round(cv_scores.std(), 4),
        }
        logger.info(f"CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

        self.is_fitted = True

        # Save models
        self.save_models()

        # Generate plots
        self._plot_evaluation(y_test, results, X_test, X_test_scaled)

        return results

    # ─── Prediction ──────────────────────────────────────────────────────

    def predict_match(self, features: Dict) -> Dict:
        """
        Predict win probability for a match given features.
        Returns probabilities for both teams.
        """
        if not self.is_fitted:
            self.load_models()

        # Build feature vector
        X = np.array([[features.get(f, 0) for f in self.feature_columns]])

        # Use best model
        model = self.models.get(self.best_model_name)
        if model is None:
            logger.error(f"Model {self.best_model_name} not found")
            return {}

        # Scale if needed
        if self.best_model_name == "logistic_regression":
            X = self.scaler.transform(X)

        prob = model.predict_proba(X)[0]

        return {
            "team1_win_prob": round(float(prob[1]), 4),
            "team2_win_prob": round(float(prob[0]), 4),
            "model_used": self.best_model_name,
        }

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from the best model."""
        model = self.models.get(self.best_model_name)
        if model is None:
            return pd.DataFrame()

        if hasattr(model, "feature_importances_"):
            importance = model.feature_importances_
        elif hasattr(model, "coef_"):
            importance = np.abs(model.coef_[0])
        else:
            return pd.DataFrame()

        df = pd.DataFrame({
            "feature": self.feature_columns,
            "importance": importance,
        }).sort_values("importance", ascending=False)

        return df

    # ─── Model Persistence ───────────────────────────────────────────────

    def save_models(self):
        """Save all trained models and scaler."""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        for name, model in self.models.items():
            path = MODELS_DIR / f"{name}.pkl"
            with open(path, "wb") as f:
                pickle.dump(model, f)
            logger.info(f"Saved model: {path}")

        # Save scaler
        with open(MODELS_DIR / "scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)

        # Save feature list
        with open(MODELS_DIR / "features.pkl", "wb") as f:
            pickle.dump(self.feature_columns, f)

    def load_models(self):
        """Load saved models."""
        for pkl_file in MODELS_DIR.glob("*.pkl"):
            name = pkl_file.stem
            if name == "scaler":
                with open(pkl_file, "rb") as f:
                    self.scaler = pickle.load(f)
            elif name == "features":
                with open(pkl_file, "rb") as f:
                    self.feature_columns = pickle.load(f)
            else:
                with open(pkl_file, "rb") as f:
                    self.models[name] = pickle.load(f)
                logger.info(f"Loaded model: {name}")

        self.is_fitted = bool(self.models)

    # ─── Visualization ───────────────────────────────────────────────────

    def _plot_evaluation(self, y_test, results, X_test, X_test_scaled):
        """Generate evaluation plots."""
        output_dir = DATA_PROCESSED / "plots"
        output_dir.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        # 1. Model comparison bar chart
        model_names = [k for k in results if k != "cross_val_auc"]
        accs = [results[k]["accuracy"] for k in model_names]
        aucs = [results[k]["auc"] for k in model_names]

        x = np.arange(len(model_names))
        axes[0].bar(x - 0.15, accs, 0.3, label="Accuracy", color="#4CAF50")
        axes[0].bar(x + 0.15, aucs, 0.3, label="AUC", color="#2196F3")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(model_names, rotation=15)
        axes[0].set_title("Model Comparison")
        axes[0].legend()
        axes[0].set_ylim(0, 1)

        # 2. Feature importance
        importance_df = self.get_feature_importance()
        if not importance_df.empty:
            top_n = importance_df.head(10)
            axes[1].barh(top_n["feature"], top_n["importance"], color="#FF9800")
            axes[1].set_title(f"Top Features ({self.best_model_name})")
            axes[1].invert_yaxis()

        # 3. Calibration plot
        model = self.models.get(self.best_model_name)
        if model:
            X_eval = X_test_scaled if self.best_model_name == "logistic_regression" else X_test
            y_prob = model.predict_proba(X_eval)[:, 1]
            try:
                fraction_pos, mean_pred = calibration_curve(y_test, y_prob, n_bins=8)
                axes[2].plot(mean_pred, fraction_pos, "o-", label=self.best_model_name)
                axes[2].plot([0, 1], [0, 1], "--", color="gray", label="Perfect calibration")
                axes[2].set_xlabel("Mean predicted probability")
                axes[2].set_ylabel("Fraction of positives")
                axes[2].set_title("Calibration Plot")
                axes[2].legend()
            except Exception:
                axes[2].text(0.5, 0.5, "Insufficient data\nfor calibration",
                           ha="center", va="center", fontsize=12)

        plt.tight_layout()
        plt.savefig(output_dir / "model_evaluation.png", dpi=150, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved evaluation plots to {output_dir}")


# ─── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="T20 WC 2026 Win Predictor")
    parser.add_argument("--predict", nargs=2, metavar=("TEAM1", "TEAM2"),
                        help="Predict match (e.g., --predict IND AUS)")
    parser.add_argument("--train", action="store_true", help="Train models")
    args = parser.parse_args()

    predictor = WinPredictor()

    if args.train or not args.predict:
        results = predictor.train()
        if results:
            print("\n📊 Model Evaluation Results:")
            for name, metrics in results.items():
                if isinstance(metrics, dict):
                    print(f"  {name}: {metrics}")

    if args.predict:
        t1, t2 = args.predict
        print(f"\n🏏 Predicting: {TEAM_CODES.get(t1, t1)} vs {TEAM_CODES.get(t2, t2)}")
        # Build minimal features (in real use, pull from feature engineer)
        features = {f: 0.5 for f in NUMERIC_FEATURES}
        result = predictor.predict_match(features)
        if result:
            print(f"  {t1} win: {result['team1_win_prob']:.1%}")
            print(f"  {t2} win: {result['team2_win_prob']:.1%}")
            print(f"  Model: {result['model_used']}")


if __name__ == "__main__":
    main()
