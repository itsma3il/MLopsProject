"""Backward-compatible wrapper for the pipeline dashboard."""

from src.core.pipeline.pipeline_dashboard import *  # noqa: F401,F403


if __name__ == "__main__":
    create_pipeline_dashboard()
