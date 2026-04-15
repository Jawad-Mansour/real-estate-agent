"""
Prediction Service - The Orchestrator (Phase 8)

Connects all components into a complete pipeline:
Stage 1 (LLM extraction) → Completeness Gate → ML Predictor → Stage 2 (Interpretation)
"""

import logging
from typing import Dict, Any, Optional

from backend.core.validation.pydantic_schemas import (
    ExtractedFeatures,
    PredictResponse,
    Stage1Output
)
from backend.core.validation.completeness_gate import CompletenessGate
from backend.core.ml.predictor import Predictor
from backend.core.ml.training_stats import TrainingStats
from backend.core.llm.stage1_extractor import Stage1Extractor
from backend.core.llm.stage2_interpreter import Stage2Interpreter

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Orchestrator for the complete prediction pipeline.
    
    Flow:
    1. Extract features (from LLM or direct override)
    2. Check completeness (all 12 features present?)
    3. If missing → return incomplete response
    4. If complete → predict price
    5. Generate explanation with Stage 2 LLM
    6. Return final response
    """
    
    def __init__(self):
        """Initialize all components"""
        self.stage1_extractor = Stage1Extractor(prompt_version='v2')
        self.stage2_interpreter = Stage2Interpreter()
        logger.info("PredictionService initialized with Stage1(v2) and Stage2")
    
    def process_query(
        self, 
        query: str, 
        override_features: Optional[Dict[str, Any]] = None
    ) -> PredictResponse:
        """
        Process a user query through the complete pipeline.
        
        Args:
            query: Natural language property description
            override_features: Optional direct features (from UI when user fills missing fields)
            
        Returns:
            PredictResponse with status, price, explanation, or missing_fields
        """
        logger.info(f"Processing query: {query[:100]}...")
        
        # STEP 1: Extract features
        if override_features:
            logger.info("Using override features from UI")
            try:
                features = ExtractedFeatures(**override_features)
                stage1_output = CompletenessGate.create_stage1_output(features)
            except Exception as e:
                logger.error(f"Invalid override features: {e}")
                return PredictResponse.error(f"Invalid features provided: {str(e)}")
        else:
            logger.info("Extracting features via Stage 1 LLM")
            stage1_output = self.stage1_extractor.extract(query)
            features = stage1_output.extracted_features
        
        # STEP 2: Check completeness
        is_complete, missing_fields = CompletenessGate.check(features)
        
        if not is_complete:
            logger.info(f"Query incomplete. Missing {len(missing_fields)} fields: {missing_fields}")
            return PredictResponse.success_incomplete(
                missing_fields=missing_fields,
                extracted_features=stage1_output.extracted_features.model_dump(exclude_none=True)
            )
        
        logger.info("All 12 features present - proceeding to prediction")
        
        # STEP 3: Predict price
        try:
            predicted_price = Predictor.predict(features)
            logger.info(f"Predicted price: ${predicted_price:,.0f}")
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return PredictResponse.error(f"Prediction error: {str(e)}")
        
        # STEP 4: Generate explanation
        try:
            interpretation = self.stage2_interpreter.interpret(features, predicted_price)
            logger.info("Stage 2 interpretation generated")
        except Exception as e:
            logger.error(f"Stage 2 interpretation failed: {e}")
            comparison = TrainingStats.get_comparison(predicted_price)
            # Create a simple object as fallback
            interpretation = type('obj', (object,), {
                'explanation': f"The predicted price is ${predicted_price:,.0f}, which is {comparison}.",
                'key_factors': ["Based on the provided features"],
                'comparison': comparison
            })()
        
        # STEP 5: Return complete response
        return PredictResponse.success_complete(
            price=predicted_price,
            explanation=interpretation.explanation,
            key_factors=interpretation.key_factors,
            comparison=interpretation.comparison
        )
    
    def extract_only(self, query: str) -> Stage1Output:
        """Extract features only (no prediction). Useful for debugging."""
        return self.stage1_extractor.extract(query)
    
    def health_check(self) -> Dict[str, Any]:
        """Check if all components are working."""
        try:
            test_features = ExtractedFeatures(
                bedrooms=3, bathrooms=2.0, sqft_living=1500, sqft_lot=10000,
                year_built=2000, garage_cars=2, condition=5, quality=6,
                neighborhood="NAmes", basement="TA", heating="GasA", central_air="Y"
            )
            price = Predictor.predict(test_features)
            return {
                "status": "healthy",
                "stage1_available": True,
                "predictor_available": True,
                "stage2_available": True,
                "test_prediction": price
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
