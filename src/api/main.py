"""API FastAPI pour la detection de fraude."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from loguru import logger

from src.api.model_loader import model_manager
from src.api.schemas import (
    BatchInput,
    BatchOutput,
    HealthResponse,
    PredictionOutput,
    TransactionInput,
)
from config.settings import API_VERSION
from src.db.database import SessionLocal, init_db
from src.db.models import Prediction
from src.core.monitoring.metrics import append_prediction_event, metrics_store, now_ms, load_reference_stats
from src.core.models.evaluation_metrics import load_threshold


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: charge modele + init DB."""
    logger.info("Demarrage API...")
    model_manager.load()
    if os.getenv("SKIP_DB_INIT", "false").lower() == "true":
        logger.info("Initialisation DB ignoree (SKIP_DB_INIT=true)")
    else:
        try:
            init_db()
            logger.info("Base de donnees initialisee")
        except Exception as e:
            logger.warning(f"DB non disponible: {e}")
    yield
    logger.info("Arret API")


app = FastAPI(
    title="Fraud Detection API",
    description="Detection de fraude par Machine Learning",
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _check_model():
    if not model_manager.is_loaded:
        raise HTTPException(503, "Modele non charge. Lancez d'abord: python -m src.train")


@app.get("/", tags=["General"])
async def root():
    return {"message": "Fraud Detection API", "version": API_VERSION, "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health():
    return HealthResponse(status="healthy", model_loaded=model_manager.is_loaded, version=API_VERSION)


@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def metrics():
    """Expose Prometheus-compatible service and ML counters."""
    return metrics_store.to_prometheus(model_loaded=model_manager.is_loaded)


@app.get("/model/info", tags=["Monitoring"])
async def model_info():
    """Return model runtime metadata and reference statistics availability."""
    return {
        "model_loaded": model_manager.is_loaded,
        "version": API_VERSION,
        "reference_stats_available": bool(load_reference_stats()),
        "decision_threshold": round(load_threshold(), 6),
        "prediction_count": metrics_store.prediction_count,
        "fraud_rate": round(metrics_store.fraud_rate, 6),
    }


@app.post("/predict", response_model=PredictionOutput, tags=["Predictions"])
async def predict(transaction: TransactionInput):
    """Predit si une transaction est frauduleuse et persiste le resultat."""
    _check_model()
    start_ms = now_ms()
    try:
        result = model_manager.predictor.predict_single(transaction.model_dump())
        latency_ms = now_ms() - start_ms
        metrics_store.record_prediction(
            probability=result["fraud_probability"],
            is_fraud=result["is_fraud"],
            latency_ms=latency_ms,
        )
        append_prediction_event({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "amount": transaction.Amount,
            "fraud_probability": result["fraud_probability"],
            "is_fraud": result["is_fraud"],
            "risk_level": result["risk_level"],
            "latency_ms": round(latency_ms, 4),
        })

        # Persister en DB
        db = SessionLocal()
        try:
            record = Prediction(
                amount=transaction.Amount,
                prediction=result["prediction"],
                fraud_probability=result["fraud_probability"],
                risk_level=result["risk_level"],
                is_fraud=result["is_fraud"],
            )
            db.add(record)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        return PredictionOutput(**result)
    except Exception as e:
        metrics_store.record_error()
        logger.error(f"Erreur prediction: {e}")
        raise HTTPException(500, str(e))


@app.post("/batch_predict", response_model=BatchOutput, tags=["Predictions"])
async def batch_predict(batch: BatchInput):
    """Prediction batch (max 1000 transactions)."""
    _check_model()
    start_ms = now_ms()
    try:
        transactions = [t.model_dump() for t in batch.transactions]
        results = model_manager.predictor.predict_batch(transactions)
        latency_ms = now_ms() - start_ms
        per_item_latency_ms = latency_ms / max(len(results), 1)
        for transaction, result in zip(batch.transactions, results):
            metrics_store.record_prediction(
                probability=result["fraud_probability"],
                is_fraud=result["is_fraud"],
                latency_ms=per_item_latency_ms,
            )
            append_prediction_event({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "amount": transaction.Amount,
                "fraud_probability": result["fraud_probability"],
                "is_fraud": result["is_fraud"],
                "risk_level": result["risk_level"],
                "latency_ms": round(per_item_latency_ms, 4),
            })

        # Persister
        db = SessionLocal()
        try:
            for t, r in zip(batch.transactions, results):
                db.add(Prediction(
                    amount=t.Amount,
                    prediction=r["prediction"],
                    fraud_probability=r["fraud_probability"],
                    risk_level=r["risk_level"],
                    is_fraud=r["is_fraud"],
                ))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

        predictions = [PredictionOutput(**r) for r in results]
        fraud_count = sum(1 for p in predictions if p.is_fraud)
        return BatchOutput(
            predictions=predictions,
            total=len(predictions),
            fraud_count=fraud_count,
            fraud_rate=round(fraud_count / len(predictions), 4),
        )
    except Exception as e:
        metrics_store.record_error()
        logger.error(f"Erreur batch: {e}")
        raise HTTPException(500, str(e))


@app.get("/predictions/history", tags=["History"])
async def get_history(limit: int = 50):
    """Retourne l'historique des predictions."""
    db = SessionLocal()
    try:
        records = db.query(Prediction).order_by(Prediction.id.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "amount": r.amount,
                "is_fraud": r.is_fraud,
                "fraud_probability": r.fraud_probability,
                "risk_level": r.risk_level,
            }
            for r in records
        ]
    except Exception as e:
        logger.warning(f"DB history error: {e}")
        return []
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    from config.settings import API_HOST, API_PORT

    uvicorn.run(app, host=API_HOST, port=API_PORT)
