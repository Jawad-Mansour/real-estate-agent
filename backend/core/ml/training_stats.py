"""
Training Statistics - Loads statistics from TRAINING data only

These statistics are used by Stage 2 LLM to provide context:
- "This price is 20% above the median"
- "The predicted price is in the top 25% of homes"

PDF #07: "Feed Stage 2 the extracted features, the prediction, and summary stats 
from your training data (median price, typical range)."
"""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TrainingStats:
    """
    Loads and provides access to training data statistics.
    
    All statistics are from TRAINING data only (NO LEAKAGE).
    These numbers represent what a "typical" house looks like.
    """
    
    _instance = None
    _stats = None
    
    def __new__(cls):
        """Singleton pattern - load stats once"""
        if cls._instance is None:
            cls._instance = super(TrainingStats, cls).__new__(cls)
            cls._instance._load_stats()
        return cls._instance
    
    def _load_stats(self):
        """Load training statistics from JSON file"""
        # Get the absolute path to backend/models/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        stats_path = os.path.join(base_dir, 'models', 'training_stats.json')
        
        if not os.path.exists(stats_path):
            raise FileNotFoundError(f"Training stats not found at {stats_path}")
        
        with open(stats_path, 'r') as f:
            self._stats = json.load(f)
        
        logger.info(f"Training stats loaded: median=${self._stats.get('median_price', 0):,.0f}")
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get all training statistics"""
        instance = cls()
        return instance._stats
    
    @classmethod
    def get_median_price(cls) -> float:
        """Get median price from training data"""
        instance = cls()
        return instance._stats.get('median_price', 0)
    
    @classmethod
    def get_mean_price(cls) -> float:
        """Get mean price from training data"""
        instance = cls()
        return instance._stats.get('mean_price', 0)
    
    @classmethod
    def get_price_range(cls) -> tuple:
        """Get min and max price from training data"""
        instance = cls()
        return (instance._stats.get('min_price', 0), instance._stats.get('max_price', 0))
    
    @classmethod
    def get_quartiles(cls) -> tuple:
        """Get Q1 and Q3 from training data"""
        instance = cls()
        return (instance._stats.get('q1_price', 0), instance._stats.get('q3_price', 0))
    
    @classmethod
    def get_comparison(cls, price: float) -> str:
        """
        Get a human-readable comparison of a price to training data.
        
        Returns strings like:
        - "21% above median"
        - "15% below median"  
        - "In the top 25% of homes"
        - "In the bottom 25% of homes"
        """
        median = cls.get_median_price()
        q1, q3 = cls.get_quartiles()
        
        if price > median:
            percent_above = ((price - median) / median) * 100
            if price > q3:
                return f"{percent_above:.0f}% above median (top 25%)"
            return f"{percent_above:.0f}% above median"
        else:
            percent_below = ((median - price) / median) * 100
            if price < q1:
                return f"{percent_below:.0f}% below median (bottom 25%)"
            return f"{percent_below:.0f}% below median"
    
    @classmethod
    def get_formatted_stats(cls) -> str:
        """Get a formatted string of key statistics for LLM context"""
        instance = cls()
        return f"""Median price: ${instance._stats.get('median_price', 0):,.0f}
Mean price: ${instance._stats.get('mean_price', 0):,.0f}
Typical range: ${instance._stats.get('q1_price', 0):,.0f} - ${instance._stats.get('q3_price', 0):,.0f}
Overall range: ${instance._stats.get('min_price', 0):,.0f} - ${instance._stats.get('max_price', 0):,.0f}"""