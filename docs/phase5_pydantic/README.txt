PHASE 5: PYDANTIC SCHEMAS - COMPLETE DOCUMENTATION
==================================================

DATE COMPLETED: April 15, 2026

================================================================================
WHAT IS PYDANTIC?
================================================================================

Pydantic is a data validation library for Python. It ensures that data entering
our system has the correct types and values.

PROBLEM IT SOLVES:
- LLMs return unstructured text (e.g., "bedrooms": "three" instead of 3)
- Users might enter invalid values (e.g., garage_cars: "huge")
- ML model needs clean, typed data to make predictions

HOW PYDANTIC HELPS:
- Converts "three" → 3 automatically
- Rejects "huge" for garage_cars (expects 0-5)
- Enforces value ranges (bedrooms cannot be 99)
- Reports exactly which fields are missing

================================================================================
WHY WE NEEDED THIS PHASE
================================================================================

LINK TO PREVIOUS PHASES:

Phase 2 (EDA):
  → Selected 12 features that matter for price prediction
  → We now need to validate that users provide these 12 features

Phase 3 (Model Training):
  → Trained Random Forest model expecting 12 specific features
  → Model will crash if it receives wrong data types

Phase 4 (Copy Artifacts):
  → Model artifacts in backend/models/ ready to be used
  → Now we need schemas to validate incoming user data

Phase 5 (THIS PHASE):
  → Creates the contract between user input and ML model
  → Ensures data is clean before it reaches the model

LINK TO NEXT PHASES:

Phase 6 (ML Loader):
  → Will load the model and use these schemas for validation

Phase 7 (LLM Client):
  → Stage 1 LLM will output data matching ExtractedFeatures schema

Phase 8 (Prediction Service):
  → Will use CompletenessGate to check if all features are present

Phase 9 (FastAPI):
  → Will use PredictRequest and PredictResponse for API endpoints

================================================================================
WHAT WE CREATED
================================================================================

FILE 1: backend/core/validation/pydantic_schemas.py
---------------------------------------------------
Contains 5 Pydantic schema classes:

| Schema | Purpose | Key Fields |
|--------|---------|------------|
| ExtractedFeatures | 12 features our model expects | bedrooms, bathrooms, sqft_living, etc. |
| Stage1Output | LLM extraction + completeness | extracted_features, missing_fields, completeness_score |
| Stage2Output | LLM interpretation | explanation, key_factors, comparison |
| PredictRequest | API request body | query, override_features |
| PredictResponse | API response body | success, status, predicted_price, explanation |
| ErrorResponse | Error handling | error_type, error_message, timestamp |

