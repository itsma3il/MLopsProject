"""Pipeline de preprocessing - ordre correct: Clean -> Split -> Fit transforms on train."""

from typing import Tuple

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.preprocessing import RobustScaler

from config.settings import (
    COLUMNS_TO_SCALE,
    DATA_RAW,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
)


def load_raw_data(filename: str = "creditcard.csv") -> pd.DataFrame:
    """Charge le dataset brut depuis data/raw/."""
    path = DATA_RAW / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset non trouve: {path}\n"
            "Telechargez-le: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud\n"
            f"Placez creditcard.csv dans: {DATA_RAW}"
        )
    df = pd.read_csv(path)
    logger.info(f"Dataset charge: {df.shape}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime doublons, NaN, cap outliers Amount au P99."""
    n_before = len(df)
    duplicate_rows = int(df.duplicated().sum())
    missing_rows = int(df.isna().any(axis=1).sum())

    df = df.drop_duplicates(keep="first", ignore_index=True)
    df = df.dropna(ignore_index=True)
    logger.info(
        f"Nettoyage: {n_before} -> {len(df)} lignes "
        f"(doublons supprimes={duplicate_rows}, lignes avec NaN supprimees={missing_rows})"
    )

    # Cap Amount au 99e percentile
    cap = np.percentile(df["Amount"], 99)
    df["Amount"] = df["Amount"].clip(upper=cap)
    return df


def split_data(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split stratifie train/test AVANT scaling."""
    from sklearn.model_selection import train_test_split

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    logger.info(f"Split: train={len(X_train)}, test={len(X_test)}")
    return X_train, X_test, y_train, y_test


def split_train_val_test(
    df: pd.DataFrame,
    val_size: float = 0.15,
    test_size: float = 0.15,
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.Series,
]:
    """Crée un split stratifié train/validation/test sans fuite.

    Les tailles sont calculées à partir du dataset initial:
    - test_size: part finale gardée pour le test
    - val_size: part finale gardée pour la validation
    """
    from sklearn.model_selection import train_test_split

    if val_size <= 0 or test_size <= 0:
        raise ValueError("val_size et test_size doivent etre strictement positifs.")
    if val_size + test_size >= 1:
        raise ValueError("val_size + test_size doit etre inferieur a 1.")

    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    val_relative_size = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=val_relative_size,
        random_state=RANDOM_STATE,
        stratify=y_train_val,
    )

    logger.info(
        f"Split train/val/test: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}"
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def fit_scaler(X_train: pd.DataFrame) -> RobustScaler:
    """Fit le scaler sur le train set uniquement."""
    scaler = RobustScaler()
    scaler.fit(X_train[COLUMNS_TO_SCALE])
    return scaler


def apply_scaling(df: pd.DataFrame, scaler: RobustScaler) -> pd.DataFrame:
    """Applique le scaling sur Amount et Time."""
    df = df.copy()
    df[COLUMNS_TO_SCALE] = scaler.transform(df[COLUMNS_TO_SCALE])
    return df


class FraudPreprocessor:
    """Façade rétrocompatible pour le notebook de preprocessing."""

    def __init__(self, scaler_type: str = "robust") -> None:
        if scaler_type != "robust":
            raise ValueError("Seul scaler_type='robust' est supporte pour le moment.")
        self.scaler_type = scaler_type
        self.scaler: RobustScaler | None = None

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return clean_data(df)

    def handle_outliers(
        self,
        df: pd.DataFrame,
        column: str,
        cap_percentile: float = 99,
    ) -> pd.DataFrame:
        """Cappe les valeurs extrêmes d'une colonne numérique au percentile demandé."""
        df = df.copy()
        cap = np.percentile(df[column], cap_percentile)
        df[column] = df[column].clip(upper=cap)
        return df

    def scale_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Scale Amount et Time avec RobustScaler."""
        if fit or self.scaler is None:
            self.scaler = fit_scaler(df)
        return apply_scaling(df, self.scaler)

    def split_data(self, df: pd.DataFrame):
        return split_data(df)

    def split_train_val_test(self, df: pd.DataFrame, val_size: float = 0.15, test_size: float = 0.15):
        return split_train_val_test(df, val_size=val_size, test_size=test_size)
