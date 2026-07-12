"""Feature engineering sur donnees BRUTES (avant scaling).

Features creees:
- transaction_hour: heure extraite de Time (secondes -> heures mod 24)
- day_period: 0=nuit, 1=matin, 2=apres-midi, 3=soir
- amount_log: log1p(Amount) - reduit l'asymetrie
- amount_bin: 0=low(<50), 1=medium(<200), 2=high(<1000), 3=very_high
- v_mean: moyenne des V1-V28
- v_std: ecart-type des V1-V28
- risk_score: combinaison des features V les plus discriminantes
- amount_x_v14: interaction Amount * |V14|
- amount_x_v17: interaction Amount * |V17|
"""

import numpy as np
import pandas as pd
from loguru import logger

# Features V les plus correlees a la fraude (identifiees par EDA)
_POS_CORR = ["V4", "V11", "V2", "V19"]
_NEG_CORR = ["V14", "V12", "V10", "V17"]

# Liste des features ajoutees par ce module
ENGINEERED_FEATURES = [
    "transaction_hour",
    "day_period",
    "amount_log",
    "amount_bin",
    "v_mean",
    "v_std",
    "risk_score",
    "amount_x_v14",
    "amount_x_v17",
]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute toutes les features engineered au DataFrame.

    IMPORTANT: doit etre appele AVANT le scaling (Amount/Time en valeurs brutes).
    """
    df = df.copy()

    # Temporelles
    df["transaction_hour"] = (df["Time"] / 3600).astype(int) % 24
    df["day_period"] = pd.cut(
        df["transaction_hour"], bins=[-1, 6, 12, 18, 24], labels=[0, 1, 2, 3]
    ).astype(int)

    # Montant
    df["amount_log"] = np.log1p(df["Amount"].clip(lower=0))
    df["amount_bin"] = pd.cut(
        df["Amount"], bins=[-np.inf, 50, 200, 1000, np.inf], labels=[0, 1, 2, 3]
    ).astype(int)

    # Agregats V
    v_cols = [f"V{i}" for i in range(1, 29)]
    df["v_mean"] = df[v_cols].mean(axis=1)
    df["v_std"] = df[v_cols].std(axis=1)

    # Risk score
    df["risk_score"] = df[_POS_CORR].sum(axis=1) - df[_NEG_CORR].sum(axis=1)

    # Interactions
    df["amount_x_v14"] = df["Amount"] * df["V14"].abs()
    df["amount_x_v17"] = df["Amount"] * df["V17"].abs()

    logger.info(f"Feature engineering: +{len(ENGINEERED_FEATURES)} features -> {df.shape[1]} colonnes")
    return df


class FraudFeatureEngineer:
    """Façade rétrocompatible pour le notebook de preprocessing."""

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        return add_features(df)
