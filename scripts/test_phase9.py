"""
Test script for Phase 9: FastAPI Routes
Run with: python scripts/test_phase9.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("TESTING PHASE 9: FASTAPI ROUTES")
print("=" * 70)

# Test 1: Health check
print("\n1. HEALTH CHECK")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Root endpoint
print("\n2. ROOT ENDPOINT")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response keys: {list(response.json().keys())}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Predict - incomplete query
print("\n3. PREDICT - INCOMPLETE QUERY")
print("-" * 40)
payload = {"query": "3-bedroom house"}
response = requests.post(f"{BASE_URL}/predict", json=payload)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response status: {data.get('status')}")
print(f"Message: {data.get('message')}")
if data.get('missing_fields'):
    print(f"Missing fields: {data.get('missing_fields')[:5]}...")

# Test 4: Predict - detailed query
print("\n4. PREDICT - DETAILED QUERY")
print("-" * 40)
payload = {
    "query": "3-bedroom house with 2 bathrooms, 1800 sqft, built 2005, 2 car garage, in NAmes, central air"
}
response = requests.post(f"{BASE_URL}/predict", json=payload)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Response status: {data.get('status')}")
if data.get('status') == 'complete':
    print(f"Price: {data.get('formatted_price')}")
    print(f"Explanation: {data.get('explanation', '')[:150]}...")

print("\n" + "=" * 70)
print("✅ PHASE 9 TESTS COMPLETE")
print("=" * 70)
