"""
Feature Validator - Range and type validation for extracted features
"""

from typing import Dict, Any, List, Tuple
from .pydantic_schemas import ExtractedFeatures


class FeatureValidator:
    """
    Validates that extracted features have reasonable values.
    
    This catches LLM hallucinations like "garage_cars": 100 or "year_built": 1800.
    """
    
    @classmethod
    def validate(cls, features: ExtractedFeatures) -> Tuple[bool, List[str]]:
        """
        Validate all features have reasonable values.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Bedrooms validation
        if features.bedrooms is not None:
            if features.bedrooms < 0 or features.bedrooms > 10:
                errors.append(f"Bedrooms must be between 0 and 10, got {features.bedrooms}")
        
        # Bathrooms validation
        if features.bathrooms is not None:
            if features.bathrooms < 0 or features.bathrooms > 8:
                errors.append(f"Bathrooms must be between 0 and 8, got {features.bathrooms}")
            # Check 0.5 increments
            if features.bathrooms * 2 != int(features.bathrooms * 2):
                errors.append(f"Bathrooms must be in 0.5 increments, got {features.bathrooms}")
        
        # Square footage validation
        if features.sqft_living is not None:
            if features.sqft_living < 300 or features.sqft_living > 10000:
                errors.append(f"Living area must be between 300 and 10,000 sq ft, got {features.sqft_living}")
        
        if features.sqft_lot is not None:
            if features.sqft_lot < 500 or features.sqft_lot > 200000:
                errors.append(f"Lot area must be between 500 and 200,000 sq ft, got {features.sqft_lot}")
        
        # Year validation
        if features.year_built is not None:
            if features.year_built < 1800 or features.year_built > 2025:
                errors.append(f"Year built must be between 1800 and 2025, got {features.year_built}")
        
        # Garage validation
        if features.garage_cars is not None:
            if features.garage_cars < 0 or features.garage_cars > 5:
                errors.append(f"Garage capacity must be between 0 and 5 cars, got {features.garage_cars}")
        
        # Quality/Condition validation
        if features.condition is not None:
            if features.condition < 1 or features.condition > 10:
                errors.append(f"Condition must be between 1 and 10, got {features.condition}")
        
        if features.quality is not None:
            if features.quality < 1 or features.quality > 10:
                errors.append(f"Quality must be between 1 and 10, got {features.quality}")
        
        # Central air validation
        if features.central_air is not None:
            if features.central_air.upper() not in ['Y', 'N']:
                errors.append(f"Central air must be Y or N, got {features.central_air}")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def to_dict(cls, features: ExtractedFeatures) -> Dict[str, Any]:
        """Convert ExtractedFeatures to dict, excluding None values"""
        return {k: v for k, v in features.model_dump().items() if v is not None}