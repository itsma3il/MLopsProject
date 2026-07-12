"""Backward-compatible wrapper for the pipeline CLI."""

from src.core.pipeline.run_pipeline import *  # noqa: F401,F403


if __name__ == "__main__":
    import runpy

    runpy.run_module("src.core.pipeline.run_pipeline", run_name="__main__")
