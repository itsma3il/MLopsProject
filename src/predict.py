"""Prediction coherente avec le pipeline leakage-free.

Le modele sauvegarde est un ImbPipeline (scaler + smote + classifier).
A predict time, seuls scaler + classifier sont utilises (SMOTE est no-op sur predict).
"""

import json
from typing import Any, Dict, List

import joblib
import pandas as pd
from loguru import logger

from config.settings import (
    FEATURE_COLUMNS_FILE,
    MODEL_FILENAME,
    MODELS_DIR,
    RISK_THRESHOLDS,
)
from src.evaluation_metrics import load_threshold
from src.feature_engineering import add_features


class FraudPredictor:
    """Prediction de fraude avec le pipeline complet."""

    def __init__(self):
        self.pipeline = joblib.load(MODELS_DIR / MODEL_FILENAME)
        with open(MODELS_DIR / FEATURE_COLUMNS_FILE) as f:
            self.feature_columns = json.load(f)
        self.decision_threshold = load_threshold()
        logger.info(f"FraudPredictor initialise (threshold={self.decision_threshold:.4f})")

    def _classify_risk(self, prob: float) -> str:
        if prob >= RISK_THRESHOLDS["high"]:
            return "CRITICAL"
        elif prob >= RISK_THRESHOLDS["medium"]:
            return "HIGH"
        elif prob >= RISK_THRESHOLDS["low"]:
            return "MEDIUM"
        return "LOW"

    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Feature engineering sur donnees brutes, puis select colonnes."""
        df = add_features(df)
        # Ajouter colonnes manquantes
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        return df[self.feature_columns]

    def predict_single(self, transaction: Dict[str, float]) -> Dict[str, Any]:
        """Prediction pour une transaction."""
        df = self._prepare(pd.DataFrame([transaction]))
        prob = float(self.pipeline.predict_proba(df)[0, 1])
        pred = int(prob >= self.decision_threshold)
        return {
            "prediction": pred,
            "is_fraud": bool(pred),
            "fraud_probability": round(prob, 4),
            "risk_level": self._classify_risk(prob),
        }

    def predict_batch(self, transactions: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Prediction batch."""
        df = self._prepare(pd.DataFrame(transactions))
        probs = self.pipeline.predict_proba(df)[:, 1]
        preds = (probs >= self.decision_threshold).astype(int)
        return [
            {
                "prediction": int(p),
                "is_fraud": bool(p),
                "fraud_probability": round(float(pr), 4),
                "risk_level": self._classify_risk(float(pr)),
            }
            for p, pr in zip(preds, probs)
        ]
