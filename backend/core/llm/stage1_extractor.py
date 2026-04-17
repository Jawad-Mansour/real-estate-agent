"""
Stage 1: Feature Extraction from Natural Language
IMPROVED VERSION - Better number extraction and pattern matching
"""

import ast
import json
import logging
import re
from typing import Dict, Any
from pathlib import Path

from .client import LLMClient
from ..validation.pydantic_schemas import ExtractedFeatures, Stage1Output
from ..validation.completeness_gate import CompletenessGate

logger = logging.getLogger(__name__)


class Stage1Extractor:
    """Extracts 12 real estate features from natural language."""
    
    PROMPT_VERSIONS = {
        'v1': 'stage1_v1.txt',
        'v2': 'stage1_v2.txt',
        'v3': 'stage1_v3.txt',
        'v4': 'stage1_v4.txt'
    }
    
    # Valid neighborhood names for mapping
    NEIGHBORHOOD_MAPPING = {
        'names': 'NAmes',
        'north ames': 'NAmes',
        'northames': 'NAmes',
        'stonebr': 'StoneBr',
        'stone brook': 'StoneBr',
        'stonebrook': 'StoneBr',
        'northridge': 'NoRidge',
        'north ridge': 'NoRidge',
        'noridge': 'NoRidge',
        'nridght': 'NridgHt',
        'northridge heights': 'NridgHt',
        'oldtown': 'OldTown',
        'old town': 'OldTown',
    }
    
    def __init__(self, prompt_version: str = 'v4'):
        self.prompt_version = prompt_version
        self.prompt_template = self._load_prompt_template(prompt_version)
    
    def _load_prompt_template(self, version: str) -> str:
        template_path = Path(__file__).parent / "prompt_templates" / self.PROMPT_VERSIONS[version]
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Extract features from this query. Query: QUERY_PLACEHOLDER"
    
    def extract(self, query: str) -> Stage1Output:
        prompt = self.prompt_template.replace('QUERY_PLACEHOLDER', query)
        
        response = LLMClient.chat_completion(
            prompt=prompt,
            temperature=0.1,
            max_tokens=1000
        )
        
        if not response:
            empty_features = ExtractedFeatures()
            return Stage1Output.from_extracted(empty_features)
        
        features_dict = self._parse_json_response(response)
        features_dict = self._enhance_extracted_features(features_dict, query)
        features_dict = self._clean_extracted_features(features_dict)
        
        try:
            features = ExtractedFeatures(**features_dict)
        except Exception as e:
            logger.error(f"Failed to create ExtractedFeatures: {e}")
            empty_features = ExtractedFeatures()
            return Stage1Output.from_extracted(empty_features)
        
        return CompletenessGate.create_stage1_output(features)
    
    def _clean_extracted_features(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        if not extracted:
            return extracted

        def normalize_string(value: Any) -> str:
            return str(value).strip().lower() if value is not None else ''

        # Fix central_air
        if 'central_air' in extracted:
            value = extracted['central_air']
            if isinstance(value, bool):
                extracted['central_air'] = 'Y' if value else 'N'
            else:
                normalized = normalize_string(value)
                if normalized in {'y', 'yes', 'true', 'ye', 'yep'}:
                    extracted['central_air'] = 'Y'
                elif normalized in {'n', 'no', 'false', 'nah'}:
                    extracted['central_air'] = 'N'

        # Fix basement
        if 'basement' in extracted:
            value = extracted['basement']
            if isinstance(value, bool):
                extracted['basement'] = 'Gd' if value else 'None'
            else:
                normalized = normalize_string(value)
                if normalized in {'ex', 'excellent'}:
                    extracted['basement'] = 'Ex'
                elif normalized in {'gd', 'good', 'finished'}:
                    extracted['basement'] = 'Gd'
                elif normalized in {'ta', 'typical', 'average', 'unfinished'}:
                    extracted['basement'] = 'TA'
                elif normalized in {'fa', 'fair'}:
                    extracted['basement'] = 'Fa'
                elif normalized in {'po', 'poor'}:
                    extracted['basement'] = 'Po'
                elif normalized in {'none', 'no', 'no basement', 'none', ''}:
                    extracted['basement'] = 'None'

        # Fix neighborhood names
        if 'neighborhood' in extracted and extracted['neighborhood']:
            normalized = normalize_string(extracted['neighborhood'])
            for key, value in self.NEIGHBORHOOD_MAPPING.items():
                if key in normalized or normalized in key:
                    extracted['neighborhood'] = value
                    break
            # Capitalize properly
            if extracted['neighborhood']:
                valid_neighborhoods = ['NAmes', 'StoneBr', 'NoRidge', 'NridgHt', 'OldTown', 
                                       'Sawyer', 'Gilbert', 'Edwards', 'Northpark', 'Blueste',
                                       'MeadowV', 'CollgCr', 'Timber', 'Veenker', 'Crawford',
                                       'Somerset', 'Mitchel', 'ClearCr', 'NWAmes', 'SWAyn']
                if extracted['neighborhood'] not in valid_neighborhoods:
                    # Try to find closest match
                    for valid in valid_neighborhoods:
                        if valid.lower() in normalized or normalized in valid.lower():
                            extracted['neighborhood'] = valid
                            break

        quality_map = {
            'needs work': 3,
            'excellent': 9,
            'good': 7,
            'average': 5,
            'fair': 4,
            'poor': 2,
            'good neighborhood': 7,
            'luxury': 9,
            'fixer upper': 3,
            'move in ready': 8,
            'like new': 8,
        }

        for key in ['quality', 'condition']:
            if key in extracted:
                value = extracted[key]
                if isinstance(value, str):
                    normalized = normalize_string(value)
                    # Check if it's a number string
                    if normalized.isdigit():
                        extracted[key] = int(normalized)
                    # Check mapping
                    elif normalized in quality_map:
                        extracted[key] = quality_map[normalized]
                    elif 'good neighborhood' in normalized:
                        extracted[key] = 7
                    elif 'needs work' in normalized:
                        extracted[key] = 3
                    elif 'luxury' in normalized and key == 'quality':
                        extracted[key] = 9
                elif isinstance(value, float):
                    extracted[key] = int(value)
                elif isinstance(value, int):
                    extracted[key] = value
                
                # Clamp values
                if extracted[key] is not None:
                    extracted[key] = max(1, min(10, extracted[key]))

        return extracted

    def _enhance_extracted_features(self, extracted: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        ONLY fills missing features - NEVER overrides existing LLM-extracted values.
        IMPROVED with better pattern matching.
        """
        if not extracted:
            extracted = {}
        
        # Save original values - we will NEVER override these
        original_values = extracted.copy()
        query_lower = query.lower()
        
        # Condition and quality mapping (only if missing)
        condition_quality_mappings = {
            'needs work': (3, 3),
            'fixer upper': (3, 3),
            'needs repairs': (3, 3),
            'run down': (2, 2),
            'poor condition': (2, 2),
            'average': (5, 5),
            'typical': (5, 5),
            'good condition': (7, 6),
            'well maintained': (7, 6),
            'nice': (6, 6),
            'excellent condition': (9, 8),
            'like new': (9, 8),
            'perfect': (9, 8),
            'move in ready': (8, 8),
            'luxury': (9, 9),
            'high-end': (9, 9),
            'premium': (9, 9),
            'upscale': (9, 9),
            'great neighborhood': (7, 7),
            'nice area': (7, 7),
            'desirable location': (7, 7),
            'good neighborhood': (7, 7),
        }
        
        for phrase, (cond, qual) in condition_quality_mappings.items():
            if phrase in query_lower:
                if extracted.get('condition') is None and original_values.get('condition') is None:
                    extracted['condition'] = cond
                if extracted.get('quality') is None and original_values.get('quality') is None:
                    extracted['quality'] = qual
                break
        
        # Bedrooms (only if missing) - IMPROVED patterns
        if extracted.get('bedrooms') is None and original_values.get('bedrooms') is None:
            bed_patterns = [
                r'(\d+)\s*bed(?:room)?s?',
                r'(\d+)\s*bed',
                r'(\d+)\s*br',
                r'(\d+)\s*-?\s*bed',
                r'(\d+)\s*bedroom',
            ]
            for pattern in bed_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        val = int(match.group(1))
                        if 1 <= val <= 10:
                            extracted['bedrooms'] = val
                            break
                    except ValueError:
                        pass
        
        # Bathrooms (only if missing) - IMPROVED patterns
        if extracted.get('bathrooms') is None and original_values.get('bathrooms') is None:
            bath_patterns = [
                r'(\d+(?:\.\d+)?)\s*bath(?:room)?s?',
                r'(\d+(?:\.\d+)?)\s*bath',
                r'(\d+(?:\.\d+)?)\s*ba',
                r'(\d+(?:\.\d+)?)\s*-?\s*bath',
            ]
            for pattern in bath_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        val = float(match.group(1))
                        if 0.5 <= val <= 8:
                            extracted['bathrooms'] = val
                            break
                    except ValueError:
                        pass
        
        # Square footage (only if missing) - IMPROVED patterns
        if extracted.get('sqft_living') is None and original_values.get('sqft_living') is None:
            sqft_patterns = [
                r'(\d+(?:,\d+)?)\s*sq(?:uare)?\s*ft',
                r'(\d+(?:,\d+)?)\s*sqft',
                r'(\d+(?:,\d+)?)\s*square\s*feet',
                r'(\d+(?:,\d+)?)\s*square\s*foot',
                r'about\s*(\d+)\s*sq',
                r'around\s*(\d+)\s*sq',
                r'~(\d+)\s*sq',
            ]
            for pattern in sqft_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        val = int(match.group(1).replace(',', ''))
                        if 300 <= val <= 10000:
                            extracted['sqft_living'] = val
                            break
                    except ValueError:
                        pass
        
        # Lot area (only if missing)
        if extracted.get('sqft_lot') is None and original_values.get('sqft_lot') is None:
            lot_patterns = [
                r'(\d+(?:,\d+)?)\s*lot',
                r'(\d+(?:,\d+)?)\s*lot\s*area',
                r'(\d+(?:,\d+)?)\s*sqft\s*lot',
            ]
            for pattern in lot_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        val = int(match.group(1).replace(',', ''))
                        if 500 <= val <= 200000:
                            extracted['sqft_lot'] = val
                            break
                    except ValueError:
                        pass
        
        # Garage (only if missing) - IMPROVED
        if extracted.get('garage_cars') is None and original_values.get('garage_cars') is None:
            if 'no garage' in query_lower or 'no car garage' in query_lower or 'without garage' in query_lower:
                extracted['garage_cars'] = 0
            else:
                garage_patterns = [
                    r'(\d+)\s*car\s*garage',
                    r'(\d+)\s*car',
                    r'garage\s*for\s*(\d+)',
                    r'(\d+)\s*-?\s*car',
                ]
                for pattern in garage_patterns:
                    match = re.search(pattern, query_lower)
                    if match:
                        try:
                            val = int(match.group(1))
                            if 0 <= val <= 5:
                                extracted['garage_cars'] = val
                                break
                        except ValueError:
                            pass
        
        # Basement (only if missing)
        if extracted.get('basement') is None and original_values.get('basement') is None:
            if 'no basement' in query_lower or 'without basement' in query_lower:
                extracted['basement'] = 'None'
            elif 'finished basement' in query_lower:
                extracted['basement'] = 'Gd'
            elif 'unfinished basement' in query_lower or 'basement' in query_lower:
                extracted['basement'] = 'TA'
        
        # Heating (only if missing) - IMPROVED
        if extracted.get('heating') is None and original_values.get('heating') is None:
            if 'gas heat' in query_lower or 'gas furnace' in query_lower or 'forced air' in query_lower:
                extracted['heating'] = 'GasA'
            elif 'electric heat' in query_lower or 'electric furnace' in query_lower:
                extracted['heating'] = 'Wall'
            elif 'heat pump' in query_lower:
                extracted['heating'] = 'GasA'
        
        # Central air (only if missing) - IMPROVED
        if extracted.get('central_air') is None and original_values.get('central_air') is None:
            if 'central air' in query_lower or 'ac' in query_lower or 'a/c' in query_lower or 'air conditioning' in query_lower:
                # Check for negation
                if 'no central air' in query_lower or 'no ac' in query_lower or 'without ac' in query_lower:
                    extracted['central_air'] = 'N'
                else:
                    extracted['central_air'] = 'Y'
            elif 'no central air' in query_lower or 'no ac' in query_lower:
                extracted['central_air'] = 'N'
        
        # Year built (only if missing) - IMPROVED
        if extracted.get('year_built') is None and original_values.get('year_built') is None:
            year_patterns = [
                r'built\s*(?:in\s*)?(\d{4})',
                r'(\d{4})\s*(?:built|home|house|construction)',
                r'year\s*(\d{4})',
                r'constructed\s*(\d{4})',
            ]
            for pattern in year_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    try:
                        year = int(match.group(1))
                        if 1800 <= year <= 2025:
                            extracted['year_built'] = year
                            break
                    except ValueError:
                        pass
        
        # Neighborhood (only if missing) - IMPROVED
        if extracted.get('neighborhood') is None and original_values.get('neighborhood') is None:
            # Check for neighborhood names in query
            for key, value in self.NEIGHBORHOOD_MAPPING.items():
                if key in query_lower:
                    extracted['neighborhood'] = value
                    break
            
            # Also check for capitalized words that might be neighborhoods
            if not extracted.get('neighborhood'):
                neighborhood_match = re.search(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)?)\b', query)
                if neighborhood_match:
                    candidate = neighborhood_match.group(1)
                    if len(candidate) > 2:
                        extracted['neighborhood'] = candidate
        
        # Restore any original values that might have been accidentally changed
        for key, original_value in original_values.items():
            if original_value is not None:
                extracted[key] = original_value
        
        return extracted

    def _regex_fallback_extraction(self, response: str) -> Dict[str, Any]:
        """Last resort fallback when JSON parsing fails."""
        logger.warning("Using regex fallback extraction")
        extracted = {}
        response_lower = response.lower()
        
        # Extract numbers
        bed_match = re.search(r'(\d+)\s*bed', response_lower)
        if bed_match:
            extracted['bedrooms'] = int(bed_match.group(1))
        
        bath_match = re.search(r'(\d+(?:\.\d+)?)\s*bath', response_lower)
        if bath_match:
            extracted['bathrooms'] = float(bath_match.group(1))
        
        sqft_match = re.search(r'(\d+)\s*sq', response_lower)
        if sqft_match:
            extracted['sqft_living'] = int(sqft_match.group(1))
        
        if 'no garage' in response_lower:
            extracted['garage_cars'] = 0
        else:
            garage_match = re.search(r'(\d+)\s*car', response_lower)
            if garage_match:
                extracted['garage_cars'] = int(garage_match.group(1))
        
        year_match = re.search(r'(\d{4})', response_lower)
        if year_match:
            year = int(year_match.group(1))
            if 1800 <= year <= 2025:
                extracted['year_built'] = year
        
        if 'needs work' in response_lower or 'fixer' in response_lower:
            extracted['condition'] = 3
            extracted['quality'] = 3
        elif 'luxury' in response_lower or 'high-end' in response_lower:
            extracted['quality'] = 9
        
        if 'no basement' in response_lower:
            extracted['basement'] = 'None'
        elif 'finished basement' in response_lower:
            extracted['basement'] = 'Gd'
        
        if 'gas' in response_lower:
            extracted['heating'] = 'GasA'
        
        if 'central air' in response_lower or 'ac' in response_lower:
            extracted['central_air'] = 'Y'
        elif 'no central air' in response_lower:
            extracted['central_air'] = 'N'
        
        return extracted

    def _extract_json_text(self, response: str) -> str:
        if not response:
            return ''
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1)
        first_brace = response.find('{')
        if first_brace == -1:
            return response
        depth = 0
        end_index = None
        for idx, char in enumerate(response[first_brace:], first_brace):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end_index = idx
                    break
        if end_index is not None:
            return response[first_brace:end_index + 1]
        return response[first_brace:]

    def _normalize_json_text(self, response: str) -> str:
        normalized = response.strip()
        normalized = re.sub(r"(?<!\\)'", '"', normalized)
        normalized = re.sub(r'([\{\s,])(\w+)(\s*):', r'\1"\2"\3:', normalized)
        normalized = re.sub(r',\s*(?=[}\]])', '', normalized)
        normalized = re.sub(r'\bTrue\b', 'true', normalized)
        normalized = re.sub(r'\bFalse\b', 'false', normalized)
        normalized = re.sub(r'\bNone\b', 'null', normalized)
        return normalized

    def _try_json_loads(self, text: str) -> Dict[str, Any] | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _try_json_loads_strict_false(self, text: str) -> Dict[str, Any] | None:
        try:
            return json.loads(text, strict=False)
        except Exception:
            return None

    def _try_ast_literal_eval(self, text: str) -> Dict[str, Any] | None:
        try:
            python_text = text.replace('null', 'None').replace('true', 'True').replace('false', 'False')
            return ast.literal_eval(python_text)
        except Exception:
            return None

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        extracted_text = self._extract_json_text(response)
        normalized_text = self._normalize_json_text(extracted_text)
        for parser in (self._try_json_loads, self._try_json_loads_strict_false, self._try_ast_literal_eval):
            parsed = parser(normalized_text)
            if isinstance(parsed, dict):
                return parsed
        logger.error("Unable to parse JSON response from LLM")
        return self._regex_fallback_extraction(response)
    
    @classmethod
    def extract_with_version(cls, query: str, version: str) -> Stage1Output:
        extractor = cls(prompt_version=version)
        return extractor.extract(query)