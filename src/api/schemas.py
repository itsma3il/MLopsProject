"""Schemas Pydantic pour l'API."""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TransactionInput(BaseModel):
    """Input: une transaction avec 30 features."""

    Time: float = Field(default=0.0)
    Amount: float = Field(..., ge=0)
    V1: float = 0.0
    V2: float = 0.0
    V3: float = 0.0
    V4: float = 0.0
    V5: float = 0.0
    V6: float = 0.0
    V7: float = 0.0
    V8: float = 0.0
    V9: float = 0.0
    V10: float = 0.0
    V11: float = 0.0
    V12: float = 0.0
    V13: float = 0.0
    V14: float = 0.0
    V15: float = 0.0
    V16: float = 0.0
    V17: float = 0.0
    V18: float = 0.0
    V19: float = 0.0
    V20: float = 0.0
    V21: float = 0.0
    V22: float = 0.0
    V23: float = 0.0
    V24: float = 0.0
    V25: float = 0.0
    V26: float = 0.0
    V27: float = 0.0
    V28: float = 0.0


class PredictionOutput(BaseModel):
    """Output: resultat de prediction."""

    prediction: int
    is_fraud: bool
    fraud_probability: float
    risk_level: str


class BatchInput(BaseModel):
    """Input batch."""

    transactions: List[TransactionInput] = Field(..., min_length=1, max_length=1000)


class BatchOutput(BaseModel):
    """Output batch."""

    predictions: List[PredictionOutput]
    total: int
    fraud_count: int
    fraud_rate: float


class HealthResponse(BaseModel):
    """Health check response."""

    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    version: str
