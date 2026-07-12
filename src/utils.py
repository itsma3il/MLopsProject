"""Utilitaires communs."""

import pandas as pd
from loguru import logger

from config.settings import DATA_PROCESSED, PROJECT_ROOT
from src.preprocessing import load_raw_data as _load_raw_data


def setup_logger(log_file: str = "fraud_detection.log") -> None:
    """Configure le logger avec rotation."""
    logger.add(
        PROJECT_ROOT / log_file,
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


def load_raw_data(filename: str = "creditcard.csv") -> pd.DataFrame:
    """Compatibilité avec les anciens notebooks: délègue au module preprocessing."""
    return _load_raw_data(filename)


def save_dataframe(df: pd.DataFrame, filename: str) -> None:
    """Sauvegarde un DataFrame dans data/processed/ par défaut."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PROCESSED / filename, index=False)
