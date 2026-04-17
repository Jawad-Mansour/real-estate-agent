"""
Training data endpoint
GET /api/training-data - Returns dataset statistics, selected features, sample rows, and correlations.
Uses CSV files if available, otherwise falls back to hardcoded data (works on Railway)
"""

import csv
import math
import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
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


def _find_project_root() -> Path:
    """Find project root by looking for 'data' directory"""
    current = Path(__file__).resolve()
    # Go up until we find a directory containing 'data' folder
    for _ in range(10):
        if (current / 'data').exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    # Fallback: go up 4 levels from backend/api/routes/
    return Path(__file__).resolve().parents[4]


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


def _float(value) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
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
    try:
        with csv_path.open(newline='', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            return [row for row in reader]
    except FileNotFoundError:
        logger.warning(f"CSV file not found: {csv_path}")
        return []
    except Exception as e:
        logger.warning(f"Error loading CSV {csv_path}: {e}")
        return []


def _get_hardcoded_data() -> TrainingDataResponse:
    """Hardcoded fallback data - used when CSV files are not available (e.g., Railway)"""
    return TrainingDataResponse(
        stats=StatsResponse(
            total_rows=2930,
            median_price=163000,
            mean_price=180796,
            min_price=34900,
            max_price=755000,
            q1_price=129500,
            q3_price=214000
        ),
        selected_features=[
            FeatureDescriptor(
                name='Overall Qual',
                description='Material and finish quality (1-10)',
                type='ordinal',
                impact='High',
                explanation='The single most important factor. A rating of 7+ adds 30%+ value.'
            ),
            FeatureDescriptor(
                name='Gr Liv Area',
                description='Above grade living area (sq ft)',
                type='numeric',
                impact='High',
                explanation='Each 100 sq ft adds approximately $5,000-$10,000.'
            ),
            FeatureDescriptor(
                name='Garage Cars',
                description='Garage capacity',
                type='numeric',
                impact='Medium',
                explanation='A 2-car garage adds roughly $20,000 in market value.'
            ),
            FeatureDescriptor(
                name='Year Built',
                description='Original construction year',
                type='numeric',
                impact='Medium',
                explanation='Newer homes (post-2000) command a 20-30% premium.'
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
                explanation='Each additional bathroom adds $15,000-$25,000.'
            ),
            FeatureDescriptor(
                name='Lot Area',
                description='Lot size (sq ft)',
                type='numeric',
                impact='Medium',
                explanation='Larger lots provide more space and privacy.'
            ),
            FeatureDescriptor(
                name='Neighborhood',
                description='Physical location within Ames',
                type='categorical',
                impact='High',
                explanation='Premium neighborhoods command 20-40% above median prices.'
            ),
            FeatureDescriptor(
                name='Bsmt Qual',
                description='Basement quality rating',
                type='categorical',
                impact='Medium',
                explanation='Ex or Gd basement quality significantly increases value.'
            ),
            FeatureDescriptor(
                name='Central Air',
                description='Central air conditioning',
                type='binary',
                impact='Low',
                explanation='Central air adds ~5% to value.'
            ),
            FeatureDescriptor(
                name='Heating',
                description='Heating type',
                type='categorical',
                impact='Low',
                explanation='Gas forced air (GasA) is the most desirable.'
            ),
            FeatureDescriptor(
                name='Bedroom AbvGr',
                description='Number of bedrooms above grade',
                type='numeric',
                impact='Low',
                explanation='Each bedroom adds $15,000-$25,000.'
            ),
        ],
        sample_data=[
            {"Bedroom AbvGr": 3, "bathrooms": 2.0, "Gr Liv Area": 1656, "Lot Area": 31770, 
             "Year Built": 1960, "Garage Cars": 2, "Overall Qual": 6, "SalePrice": 215000},
            {"Bedroom AbvGr": 4, "bathrooms": 2.5, "Gr Liv Area": 2500, "Lot Area": 15000, 
             "Year Built": 2005, "Garage Cars": 2, "Overall Qual": 8, "SalePrice": 425000},
            {"Bedroom AbvGr": 2, "bathrooms": 1.0, "Gr Liv Area": 1120, "Lot Area": 8500, 
             "Year Built": 1955, "Garage Cars": 1, "Overall Qual": 5, "SalePrice": 135000},
            {"Bedroom AbvGr": 5, "bathrooms": 3.5, "Gr Liv Area": 3200, "Lot Area": 25000, 
             "Year Built": 2008, "Garage Cars": 3, "Overall Qual": 9, "SalePrice": 550000},
            {"Bedroom AbvGr": 3, "bathrooms": 2.0, "Gr Liv Area": 1800, "Lot Area": 12000, 
             "Year Built": 1995, "Garage Cars": 2, "Overall Qual": 7, "SalePrice": 285000},
        ],
        correlations={
            'Overall Qual': 0.79,
            'Gr Liv Area': 0.71,
            'Garage Cars': 0.62,
            'Year Built': 0.57,
            'Total Bsmt SF': 0.61,
            'bathrooms': 0.65,
            'Lot Area': 0.26,
        }
    )


def _load_training_data() -> TrainingDataResponse:
    """Try to load from CSV files, fall back to hardcoded data if files don't exist"""
    root = _find_project_root()
    
    processed_path = root / 'data' / 'processed' / 'ames_selected.csv'
    raw_path = root / 'data' / 'raw' / 'ames.csv'
    
    logger.info(f"Project root: {root}")
    logger.info(f"Looking for processed data at: {processed_path}")
    logger.info(f"Looking for raw data at: {raw_path}")
    
    # Check if files exist
    if not processed_path.exists() or not raw_path.exists():
        logger.warning("CSV files not found - using hardcoded fallback data")
        return _get_hardcoded_data()
    
    processed_rows = _load_csv_rows(processed_path)
    raw_rows = _load_csv_rows(raw_path)
    
    if not processed_rows:
        logger.warning("No processed data loaded - using hardcoded fallback data")
        return _get_hardcoded_data()
    
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
            explanation='The single most important factor. A rating of 7+ adds 30%+ value.'
        ),
        FeatureDescriptor(
            name='Gr Liv Area',
            description='Above grade living area (sq ft)',
            type='numeric',
            impact='High',
            explanation='Each 100 sq ft adds approximately $5,000-$10,000.'
        ),
        FeatureDescriptor(
            name='Garage Cars',
            description='Garage capacity',
            type='numeric',
            impact='Medium',
            explanation='A 2-car garage adds roughly $20,000 in market value.'
        ),
        FeatureDescriptor(
            name='Year Built',
            description='Original construction year',
            type='numeric',
            impact='Medium',
            explanation='Newer homes (post-2000) command a 20-30% premium.'
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
            explanation='Each additional bathroom adds $15,000-$25,000.'
        ),
        FeatureDescriptor(
            name='Lot Area',
            description='Lot size (sq ft)',
            type='numeric',
            impact='Medium',
            explanation='Larger lots provide more space and privacy.'
        ),
        FeatureDescriptor(
            name='Neighborhood',
            description='Physical location within Ames',
            type='categorical',
            impact='High',
            explanation='Premium neighborhoods command 20-40% above median prices.'
        ),
        FeatureDescriptor(
            name='Bsmt Qual',
            description='Basement quality rating',
            type='categorical',
            impact='Medium',
            explanation='Ex or Gd basement quality significantly increases value.'
        ),
        FeatureDescriptor(
            name='Central Air',
            description='Central air conditioning',
            type='binary',
            impact='Low',
            explanation='Central air adds ~5% to value.'
        ),
        FeatureDescriptor(
            name='Heating',
            description='Heating type',
            type='categorical',
            impact='Low',
            explanation='Gas forced air (GasA) is the most desirable.'
        ),
        FeatureDescriptor(
            name='Bedroom AbvGr',
            description='Number of bedrooms above grade',
            type='numeric',
            impact='Low',
            explanation='Each bedroom adds $15,000-$25,000.'
        ),
    ]

    sample_data = []
    for row in processed_rows[:10]:
        sample_row = {}
        for k in ['Bedroom AbvGr', 'bathrooms', 'Gr Liv Area', 'Lot Area', 'Year Built', 'Garage Cars', 'Overall Qual', 'SalePrice']:
            sample_row[k] = row.get(k, '')
        sample_data.append(sample_row)

    correlations = {}
    if raw_rows:
        correlations['Overall Qual'] = round(_pearson_correlation(raw_rows, 'Overall Qual'), 2)
        correlations['Gr Liv Area'] = round(_pearson_correlation(raw_rows, 'Gr Liv Area'), 2)
        correlations['Garage Cars'] = round(_pearson_correlation(raw_rows, 'Garage Cars'), 2)
        correlations['Year Built'] = round(_pearson_correlation(raw_rows, 'Year Built'), 2)
        correlations['Total Bsmt SF'] = round(_pearson_correlation(raw_rows, 'Total Bsmt SF'), 2)
        correlations['Lot Area'] = round(_pearson_correlation(raw_rows, 'Lot Area'), 2)
    
    if processed_rows:
        correlations['bathrooms'] = round(_pearson_correlation(processed_rows, 'bathrooms'), 2)

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