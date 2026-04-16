# Prompt Versioning Results (PDF #08)

## Test Date: April 16, 2026

## Prompt Variants Tested:

| Version | Approach | Description |
|---------|----------|-------------|
| V1 | Strict JSON | Direct instructions with strict JSON output |
| V2 | Few-shot examples | Examples of correct extractions |
| V3 | Chain of thought | Step-by-step reasoning before output |

## Test Queries (4):

1. "3-bedroom ranch with big garage in a good neighborhood"
2. "Luxury 4-bed, 3.5-bath colonial in Northwood, 2500 sqft, built 2015"
3. "Small 2-bed cottage near downtown, needs work"
4. "Spacious family home with finished basement and central air"

## Results:

| Version | Avg Completeness | Complete Predictions |
|---------|------------------|---------------------|
| V1 | 31.2% | 0/4 |
| V2 | 37.5% | 0/4 |
| V3 | 6.0% | 0/4 |

## Winner: Version V2

**Reason:** Highest average completeness score (37.5%). The few-shot examples helped the LLM understand the expected output format better than strict instructions alone.

## Winner saved as default in Stage1Extractor.
