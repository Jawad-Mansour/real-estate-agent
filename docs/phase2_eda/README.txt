PHASE 2: EXPLORATORY DATA ANALYSIS (EDA)
========================================

NOTEBOOK: 01_EDA_and_Exploration.ipynb

KEY DISCOVERIES:
----------------

1. TARGET VARIABLE (SalePrice):
   - Mean: ~$180,000
   - Median: ~$160,000
   - Skewness: 1.88 (right-skewed)
   - Interpretation: More cheap houses, few expensive mansions

2. TOP CORRELATIONS WITH SALEPRICE:
   | Feature        | Correlation | Why Important |
   |----------------|-------------|----------------|
   | Overall Qual   | 0.799       | Quality is #1 predictor |
   | Gr Liv Area    | 0.707       | Bigger house = higher price |
   | Garage Cars    | 0.648       | Parking adds value |
   | Year Built     | 0.558       | Newer homes cost more |
   | Total Bsmt SF  | 0.548       | Finished basement adds value |

3. MISSING VALUE ANALYSIS:
   | Column        | Missing % | Imputation Strategy |
   |---------------|-----------|---------------------|
   | Pool QC       | ~99%      | Fill with 'None' (no pool) |
   | Misc Feature  | ~96%      | Fill with 'None' |
   | Alley         | ~93%      | Fill with 'None' (no alley) |
   | Fence         | ~80%      | Fill with 'None' (no fence) |
   | Fireplace Qu  | ~50%      | Fill with 'None' (no fireplace) |
   | Lot Frontage  | ~20%      | Median imputation |
   | Bsmt Qual     | ~5%       | Fill with 'None' (no basement) |

4. CATEGORICAL COLUMN CARDINALITY:
   | Column        | Unique Values | Encoding Strategy |
   |---------------|---------------|-------------------|
   | Neighborhood  | 25+           | One-hot encoding |
   | MS Zoning     | ~7            | One-hot encoding |
   | Central Air   | 2             | Binary (Y=1, N=0) |
   | Heating       | ~6            | One-hot encoding |

FEATURE SELECTION (12 FEATURES) - PDF #04:
------------------------------------------
We selected 12 features based on:
1. Correlation strength with SalePrice
2. Domain knowledge (real estate importance)
3. Data availability (not too many missing values)
4. Feature variety (numeric, ordinal, categorical)

SELECTED FEATURES WITH JUSTIFICATION:
+----+----------------+------------+--------+---------------------------------+
| #  | Feature        | Type       | Corr   | Why Selected                    |
+----+----------------+------------+--------+---------------------------------+
| 1  | Overall Qual   | Ordinal    | 0.799  | Strongest predictor             |
| 2  | Gr Liv Area    | Numeric    | 0.707  | Size = value                    |
| 3  | Garage Cars    | Numeric    | 0.648  | Parking premium                 |
| 4  | Year Built     | Numeric    | 0.558  | Newer is better                 |
| 5  | bathrooms      | Numeric    | ~0.55  | Essential amenity               |
| 6  | Lot Area       | Numeric    | 0.267  | Land value                      |
| 7  | Bedroom AbvGr  | Numeric    | 0.144  | Core real estate feature        |
| 8  | Neighborhood   | Categorical| N/A    | Location premium (25+ areas)    |
| 9  | Bsmt Qual      | Categorical| N/A    | Finished basement adds value    |
| 10 | Central Air    | Binary     | N/A    | Modern amenity (Y/N)            |
| 11 | Heating        | Categorical| N/A    | Heating type affects desirability|
| 12 | Overall Cond   | Ordinal    |-0.102  | Poor condition = lower price    |

WHY NOT OTHER FEATURES:
+--------------------+--------------------------------------------------+
| Excluded Feature   | Reason                                           |
+--------------------+--------------------------------------------------+
| Pool Area          | Too rare (1% of houses) - would cause overfitting|
| MS Zoning          | Redundant with neighborhood                      |
| Lot Frontage       | 20% missing, weak correlation                    |
| Alley              | 93% missing (most houses have no alley)          |
| Fireplaces         | Low correlation, not essential                   |
| Sale Condition     | Not a physical feature of the house              |
+--------------------+--------------------------------------------------+

DATA TYPES OF SELECTED FEATURES:
+----------------+----------------+---------------------------------+
| Feature        | Type           | Notes                           |
+----------------+----------------+---------------------------------+
| Bedroom AbvGr  | Numerical      | Integer count (1-5)             |
| Gr Liv Area    | Numerical      | Square feet (continuous)        |
| Lot Area       | Numerical      | Square feet (continuous)        |
| Year Built     | Numerical      | Year (ordinal - ordered)        |
| Garage Cars    | Numerical      | Integer count (0-3)             |
| Neighborhood   | Categorical    | 25+ unique text values          |
| Overall Cond   | Ordinal        | 1-10 scale (ordered)            |
| Overall Qual   | Ordinal        | 1-10 scale (ordered)            |
| Bsmt Qual      | Categorical    | Ex/Gd/TA/Fa/Po/NA               |
| Heating        | Categorical    | GasA, GasW, Wall, etc.          |
| Central Air    | Binary         | Y or N                          |
| bathrooms      | Numerical      | Float (1.0, 1.5, 2.0)           |
| SalePrice      | Numerical      | Target (what we predict)        |
+----------------+----------------+---------------------------------+

OUTPUT FILES CREATED:
---------------------
data/processed/ames_selected.csv  (2930 rows, 13 columns)

PDF REQUIREMENTS MET:
---------------------
[✓] #02: Missing value audit completed
[✓] #04: Feature selection (8-12 features) with justification

NEXT STEPS (PHASE 3):
---------------------
- Split data into train/val/test (70/15/15)
- Fit imputers, scalers, encoders on TRAIN only
- Train Linear Regression and Random Forest
- Evaluate on test set ONCE
- Export model artifacts (model.joblib, preprocessor.joblib)

