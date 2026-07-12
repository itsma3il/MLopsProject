"""dlt + DuckDB ingestion pipeline for the Kaggle fraud dataset."""

from __future__ import annotations

import os
import sys
import time
import shutil
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

from config.settings import DLT_PIPELINE_NAME, DUCKDB_PATH
from src.utils.validation import assert_creditcard_contract
from src.core.data.dataset_loader import ensure_dataset


RAW_TABLE_NAME = "creditcard_transactions"
DLT_DATA_DIR = Path(".dlt")  # dlt's local state directory


def clear_dlt_state():
    """Clear dlt's local state to prevent loading pending packages."""
    dlt_dir = Path(DLT_PIPELINE_NAME)
    if dlt_dir.exists():
        logger.info(f"Clearing dlt state directory: {dlt_dir}")
        shutil.rmtree(dlt_dir)
    
    # Also clear any .dlt directory
    if DLT_DATA_DIR.exists():
        logger.info(f"Clearing .dlt directory: {DLT_DATA_DIR}")
        shutil.rmtree(DLT_DATA_DIR)


def load_source_dataframe(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the Kaggle CSV and validate it against the project contract."""
    logger.info("Loading source dataframe...")
    path = csv_path or ensure_dataset()
    
    # Read CSV with optimized dtypes
    logger.info(f"Reading CSV from: {path}")
    start_time = time.time()
    
    # Define dtypes to reduce memory usage
    dtypes = {
        'Time': 'float32',
        'V1': 'float32',
        'V2': 'float32',
        'V3': 'float32',
        'V4': 'float32',
        'V5': 'float32',
        'V6': 'float32',
        'V7': 'float32',
        'V8': 'float32',
        'V9': 'float32',
        'V10': 'float32',
        'V11': 'float32',
        'V12': 'float32',
        'V13': 'float32',
        'V14': 'float32',
        'V15': 'float32',
        'V16': 'float32',
        'V17': 'float32',
        'V18': 'float32',
        'V19': 'float32',
        'V20': 'float32',
        'V21': 'float32',
        'V22': 'float32',
        'V23': 'float32',
        'V24': 'float32',
        'V25': 'float32',
        'V26': 'float32',
        'V27': 'float32',
        'V28': 'float32',
        'Amount': 'float32',
        'Class': 'int8'
    }
    
    df = pd.read_csv(path, dtype=dtypes)
    elapsed = time.time() - start_time
    logger.info(f"CSV loaded in {elapsed:.2f} seconds")
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
    
    assert_creditcard_contract(df)
    return df


def ingest_with_dlt(csv_path: Optional[Path] = None, duckdb_path: str = DUCKDB_PATH, force_fresh: bool = True):
    """Load the contract-valid CSV into DuckDB with dlt."""
    os.environ.setdefault("DLT_TELEMETRY", "false")
    
    try:
        import dlt
    except ImportError as exc:
        raise RuntimeError("Install dlt with DuckDB support: pip install 'dlt[duckdb]'") from exc

    # Clear dlt state to prevent loading pending packages
    if force_fresh:
        logger.info("Force fresh start - clearing dlt state...")
        clear_dlt_state()
        
        # Also clear the DuckDB database if it exists
        if Path(duckdb_path).exists():
            logger.info(f"Removing existing DuckDB database: {duckdb_path}")
            Path(duckdb_path).unlink(missing_ok=True)

    logger.info("Starting ingestion pipeline...")
    df = load_source_dataframe(csv_path)
    
    # Create DuckDB directory
    Path(duckdb_path).parent.mkdir(parents=True, exist_ok=True)

    # Configure pipeline
    pipeline = dlt.pipeline(
        pipeline_name=DLT_PIPELINE_NAME,
        destination=dlt.destinations.duckdb(duckdb_path),
        dataset_name="raw",
        # Add this to ensure fresh start
        dev_mode=True,
    )
    
    logger.info("Running dlt pipeline...")
    logger.info(f"Loading {len(df)} rows into table: {RAW_TABLE_NAME}")
    start_time = time.time()
    
    # Pass DataFrame directly
    load_info = pipeline.run(
        df,
        table_name=RAW_TABLE_NAME,
        write_disposition="replace",
    )
    
    elapsed = time.time() - start_time
    logger.info(f"dlt ingestion completed in {elapsed:.2f} seconds")
    logger.info(f"Load info: {load_info}")
    logger.info(f"Dataset loaded into: {duckdb_path}")
    
    return load_info


def ingest_with_duckdb_direct(csv_path: Optional[Path] = None, duckdb_path: str = DUCKDB_PATH):
    """Direct DuckDB ingestion (faster alternative to dlt)."""
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("Install duckdb: pip install duckdb") from exc

    logger.info("Starting direct DuckDB ingestion...")
    path = csv_path or ensure_dataset()
    
    # Create DuckDB directory
    Path(duckdb_path).parent.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    
    # Connect to DuckDB
    with duckdb.connect(duckdb_path) as con:
        # Create schema if not exists
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        
        # Drop table if exists (for replace)
        con.execute(f"DROP TABLE IF EXISTS raw.{RAW_TABLE_NAME}")
        
        # Load CSV directly into DuckDB (this is very fast)
        logger.info(f"Loading {path} into DuckDB...")
        con.execute(f"""
            CREATE TABLE raw.{RAW_TABLE_NAME} AS 
            SELECT * FROM read_csv_auto('{path}')
        """)
        
        # Verify count
        count = con.execute(f"SELECT COUNT(*) FROM raw.{RAW_TABLE_NAME}").fetchone()[0]
        elapsed = time.time() - start_time
        
        logger.info(f"Loaded {count} rows in {elapsed:.2f} seconds")
        logger.info(f"Table created: raw.{RAW_TABLE_NAME}")
        
        # Show schema
        schema = con.execute(f"DESCRIBE raw.{RAW_TABLE_NAME}").fetchall()
        logger.info(f"Table schema: {len(schema)} columns")
        
        return count


def assert_duckdb_table(duckdb_path: str = DUCKDB_PATH, table_name: str = RAW_TABLE_NAME) -> int:
    """Assert that the raw DuckDB table exists and contains rows."""
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("Install duckdb: pip install duckdb") from exc

    if not Path(duckdb_path).exists():
        raise FileNotFoundError(f"DuckDB database not found: {duckdb_path}")

    with duckdb.connect(duckdb_path) as con:
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw' AND table_name = ?
            """,
            [table_name],
        ).fetchone()[0]
        if not exists:
            raise RuntimeError(f"DuckDB table raw.{table_name} does not exist")

        rows = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
        if rows <= 0:
            raise RuntimeError(f"DuckDB table raw.{table_name} is empty")
        return int(rows)


def ingest_with_fallback(csv_path: Optional[Path] = None, duckdb_path: str = DUCKDB_PATH):
    """Try direct DuckDB first (faster), then dlt if needed."""
    try:
        logger.info("Using direct DuckDB ingestion (faster)...")
        return ingest_with_duckdb_direct(csv_path, duckdb_path)
    except Exception as e:
        logger.warning(f"Direct DuckDB failed: {e}")
        logger.info("Falling back to dlt ingestion...")
        return ingest_with_dlt(csv_path, duckdb_path)


if __name__ == "__main__":
    logger.info("=== Starting Data Ingestion ===")
    try:
        # Use direct DuckDB by default (faster and more reliable)
        ingest_with_duckdb_direct()
        logger.info("=== Ingestion Complete ===")
        sys.stdout.flush()
        sys.stderr.flush()
    except KeyboardInterrupt:
        logger.warning("Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
