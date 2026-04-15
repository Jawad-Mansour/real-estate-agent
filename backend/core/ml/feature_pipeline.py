"""
Feature Pipeline - Transforms user input to model-ready format

Takes extracted features (as dict or ExtractedFeatures) and:
1. Converts to DataFrame with correct column order
2. Applies the fitted preprocessor (imputation, encoding, scaling)
3. Returns numpy array ready for model.predict()
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ..validation.pydantic_schemas import ExtractedFeatures
from .model_loader import ModelLoader
import logging

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """
    Transforms user-provided features into model-ready format.
    
    The preprocessor expects:
    - 12 features in a specific order
    - Same column names as training data
    - Categorical values that match training categories
    """
    
    # The exact order of columns as expected by the preprocessor
    # This MUST match the order used during training (from Phase 3)
    COLUMN_ORDER = [
        'Bedroom AbvGr',
        'Gr Liv Area', 
        'Lot Area',
        'Year Built',
        'Garage Cars',
        'bathrooms',
        'Overall Cond',
        'Overall Qual',
        'Neighborhood',
        'Bsmt Qual',
        'Heating',
        'Central Air'
    ]
    
    @classmethod
    def _features_to_dataframe(cls, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert features dict to DataFrame with correct column order.
        
        Maps our feature names (bedrooms, sqft_living, etc.) to 
        the original column names (Bedroom AbvGr, Gr Liv Area, etc.)
        """
        # Mapping from our schema names to original column names
        name_mapping = {
            'bedrooms': 'Bedroom AbvGr',
            'sqft_living': 'Gr Liv Area',
            'sqft_lot': 'Lot Area',
            'year_built': 'Year Built',
            'garage_cars': 'Garage Cars',
            'bathrooms': 'bathrooms',
            'condition': 'Overall Cond',
            'quality': 'Overall Qual',
            'neighborhood': 'Neighborhood',
            'basement': 'Bsmt Qual',
            'heating': 'Heating',
            'central_air': 'Central Air'
        }
        
        # Create a dict with original column names
        mapped_features = {}
        for our_name, original_name in name_mapping.items():
            if our_name in features:
                mapped_features[original_name] = features[our_name]
            else:
                mapped_features[original_name] = None
        
        # Create DataFrame with correct column order
        df = pd.DataFrame([mapped_features])
        df = df[cls.COLUMN_ORDER]
        
        return df
    
    @classmethod
    def transform(cls, features: ExtractedFeatures) -> np.ndarray:
        """
        Transform ExtractedFeatures to model-ready numpy array.
        
        Args:
            features: Validated ExtractedFeatures object
            
        Returns:
            numpy array ready for model.predict()
            
        Example:
            features = ExtractedFeatures(bedrooms=3, bathrooms=2.0, ...)
            X = FeaturePipeline.transform(features)
            prediction = model.predict(X)[0]
        """
        # Convert to dict
        features_dict = features.model_dump(exclude_none=False)
        
        # Convert to DataFrame with correct column order
        df = cls._features_to_dataframe(features_dict)
        
        logger.debug(f"Input DataFrame shape: {df.shape}")
        logger.debug(f"Input DataFrame columns: {df.columns.tolist()}")
        
        # Get preprocessor from ModelLoader
        _, preprocessor = ModelLoader.get_model()
        
        # Transform using fitted preprocessor
        X_transformed = preprocessor.transform(df)
        
        logger.debug(f"Transformed shape: {X_transformed.shape}")
        
        return X_transformed
    
    @classmethod
    def transform_dict(cls, features_dict: Dict[str, Any]) -> np.ndarray:
        """
        Transform a dictionary of features to model-ready numpy array.
        
        Useful when you have a dict from Stage 1 LLM output.
        """
        # Create ExtractedFeatures object (validates types)
        features = ExtractedFeatures(**features_dict)
        return cls.transform(features)
    
    @classmethod
    def get_expected_features(cls) -> List[str]:
        """Return list of expected feature names (for debugging)"""
        return cls.COLUMN_ORDER