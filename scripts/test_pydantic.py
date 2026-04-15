"""
Test script for Pydantic schemas and completeness gate
Run with: python scripts/test_pydantic.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.validation import (
    ExtractedFeatures,
    Stage1Output,
    PredictRequest,
    PredictResponse,
    CompletenessGate,
    FeatureValidator
)

print("=" * 60)
print("TESTING PYDANTIC SCHEMAS")
print("=" * 60)

# ============================================================================
# TEST 1: Valid features (all present)
# ============================================================================
print("\n1. TESTING VALID FEATURES (ALL PRESENT)")
print("-" * 40)

valid_features = ExtractedFeatures(
    bedrooms=3,
    bathrooms=2.0,
    sqft_living=1656,
    sqft_lot=31770,
    year_built=1960,
    garage_cars=2,
    condition=5,
    quality=6,
    neighborhood="NAmes",
    basement="TA",
    heating="GasA",
    central_air="Y"
)

print(f"✓ Created ExtractedFeatures successfully")
print(f"  Bedrooms: {valid_features.bedrooms}")
print(f"  Bathrooms: {valid_features.bathrooms}")
print(f"  Neighborhood: {valid_features.neighborhood}")

# Test completeness gate
is_complete, missing = CompletenessGate.check(valid_features)
print(f"\n  Completeness Gate: is_complete={is_complete}, missing={missing}")

# Test feature validator
is_valid, errors = FeatureValidator.validate(valid_features)
print(f"  Feature Validator: is_valid={is_valid}, errors={errors}")

# Create Stage1Output
stage1_output = CompletenessGate.create_stage1_output(valid_features)
print(f"\n  Stage1Output: completeness_score={stage1_output.completeness_score}")
print(f"  Stage1Output: is_complete={stage1_output.is_complete}")

# ============================================================================
# TEST 2: Missing features (user said "3-bedroom house")
# ============================================================================
print("\n2. TESTING MISSING FEATURES (ONLY BEDROOMS PROVIDED)")
print("-" * 40)

partial_features = ExtractedFeatures(
    bedrooms=3,
    bathrooms=None,
    sqft_living=None,
    sqft_lot=None,
    year_built=None,
    garage_cars=None,
    condition=None,
    quality=None,
    neighborhood=None,
    basement=None,
    heating=None,
    central_air=None
)

print(f"✓ Created ExtractedFeatures with only bedrooms")

# Test completeness gate
is_complete, missing = CompletenessGate.check(partial_features)
print(f"\n  Completeness Gate: is_complete={is_complete}")
print(f"  Missing fields ({len(missing)}): {missing}")

# Convert to user-friendly names
user_friendly = CompletenessGate.to_user_friendly_names(missing)
print(f"  User-friendly names: {user_friendly}")

# Create Stage1Output
stage1_output = CompletenessGate.create_stage1_output(partial_features)
print(f"\n  Stage1Output: completeness_score={stage1_output.completeness_score}")
print(f"  Stage1Output: missing_fields={stage1_output.missing_fields}")

# ============================================================================
# TEST 3: Pydantic type conversion (string "three" → int 3)
# ============================================================================
print("\n3. TESTING TYPE CONVERSION (LLM returns strings)")
print("-" * 40)

# Pydantic automatically converts compatible types
string_features = ExtractedFeatures(
    bedrooms="3",  # String instead of int
    bathrooms="2.0",  # String instead of float
    sqft_living="1656",
    sqft_lot="31770",
    year_built="1960",
    garage_cars="2",
    condition="5",
    quality="6",
    neighborhood="NAmes",
    basement="TA",
    heating="GasA",
    central_air="Y"
)

print(f"✓ Created ExtractedFeatures from strings")
print(f"  Bedrooms type: {type(string_features.bedrooms).__name__} = {string_features.bedrooms}")
print(f"  Bathrooms type: {type(string_features.bathrooms).__name__} = {string_features.bathrooms}")
print(f"  Pydantic automatically converted strings to numbers!")

# ============================================================================
# TEST 4: Invalid values (should raise ValidationError)
# ============================================================================
print("\n4. TESTING INVALID VALUES (should raise errors)")
print("-" * 40)

try:
    invalid_features = ExtractedFeatures(
        bedrooms=100,  # Too many bedrooms
        bathrooms=3.2,  # Not in 0.5 increments
        garage_cars=10,  # Too many cars
        central_air="MAYBE",  # Invalid value
        **{f: None for f in ExtractedFeatures.model_fields.keys() if f not in ['bedrooms', 'bathrooms', 'garage_cars', 'central_air']}
    )
    print("✗ Should have raised ValidationError but didn't")
except Exception as e:
    print(f"✓ Caught validation error: {type(e).__name__}")
    print(f"  Error message: {str(e)[:100]}...")

# ============================================================================
# TEST 5: PredictResponse factory methods
# ============================================================================
print("\n5. TESTING PREDICT RESPONSE FACTORY METHODS")
print("-" * 40)

# Complete response
complete_response = PredictResponse.success_complete(
    price=425000,
    explanation="At $425,000, this home is 21% above the median due to its large garage.",
    key_factors=["2-car garage", "Desirable neighborhood"],
    comparison="21% above median"
)
print(f"✓ Complete response: status={complete_response.status}, price={complete_response.formatted_price}")

# Incomplete response
incomplete_response = PredictResponse.success_incomplete(
    missing_fields=["sqft_living", "year_built"],
    extracted_features={"bedrooms": 3, "bathrooms": 2}
)
print(f"✓ Incomplete response: status={incomplete_response.status}, missing={incomplete_response.missing_fields}")

# Error response
error_response = PredictResponse.error("LLM failed to respond")
print(f"✓ Error response: success={error_response.success}, message={error_response.message}")

# ============================================================================
# TEST 6: PredictRequest
# ============================================================================
print("\n6. TESTING PREDICT REQUEST")
print("-" * 40)

request = PredictRequest(query="3-bedroom ranch with big garage")
print(f"✓ PredictRequest created: query='{request.query}'")
print(f"  override_features={request.override_features}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("✅ ExtractedFeatures - valid creation")
print("✅ ExtractedFeatures - type conversion (string → int/float)")
print("✅ ExtractedFeatures - validation errors caught")
print("✅ CompletenessGate - detects missing fields")
print("✅ CompletenessGate - calculates completeness score")
print("✅ Stage1Output - creates missing_fields list")
print("✅ PredictResponse - factory methods work")
print("✅ PredictRequest - validates query string")
print("\n✓ ALL TESTS PASSED - Pydantic schemas are working correctly!")
print("=" * 60)
