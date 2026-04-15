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
    
    def _load_artifacts(self):
        """Load model and preprocessor from disk"""
        # Get the absolute path to backend/models/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(base_dir, 'models')
        
        model_path = os.path.join(models_dir, 'model.joblib')
        preprocessor_path = os.path.join(models_dir, 'preprocessor.joblib')
        
        # Check if files exist
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found at {preprocessor_path}")
        
        # Load artifacts
        logger.info(f"Loading model from {model_path}...")
        self._model = joblib.load(model_path)
        logger.info(f"Model loaded successfully: {type(self._model).__name__}")
        
        logger.info(f"Loading preprocessor from {preprocessor_path}...")
        self._preprocessor = joblib.load(preprocessor_path)
        logger.info("Preprocessor loaded successfully")
    
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