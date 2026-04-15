"""
Test script for Phase 8: Prediction Service
Run with: python scripts/test_phase8.py
"""

import sys
import os

sys.path.insert(0, os.getcwd())

print("=" * 70)
print("TESTING PHASE 8: PREDICTION SERVICE (ORCHESTRATOR)")
print("=" * 70)

from backend.services.prediction_service import PredictionService

# Initialize service
service = PredictionService()

# Test 1: Health check
print("\n1. HEALTH CHECK")
print("-" * 40)
health = service.health_check()
print(f"Status: {health['status']}")
if health['status'] == 'healthy':
    print(f"Test prediction: ${health['test_prediction']:,.0f}")

# Test 2: Incomplete query (should return missing_fields)
print("\n2. INCOMPLETE QUERY (Only bedrooms)")
print("-" * 40)
query = "3-bedroom house"
print(f"Query: '{query}'")
response = service.process_query(query)
print(f"Status: {response.status}")
print(f"Message: {response.message}")
if response.status == 'incomplete':
    print(f"Missing fields ({len(response.missing_fields)}): {response.missing_fields[:5]}...")
    print(f"Extracted: {response.extracted_features}")

# Test 3: Detailed query (should predict)
print("\n3. DETAILED QUERY (Should predict)")
print("-" * 40)
query = "3-bedroom house with 2 bathrooms, 1800 sqft, built 2005, 2 car garage, in NAmes, central air"
print(f"Query: '{query}'")
response = service.process_query(query)
print(f"Status: {response.status}")
if response.status == 'complete':
    print(f"Price: {response.formatted_price}")
    print(f"Comparison: {response.comparison}")
    print(f"Key factors: {response.key_factors}")
    print(f"\nExplanation: {response.explanation}")

# Test 4: Override features (user filled missing fields)
print("\n4. OVERRIDE FEATURES (User provided complete data)")
print("-" * 40)
override = {
    "bedrooms": 4,
    "bathrooms": 2.5,
    "sqft_living": 2500,
    "sqft_lot": 15000,
    "year_built": 2010,
    "garage_cars": 2,
    "condition": 7,
    "quality": 8,
    "neighborhood": "StoneBr",
    "basement": "Gd",
    "heating": "GasA",
    "central_air": "Y"
}
response = service.process_query(query="[User filled form]", override_features=override)
print(f"Status: {response.status}")
if response.status == 'complete':
    print(f"Price: {response.formatted_price}")
    print(f"Explanation: {response.explanation[:200]}...")

print("\n" + "=" * 70)
print("✅ PHASE 8 TESTS COMPLETE")
print("=" * 70)
