"""
Training data endpoint
GET /api/training-data - Returns dataset statistics, selected features, sample rows, and correlations.
"""

import csv
import math
import re
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/training-data", tags=["Training Data"])


class FeatureDescriptor(BaseModel):
    name: str
    description: str
    type: str
    impact: str
    explanation: str


class StatsResponse(BaseModel):
    total_rows: int
    median_price: int
    mean_price: int
    min_price: int
    max_price: int
    q1_price: int
    q3_price: int


class TrainingDataResponse(BaseModel):
    stats: StatsResponse
    selected_features: List[FeatureDescriptor]
    sample_data: List[Dict[str, Any]]
    correlations: Dict[str, float]


_training_data_cache: TrainingDataResponse = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _percentile(values: List[float], percent: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = (len(values) - 1) * percent
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return values[int(index)]
    factor = index - lower
    return values[lower] * (1 - factor) + values[upper] * factor


def _float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return float('nan')


def _extract_number_from_text(text: str) -> float:
    """Extract first number from text like 'I would prefer 2' -> 2"""
    if text is None:
        return float('nan')
    numbers = re.findall(r'\d+\.?\d*', str(text))
    if numbers:
        return float(numbers[0])
    return float('nan')


def _pearson_correlation(rows: List[Dict[str, str]], feature_name: str) -> float:
    values = []
    prices = []
    for row in rows:
        x = _float(row.get(feature_name, ''))
        y = _float(row.get('SalePrice', ''))
        if math.isnan(x) or math.isnan(y):
            continue
        values.append(x)
        prices.append(y)
    n = len(values)
    if n < 2:
        return 0.0
    mean_x = sum(values) / n
    mean_y = sum(prices) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(values, prices)) / n
    sigma_x = math.sqrt(sum((x - mean_x) ** 2 for x in values) / n)
    sigma_y = math.sqrt(sum((y - mean_y) ** 2 for y in prices) / n)
    if sigma_x == 0 or sigma_y == 0:
        return 0.0
    return cov / (sigma_x * sigma_y)


def _load_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open(newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        return [row for row in reader]


def _load_training_data() -> TrainingDataResponse:
    processed_path = _repo_root() / 'data' / 'processed' / 'ames_selected.csv'
    raw_path = _repo_root() / 'data' / 'raw' / 'ames.csv'

    processed_rows = _load_csv_rows(processed_path)
    raw_rows = _load_csv_rows(raw_path)

    prices = [_float(row.get('SalePrice', '')) for row in processed_rows]
    prices = [price for price in prices if not math.isnan(price)]

    stats = StatsResponse(
        total_rows=len(processed_rows),
        median_price=int(_percentile(prices, 0.5)),
        mean_price=int(round(sum(prices) / len(prices))) if prices else 0,
        min_price=int(min(prices)) if prices else 0,
        max_price=int(max(prices)) if prices else 0,
        q1_price=int(_percentile(prices, 0.25)),
        q3_price=int(_percentile(prices, 0.75))
    )

    selected_features = [
        FeatureDescriptor(
            name='Overall Qual',
            description='Material and finish quality (1-10)',
            type='ordinal',
            impact='High',
            explanation='The single most important factor. A rating of 7+ adds 30%+ value compared to average homes.'
        ),
        FeatureDescriptor(
            name='Gr Liv Area',
            description='Above grade living area (sq ft)',
            type='numeric',
            impact='High',
            explanation='Each 100 sq ft adds approximately $5,000-$10,000 to the property value.'
        ),
        FeatureDescriptor(
            name='Garage Cars',
            description='Garage capacity',
            type='numeric',
            impact='Medium',
            explanation='A 2-car garage adds roughly $20,000 in market value compared to no garage.'
        ),
        FeatureDescriptor(
            name='Year Built',
            description='Original construction year',
            type='numeric',
            impact='Medium',
            explanation='Newer homes (post-2000) command a 20-30% premium over older properties.'
        ),
        FeatureDescriptor(
            name='Total Bsmt SF',
            description='Basement square footage',
            type='numeric',
            impact='Medium',
            explanation='Finished basement adds 10-15% to overall property value.'
        ),
        FeatureDescriptor(
            name='bathrooms',
            description='Number of bathrooms (full + 0.5*half)',
            type='numeric',
            impact='Medium',
            explanation='Each additional bathroom adds $15,000-$25,000 in value.'
        ),
        FeatureDescriptor(
            name='Lot Area',
            description='Lot size (sq ft)',
            type='numeric',
            impact='Medium',
            explanation='Larger lots provide more space and privacy, adding land value.'
        ),
        FeatureDescriptor(
            name='Neighborhood',
            description='Physical location within Ames',
            type='categorical',
            impact='High',
            explanation='Premium neighborhoods like StoneBr and NoRidge command 20-40% above median prices.'
        ),
        FeatureDescriptor(
            name='Bsmt Qual',
            description='Basement quality rating',
            type='categorical',
            impact='Medium',
            explanation='Ex (Excellent) or Gd (Good) basement quality significantly increases value.'
        ),
        FeatureDescriptor(
            name='Central Air',
            description='Central air conditioning',
            type='binary',
            impact='Low',
            explanation='Central air adds ~5% to value and improves buyer appeal.'
        ),
        FeatureDescriptor(
            name='Heating',
            description='Heating type',
            type='categorical',
            impact='Low',
            explanation='Gas forced air (GasA) is the most desirable heating type.'
        ),
        FeatureDescriptor(
            name='Bedroom AbvGr',
            description='Number of bedrooms above grade',
            type='numeric',
            impact='Low',
            explanation='Each additional bedroom adds $15,000-$25,000, but diminishing returns after 4 bedrooms.'
        ),
    ]

    sample_data = [
        {k: row.get(k, '') for k in ['Bedroom AbvGr', 'bathrooms', 'Gr Liv Area', 'Lot Area', 'Year Built', 'Garage Cars', 'Overall Qual', 'SalePrice']}
        for row in processed_rows[:10]
    ]

    correlations = {
        'Overall Qual': round(_pearson_correlation(raw_rows, 'Overall Qual'), 2),
        'Gr Liv Area': round(_pearson_correlation(raw_rows, 'Gr Liv Area'), 2),
        'Garage Cars': round(_pearson_correlation(raw_rows, 'Garage Cars'), 2),
        'Year Built': round(_pearson_correlation(raw_rows, 'Year Built'), 2),
        'Total Bsmt SF': round(_pearson_correlation(raw_rows, 'Total Bsmt SF'), 2),
        'bathrooms': round(_pearson_correlation(processed_rows, 'bathrooms'), 2),
        'Lot Area': round(_pearson_correlation(raw_rows, 'Lot Area'), 2),
    }

    return TrainingDataResponse(
        stats=stats,
        selected_features=selected_features,
        sample_data=sample_data,
        correlations=correlations,
    )


@router.get('', response_model=TrainingDataResponse, status_code=status.HTTP_200_OK)
async def get_training_data() -> TrainingDataResponse:
    """Return training data statistics and sample rows from the selected dataset."""
    global _training_data_cache
    if _training_data_cache is None:
        _training_data_cache = _load_training_data()
    return _training_data_cache