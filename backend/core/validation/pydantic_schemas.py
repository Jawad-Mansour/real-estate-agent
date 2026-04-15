"""
Pydantic Schemas for AI Real Estate Agent

These schemas validate and type-check all data flowing through the system.
They convert LLM string outputs ("three" → 3) and enforce completeness.

PDF Requirements:
- #06: Stage 1 feature extraction with completeness signal
- #09: Two Pydantic schemas minimum + error handling
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# ============================================================================
# SCHEMA 1: Extracted Features (12 fields - matches our model)
# ============================================================================

class ExtractedFeatures(BaseModel):
    """
    The 12 features our ML model expects.
    
    All fields are Optional because the LLM may not extract them all.
    The completeness gate will check which ones are missing.
    
    PDF #06: "Include a completeness signal - which features were confidently 
    extracted vs which are missing. Do not silently fill gaps with defaults."
    """
    
    # Numeric features
    bedrooms: Optional[int] = Field(None, ge=0, le=10, description="Number of bedrooms (0-10)")
    bathrooms: Optional[float] = Field(None, ge=0, le=8, description="Number of bathrooms (0-8, 0.5 increments)")
    sqft_living: Optional[int] = Field(None, ge=300, le=10000, description="Living area square feet")
    sqft_lot: Optional[int] = Field(None, ge=500, le=200000, description="Lot area square feet")
    year_built: Optional[int] = Field(None, ge=1800, le=2025, description="Year built")
    garage_cars: Optional[int] = Field(None, ge=0, le=5, description="Garage capacity in cars")
    
    # Ordinal features (have order)
    condition: Optional[int] = Field(None, ge=1, le=10, description="Overall condition (1-10)")
    quality: Optional[int] = Field(None, ge=1, le=10, description="Overall quality (1-10)")
    
    # Categorical features
    neighborhood: Optional[str] = Field(None, max_length=50, description="Neighborhood name")
    basement: Optional[str] = Field(None, description="Basement quality (Ex/Gd/TA/Fa/Po/None)")
    heating: Optional[str] = Field(None, description="Heating type (GasA/GasW/Wall/etc.)")
    central_air: Optional[str] = Field(None, pattern="^(Y|N|y|n)$", description="Central air (Y/N)")
    
    # Validators for specific fields
    @field_validator('bathrooms')
    @classmethod
    def validate_bathrooms(cls, v):
        """Ensure bathrooms are in 0.5 increments"""
        if v is not None and v * 2 != int(v * 2):
            raise ValueError(f'Bathrooms must be in 0.5 increments, got {v}')
        return v
    
    @field_validator('central_air')
    @classmethod
    def validate_central_air(cls, v):
        """Convert lowercase to uppercase and validate"""
        if v is not None:
            v = v.upper()
            if v not in ['Y', 'N']:
                raise ValueError(f'Central air must be Y or N, got {v}')
        return v
    
    @field_validator('basement')
    @classmethod
    def validate_basement(cls, v):
        """Validate basement quality values"""
        if v is not None:
            valid_values = ['Ex', 'Gd', 'TA', 'Fa', 'Po', 'None', 'NA']
            if v not in valid_values:
                # Try to map common variations
                v_upper = v.upper()
                if v_upper in ['EX', 'EXCELLENT']:
                    return 'Ex'
                elif v_upper in ['GD', 'GOOD']:
                    return 'Gd'
                elif v_upper in ['TA', 'TYPICAL', 'AVERAGE']:
                    return 'TA'
                elif v_upper in ['FA', 'FAIR']:
                    return 'Fa'
                elif v_upper in ['PO', 'POOR']:
                    return 'Po'
                elif v_upper in ['NONE', 'NO', 'NA', 'MISSING']:
                    return 'None'
                else:
                    raise ValueError(f'Invalid basement quality: {v}. Must be Ex/Gd/TA/Fa/Po/None')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "bedrooms": 3,
                "bathrooms": 2.0,
                "sqft_living": 1656,
                "sqft_lot": 31770,
                "year_built": 1960,
                "garage_cars": 2,
                "condition": 5,
                "quality": 6,
                "neighborhood": "NAmes",
                "basement": "TA",
                "heating": "GasA",
                "central_air": "Y"
            }
        }


# ============================================================================
# SCHEMA 2: Stage 1 Output (with completeness metadata)
# ============================================================================

class Stage1Output(BaseModel):
    """
    Output from Stage 1 LLM extraction.
    
    Contains both the extracted features AND a list of which features are missing.
    This is the "completeness signal" required by PDF #06.
    """
    
    extracted_features: ExtractedFeatures
    missing_fields: List[str] = Field(
        default_factory=list,
        description="List of feature names that were not extracted from the query"
    )
    completeness_score: float = Field(
        ge=0, le=1,
        description="Percentage of features extracted (0.0 to 1.0)"
    )
    raw_llm_output: Optional[str] = Field(
        None,
        description="Raw LLM response for debugging"
    )
    
    @classmethod
    def from_extracted(cls, features: ExtractedFeatures) -> "Stage1Output":
        """Create Stage1Output by checking which fields are missing"""
        # Get all field names
        all_fields = features.model_fields.keys()
        
        # Find which fields are None (missing)
        missing = []
        for field in all_fields:
            value = getattr(features, field)
            if value is None:
                missing.append(field)
        
        # Calculate completeness score
        total_fields = len(all_fields)
        extracted_count = total_fields - len(missing)
        completeness = extracted_count / total_fields if total_fields > 0 else 0.0
        
        return cls(
            extracted_features=features,
            missing_fields=missing,
            completeness_score=round(completeness, 2)
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if all features are present (completeness_score == 1.0)"""
        return self.completeness_score == 1.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "extracted_features": {
                    "bedrooms": 3,
                    "bathrooms": None,
                    "sqft_living": None,
                    "sqft_lot": None,
                    "year_built": None,
                    "garage_cars": None,
                    "condition": None,
                    "quality": None,
                    "neighborhood": None,
                    "basement": None,
                    "heating": None,
                    "central_air": None
                },
                "missing_fields": ["bathrooms", "sqft_living", "sqft_lot", "year_built", 
                                   "garage_cars", "condition", "quality", "neighborhood", 
                                   "basement", "heating", "central_air"],
                "completeness_score": 0.08
            }
        }


