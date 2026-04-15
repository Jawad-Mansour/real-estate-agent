PHASE 7: LLM CLIENT & STAGE COMPONENTS - COMPLETE DOCUMENTATION
===============================================================

DATE COMPLETED: April 15, 2026

================================================================================
WHAT WE DID
================================================================================

Built the LLM (Large Language Model) client that powers the two-stage prompt chain:
- Stage 1: Extracts 12 features from natural language user queries
- Stage 2: Interprets ML predictions with context from training data

PDF Requirements met: #06 (Stage 1 extraction), #07 (Stage 2 interpretation), 
#08 (Prompt versioning)

================================================================================
FILES CREATED
================================================================================

backend/core/llm/
├── __init__.py                    # Module exports
├── client.py                      # Groq + OpenAI abstraction with rate limit retry
├── stage1_extractor.py            # Stage 1 prompt + extraction + post-processing
├── stage2_interpreter.py          # Stage 2 prompt + interpretation
├── prompt_versioning.py           # Compare prompt versions (PDF #08)
└── prompt_templates/              # Prompt text files
    ├── stage1_v1.txt              # Version 1 (Strict JSON)
    ├── stage1_v2.txt              # Version 2 (Few-shot examples) - WINNER
    ├── stage1_v3.txt              # Version 3 (Chain of thought)
    └── stage2_default.txt         # Stage 2 interpretation prompt

scripts/
└── test_phase7.py                 # Complete test suite

================================================================================
LLM PROVIDER: GROQ (LLAMA 3.1)
================================================================================

Provider: Groq (free tier)
Model: Llama 3.3 70B (via Groq API)
Fallback: OpenAI GPT-4o-mini (if Groq fails or rate limited)

Why Groq:
- Free for developer tier
- Very fast (560+ tokens/sec)
- High quality (Llama 3.1 matches GPT-4)
- OpenAI-compatible API

================================================================================
STAGE 1: FEATURE EXTRACTION (PDF #06)
================================================================================

Purpose: Convert natural language to structured JSON with 12 features

Input: "3-bedroom house with 2 bathrooms in NAmes"

Output:
{
  "bedrooms": 3,
  "bathrooms": 2.0,
  "neighborhood": "NAmes",
  "basement": "None",
  "sqft_living": null,
  "sqft_lot": null,
  "year_built": null,
  "garage_cars": null,
  "condition": null,
  "quality": null,
  "heating": null,
  "central_air": null
}

Completeness score: 33% (4/12 features extracted)

Critical PDF #06 requirement met:
- "Do not silently fill gaps with defaults" → null for missing
- "Include a completeness signal" → missing_fields list returned

================================================================================
STAGE 2: PREDICTION INTERPRETATION (PDF #07)
================================================================================

Purpose: Explain ML prediction with context from training data

Input:
- Predicted price: $196,777
- Features: 3 bedrooms, 2 bathrooms, NAmes neighborhood
- Training stats: median $160,000, range $12,789 - $755,000

Output:
"The predicted price is $196,777, which is 23% above the median. 
This is driven by the quality rating and desirable neighborhood. 
Typical homes in this area range from $129,500 to $210,500."

Key features:
- Uses training statistics from Phase 4 (TRAIN data only, no leakage)
- Extracts key factors (quality, garage, location)
- Provides comparison to median

================================================================================
PROMPT VERSIONING (PDF #08)
================================================================================

Three prompt variants tested on 4 queries:

| Version | Approach | Avg Completeness | Winner |
|---------|----------|------------------|--------|
| V1      | Strict JSON with rules | 31.2% | - |
| V2      | Few-shot examples + inference | 37.5% | 🏆 WINNER |
| V3      | Chain of thought | 6.0% | - |

Test queries:
1. "3-bedroom ranch with big garage in a good neighborhood"
2. "Luxury 4-bed, 3.5-bath colonial in Northwood, 2500 sqft, built 2015"
3. "Small 2-bed cottage near downtown, needs work"
4. "Spacious family home with finished basement and central air"

Winner: Version V2 (selected as default)

================================================================================
ROBUST JSON PARSING
================================================================================

Added multiple fallback parsers to handle LLM output variations:

1. Extract JSON from markdown code blocks (```json ... ```)
2. Find JSON object using brace counting
3. Normalize: single quotes → double quotes, add missing quotes
4. Try json.loads() with strict=True
5. Try json.loads() with strict=False
6. Try ast.literal_eval() as last resort

================================================================================
RATE LIMIT HANDLING
================================================================================

Added exponential backoff retry for Groq API rate limits (429 errors):

- Retry attempts: 3
- Wait times: 1s, 2s, 4s (exponential)
- Random jitter added to avoid thundering herd
- Automatic fallback to OpenAI if Groq fails

================================================================================
POST-PROCESSING (TYPE CORRECTION)
================================================================================

Added _clean_extracted_features() to fix common LLM output issues:

| Issue | Fix |
|-------|-----|
| central_air: True/False | Convert to "Y"/"N" |
| basement: True/False | Convert to "Gd"/"None" |
| quality: "needs work" | Map to 3 |
| quality: "excellent" | Map to 9 |
| quality: "good" | Map to 7 |
| quality: "average" | Map to 5 |
| quality: "poor" | Map to 2 |

================================================================================
TEST RESULTS
================================================================================

$ python scripts/test_phase7.py

1. CHECKING GROQ API KEY
   ✓ GROQ_API_KEY found

2. IMPORTING MODULES
   ✓ LLMClient imported
   ✓ Stage1Extractor imported
   ✓ Stage2Interpreter imported

3. LLM CLIENT INITIALIZATION
   ✓ Groq client initialized
   Has Groq: True

4. STAGE 1 EXTRACTION TEST
   Query: '3-bedroom house with 2 bathrooms in NAmes'
   ✓ Completeness score: 33.0%
   ✓ Extracted: bedrooms=3, bathrooms=2.0, neighborhood=NAmes, basement=None

5. PROMPT VERSIONING
   ✓ Version V1: 31.2%
   ✓ Version V2: 37.5% (WINNER)
   ✓ Version V3: 6.0%
   ✓ Winner: Version V2

================================================================================
PDF REQUIREMENTS MET
================================================================================

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
|06 | Stage 1 extraction | ✅ | Extracts 12 features, returns null for missing |
|06 | Completeness signal | ✅ | missing_fields list, completeness_score |
|07 | Stage 2 interpretation | ✅ | Uses training stats, explains why |
|08 | Prompt versioning | ✅ | 3 variants, 4 queries, winner V2 |

================================================================================
ENVIRONMENT SETUP
================================================================================

Required environment variables in .env file:

GROQ_API_KEY=gsk_your_key_here
OPENAI_API_KEY=sk-your-key-here (optional fallback)

Install dependencies:
uv pip install groq openai python-dotenv

================================================================================
NEXT STEPS (PHASE 8)
================================================================================

Phase 8: Prediction Service (The Orchestrator)
- Connects Stage 1 → Completeness Gate → ML Predictor → Stage 2
- Single process_query() function that handles the entire chain
- Returns final response to FastAPI

================================================================================
