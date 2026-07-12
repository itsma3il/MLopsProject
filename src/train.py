"""Backward-compatible wrapper for model training."""

from src.core.models.train import *  # noqa: F401,F403


if __name__ == "__main__":
    run_training_pipeline()