# ============================================================================
# SCHEMA 3: Stage 2 Output (Prediction Interpretation)
# ============================================================================

class Stage2Output(BaseModel):
    """Output from Stage 2 LLM interpretation"""
    
    explanation: str = Field(
        description="Natural language explanation of the prediction"
    )
    key_factors: List[str] = Field(
        default_factory=list,
        description="List of key factors driving the price"
    )
    comparison: str = Field(
        description="How this price compares to median (e.g., '21% above median')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "explanation": "At $425,000, this home is 21% above the median due to its large garage and desirable neighborhood.",
                "key_factors": ["2-car garage", "Desirable neighborhood", "Excellent quality"],
                "comparison": "21% above median"
            }
        }


# ============================================================================
# SCHEMA 4: API Request/Response
# ============================================================================

class PredictRequest(BaseModel):
    """API request body for prediction endpoint"""
    
    query: str = Field(
        min_length=1,
        max_length=500,
        description="Natural language description of the property"
    )
    # Optional: for when user fills missing fields manually
    override_features: Optional[ExtractedFeatures] = Field(
        None,
        description="Override extracted features with user-provided values"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "3-bedroom ranch with a big garage in a good neighborhood"
            }
        }


class PredictResponse(BaseModel):
    """API response body for prediction endpoint"""
    
    success: bool = Field(description="Whether the request succeeded")
    status: str = Field(description="Status: 'complete', 'incomplete', or 'error'")
    message: str = Field(description="Human-readable message")
    
    # For incomplete status (missing fields)
    missing_fields: Optional[List[str]] = Field(
        None,
        description="List of missing features that need user input"
    )
    extracted_features: Optional[Dict[str, Any]] = Field(
        None,
        description="Features extracted by Stage 1 LLM"
    )
    
    # For complete status (prediction ready)
    predicted_price: Optional[float] = Field(
        None,
        description="Predicted sale price in dollars"
    )
    formatted_price: Optional[str] = Field(
        None,
        description="Formatted price (e.g., '$425,000')"
    )
    explanation: Optional[str] = Field(
        None,
        description="Stage 2 LLM explanation"
    )
    key_factors: Optional[List[str]] = Field(
        None,
        description="Key factors driving the price"
    )
    comparison: Optional[str] = Field(
        None,
        description="Comparison to median price"
    )
    
    @classmethod
    def success_complete(cls, price: float, explanation: str, key_factors: List[str], comparison: str) -> "PredictResponse":
        """Create a successful response with prediction"""
        return cls(
            success=True,
            status="complete",
            message="Prediction completed successfully",
            predicted_price=price,
            formatted_price=f"${price:,.0f}",
            explanation=explanation,
            key_factors=key_factors,
            comparison=comparison
        )
    
    @classmethod
    def success_incomplete(cls, missing_fields: List[str], extracted_features: Dict[str, Any]) -> "PredictResponse":
        """Create a response indicating missing fields need user input"""
        return cls(
            success=True,
            status="incomplete",
            message=f"Missing {len(missing_fields)} features. Please provide them.",
            missing_fields=missing_fields,
            extracted_features=extracted_features
        )
    
    @classmethod
    def error(cls, error_message: str) -> "PredictResponse":
        """Create an error response"""
        return cls(
            success=False,
            status="error",
            message=f"Error: {error_message}"
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status": "complete",
                "message": "Prediction completed successfully",
                "predicted_price": 425000,
                "formatted_price": "$425,000",
                "explanation": "At $425,000, this home is 21% above the median due to its large garage and desirable neighborhood.",
                "key_factors": ["2-car garage", "Desirable neighborhood", "Excellent quality"],
                "comparison": "21% above median"
            }
        }


# ============================================================================
# SCHEMA 5: Error Response (for API error handling)
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response for API failures"""
    
    success: bool = Field(default=False)
    error_type: str = Field(description="Type of error (validation_error, api_error, etc.)")
    error_message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def validation_error(cls, message: str, details: Dict = None) -> "ErrorResponse":
        """Create validation error response"""
        return cls(
            error_type="validation_error",
            error_message=message,
            details=details
        )
    
    @classmethod
    def api_error(cls, message: str) -> "ErrorResponse":
        """Create API error response"""
        return cls(
            error_type="api_error",
            error_message=message
        )
    
    @classmethod
    def model_error(cls, message: str) -> "ErrorResponse":
        """Create model loading/prediction error response"""
        return cls(
            error_type="model_error",
            error_message=message
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_type": "validation_error",
                "error_message": "Invalid value for garage_cars: expected integer 0-5, got 'huge'",
                "timestamp": "2026-04-15T10:30:00"
            }
        }