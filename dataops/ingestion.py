"""Backward-compatible wrapper for data ingestion."""

from src.core.data.ingestion import *  # noqa: F401,F403


if __name__ == "__main__":
    ingest_with_duckdb_direct()
