"""Lightweight service and ML monitoring for the FastAPI application."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Any

from config.settings import DATA_MONITORING, MODELS_DIR, REFERENCE_STATS_FILE


PREDICTION_EVENTS = DATA_MONITORING / "prediction_events.jsonl"


@dataclass
class MetricsStore:
    """In-memory counters exported as Prometheus-compatible text."""

    prediction_count: int = 0
    fraud_count: int = 0
    error_count: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    probabilities: list[float] = field(default_factory=list)

    def record_prediction(self, probability: float, is_fraud: bool, latency_ms: float) -> None:
        self.prediction_count += 1
        self.fraud_count += int(is_fraud)
        self.latencies_ms.append(float(latency_ms))
        self.probabilities.append(float(probability))

    def record_error(self) -> None:
        self.error_count += 1

    @property
    def fraud_rate(self) -> float:
        if self.prediction_count == 0:
            return 0.0
        return self.fraud_count / self.prediction_count

    @property
    def avg_latency_ms(self) -> float:
        return mean(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def avg_probability(self) -> float:
        return mean(self.probabilities) if self.probabilities else 0.0

    def to_prometheus(self, model_loaded: bool) -> str:
        lines = [
            "# HELP fraud_api_model_loaded Whether the model is loaded.",
            "# TYPE fraud_api_model_loaded gauge",
            f"fraud_api_model_loaded {int(model_loaded)}",
            "# HELP fraud_api_predictions_total Total predictions served.",
            "# TYPE fraud_api_predictions_total counter",
            f"fraud_api_predictions_total {self.prediction_count}",
            "# HELP fraud_api_prediction_errors_total Total prediction errors.",
            "# TYPE fraud_api_prediction_errors_total counter",
            f"fraud_api_prediction_errors_total {self.error_count}",
            "# HELP fraud_api_prediction_latency_ms Average prediction latency in ms.",
            "# TYPE fraud_api_prediction_latency_ms gauge",
            f"fraud_api_prediction_latency_ms {self.avg_latency_ms:.4f}",
            "# HELP fraud_api_fraud_rate Share of predictions classified as fraud.",
            "# TYPE fraud_api_fraud_rate gauge",
            f"fraud_api_fraud_rate {self.fraud_rate:.6f}",
            "# HELP fraud_api_avg_fraud_probability Average predicted fraud probability.",
            "# TYPE fraud_api_avg_fraud_probability gauge",
            f"fraud_api_avg_fraud_probability {self.avg_probability:.6f}",
        ]
        return "\n".join(lines) + "\n"


metrics_store = MetricsStore()


def now_ms() -> float:
    return time.perf_counter() * 1000


def append_prediction_event(payload: dict[str, Any]) -> None:
    """Persist a prediction event for simple offline monitoring."""
    DATA_MONITORING.mkdir(parents=True, exist_ok=True)
    with PREDICTION_EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def load_reference_stats() -> dict[str, Any]:
    """Load training reference statistics used for simple drift reporting."""
    path = MODELS_DIR / REFERENCE_STATS_FILE
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)
