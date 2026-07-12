"""Data contract validation for the Kaggle credit-card fraud dataset."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


EXPECTED_COLUMNS = ["Time", *[f"V{i}" for i in range(1, 29)], "Amount", "Class"]


@dataclass(frozen=True)
class ContractResult:
    """Validation result returned by the data contract checker."""

    valid: bool
    errors: list[str]
    warnings: list[str]


def _missing_columns(columns: Iterable[str]) -> list[str]:
    present = set(columns)
    return [column for column in EXPECTED_COLUMNS if column not in present]


def validate_creditcard_contract(df: pd.DataFrame) -> ContractResult:
    """Validate the minimum schema and quality rules expected by the project.

    The contract intentionally stays close to the public Kaggle dataset shape:
    numeric Time/Amount/V1..V28 features and binary Class labels.
    """
    errors: list[str] = []
    warnings: list[str] = []

    missing = _missing_columns(df.columns)
    if missing:
        errors.append(f"Missing required columns: {missing}")

    extra = [column for column in df.columns if column not in EXPECTED_COLUMNS]
    if extra:
        warnings.append(f"Extra columns ignored by the ML pipeline: {extra}")

    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            continue
        null_count = int(df[column].isna().sum())
        if null_count:
            errors.append(f"{column} contains {null_count} null values")
        if not pd.api.types.is_numeric_dtype(df[column]):
            errors.append(f"{column} must be numeric")

    if "Amount" in df.columns and (df["Amount"] < 0).any():
        errors.append("Amount must be greater than or equal to zero")

    if "Class" in df.columns:
        class_values = set(df["Class"].dropna().astype(int).unique().tolist())
        if not class_values.issubset({0, 1}):
            errors.append(f"Class must contain only 0/1 labels, got {sorted(class_values)}")
        if len(class_values) < 2:
            warnings.append("Class has a single value; acceptable for CI samples but not model training")

    if len(df) == 0:
        errors.append("Dataset must contain at least one row")

    return ContractResult(valid=not errors, errors=errors, warnings=warnings)


def assert_creditcard_contract(df: pd.DataFrame) -> None:
    """Raise a ValueError when the credit-card data contract is violated."""
    result = validate_creditcard_contract(df)
    if not result.valid:
        raise ValueError("; ".join(result.errors))
