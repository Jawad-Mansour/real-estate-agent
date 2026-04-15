"""
Prediction endpoint - Main API route
POST /predict - Accepts natural language query, returns price prediction
"""

import logging
import time
import uuid
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.services.prediction_service import PredictionService
from backend.core.validation.pydantic_schemas import PredictResponse
from backend.utils.exceptions import ValidationException
from backend.utils.validators import validate_query
from backend.api.dependencies import get_prediction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Prediction"])


class PredictRequest(BaseModel):
    """Request body for prediction endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="Natural language property description")
    override_features: Optional[Dict[str, Any]] = Field(None, description="Override extracted features (from UI form)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "3-bedroom ranch with a big garage in a good neighborhood",
                "override_features": None
            }
        }


@router.post("", response_model=PredictResponse, status_code=status.HTTP_200_OK)
async def predict(
    request: PredictRequest,
    service: PredictionService = Depends(get_prediction_service)
) -> PredictResponse:
    """
    Predict house price from natural language description.
    
    Two flows:
    1. Normal: Query -> Stage1 LLM extraction -> Completeness gate -> ML -> Stage2
    2. Override: Query + override_features -> Skip Stage1 -> ML -> Stage2
    
    Returns:
        - If incomplete: status="incomplete" with missing_fields list
        - If complete: status="complete" with price and explanation
        - If error: status="error" with message
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    logger.info(f"[{request_id}] Predict request: {request.query[:100]}...")
    
    try:
        # Validate input
        validated_query = validate_query(request.query)
        
        # Process through prediction service
        response = service.process_query(
            query=validated_query,
            override_features=request.override_features
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        logger.info(f"[{request_id}] Response status={response.status}, time={processing_time_ms:.0f}ms")
        
        return response
        
    except ValidationException as e:
        logger.warning(f"[{request_id}] Validation error: {e.message}")
        return PredictResponse.error(e.message)
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        return PredictResponse.error(f"Internal server error: {str(e)}")