"""
Test the trained model with actual data from the CSV
Run with: python scripts/test_model_real_data.py
"""

import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.getcwd())

from backend.core.ml import ModelLoader, Predictor
from backend.core.validation import ExtractedFeatures

print("=" * 70)
print("TESTING MODEL WITH REAL AMES HOUSING DATA")
print("=" * 70)

# Load the model once
model, preprocessor = ModelLoader.get_model()

# Load the processed dataset (12 features)
df = pd.read_csv('data/processed/ames_selected.csv')
print(f"\n✓ Loaded {len(df)} rows from processed dataset")

# Take first 10 rows as test samples
test_samples = df.head(10).copy()
print(f"✓ Testing on first 10 rows")

print("\n" + "=" * 70)
print("PREDICTION RESULTS (Actual vs Predicted)")
print("=" * 70)

results = []
for idx, row in test_samples.iterrows():
    # Extract actual price
    actual_price = row['SalePrice']
    
    # Create features object from row data
    features = ExtractedFeatures(
        bedrooms=int(row['Bedroom AbvGr']),
        bathrooms=float(row['bathrooms']),
        sqft_living=int(row['Gr Liv Area']),
        sqft_lot=int(row['Lot Area']),
        year_built=int(row['Year Built']),
        garage_cars=int(row['Garage Cars']) if not pd.isna(row['Garage Cars']) else 0,
        condition=int(row['Overall Cond']),
        quality=int(row['Overall Qual']),
        neighborhood=str(row['Neighborhood']),
        basement=str(row['Bsmt Qual']) if not pd.isna(row['Bsmt Qual']) else 'None',
        heating=str(row['Heating']),
        central_air=str(row['Central Air'])
    )
    
    # Predict
    predicted_price = Predictor.predict(features)
    
    # Calculate error
    error = predicted_price - actual_price
    error_pct = (error / actual_price) * 100
    
    results.append({
        'index': idx,
        'actual': actual_price,
        'predicted': predicted_price,
        'error': error,
        'error_pct': error_pct
    })
    
    print(f"\nSample {idx + 1}:")
    print(f"  Bedrooms: {features.bedrooms}, Bathrooms: {features.bathrooms}, Sqft: {features.sqft_living}")
    print(f"  Neighborhood: {features.neighborhood}, Quality: {features.quality}")
    print(f"  Actual: ${actual_price:,.0f}")
    print(f"  Predicted: ${predicted_price:,.0f}")
    print(f"  Error: ${error:+,.0f} ({error_pct:+.1f}%)")

# Summary statistics
print("\n" + "=" * 70)
print("SUMMARY STATISTICS")
print("=" * 70)

results_df = pd.DataFrame(results)
print(f"\nMean Actual Price: ${results_df['actual'].mean():,.0f}")
print(f"Mean Predicted Price: ${results_df['predicted'].mean():,.0f}")
print(f"Mean Absolute Error: ${results_df['error'].abs().mean():,.0f}")
print(f"Mean Absolute Percentage Error: {results_df['error_pct'].abs().mean():.1f}%")
print(f"RMSE: ${np.sqrt((results_df['error']**2).mean()):,.0f}")

# Calculate R²
ss_res = np.sum((results_df['actual'] - results_df['predicted']) ** 2)
ss_tot = np.sum((results_df['actual'] - results_df['actual'].mean()) ** 2)
r2 = 1 - (ss_res / ss_tot)
print(f"R² Score: {r2:.4f}")

print("\n" + "=" * 70)
print("✅ Model test complete!")
print("=" * 70)
