"""Dagster assets for the DataOps and MLOps lifecycle."""

from __future__ import annotations

import subprocess
from pathlib import Path

from dagster import AssetExecutionContext, Definitions, MaterializeResult, asset

from config.settings import DATA_RAW, DUCKDB_PATH, PROJECT_ROOT
from dataops.ingestion import assert_duckdb_table, ingest_with_dlt
from monitoring.metrics import load_reference_stats
from src.dataset_loader import ensure_dataset
from src.evaluate import run_evaluation
from src.train import run_training_pipeline


DBT_DIR = PROJECT_ROOT / "dbt_fraud"


@asset(description="Download the Kaggle fraud dataset and cache it under data/raw.")
def download_dataset() -> MaterializeResult:
    path = ensure_dataset()
    return MaterializeResult(metadata={"path": str(path)})


@asset(deps=[download_dataset], description="Load Kaggle CSV into DuckDB raw schema with dlt.")
def ingest_data(context: AssetExecutionContext) -> MaterializeResult:
    ingest_with_dlt(DATA_RAW / "creditcard.csv")
    rows = assert_duckdb_table()
    context.log.info(f"Loaded {rows} raw transactions into {DUCKDB_PATH}")
    return MaterializeResult(metadata={"duckdb_path": DUCKDB_PATH, "rows": rows})


@asset(deps=[ingest_data], description="Run dbt transformations and data tests on DuckDB.")
def dbt_transform(context: AssetExecutionContext) -> MaterializeResult:
    cmd = ["dbt", "build", "--profiles-dir", ".", "--project-dir", "."]
    result = subprocess.run(cmd, cwd=DBT_DIR, check=True, capture_output=True, text=True)
    context.log.info(result.stdout)
    return MaterializeResult(metadata={"dbt_project": str(DBT_DIR)})


@asset(deps=[dbt_transform], description="Train the sklearn/imblearn fraud classifier and log MLflow artifacts.")
def train_model() -> MaterializeResult:
    result = run_training_pipeline()
    return MaterializeResult(metadata={"best_model": result["best_model"]})


@asset(deps=[train_model], description="Evaluate the promoted local model on the untouched test split.")
def evaluate_model() -> MaterializeResult:
    metrics = run_evaluation()
    return MaterializeResult(metadata={k: v for k, v in metrics.items() if k != "confusion_matrix"})


@asset(deps=[evaluate_model], description="Expose training reference statistics for drift monitoring.")
def monitor_model() -> MaterializeResult:
    stats = load_reference_stats()
    return MaterializeResult(metadata={"reference_stats_available": bool(stats)})


defs = Definitions(
    assets=[
        download_dataset,
        ingest_data,
        dbt_transform,
        train_model,
        evaluate_model,
        monitor_model,
    ]
)
