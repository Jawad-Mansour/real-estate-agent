"""
Test the model with custom property descriptions
Run with: python scripts/test_custom_predictions.py
"""

import sys
import os

sys.path.insert(0, os.getcwd())

from backend.core.ml import ModelLoader, Predictor
from backend.core.validation import ExtractedFeatures

print("=" * 70)
print("TEST MODEL WITH CUSTOM PROPERTIES")
print("=" * 70)

# Load model once
model, preprocessor = ModelLoader.get_model()

# ============================================================================
# TEST CASE 1: Average House (Typical Ames home)
# ============================================================================
print("\n" + "=" * 70)
print("TEST CASE 1: AVERAGE HOUSE")
print("=" * 70)

avg_house = ExtractedFeatures(
    bedrooms=3,
    bathrooms=2.0,
    sqft_living=1500,
    sqft_lot=10000,
    year_built=1975,
    garage_cars=2,
    condition=5,
    quality=5,
    neighborhood="NAmes",
    basement="TA",
    heating="GasA",
    central_air="Y"
)

price = Predictor.predict(avg_house)
print(f"\nProperty Description:")
print(f"  - 3 bedrooms, 2 bathrooms")
print(f"  - 1,500 sq ft living area")
print(f"  - 10,000 sq ft lot")
print(f"  - Built in 1975")
print(f"  - 2-car garage")
print(f"  - Average condition (5/10), Average quality (5/10)")
print(f"  - NAmes neighborhood")
print(f"\n💰 PREDICTED PRICE: ${price:,.0f}")
print(f"📊 Comparison: {((price - 160000) / 160000 * 100):+.0f}% vs median ($160,000)")

# ============================================================================
# TEST CASE 2: Luxury House (High quality, desirable neighborhood)
# ============================================================================
print("\n" + "=" * 70)
print("TEST CASE 2: LUXURY HOUSE")
print("=" * 70)

luxury_house = ExtractedFeatures(
    bedrooms=4,
    bathrooms=3.5,
    sqft_living=3500,
    sqft_lot=20000,
    year_built=2015,
    garage_cars=3,
    condition=9,
    quality=9,
    neighborhood="StoneBr",
    basement="Ex",
    heating="GasA",
    central_air="Y"
)

price = Predictor.predict(luxury_house)
print(f"\nProperty Description:")
print(f"  - 4 bedrooms, 3.5 bathrooms")
print(f"  - 3,500 sq ft living area")
print(f"  - 20,000 sq ft lot")
print(f"  - Built in 2015 (newer)")
print(f"  - 3-car garage")
print(f"  - Excellent condition (9/10), Excellent quality (9/10)")
print(f"  - StoneBr neighborhood (premium)")
print(f"\n💰 PREDICTED PRICE: ${price:,.0f}")
print(f"📊 Comparison: {((price - 160000) / 160000 * 100):+.0f}% vs median ($160,000)")

# ============================================================================
# TEST CASE 3: Small Starter Home
# ============================================================================
print("\n" + "=" * 70)
print("TEST CASE 3: SMALL STARTER HOME")
print("=" * 70)

starter_home = ExtractedFeatures(
    bedrooms=2,
    bathrooms=1.0,
    sqft_living=900,
    sqft_lot=5000,
    year_built=1950,
    garage_cars=1,
    condition=4,
    quality=4,
    neighborhood="OldTown",
    basement="Po",
    heating="GasW",
    central_air="N"
)

price = Predictor.predict(starter_home)
print(f"\nProperty Description:")
print(f"  - 2 bedrooms, 1 bathroom")
print(f"  - 900 sq ft living area")
print(f"  - 5,000 sq ft lot")
print(f"  - Built in 1950 (older)")
print(f"  - 1-car garage")
print(f"  - Poor condition (4/10), Poor quality (4/10)")
print(f"  - OldTown neighborhood")
print(f"\n💰 PREDICTED PRICE: ${price:,.0f}")
print(f"📊 Comparison: {((price - 160000) / 160000 * 100):+.0f}% vs median ($160,000)")

# ============================================================================
# TEST CASE 4: Your Custom Property
# ============================================================================
print("\n" + "=" * 70)
print("TEST CASE 4: CUSTOM PROPERTY (Enter your own)")
print("=" * 70)

print("\nEnter your own property details (press Enter to use defaults):")

# Get user input with defaults
bedrooms = input("  Bedrooms (default 3): ") or "3"
bathrooms = input("  Bathrooms (default 2.0): ") or "2.0"
sqft = input("  Living area sq ft (default 2000): ") or "2000"
lot = input("  Lot area sq ft (default 10000): ") or "10000"
year = input("  Year built (default 2000): ") or "2000"
garage = input("  Garage cars (default 2): ") or "2"
quality = input("  Quality (1-10, default 6): ") or "6"
neighborhood = input("  Neighborhood (NAmes, StoneBr, Gilbert, OldTown): ") or "NAmes"

custom_house = ExtractedFeatures(
    bedrooms=int(bedrooms),
    bathrooms=float(bathrooms),
    sqft_living=int(sqft),
    sqft_lot=int(lot),
    year_built=int(year),
    garage_cars=int(garage),
    condition=5,
    quality=int(quality),
    neighborhood=neighborhood,
    basement="TA",
    heating="GasA",
    central_air="Y"
)

price = Predictor.predict(custom_house)
print(f"\n💰 PREDICTED PRICE: ${price:,.0f}")
print(f"📊 Comparison: {((price - 160000) / 160000 * 100):+.0f}% vs median ($160,000)")

print("\n" + "=" * 70)
print("✅ Test complete! Do these prices seem realistic to you?")
print("=" * 70)
