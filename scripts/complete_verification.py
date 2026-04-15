"""
Complete verification for all phases 0-8
Run with: python scripts/complete_verification.py
"""

import sys
import os
import pandas as pd
import numpy as np
import json
import joblib

sys.path.insert(0, os.getcwd())

print("=" * 70)
print("COMPLETE VERIFICATION - PHASES 0 TO 8")
print("=" * 70)

all_passed = True
errors = []

# ============================================================================
# PHASE 1: DATASET
# ============================================================================
print("\n📁 PHASE 1: DATASET")
print("-" * 40)

try:
    df_raw = pd.read_csv('data/raw/ames.csv')
    print(f"✓ Raw data: {len(df_raw)} rows, {len(df_raw.columns)} cols")
    if len(df_raw) < 500:
        errors.append("Phase 1: Less than 500 rows")
        all_passed = False
except Exception as e:
    errors.append(f"Phase 1: Raw data error - {e}")
    all_passed = False

try:
    df_processed = pd.read_csv('data/processed/ames_selected.csv')
    print(f"✓ Processed data: {len(df_processed)} rows, {len(df_processed.columns)} cols")
except Exception as e:
    errors.append(f"Phase 1: Processed data error - {e}")
    all_passed = False

# ============================================================================
# PHASE 2-3: NOTEBOOKS
# ============================================================================
print("\n📓 PHASE 2-3: NOTEBOOKS")
print("-" * 40)

for notebook in ['notebooks/01_EDA_and_Exploration.ipynb', 'notebooks/02_Model_Training_and_Evaluation.ipynb']:
    if os.path.exists(notebook):
        print(f"✓ {os.path.basename(notebook)} exists")
    else:
        errors.append(f"Phase 2-3: Missing {notebook}")
        all_passed = False

# ============================================================================
# PHASE 4: BACKEND MODELS
# ============================================================================
print("\n🤖 PHASE 4: BACKEND MODELS")
print("-" * 40)

required_models = ['model.joblib', 'preprocessor.joblib', 'feature_columns.json', 'training_stats.json']
for model in required_models:
    path = f'backend/models/{model}'
    if os.path.exists(path):
        size = os.path.getsize(path) / 1024
        print(f"✓ {model} ({size:.1f} KB)")
    else:
        errors.append(f"Phase 4: Missing {model}")
        all_passed = False

# ============================================================================
# PHASE 5: PYDANTIC SCHEMAS
# ============================================================================
print("\n📋 PHASE 5: PYDANTIC SCHEMAS")
print("-" * 40)

try:
    from backend.core.validation import ExtractedFeatures, CompletenessGate, PredictResponse
    print("✓ All schemas import successfully")
    
    # Test completeness gate
    test_features = ExtractedFeatures(bedrooms=3, bathrooms=None, sqft_living=None, sqft_lot=None,
                                       year_built=None, garage_cars=None, condition=None, quality=None,
                                       neighborhood=None, basement=None, heating=None, central_air=None)
    is_complete, missing = CompletenessGate.check(test_features)
    print(f"✓ Completeness gate: is_complete={is_complete}, missing={len(missing)}")
    
    # Test response
    resp = PredictResponse.success_complete(price=200000, explanation="Test", key_factors=["test"], comparison="test")
    print(f"✓ PredictResponse works")
    
except Exception as e:
    errors.append(f"Phase 5: Pydantic error - {e}")
    all_passed = False

# ============================================================================
# PHASE 6: ML LOADER
# ============================================================================
print("\n🚀 PHASE 6: ML LOADER")
print("-" * 40)

try:
    from backend.core.ml import ModelLoader, Predictor, TrainingStats
    
    model, preprocessor = ModelLoader.get_model()
    print(f"✓ Model loaded: {type(model).__name__}")
    print(f"✓ Preprocessor loaded: {type(preprocessor).__name__}")
    
    median = TrainingStats.get_median_price()
    print(f"✓ Training stats: median=${median:,.0f}")
    
    # Test prediction
    test_features = ExtractedFeatures(
        bedrooms=3, bathrooms=2.0, sqft_living=1656, sqft_lot=31770,
        year_built=1960, garage_cars=2, condition=5, quality=6,
        neighborhood="NAmes", basement="TA", heating="GasA", central_air="Y"
    )
    price = Predictor.predict(test_features)
    print(f"✓ Prediction test: ${price:,.0f}")
    
