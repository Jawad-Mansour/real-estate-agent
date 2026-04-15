"""
Dependency injection for model and services.
Ensures singleton instances are reused across requests.
"""

from functools import lru_cache

from backend.core.ml.model_loader import ModelLoader
from backend.services.prediction_service import PredictionService


@lru_cache(maxsize=1)
def get_model():
    """
    Get loaded model (cached after first call).
    PDF #10: Model loads at startup, not per request.
    """
    model, _ = ModelLoader.get_model()
    return model


@lru_cache(maxsize=1)
def get_preprocessor():
    """Get loaded preprocessor (cached after first call)"""
    _, preprocessor = ModelLoader.get_model()
    return preprocessor


@lru_cache(maxsize=1)
def get_prediction_service():
    """Get PredictionService singleton"""
    return PredictionService()