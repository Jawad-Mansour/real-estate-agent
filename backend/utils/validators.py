"""
Input validation utilities
"""

import re
from typing import Dict, Any, Tuple, List
from backend.utils.exceptions import ValidationException


def validate_query(query: str) -> str:
    """
    Validate user query string
    
    Args:
        query: User input query
    
    Returns:
        Stripped and validated query
    
    Raises:
        ValidationException: If query is invalid
    """
    if not query:
        raise ValidationException("Query cannot be empty", field="query")
    
    if not isinstance(query, str):
        raise ValidationException("Query must be a string", field="query")
    
    stripped = query.strip()
    
    if len(stripped) == 0:
        raise ValidationException("Query cannot be empty", field="query")
    
    if len(stripped) > 500:
        raise ValidationException("Query too long (max 500 characters)", field="query")
    
    # Check for potentially harmful content (basic)
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'\\x',
        r'__import__',
        r'eval\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, stripped, re.IGNORECASE):
            raise ValidationException("Query contains invalid characters", field="query")
    
    return stripped


def validate_features(features: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that features have correct types and ranges
    
    Args:
        features: Dictionary of feature values
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = [
        'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot',
        'year_built', 'garage_cars', 'condition', 'quality',
        'neighborhood', 'basement', 'heating', 'central_air'
    ]
    
    for field in required_fields:
        if field not in features:
            errors.append(f"Missing required field: {field}")
    
    # Type and range validation
    if 'bedrooms' in features:
        try:
            val = int(features['bedrooms'])
            if val < 0 or val > 10:
                errors.append(f"bedrooms must be between 0 and 10, got {val}")
        except (ValueError, TypeError):
            errors.append(f"bedrooms must be an integer, got {features['bedrooms']}")
    
    if 'bathrooms' in features:
        try:
            val = float(features['bathrooms'])
            if val < 0 or val > 8:
                errors.append(f"bathrooms must be between 0 and 8, got {val}")
            if val * 2 != int(val * 2):
                errors.append(f"bathrooms must be in 0.5 increments, got {val}")
        except (ValueError, TypeError):
            errors.append(f"bathrooms must be a number, got {features['bathrooms']}")
    
    if 'sqft_living' in features:
        try:
            val = int(features['sqft_living'])
            if val < 300 or val > 10000:
                errors.append(f"sqft_living must be between 300 and 10000, got {val}")
        except (ValueError, TypeError):
            errors.append(f"sqft_living must be an integer, got {features['sqft_living']}")
    
    if 'sqft_lot' in features:
        try:
            val = int(features['sqft_lot'])
            if val < 500 or val > 200000:
                errors.append(f"sqft_lot must be between 500 and 200000, got {val}")
        except (ValueError, TypeError):
            errors.append(f"sqft_lot must be an integer, got {features['sqft_lot']}")
    
    if 'year_built' in features:
        try:
            val = int(features['year_built'])
            if val < 1800 or val > 2025:
                errors.append(f"year_built must be between 1800 and 2025, got {val}")
        except (ValueError, TypeError):
            errors.append(f"year_built must be an integer, got {features['year_built']}")
    
    if 'garage_cars' in features:
        try:
            val = int(features['garage_cars'])
            if val < 0 or val > 5:
                errors.append(f"garage_cars must be between 0 and 5, got {val}")
        except (ValueError, TypeError):
            errors.append(f"garage_cars must be an integer, got {features['garage_cars']}")
    
    if 'condition' in features:
        try:
            val = int(features['condition'])
            if val < 1 or val > 10:
                errors.append(f"condition must be between 1 and 10, got {val}")
        except (ValueError, TypeError):
            errors.append(f"condition must be an integer, got {features['condition']}")
    
    if 'quality' in features:
        try:
            val = int(features['quality'])
            if val < 1 or val > 10:
                errors.append(f"quality must be between 1 and 10, got {val}")
        except (ValueError, TypeError):
            errors.append(f"quality must be an integer, got {features['quality']}")
    
    if 'central_air' in features:
        val = str(features['central_air']).upper()
        if val not in ['Y', 'N']:
            errors.append(f"central_air must be Y or N, got {features['central_air']}")
    
    return (len(errors) == 0, errors)