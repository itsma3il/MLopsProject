"""Tests for data contract validation and Kaggle dataset loading."""

from pathlib import Path

import pandas as pd

from src.utils.validation import EXPECTED_COLUMNS, validate_creditcard_contract


def test_sample_fixture_matches_contract():
    df = pd.read_csv(Path("samples") / "creditcard_sample.csv")
    result = validate_creditcard_contract(df)
    assert result.valid, result.errors
    assert list(df.columns) == EXPECTED_COLUMNS


def test_contract_rejects_missing_column():
    df = pd.read_csv(Path("samples") / "creditcard_sample.csv").drop(columns=["Amount"])
    result = validate_creditcard_contract(df)
    assert not result.valid
    assert any("Missing required columns" in error for error in result.errors)
