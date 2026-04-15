"""API module - FastAPI routes and dependencies"""

from .routes import predict, health

__all__ = ['predict', 'health']