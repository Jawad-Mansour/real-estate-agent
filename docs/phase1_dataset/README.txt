PHASE 1: DATASET DOWNLOAD & INITIAL INSPECTION
===============================================

DATASET: AMES HOUSING
---------------------
Source: Kaggle (house-prices-advanced-regression-techniques)

DATASET STATISTICS:
-------------------
- Rows: 2,930
- Columns: 82
- Target: SalePrice (what we predict)
- Missing values: Present in multiple columns

WHY AMES HOUSING (MEETS PDF REQUIREMENTS):
------------------------------------------
| PDF Requirement | How Ames Fulfills |
|-----------------|-------------------|
| 500+ rows       | 2,930 rows        |
| Categorical col | Neighborhood (25+ categories) |
| Missing values  | BsmtQual, LotFrontage, etc. |
| Meaningful target | SalePrice (real estate) |

FILE LOCATION:
--------------
data/raw/ames.csv              # Original - NEVER MODIFIED
data/metadata/data_dictionary.md  # Column descriptions

INITIAL INSPECTION FINDINGS:
----------------------------
- No duplicate rows
- Mixed data types (int64, float64, object)
- Structural missingness detected
  (garage columns missing together = house has no garage)

PDF REQUIREMENTS VERIFIED:
--------------------------
[✓] 500+ rows confirmed
[✓] Categorical column exists (Neighborhood)
[✓] Missing values exist (BsmtQual has NA = No Basement)

