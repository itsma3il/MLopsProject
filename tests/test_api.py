"""Tests pour le pipeline ML et l'API."""

import os

import numpy as np
import pandas as pd
import httpx
import pytest

os.environ["SKIP_DB_INIT"] = "true"

from api.main import app
from src.feature_engineering import ENGINEERED_FEATURES, add_features
from src.preprocessing import apply_scaling, clean_data, fit_scaler


@pytest.fixture
def anyio_backend():
    return "asyncio"


# === TESTS PREPROCESSING ===


class TestPreprocessing:
    def _make_df(self, n=100):
        """Cree un DataFrame synthetique similaire au dataset reel."""
        rng = np.random.default_rng(42)
        data = {"Time": rng.uniform(0, 172800, n), "Amount": rng.exponential(50, n)}
        for i in range(1, 29):
            data[f"V{i}"] = rng.standard_normal(n)
        data["Class"] = np.concatenate([np.zeros(n - 5), np.ones(5)])
        return pd.DataFrame(data)

    def test_clean_data_removes_duplicates(self):
        df = self._make_df()
        df = pd.concat([df, df.iloc[:3]], ignore_index=True)
        cleaned = clean_data(df)
        assert len(cleaned) == 100

    def test_fit_scaler_returns_scaler(self):
        df = self._make_df()
        scaler = fit_scaler(df)
        assert hasattr(scaler, "transform")

    def test_apply_scaling_changes_values(self):
        df = self._make_df()
        scaler = fit_scaler(df)
        scaled = apply_scaling(df, scaler)
        assert not np.allclose(scaled["Amount"].values, df["Amount"].values)


# === TESTS FEATURE ENGINEERING ===


class TestFeatureEngineering:
    def _make_df(self, n=50):
        rng = np.random.default_rng(42)
        data = {"Time": rng.uniform(0, 172800, n), "Amount": rng.exponential(50, n)}
        for i in range(1, 29):
            data[f"V{i}"] = rng.standard_normal(n)
        data["Class"] = np.zeros(n)
        return pd.DataFrame(data)

    def test_add_features_creates_expected_columns(self):
        df = add_features(self._make_df())
        for feat in ENGINEERED_FEATURES:
            assert feat in df.columns, f"Missing: {feat}"

    def test_add_features_no_nans(self):
        df = add_features(self._make_df())
        assert df[ENGINEERED_FEATURES].isna().sum().sum() == 0


# === TESTS API ===


class TestAPI:
    def _sample(self):
        data = {"Time": 0.0, "Amount": 149.62}
        data.update({f"V{i}": 0.0 for i in range(1, 29)})
        return data

    @pytest.mark.anyio
    async def test_root(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/")
        assert r.status_code == 200
        assert "version" in r.json()

    @pytest.mark.anyio
    async def test_health(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    @pytest.mark.anyio
    async def test_metrics_endpoint(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/metrics")
        assert r.status_code == 200
        assert "fraud_api_predictions_total" in r.text

    @pytest.mark.anyio
    async def test_model_info_endpoint(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.get("/model/info")
        assert r.status_code == 200
        assert "model_loaded" in r.json()

    @pytest.mark.anyio
    async def test_predict_no_model_returns_503(self):
        """Si le modele n'est pas charge, retourne 503."""
        from api.model_loader import model_manager
        if not model_manager.is_loaded:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                r = await client.post("/predict", json=self._sample())
            assert r.status_code == 503

    @pytest.mark.anyio
    async def test_predict_invalid_input_returns_422(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/predict", json={"invalid": "data"})
        assert r.status_code == 422

    @pytest.mark.anyio
    async def test_batch_empty_returns_422(self):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r = await client.post("/batch_predict", json={"transactions": []})
        assert r.status_code == 422
