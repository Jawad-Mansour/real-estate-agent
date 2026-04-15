"""
Completeness Gate - PDF #06

This module ensures ML prediction only runs when ALL features are present.
If any feature is missing, it returns the missing list to the UI.
"""

from typing import List, Tuple, Dict, Any
from .pydantic_schemas import ExtractedFeatures, Stage1Output


class CompletenessGate:
    """
    Gate that prevents ML prediction when features are missing.
    
    PDF #06: "Do not silently fill gaps with defaults. If the user says '3-bed
    in a good area' and your model needs 12 features, Stage 1 reports what it
    found and what is still needed."
    """
    
    # All 12 feature names our model expects
    REQUIRED_FEATURES = [
        'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot',
        'year_built', 'garage_cars', 'condition', 'quality',
        'neighborhood', 'basement', 'heating', 'central_air'
    ]
    
    @classmethod
    def check(cls, features: ExtractedFeatures) -> Tuple[bool, List[str]]:
        """
        Check if all required features are present.
        
        Returns:
            Tuple of (is_complete, missing_fields)
            
        Example:
            is_complete, missing = CompletenessGate.check(features)
            if not is_complete:
                return {"status": "incomplete", "missing_fields": missing}
        """
        missing = []
        
        for field_name in cls.REQUIRED_FEATURES:
            value = getattr(features, field_name, None)
            if value is None:
                missing.append(field_name)
        
        return (len(missing) == 0, missing)
    
    @classmethod
    def create_stage1_output(cls, features: ExtractedFeatures) -> Stage1Output:
        """Create Stage1Output with completeness metadata"""
        return Stage1Output.from_extracted(features)
    
    @classmethod
    def to_user_friendly_names(cls, missing_fields: List[str]) -> List[str]:
        """Convert field names to user-friendly display names"""
        mapping = {
            'bedrooms': 'Number of bedrooms',
            'bathrooms': 'Number of bathrooms',
            'sqft_living': 'Living area (sq ft)',
            'sqft_lot': 'Lot area (sq ft)',
            'year_built': 'Year built',
            'garage_cars': 'Garage capacity (cars)',
            'condition': 'Overall condition (1-10)',
            'quality': 'Overall quality (1-10)',
            'neighborhood': 'Neighborhood',
            'basement': 'Basement quality',
            'heating': 'Heating type',
            'central_air': 'Central air conditioning'
        }
        
        return [mapping.get(field, field) for field in missing_fields]