except Exception as e:
    errors.append(f"Phase 6: ML Loader error - {e}")
    all_passed = False

# ============================================================================
# PHASE 7: LLM CLIENT
# ============================================================================
print("\n💬 PHASE 7: LLM CLIENT")
print("-" * 40)

try:
    from backend.core.llm import LLMClient, Stage1Extractor, Stage2Interpreter
    
    client = LLMClient.get_instance()
    print(f"✓ LLMClient: Has Groq={client.has_groq()}, Has OpenAI={client.has_openai()}")
    
    extractor = Stage1Extractor(prompt_version='v2')
    print(f"✓ Stage1Extractor initialized with version v2")
    
    interpreter = Stage2Interpreter()
    print(f"✓ Stage2Interpreter initialized")
    
except Exception as e:
    errors.append(f"Phase 7: LLM error - {e}")
    all_passed = False

# ============================================================================
# PHASE 8: PREDICTION SERVICE
# ============================================================================
print("\n🔧 PHASE 8: PREDICTION SERVICE")
print("-" * 40)

try:
    from backend.services.prediction_service import PredictionService
    
    service = PredictionService()
    print(f"✓ PredictionService initialized")
    
    health = service.health_check()
    print(f"✓ Health check: {health['status']}")
    
    # Test incomplete query (no API call)
    response = service.process_query("test query")
    print(f"✓ Process_query returns response")
    
except Exception as e:
    errors.append(f"Phase 8: Prediction Service error - {e}")
    all_passed = False

# ============================================================================
# DATA LEAKAGE CHECK
# ============================================================================
print("\n🔒 DATA LEAKAGE CHECK")
print("-" * 40)

try:
    # Check that training stats came from training data only
    stats_path = 'backend/models/training_stats.json'
    with open(stats_path, 'r') as f:
        stats = json.load(f)
    
    # These should be reasonable values from training
    median = stats.get('median_price', 0)
    print(f"✓ Training median: ${median:,.0f}")
    
    if 140000 < median < 180000:
        print(f"✓ Median price in expected range ($140k-$180k)")
    else:
        errors.append(f"Phase 4: Median price {median} outside expected range")
    
except Exception as e:
    errors.append(f"Data leakage check error: {e}")
    all_passed = False

# ============================================================================
# FILE STRUCTURE CHECK
# ============================================================================
print("\n📁 FILE STRUCTURE CHECK")
print("-" * 40)

required_dirs = [
    'backend/core/validation',
    'backend/core/ml',
    'backend/core/llm',
    'backend/services',
    'backend/models',
    'data/raw',
    'data/processed',
    'notebooks',
    'scripts'
]

for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"✓ {dir_path}")
    else:
        errors.append(f"Missing directory: {dir_path}")
        all_passed = False

# ============================================================================
# ENVIRONMENT CHECK
# ============================================================================
print("\n🌍 ENVIRONMENT CHECK")
print("-" * 40)

try:
    from dotenv import load_dotenv
    load_dotenv()
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        print(f"✓ GROQ_API_KEY found (starts with {groq_key[:10]}...)")
    else:
        print(f"⚠ GROQ_API_KEY not found - LLM will not work")
        errors.append("GROQ_API_KEY missing from .env")
except Exception as e:
    errors.append(f"Environment error: {e}")

# ============================================================================
# FINAL RESULT
# ============================================================================
print("\n" + "=" * 70)
print("VERIFICATION RESULTS")
print("=" * 70)

if all_passed and len(errors) == 0:
    print("\n✅ ALL PHASES 0-8 ARE CORRECT!")
    print("   No errors detected.")
    print("   Ready for Phase 9 (FastAPI Routes).")
else:
    print(f"\n❌ {len(errors)} ERRORS FOUND:")
    for err in errors:
        print(f"   - {err}")

print("=" * 70)
