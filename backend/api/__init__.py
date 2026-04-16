"""API module - FastAPI routes and dependencies"""

from .routes import predict, health, training_data

__all__ = ['predict', 'health', 'training_data']