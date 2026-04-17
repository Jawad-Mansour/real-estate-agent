"""
Model Loader - Singleton Pattern

Loads model and preprocessor ONCE at startup and reuses them for all requests.
This is critical for PDF #10: "Model loads at startup"

Why Singleton?
- Loading model from disk takes ~100ms
- If loaded per request, API becomes slow
- With singleton: load once (100ms), then each prediction is ~10ms
"""

import joblib
import os
import numpy as np
from typing import Tuple, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Singleton class that loads and holds the ML model and preprocessor.
    
    Usage:
        model, preprocessor = ModelLoader.get_model()
        prediction = model.predict(preprocessor.transform(data))
    """
    
    _instance = None
    _model = None
    _preprocessor = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_artifacts()
        return cls._instance
    
    def _create_mock_model(self):
        """Create a mock model for development when real model files are missing"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler
            from sklearn.compose import ColumnTransformer
            
            logger.warning("Creating mock model for development (real model files not found)")
            
            # Create mock model
            self._model = RandomForestRegressor(n_estimators=10, random_state=42)
            
            # Create mock preprocessor
            self._preprocessor = ColumnTransformer([
                ('scaler', StandardScaler(), [0, 1, 2, 3, 4, 5])
            ])
            
            # Fit with dummy data to make it usable
            dummy_X = np.random.randn(10, 6)
            dummy_y = np.random.randn(10) * 50000 + 200000
            self._model.fit(dummy_X, dummy_y)
            self._preprocessor.fit(dummy_X)
            
            logger.info("Mock model and preprocessor created successfully")
        except Exception as e:
            logger.error(f"Failed to create mock model: {e}")
            raise
    
    def _load_artifacts(self):
        """Load model and preprocessor from disk with fallback for development"""
        # Get the absolute path to backend/models/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(base_dir, 'models')
        
        model_path = os.path.join(models_dir, 'model.joblib')
        preprocessor_path = os.path.join(models_dir, 'preprocessor.joblib')
        
        # Check if files exist - if not, use mock model for development
        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            logger.warning(f"Model files not found at {models_dir}. Using mock model for development.")
            self._create_mock_model()
            return
        
        # Load real artifacts
        try:
            logger.info(f"Loading model from {model_path}...")
            self._model = joblib.load(model_path)
            logger.info(f"Model loaded successfully: {type(self._model).__name__}")
            
            logger.info(f"Loading preprocessor from {preprocessor_path}...")
            self._preprocessor = joblib.load(preprocessor_path)
            logger.info("Preprocessor loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model files: {e}. Using mock model instead.")
            self._create_mock_model()
    
    @classmethod
    def get_model(cls) -> Tuple[Any, Any]:
        """
        Get the loaded model and preprocessor.
        
        Returns:
            Tuple of (model, preprocessor)
            
        Example:
            model, preprocessor = ModelLoader.get_model()
            prediction = model.predict(preprocessor.transform(data))
        """
        instance = cls()
        return instance._model, instance._preprocessor
    
    @classmethod
    def get_model_only(cls) -> Any:
        """Get only the model (if preprocessor not needed)"""
        instance = cls()
        return instance._model
    
    @classmethod
    def get_preprocessor_only(cls) -> Any:
        """Get only the preprocessor"""
        instance = cls()
        return instance._preprocessor
    
    @classmethod
    def is_loaded(cls) -> bool:
        """Check if model and preprocessor are loaded"""
        instance = cls()
        return instance._model is not None and instance._preprocessor is not None