"""
Predictor - Makes price predictions from extracted features

Uses the loaded model and preprocessor to predict house prices.
Handles the complete prediction flow:
    ExtractedFeatures → Transform → Model.predict → Price
"""

import numpy as np
from typing import Dict, Any, Optional
from ..validation.pydantic_schemas import ExtractedFeatures
from .model_loader import ModelLoader
from .feature_pipeline import FeaturePipeline
import logging

logger = logging.getLogger(__name__)


class Predictor:
    """
    Makes price predictions from extracted features.
    
    Usage:
        features = ExtractedFeatures(bedrooms=3, bathrooms=2.0, ...)
        price = Predictor.predict(features)
        print(f"${price:,.0f}")
    """
    
    @classmethod
    def predict(cls, features: ExtractedFeatures) -> float:
        """
        Predict house price from extracted features.
        
        Args:
            features: Validated ExtractedFeatures object (all 12 fields present)
            
        Returns:
            Predicted price in dollars
            
        Raises:
            ValueError: If features are invalid or missing
        """
        # Validate that all features are present
        missing = []
        for field in ExtractedFeatures.model_fields.keys():
            if getattr(features, field) is None:
                missing.append(field)
        
        if missing:
            raise ValueError(f"Cannot predict: missing features {missing}")
        
        # Transform features to model input
        X = FeaturePipeline.transform(features)
        
        # Get model
        model, _ = ModelLoader.get_model()
        
        # Predict
        prediction = model.predict(X)[0]
        
        # Round to nearest dollar
        prediction = float(np.round(prediction))
        
        logger.info(f"Predicted price: ${prediction:,.0f}")
        
        return prediction
    
    @classmethod
    def predict_from_dict(cls, features_dict: Dict[str, Any]) -> float:
        """
        Predict house price from a dictionary of features.
        
        Useful when you have a dict from Stage 1 LLM output.
        """
        features = ExtractedFeatures(**features_dict)
        return cls.predict(features)
    
    @classmethod
    def predict_batch(cls, features_list: list) -> list:
        """
        Predict multiple house prices from a list of features.
        
        Args:
            features_list: List of ExtractedFeatures objects
            
        Returns:
            List of predicted prices
        """
        return [cls.predict(features) for features in features_list]