FILE 2: backend/core/validation/completeness_gate.py
----------------------------------------------------
Prevents ML prediction when features are missing (PDF #06).

Key functions:
- check(features) → (is_complete, missing_fields)
- create_stage1_output(features) → Stage1Output with completeness_score
- to_user_friendly_names(missing_fields) → readable names for UI

FILE 3: backend/core/validation/feature_validator.py
-----------------------------------------------------
Validates ranges and types of extracted features.

Example validations:
- bedrooms: 0-10
- bathrooms: 0-8 (0.5 increments)
- year_built: 1800-2025
- garage_cars: 0-5

FILE 4: backend/core/validation/__init__.py
--------------------------------------------
Makes all schemas importable as:
from backend.core.validation import ExtractedFeatures, CompletenessGate, etc.

FILE 5: scripts/test_pydantic.py
---------------------------------
Test script to verify all schemas work correctly.

================================================================================
THE COMPLETENESS GATE (CRITICAL FOR PDF #06)
================================================================================

PDF #06 says: "Do not silently fill gaps with defaults. If the user says
'3-bed in a good area' and your model needs 12 features, Stage 1 reports
what it found and what is still needed."

HOW OUR COMPLETENESS GATE WORKS:

User Query: "3-bedroom house in NAmes"
         │
         ▼
Stage 1 LLM extracts: {"bedrooms": 3, "neighborhood": "NAmes", ... others: null}
         │
         ▼
Completeness Gate checks: Are all 12 features present?
         │
         ├── NO → Return missing_fields = ["bathrooms", "sqft_living", ...]
         │         UI shows forms for missing fields
         │         ML prediction NEVER runs
         │
         └── YES → Proceed to ML prediction

EXAMPLE OUTPUT WHEN INCOMPLETE:
{
  "success": true,
  "status": "incomplete",
  "message": "Missing 10 features. Please provide them.",
  "missing_fields": ["bathrooms", "sqft_living", "sqft_lot", ...],
  "extracted_features": {"bedrooms": 3, "neighborhood": "NAmes"}
}

================================================================================
TYPE CONVERSION (WHAT PYDANTIC DOES AUTOMATICALLY)
================================================================================

LLM might return strings. Pydantic converts them:

| LLM Output | Pydantic Converts To |
|------------|---------------------|
| "bedrooms": "three" | ❌ Rejects (can't convert) |
| "bedrooms": "3" | ✅ 3 (int) |
| "bathrooms": "2.5" | ✅ 2.5 (float) |
| "central_air": "yes" | ✅ "Y" (after validator) |
| "garage_cars": "huge" | ❌ Rejects (must be 0-5) |

================================================================================
VALIDATION RULES
================================================================================

Each field has specific validation rules:

| Field | Type | Range | Special Rules |
|-------|------|-------|---------------|
| bedrooms | int | 0-10 | - |
| bathrooms | float | 0-8 | Must be in 0.5 increments |
| sqft_living | int | 300-10000 | - |
| sqft_lot | int | 500-200000 | - |
| year_built | int | 1800-2025 | - |
| garage_cars | int | 0-5 | - |
| condition | int | 1-10 | - |
| quality | int | 1-10 | - |
| neighborhood | str | max 50 chars | Free text |
| basement | str | - | Ex/Gd/TA/Fa/Po/None |
| heating | str | - | GasA, GasW, Wall, etc. |
| central_air | str | - | Y or N (case insensitive) |

================================================================================
TEST RESULTS
================================================================================

All 6 tests passed:

TEST 1: Valid features (all present)
  → is_complete=True, missing=[]
  → Feature Validator: is_valid=True

TEST 2: Missing features (only bedrooms)
  → is_complete=False
  → Detected 11 missing fields correctly
  → completeness_score=0.08

TEST 3: Type conversion (strings → numbers)
  → "3" → 3 (int)
  → "2.0" → 2.0 (float)

TEST 4: Invalid values
  → bedrooms=100 → ValidationError caught
  → bathrooms=3.2 → ValidationError caught
  → garage_cars=10 → ValidationError caught

TEST 5: PredictResponse factory methods
  → success_complete() creates complete response
  → success_incomplete() creates incomplete response
  → error() creates error response

TEST 6: PredictRequest
  → Validates query string (min 1 char, max 500)

================================================================================
HOW THIS LINKS TO PDF REQUIREMENTS
================================================================================

| PDF # | Requirement | How Phase 5 Satisfies It |
|-------|-------------|--------------------------|
| #06 | Stage 1 - completeness signal | CompletenessGate returns missing_fields list |
| #06 | Do not silently fill gaps | ML prediction only runs when is_complete=True |
| #09 | Two Pydantic schemas minimum | ExtractedFeatures + PredictResponse (plus 4 more) |
| #09 | Error handling | ErrorResponse schema with error_type |
| #09 | Catch validation failures | Pydantic ValidationError caught and formatted |

================================================================================
FILES CREATED IN THIS PHASE
================================================================================

backend/core/validation/
├── __init__.py                 # Module exports
├── pydantic_schemas.py         # 5 schema classes (270 lines)
├── completeness_gate.py        # Completeness checking logic (80 lines)
└── feature_validator.py        # Range validation (100 lines)

scripts/
└── test_pydantic.py            # Test script (200 lines)

docs/phase5_pydantic/
└── README.txt                  # This file

================================================================================
NEXT STEPS (PHASE 6)
================================================================================

Phase 6: ML Loader & Predictor
- Load model.joblib ONCE at startup (singleton pattern)
- Load preprocessor.joblib for transforming user input
- Create predict() function that uses these schemas
- Will use ExtractedFeatures as input, returns price prediction

The CompletenessGate from Phase 5 will call Phase 6's predictor ONLY when
is_complete=True (all 12 features present).

================================================================================
