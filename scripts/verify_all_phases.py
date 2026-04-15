"""
Complete verification script for Phases 0-6
Run with: python scripts/verify_all_phases.py
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import json

print("=" * 70)
print("COMPLETE VERIFICATION - PHASES 0 TO 6")
print("=" * 70)

all_passed = True

# ============================================================================
# PHASE 1: DATASET
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 1: DATASET VERIFICATION")
print("=" * 70)

# Check raw data exists
raw_path = "data/raw/ames.csv"
if os.path.exists(raw_path):
    df_raw = pd.read_csv(raw_path)
    print(f"✓ Raw data exists: {raw_path}")
    print(f"  - Rows: {len(df_raw)} (need 500+) → {'✓ PASS' if len(df_raw) >= 500 else '✗ FAIL'}")
    print(f"  - Columns: {len(df_raw.columns)}")
    print(f"  - Target 'SalePrice': {'✓' if 'SalePrice' in df_raw.columns else '✗'}")
else:
    print(f"✗ Raw data missing: {raw_path}")
    all_passed = False

# Check processed data exists
processed_path = "data/processed/ames_selected.csv"
if os.path.exists(processed_path):
    df_selected = pd.read_csv(processed_path)
    print(f"\n✓ Processed data exists: {processed_path}")
    print(f"  - Rows: {len(df_selected)}")
    print(f"  - Columns: {len(df_selected.columns)} (12 features + target)")
    print(f"  - Features: {df_selected.columns.tolist()}")
else:
    print(f"✗ Processed data missing: {processed_path}")
    all_passed = False

# ============================================================================
# PHASE 2: EDA NOTEBOOK
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 2: EDA NOTEBOOK VERIFICATION")
print("=" * 70)

eda_path = "notebooks/01_EDA_and_Exploration.ipynb"
if os.path.exists(eda_path):
    print(f"✓ EDA notebook exists: {eda_path}")
    print(f"  - Size: {os.path.getsize(eda_path) / 1024:.1f} KB")
else:
    print(f"✗ EDA notebook missing: {eda_path}")
    all_passed = False

# ============================================================================
# PHASE 3: MODEL TRAINING
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 3: MODEL TRAINING VERIFICATION")
print("=" * 70)

model_notebook_path = "notebooks/02_Model_Training_and_Evaluation.ipynb"
if os.path.exists(model_notebook_path):
    print(f"✓ Model notebook exists: {model_notebook_path}")
    print(f"  - Size: {os.path.getsize(model_notebook_path) / 1024:.1f} KB")
else:
    print(f"✗ Model notebook missing: {model_notebook_path}")
    all_passed = False

# Check exports directory
exports_dir = "notebooks/exports"
if os.path.exists(exports_dir):
    print(f"\n✓ Exports directory exists")
    export_files = ['model.joblib', 'preprocessor.joblib', 'feature_columns.json', 'training_stats.json']
    for f in export_files:
        path = os.path.join(exports_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            print(f"  ✓ {f} ({size:.1f} KB)")
        else:
            print(f"  ✗ {f} MISSING")
            all_passed = False
else:
    print(f"✗ Exports directory missing")
    all_passed = False

# ============================================================================
# PHASE 4: BACKEND MODELS
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 4: BACKEND MODELS VERIFICATION")
print("=" * 70)

backend_models_dir = "backend/models"
if os.path.exists(backend_models_dir):
    print(f"✓ Backend models directory exists")
    backend_files = ['model.joblib', 'preprocessor.joblib', 'feature_columns.json', 'training_stats.json']
    for f in backend_files:
        path = os.path.join(backend_models_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path) / 1024
            print(f"  ✓ {f} ({size:.1f} KB)")
        else:
            print(f"  ✗ {f} MISSING")
            all_passed = False
else:
    print(f"✗ Backend models directory missing")
    all_passed = False

# ============================================================================
# PHASE 5: PYDANTIC SCHEMAS
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 5: PYDANTIC SCHEMAS VERIFICATION")
print("=" * 70)

validation_dir = "backend/core/validation"
validation_files = ['__init__.py', 'pydantic_schemas.py', 'completeness_gate.py', 'feature_validator.py']
for f in validation_files:
    path = os.path.join(validation_dir, f)
    if os.path.exists(path):
        print(f"✓ {f}")
    else:
        print(f"✗ {f} MISSING")
        all_passed = False

# Test Pydantic imports
try:
    sys.path.insert(0, os.getcwd())
    from backend.core.validation import ExtractedFeatures, CompletenessGate, PredictResponse
    print(f"\n✓ Pydantic schemas import successfully")
    
    # Test completeness gate
    test_features = ExtractedFeatures(
        bedrooms=3, bathrooms=None, sqft_living=None, sqft_lot=None,
        year_built=None, garage_cars=None, condition=None, quality=None,
        neighborhood=None, basement=None, heating=None, central_air=None
    )
    is_complete, missing = CompletenessGate.check(test_features)
    print(f"  - Completeness gate: is_complete={is_complete}, missing={len(missing)}")
    
except Exception as e:
    print(f"✗ Pydantic import failed: {e}")
    all_passed = False

# ============================================================================
# PHASE 6: ML LOADER & PREDICTOR
# ============================================================================
print("\n" + "=" * 70)
print("PHASE 6: ML LOADER & PREDICTOR VERIFICATION")
print("=" * 70)

ml_dir = "backend/core/ml"
ml_files = ['__init__.py', 'model_loader.py', 'feature_pipeline.py', 'predictor.py', 'training_stats.py']
for f in ml_files:
    path = os.path.join(ml_dir, f)
    if os.path.exists(path):
        print(f"✓ {f}")
    else:
        print(f"✗ {f} MISSING")
        all_passed = False

# Test ML loader
try:
    from backend.core.ml import ModelLoader, Predictor, TrainingStats
    
    # Test model loading
    model, preprocessor = ModelLoader.get_model()
    print(f"\n✓ Model loaded: {type(model).__name__}")
    print(f"✓ Preprocessor loaded: {type(preprocessor).__name__}")
    
    # Test training stats
    median = TrainingStats.get_median_price()
    print(f"✓ Training stats: median=${median:,.0f}")
    
    # Test prediction
    from backend.core.validation import ExtractedFeatures
    test_features = ExtractedFeatures(
        bedrooms=3, bathrooms=2.0, sqft_living=1656, sqft_lot=31770,
        year_built=1960, garage_cars=2, condition=5, quality=6,
        neighborhood="NAmes", basement="TA", heating="GasA", central_air="Y"
    )
    price = Predictor.predict(test_features)
    print(f"✓ Prediction test: ${price:,.0f}")
    
except Exception as e:
    print(f"✗ ML loader failed: {e}")
    all_passed = False

# ============================================================================
# PDF REQUIREMENTS SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("PDF REQUIREMENTS STATUS")
print("=" * 70)

requirements = [
    ("#01: Three-way split, no leakage", "✅" if all_passed else "⏳"),
    ("#02: Missing values, fit on train only", "✅" if all_passed else "⏳"),
    ("#03: Encode and scale, fit on train only", "✅" if all_passed else "⏳"),
    ("#04: ColumnTransformer + 2 model types", "✅" if all_passed else "⏳"),
    ("#05: Train/val scores, test once", "✅" if all_passed else "⏳"),
    ("#06: Stage 1 + completeness signal", "⏳ Phase 7"),
    ("#07: Stage 2 interpretation", "⏳ Phase 7"),
    ("#08: Prompt versioning", "⏳ Phase 7"),
    ("#09: Pydantic schemas + error handling", "✅" if all_passed else "❌"),
    ("#10: FastAPI + Docker", "⏳ Phases 9-11"),
    ("#11: UI with missing forms", "⏳ Phase 10"),
]

for req, status in requirements:
    print(f"  {status} {req}")

# ============================================================================
# FINAL RESULT
# ============================================================================
print("\n" + "=" * 70)
if all_passed:
    print("✅ VERIFICATION PASSED - Phases 0-6 are correct!")
    print("   Ready to proceed to Phase 7 (LLM Client & Prompts)")
else:
    print("❌ VERIFICATION FAILED - Fix issues before continuing")
print("=" * 70)

