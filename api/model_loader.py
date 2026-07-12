"""Chargement du modele pour l'API."""

from typing import Optional

from loguru import logger

from src.predict import FraudPredictor


class ModelManager:
    """Singleton pour le chargement du modele."""

    _predictor: Optional[FraudPredictor] = None

    def load(self) -> None:
        """Charge le modele. Appele au demarrage de l'API."""
        try:
            self._predictor = FraudPredictor()
            logger.info("Modele charge avec succes")
        except FileNotFoundError as e:
            logger.warning(f"Modele non trouve: {e}")
            self._predictor = None

    @property
    def predictor(self) -> Optional[FraudPredictor]:
        return self._predictor

    @property
    def is_loaded(self) -> bool:
        return self._predictor is not None


model_manager = ModelManager()
