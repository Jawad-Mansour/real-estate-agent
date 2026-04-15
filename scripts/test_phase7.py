"""
Test script for Phase 7: LLM Client & Stages
Run with: python scripts/test_phase7.py
"""

import sys
import os

sys.path.insert(0, os.getcwd())

print("=" * 70)
print("TESTING PHASE 7: LLM CLIENT & STAGES")
print("=" * 70)

# Test 1: Check Groq API key
print("\n1. CHECKING GROQ API KEY")
print("-" * 40)

from dotenv import load_dotenv
load_dotenv()

groq_key = os.getenv('GROQ_API_KEY')
if groq_key:
    print(f"✓ GROQ_API_KEY found: {groq_key[:10]}...")
else:
    print("✗ GROQ_API_KEY not found in .env file")
    print("  Please create .env file with: GROQ_API_KEY=your_key_here")

# Test 2: Import modules
print("\n2. IMPORTING MODULES")
print("-" * 40)

try:
    from backend.core.llm import LLMClient, Stage1Extractor, Stage2Interpreter
    print("✓ LLMClient imported")
    print("✓ Stage1Extractor imported")
    print("✓ Stage2Extractor imported")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 3: LLM Client initialization
print("\n3. LLM CLIENT INITIALIZATION")
print("-" * 40)

client = LLMClient.get_instance()
print(f"✓ LLMClient instance created")
print(f"  Has Groq: {client.has_groq()}")
print(f"  Has OpenAI: {client.has_openai()}")

# Test 4: Stage 1 extraction (if API key exists)
print("\n4. STAGE 1 EXTRACTION TEST")
print("-" * 40)

if groq_key:
    extractor = Stage1Extractor(prompt_version='v2')
    test_query = "3-bedroom house with 2 bathrooms in NAmes"
    
    print(f"Query: '{test_query}'")
    print("Calling LLM (may take a few seconds)...")
    
    result = extractor.extract(test_query)
    
    print(f"\n✓ Extraction complete!")
    print(f"  Completeness score: {result.completeness_score:.1%}")
    print(f"  Missing fields: {result.missing_fields}")
    print(f"  Extracted features:")
    for field, value in result.extracted_features.model_dump().items():
        if value is not None:
            print(f"    - {field}: {value}")
else:
    print("⚠ Skipping - no API key found")

# Test 5: Prompt versioning
print("\n5. PROMPT VERSIONING (PDF #08)")
print("-" * 40)

if groq_key:
    from backend.core.llm.prompt_versioning import PromptVersioning
    
    print("Running comparison on 4 test queries...")
    print("(This may take 30-60 seconds)...")
    
    winner = PromptVersioning.print_comparison()
    print(f"\n✓ Winner: Version {winner}")
else:
    print("⚠ Skipping - no API key found")

print("\n" + "=" * 70)
print("✅ PHASE 7 TESTS COMPLETE")
print("=" * 70)
