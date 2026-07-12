"""Backward-compatible wrapper for model evaluation."""

from src.core.models.evaluate import *  # noqa: F401,F403


if __name__ == "__main__":
    import json

    metrics = run_evaluation()
    print(json.dumps({k: v for k, v in metrics.items() if k != "confusion_matrix"}, indent=2))
