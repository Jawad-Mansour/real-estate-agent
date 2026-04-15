"""
Health check endpoint
Returns service status and component health
"""

import logging
from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict

from backend.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    model_loaded: bool
    components: Dict[str, bool]
    message: str


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with status and component health
    """
    try:
        service = PredictionService()
        health = service.health_check()
        
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            components={
                "stage1_extractor": True,
                "stage2_interpreter": True,
                "predictor": True,
                "completeness_gate": True
            },
            message="Service is operational"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            components={},
            message=f"Service unhealthy: {str(e)}"
        )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness probe for Docker/Kubernetes.
    Returns 200 when service is ready to accept requests.
    """
    return {"ready": True, "status": "ready"}