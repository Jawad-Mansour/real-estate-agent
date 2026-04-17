"""
Stage 2: Prediction Interpretation
"""

import logging
from pathlib import Path
from typing import List

from .client import LLMClient
from ..validation.pydantic_schemas import ExtractedFeatures, Stage2Output
from ..ml.training_stats import TrainingStats

logger = logging.getLogger(__name__)


class Stage2Interpreter:
    """Interprets ML prediction with context from training data."""
    
    def __init__(self):
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        template_path = Path(__file__).parent / "prompt_templates" / "stage2_default.txt"
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Explain price PRICE_PLACEHOLDER with features FEATURES_PLACEHOLDER"
    
    def interpret(self, features: ExtractedFeatures, predicted_price: float) -> Stage2Output:
        stats = TrainingStats.get_stats()
        
        features_str = self._format_features(features)
        
        # Replace placeholders
        prompt = self.prompt_template
        prompt = prompt.replace('FEATURES_PLACEHOLDER', features_str)
        prompt = prompt.replace('PRICE_PLACEHOLDER', f"${predicted_price:,.0f}")
        prompt = prompt.replace('MEDIAN_PLACEHOLDER', f"${stats.get('median_price', 160000):,.0f}")
        prompt = prompt.replace('MIN_PLACEHOLDER', f"${stats.get('min_price', 12789):,.0f}")
        prompt = prompt.replace('MAX_PLACEHOLDER', f"${stats.get('max_price', 755000):,.0f}")
        prompt = prompt.replace('Q1_PLACEHOLDER', f"${stats.get('q1_price', 129500):,.0f}")
        prompt = prompt.replace('Q3_PLACEHOLDER', f"${stats.get('q3_price', 210500):,.0f}")
        
        response = LLMClient.chat_completion(
            prompt=prompt,
            temperature=0.1,
            max_tokens=500
        )
        
        if not response:
            comparison = TrainingStats.get_comparison(predicted_price)
            key_factors = self._extract_key_factors(features)
            explanation = f"The predicted price is ${predicted_price:,.0f}, which is {comparison}."
            if key_factors and key_factors != ["Standard home features"]:
                explanation += f" Key factors include: {', '.join(key_factors[:2])}."
            return Stage2Output(
                explanation=explanation,
                key_factors=key_factors,
                comparison=comparison
            )
        
        key_factors = self._extract_key_factors(features)
        comparison = TrainingStats.get_comparison(predicted_price)
        
        return Stage2Output(
            explanation=response.strip(),
            key_factors=key_factors,
            comparison=comparison
        )
    
    def _format_features(self, features: ExtractedFeatures) -> str:
        lines = []
        for field in ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'year_built', 
                      'garage_cars', 'condition', 'quality', 'neighborhood', 'basement', 
                      'heating', 'central_air']:
            value = getattr(features, field, None)
            if value is not None:
                lines.append(f"  - {field}: {value}")
        return "\n".join(lines) if lines else "  - No specific features provided"
    
    def _extract_key_factors(self, features: ExtractedFeatures) -> List[str]:
        key_factors = []
        
        if features.quality and features.quality >= 7:
            key_factors.append(f"High quality rating ({features.quality}/10)")
        if features.garage_cars and features.garage_cars >= 2:
            key_factors.append(f"{features.garage_cars}-car garage")
        if features.sqft_living and features.sqft_living >= 2500:
            key_factors.append(f"Large living space ({features.sqft_living} sq ft)")
        if features.neighborhood in ['StoneBr', 'NoRidge', 'NridgHt']:
            key_factors.append(f"Premium neighborhood ({features.neighborhood})")
        if features.central_air == 'Y':
            key_factors.append("Central air conditioning")
        if features.basement in ['Ex', 'Gd']:
            key_factors.append("Finished basement")
        
        return key_factors[:3] if key_factors else ["Standard home features"]
