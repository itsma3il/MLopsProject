"""Configuration centralisee du projet fraud-detection."""

import os
from pathlib import Path

# === PATHS ===
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_WAREHOUSE = PROJECT_ROOT / "data" / "warehouse"
DATA_MONITORING = PROJECT_ROOT / "data" / "monitoring"
MODELS_DIR = PROJECT_ROOT / "models"
FIGURES_DIR = PROJECT_ROOT / "figures"

# === DATABASE ===
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fraud_detection",
)

# === MODEL ===
MODEL_FILENAME = "best_model.joblib"
SCALER_FILENAME = "scaler.joblib"
FEATURE_COLUMNS_FILE = "feature_columns.json"
METRICS_FILE = "metrics.json"
REFERENCE_STATS_FILE = "reference_stats.json"
THRESHOLD_FILE = "decision_threshold.json"

# === ML PIPELINE ===
RANDOM_STATE = 42
TEST_SIZE = 0.2
SMOTE_STRATEGY = 0.5
CV_FOLDS = 5
THRESHOLD_OPTIMIZATION_METRIC = "f1_score"

# === FEATURES ===
COLUMNS_TO_SCALE = ["Amount", "Time"]
TARGET_COLUMN = "Class"

# === RISK THRESHOLDS ===
RISK_THRESHOLDS = {"low": 0.3, "medium": 0.6, "high": 0.8}

# === API ===
API_VERSION = "2.0.0"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# === DATAOPS / MLOPS ===
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(DATA_WAREHOUSE / "fraud.duckdb"))
DLT_PIPELINE_NAME = os.getenv("DLT_PIPELINE_NAME", "fraud_detection_ingestion")
MLRUNS_DIR = PROJECT_ROOT / "mlruns"
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"file://{MLRUNS_DIR}")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "fraud-detection")
MLFLOW_REGISTERED_MODEL = os.getenv("MLFLOW_REGISTERED_MODEL", "fraud_detection_classifier")
