"""Evaluation sur test set INTOUCHE (pas de SMOTE, pas de scaling externe)."""

import json
from typing import Any, Dict

import joblib
import pandas as pd
from loguru import logger

from config.settings import DATA_PROCESSED, METRICS_FILE, MODEL_FILENAME, MODELS_DIR
from src.evaluation_metrics import compute_imbalanced_metrics, load_threshold


def evaluate_model(model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """Evalue le pipeline sur le test set original avec le seuil sauvegarde."""
    y_proba = model.predict_proba(X_test)[:, 1]
    threshold = load_threshold()
    metrics = compute_imbalanced_metrics(y_test, y_proba, threshold=threshold)
    metrics["metric_note"] = (
        "Accuracy is reported for completeness only. Fraud is a rare-event problem; "
        "use PR-AUC, recall, precision, F1, MCC and balanced_accuracy for model selection."
    )

    logger.info("=== EVALUATION (test set) ===")
    for k, v in metrics.items():
        if k not in ("confusion_matrix", "metric_note"):
            logger.info(f"  {k}: {v:.4f}")
    logger.info(f"  TN={metrics['tn']} FP={metrics['fp']} FN={metrics['fn']} TP={metrics['tp']}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODELS_DIR / METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics


def run_evaluation() -> Dict[str, float]:
    """Charge pipeline + test data et evalue."""
    pipeline = joblib.load(MODELS_DIR / MODEL_FILENAME)
    X_test = pd.read_csv(DATA_PROCESSED / "X_test.csv")
    y_test = pd.read_csv(DATA_PROCESSED / "y_test.csv").squeeze()
    return evaluate_model(pipeline, X_test, y_test)


if __name__ == "__main__":
    metrics = run_evaluation()
    print(json.dumps({k: v for k, v in metrics.items() if k != "confusion_matrix"}, indent=2))


def compute_metrics(model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """Backward-compatible alias used in older notebooks."""
    return evaluate_model(model, X_test, y_test)


def full_evaluation(models: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    """Evaluate multiple models and return a DataFrame summary sorted by F1-score.

    Parameters
    - models: dict of name -> estimator
    - X_test, y_test: test set
    """
    rows = []
    for name, model in models.items():
        try:
            metrics = evaluate_model(model, X_test, y_test)
            rows.append({"model": name, **metrics})
        except Exception as e:
            logger.error(f"Error evaluating {name}: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows).set_index("model")
    if "f1_score" in df.columns:
        df = df.sort_values(by="f1_score", ascending=False)
    return df
