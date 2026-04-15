"""
Stage 1: Feature Extraction from Natural Language
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
        'v3': 'stage1_v3.txt'
    }
    
    def __init__(self, prompt_version: str = 'v2'):
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
        # Replace placeholder with actual query
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

        if 'central_air' in extracted:
            value = extracted['central_air']
            if isinstance(value, bool):
                extracted['central_air'] = 'Y' if value else 'N'
            else:
                normalized = normalize_string(value)
                if normalized in {'y', 'yes', 'true'}:
                    extracted['central_air'] = 'Y'
                elif normalized in {'n', 'no', 'false'}:
                    extracted['central_air'] = 'N'
                elif normalized in {'y', 'n'}:
                    extracted['central_air'] = normalized.upper()

        if 'basement' in extracted:
            value = extracted['basement']
            if isinstance(value, bool):
                extracted['basement'] = 'Gd' if value else 'None'
            else:
                normalized = normalize_string(value)
                if normalized in {'ex', 'excellent'}:
                    extracted['basement'] = 'Ex'
                elif normalized in {'gd', 'good'}:
                    extracted['basement'] = 'Gd'
                elif normalized in {'ta', 'typical', 'average'}:
                    extracted['basement'] = 'TA'
                elif normalized in {'fa', 'fair'}:
                    extracted['basement'] = 'Fa'
                elif normalized in {'po', 'poor'}:
                    extracted['basement'] = 'Po'
                elif normalized in {'none', 'no', 'no basement', ''}:
                    extracted['basement'] = 'None'

        quality_map = {
            'needs work': 3,
            'excellent': 9,
            'good': 7,
            'average': 5,
            'fair': 4,
            'poor': 2,
            'good neighborhood': 7,
            'luxury': 9,
        }

        for key in ['quality', 'condition']:
            if key in extracted:
                value = extracted[key]
                if isinstance(value, str):
                    normalized = normalize_string(value)
                    if normalized in quality_map:
                        extracted[key] = quality_map[normalized]
                    elif 'good neighborhood' in normalized:
                        extracted[key] = 7
                    elif 'needs work' in normalized:
                        extracted[key] = 3
                    elif 'luxury' in normalized and key == 'quality':
                        extracted[key] = 9
                    elif normalized.isdigit():
                        extracted[key] = int(normalized)
                elif isinstance(value, float):
                    extracted[key] = int(value)
                elif isinstance(value, int):
                    extracted[key] = value

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
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parse error with strict loads: {e}")
            return None

    def _try_json_loads_strict_false(self, text: str) -> Dict[str, Any] | None:
        try:
            return json.loads(text, strict=False)
        except Exception as e:
            logger.debug(f"JSON parse error with strict=False: {e}")
            return None

    def _try_ast_literal_eval(self, text: str) -> Dict[str, Any] | None:
        try:
            python_text = text.replace('null', 'None').replace('true', 'True').replace('false', 'False')
            return ast.literal_eval(python_text)
        except Exception as e:
            logger.debug(f"ast.literal_eval parse error: {e}")
            return None

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        extracted_text = self._extract_json_text(response)
        normalized_text = self._normalize_json_text(extracted_text)

        for parser in (self._try_json_loads, self._try_json_loads_strict_false, self._try_ast_literal_eval):
            parsed = parser(normalized_text)
            if isinstance(parsed, dict):
                return parsed

        logger.error("Unable to parse JSON response from LLM")
        return {}
    
    @classmethod
    def extract_with_version(cls, query: str, version: str) -> Stage1Output:
        extractor = cls(prompt_version=version)
        return extractor.extract(query)
