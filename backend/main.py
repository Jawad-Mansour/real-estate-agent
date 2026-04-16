"""
FastAPI Application Entry Point

PDF #10: Model loads at startup, single POST route
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routes import predict, health, training_data
from backend.core.ml.model_loader import ModelLoader
from backend.utils.exceptions import AppException, validation_error_handler, app_exception_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    PDF #10: Model loads at startup, not per request.
    """
    # Startup
    logger.info("Starting FastAPI application...")
    try:
        # Force model to load once at startup
        model, preprocessor = ModelLoader.get_model()
        logger.info(" Model and preprocessor loaded successfully at startup")
    except Exception as e:
        logger.error(f" Failed to load model at startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="AI Real Estate Agent",
    description="Natural language property price prediction with LLM prompt chaining",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(AppException, app_exception_handler)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    # Mount static assets (CSS, JS, images)
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Serve index.html at root
    @app.get("/", tags=["Frontend"])
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    logger.info("Frontend static files mounted successfully")
else:
    logger.warning(f"Frontend path not found: {frontend_path}")


@app.get("/api", tags=["Root"])
async def api_root():
    """Root endpoint - API information"""
    return {
        "service": "AI Real Estate Agent",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/predict", "method": "POST", "description": "Predict house price"},
            {"path": "/api/training-data", "method": "GET", "description": "Training dataset summary"},
            {"path": "/api", "method": "GET", "description": "API information"},
            {"path": "/", "method": "GET", "description": "Frontend UI"}
        ]
    }


# Include routers
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(training_data.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)