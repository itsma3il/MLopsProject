"""Modeles SQLAlchemy pour la persistance des predictions."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from db.database import Base


class Prediction(Base):
    """Stocke chaque prediction effectuee par l'API."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    amount = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)  # 0 ou 1
    fraud_probability = Column(Float, nullable=False)
    risk_level = Column(String(10), nullable=False)
    is_fraud = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Prediction id={self.id} fraud={self.is_fraud} prob={self.fraud_probability}>"
