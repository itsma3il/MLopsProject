"""Tests for imbalanced fraud metrics and threshold selection."""

import numpy as np

from src.core.models.evaluation_metrics import compute_imbalanced_metrics, optimize_threshold, predictions_from_threshold


def test_predictions_from_threshold():
    probabilities = np.array([0.1, 0.49, 0.5, 0.9])
    assert predictions_from_threshold(probabilities, 0.5).tolist() == [0, 0, 1, 1]


def test_compute_imbalanced_metrics_includes_rare_event_metrics():
    y_true = np.array([0, 0, 0, 1, 1])
    y_proba = np.array([0.01, 0.2, 0.8, 0.7, 0.9])

    metrics = compute_imbalanced_metrics(y_true, y_proba, threshold=0.5)

    assert metrics["confusion_matrix"] == [[2, 1], [0, 2]]
    assert metrics["balanced_accuracy"] > 0
    assert metrics["mcc"] > 0
    assert metrics["pr_auc"] > 0


def test_optimize_threshold_returns_validation_threshold():
    y_true = np.array([0, 0, 0, 1, 1])
    y_proba = np.array([0.01, 0.2, 0.45, 0.4, 0.9])

    threshold, metrics = optimize_threshold(y_true, y_proba)

    assert 0 <= threshold <= 1
    assert metrics["f1_score"] >= compute_imbalanced_metrics(y_true, y_proba, threshold=0.5)["f1_score"]
