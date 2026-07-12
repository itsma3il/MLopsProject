"""Tests for the Kaggle-backed dataset loader."""

from pathlib import Path

from src import dataset_loader


def test_download_real_dataset_uses_kagglehub(monkeypatch, tmp_path):
    kaggle_dir = tmp_path / "kaggle"
    kaggle_dir.mkdir()
    source = kaggle_dir / "creditcard.csv"
    source.write_text((Path("samples") / "creditcard_sample.csv").read_text(), encoding="utf-8")

    destination_dir = tmp_path / "raw"
    monkeypatch.setattr(dataset_loader, "DATA_RAW", destination_dir)
    monkeypatch.setattr(dataset_loader.kagglehub, "dataset_download", lambda name: str(kaggle_dir))

    result = dataset_loader.download_real_dataset()

    assert result == destination_dir / "creditcard.csv"
    assert result.exists()
