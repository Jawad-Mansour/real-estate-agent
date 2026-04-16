"""
Root entry point for uvicorn.

Uvicorn is configured to load `main:app`, so this module re-exports the
FastAPI application instance from `backend/main.py` where all routes,
middleware, and startup logic are defined.
"""

from backend.main import app  # noqa: F401 — re-exported for uvicorn

__all__ = ["app"]
