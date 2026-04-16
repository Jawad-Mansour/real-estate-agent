#!/usr/bin/env python3
"""
Final validation script for AI Real Estate Agent
Run: python scripts/final_validation.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("1. Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] == True
    print("   ✓ Health check passed")
    return True

def test_predict_incomplete():
    print("\n2. Testing Incomplete Query...")
    response = requests.post(f"{BASE_URL}/predict", 
        json={"query": "3-bedroom house in NAmes"})
    data = response.json()
    assert data["status"] == "incomplete"
    print(f"   ✓ Incomplete query detected - missing features")
    return True

def test_predict_complete():
    print("\n3. Testing Complete Query...")
    response = requests.post(f"{BASE_URL}/predict", 
        json={"query": "3 bedroom, 2 bathroom, 1800 sqft, 10000 lot, 2005, 2 car, NAmes, condition 5, quality 6, TA basement, gas heating, central air"})
    data = response.json()
    assert data["status"] == "complete"
    assert data["predicted_price"] is not None
    print(f"   ✓ Complete query returned price: ${data['predicted_price']:,.0f}")
    return True

def main():
    print("=" * 50)
    print("FINAL VALIDATION - AI Real Estate Agent")
    print("=" * 50)
    
    try:
        test_health()
        test_predict_incomplete()
        test_predict_complete()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nProject is ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")

if __name__ == "__main__":
    main()
