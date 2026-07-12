"""Metrics and threshold utilities for imbalanced fraud classification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)

from config.settings import MODELS_DIR, THRESHOLD_FILE


DEFAULT_DECISION_THRESHOLD = 0.5


def predictions_from_threshold(y_proba: np.ndarray, threshold: float) -> np.ndarray:
    """Convert fraud probabilities to binary predictions."""
    return (np.asarray(y_proba) >= threshold).astype(int)


def compute_imbalanced_metrics(
    y_true: Any,
    y_proba: Any,
    threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> dict[str, Any]:
    """Compute metrics that are meaningful for rare-event fraud detection."""
    y_true = np.asarray(y_true).astype(int)
    y_proba = np.asarray(y_proba).astype(float)
    y_pred = predictions_from_threshold(y_proba, threshold)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0
    false_negative_rate = fn / (fn + tp) if (fn + tp) else 0.0
    fraud_rate = float(np.mean(y_true))

    return {
        "decision_threshold": float(threshold),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": float(specificity),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "false_positive_rate": float(false_positive_rate),
        "false_negative_rate": float(false_negative_rate),
        "fraud_rate": fraud_rate,
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def optimize_threshold(
    y_true: Any,
    y_proba: Any,
    metric: str = "f1_score",
) -> tuple[float, dict[str, Any]]:
    """Choose a validation threshold without touching the final test set."""
    y_true = np.asarray(y_true).astype(int)
    y_proba = np.asarray(y_proba).astype(float)
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)

    candidates: list[tuple[float, dict[str, Any]]] = [
        (DEFAULT_DECISION_THRESHOLD, compute_imbalanced_metrics(y_true, y_proba, DEFAULT_DECISION_THRESHOLD))
    ]
    for threshold in thresholds:
        metrics = compute_imbalanced_metrics(y_true, y_proba, float(threshold))
        candidates.append((float(threshold), metrics))

    if metric == "f1_score":
        key = lambda item: (item[1]["f1_score"], item[1]["recall"], item[1]["precision"])
    elif metric == "recall_at_precision_80":
        key = lambda item: (
            item[1]["recall"] if item[1]["precision"] >= 0.80 else -1.0,
            item[1]["f1_score"],
        )
    else:
        raise ValueError(f"Unsupported threshold optimization metric: {metric}")

    best_threshold, best_metrics = max(candidates, key=key)
    best_metrics["threshold_optimization_metric"] = metric
    best_metrics["pr_curve_points"] = int(len(precision))
    return best_threshold, best_metrics


def save_threshold(threshold: float, metrics: dict[str, Any], path: Path | None = None) -> None:
    """Persist the selected decision threshold and its validation metrics."""
    target = path or MODELS_DIR / THRESHOLD_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "decision_threshold": float(threshold),
                "validation_metrics": metrics,
            },
            f,
            indent=2,
        )


def load_threshold(path: Path | None = None) -> float:
    """Load the saved threshold, falling back to sklearn's default 0.5."""
    target = path or MODELS_DIR / THRESHOLD_FILE
    if not target.exists():
        return DEFAULT_DECISION_THRESHOLD
    with target.open(encoding="utf-8") as f:
        payload = json.load(f)
    return float(payload.get("decision_threshold", DEFAULT_DECISION_THRESHOLD))
