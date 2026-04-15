"""
Prompt Versioning - PDF #08
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
import os

from .stage1_extractor import Stage1Extractor

logger = logging.getLogger(__name__)


class PromptVersioning:
    TEST_QUERIES = [
        "3-bedroom ranch with big garage in a good neighborhood",
        "Luxury 4-bed, 3.5-bath colonial in Northwood, 2500 sqft, built 2015",
        "Small 2-bed cottage near downtown, needs work",
        "Spacious family home with finished basement and central air"
    ]
    
    @classmethod
    def run_comparison(cls) -> Dict[str, Any]:
        results = {}
        
        for version in ['v1', 'v2', 'v3']:
            version_results = []
            for query in cls.TEST_QUERIES:
                output = Stage1Extractor.extract_with_version(query, version)
                version_results.append({
                    'query': query,
                    'completeness_score': output.completeness_score,
                    'missing_count': len(output.missing_fields),
                    'extracted_fields': {k: v for k, v in output.extracted_features.model_dump().items() if v is not None},
                    'is_complete': output.is_complete
                })
            
            avg_completeness = sum(r['completeness_score'] for r in version_results) / len(version_results)
            complete_count = sum(1 for r in version_results if r['is_complete'])
            
            results[version] = {
                'results': version_results,
                'metrics': {
                    'avg_completeness': round(avg_completeness, 3),
                    'complete_count': complete_count,
                    'total_queries': len(cls.TEST_QUERIES)
                }
            }
        
        winner = cls._determine_winner(results)
        
        return {
            'comparison': results,
            'winner': winner,
            'timestamp': datetime.now().isoformat()
        }
    
    @classmethod
    def _determine_winner(cls, results: Dict) -> str:
        best_version = None
        best_score = -1
        priority = {'v2': 0, 'v1': 1, 'v3': 2}

        for version, data in results.items():
            score = data['metrics']['avg_completeness']
            if score > best_score:
                best_score = score
                best_version = version
            elif score == best_score:
                current_priority = priority.get(version, 99)
                best_priority = priority.get(best_version, 99)
                if current_priority < best_priority:
                    best_version = version
        return best_version
    
    @classmethod
    def print_comparison(cls):
        print("\n" + "=" * 70)
        print("PROMPT VERSIONING COMPARISON (PDF #08)")
        print("=" * 70)
        
        results = cls.run_comparison()
        
        for version, data in results['comparison'].items():
            print(f"\n VERSION {version.upper()}:")
            print(f"   Avg Completeness: {data['metrics']['avg_completeness']:.1%}")
            print(f"   Complete: {data['metrics']['complete_count']}/{data['metrics']['total_queries']}")
        
        print("\n" + "=" * 70)
        print(f" WINNER: Version {results['winner'].upper()}")
        print("=" * 70)
        
        return results['winner']
    
    @classmethod
    def save_results(cls, filepath: str = "logs/prompt_versioning_results.json"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        results = cls.run_comparison()
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n Results saved to {filepath}")
        return results
