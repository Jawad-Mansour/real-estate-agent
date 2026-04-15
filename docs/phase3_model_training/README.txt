PHASE 3: MODEL TRAINING - COMPLETE DOCUMENTATION
=================================================

DATE COMPLETED: April 15, 2026

NOTEBOOK: 02_Model_Training_and_Evaluation.ipynb

================================================================================
OVERVIEW
================================================================================

In Phase 3, we trained machine learning models to predict house prices (SalePrice)
using the 12 features selected in Phase 2. We followed strict no-leakage principles:
split FIRST, then fit preprocessing on TRAIN only, then transform validation/test.

================================================================================
DATA SPLIT (NO LEAKAGE) - PDF #01
================================================================================

Split performed BEFORE any preprocessing:

| Split       | Rows | Percentage | Purpose                          |
|-------------|------|------------|----------------------------------|
| Training    | 2051 | 70%        | Learn patterns, fit model        |
| Validation  | 439  | 15%        | Tune hyperparameters             |
| Test        | 440  | 15%        | Final evaluation (ONCE)          |

Target distribution across splits (similar = randomization worked):
- Train mean: $178,641
- Validation mean: $184,719
- Test mean: $186,926

✓ No overlap between splits - Data leakage prevented

================================================================================
FEATURE TYPES IDENTIFIED
================================================================================

NUMERIC COLUMNS (8) - need imputation + scaling:
- Bedroom AbvGr (0 missing)
- Gr Liv Area (0 missing)
- Lot Area (0 missing)
- Year Built (0 missing)
- Garage Cars (1 missing → structural = no garage)
- bathrooms (0 missing)
- Overall Cond (0 missing)
- Overall Qual (0 missing)

CATEGORICAL COLUMNS (4) - need imputation + encoding:
- Neighborhood: 28 unique values, 0 missing
- Bsmt Qual: 6 unique values, 53 missing (structural = no basement)
- Heating: 6 unique values, 0 missing
- Central Air: 2 unique values, 0 missing

================================================================================
PREPROCESSING PIPELINE - PDF #02, #03, #04
================================================================================

ColumnTransformer with two pipelines:

NUMERIC PIPELINE:
1. SimpleImputer(strategy='median') - fills missing with median from TRAIN only
2. StandardScaler() - scales to mean=0, std=1

CATEGORICAL PIPELINE:
1. SimpleImputer(strategy='constant', fill_value='missing') - fills missing
2. OneHotEncoder(handle_unknown='ignore') - creates binary columns per category

FITTED ON TRAIN ONLY - NO LEAKAGE:
- Numeric medians learned from train: 3 beds, 1972 built, 2 garage, etc.
- Categories learned from train: Neighborhood (28), Bsmt Qual (6), Heating (6), Central Air (2)

TRANSFORM APPLIED TO ALL SETS:
- Training set shape: (2051, 50)  ← 12 original → 50 after encoding
- Validation set shape: (439, 50)
- Test set shape: (440, 50)

================================================================================
MODELS TRAINED - PDF #04
================================================================================

MODEL 1: LINEAR REGRESSION (Baseline)
--------------------------------------
Train R²: 0.8457
Train RMSE: $30,647
Validation R²: 0.8804
Validation RMSE: $28,623
Gap (Train - Val R²): -0.0347 ✓ Small gap - generalizes well

MODEL 2: RANDOM FOREST (Primary)
---------------------------------
Hyperparameters:
- n_estimators: 200 (number of trees)
- max_depth: 15 (prevents overfitting)
- min_samples_split: 5
- min_samples_leaf: 2
- random_state: 42

Train R²: 0.9609
Train RMSE: $15,427
Validation R²: 0.8968
Validation RMSE: $26,585
Gap (Train - Val R²): 0.0641 ✓ Small gap - generalizes well

================================================================================
MODEL COMPARISON - PDF #05
================================================================================

| Model            | Train R² | Validation R² | Validation RMSE | Winner |
|------------------|----------|---------------|-----------------|--------|
| Random Forest    | 0.9609   | 0.8968        | $26,585         | ✓ WINNER |
| Linear Regression| 0.8457   | 0.8804        | $28,623         | Baseline |

BEST MODEL: Random Forest
- Validation R²: 0.8968 (explains 89.7% of variance)
- Validation RMSE: $26,585 (average error)

================================================================================
FEATURE IMPORTANCE (Random Forest)
================================================================================

Top 15 features ranked by importance:

| Rank | Feature              | Importance | Cumulative |
|------|----------------------|------------|------------|
| 1    | Overall Qual         | 62.56%     | 62.56%     |
| 2    | Gr Liv Area          | 15.03%     | 77.59%     |
| 3    | Lot Area             | 5.63%      | 83.22%     |
| 4    | bathrooms            | 4.49%      | 87.71%     |
| 5    | Year Built           | 3.77%      | 91.48%     |
| 6    | Garage Cars          | 3.41%      | 94.89%     |
| 7    | Bedroom AbvGr        | 0.79%      | 95.68%     |
| 8    | Overall Cond         | 0.67%      | 96.35%     |
| 9    | Bsmt Qual_Ex         | 0.65%      | 97.00%     |
| 10   | Bsmt Qual_Gd         | 0.45%      | 97.45%     |
| 11   | Central Air_N        | 0.31%      | 97.76%     |
| 12   | Neighborhood_NoRidge | 0.28%      | 98.04%     |
| 13   | Central Air_Y        | 0.25%      | 98.29%     |
| 14   | Neighborhood_Crawfor | 0.22%      | 98.51%     |
| 15   | Neighborhood_OldTown | 0.19%      | 98.70%     |

KEY INSIGHT: Top 6 features (Overall Qual, Gr Liv Area, Lot Area, bathrooms,
Year Built, Garage Cars) explain 94.89% of the model's predictive power.

================================================================================
FINAL TEST EVALUATION (ONCE) - PDF #05
================================================================================

Test set was completely untouched until this point.

RESULTS ON UNSEEN DATA (440 rows):

| Metric     | Value      | Interpretation                          |
|------------|------------|-----------------------------------------|
| Test R²    | 0.8547     | Model explains 85.5% of price variance  |
| Test RMSE  | $32,361    | Average prediction error                |
| Test MAE   | $18,457    | Typical error ~$18k                     |
| Test MAPE  | 10.1%      | Average error ~10% of actual price      |

Validation vs Test Comparison:
- Validation R²: 0.8968
- Test R²: 0.8547
- Difference: 0.0421 (small - model generalizes well)

================================================================================
RESIDUAL ANALYSIS
================================================================================

Residuals = Actual - Predicted (on test set)

| Metric              | Value      | Ideal        | Status |
|---------------------|------------|--------------|--------|
| Mean of residuals   | $87        | Near 0       | ✓ PASS |
| Std of residuals    | $32,398    | -            | -      |

Residual plots saved to: ../docs/residuals.png
Actual vs Predicted plot saved to: ../docs/actual_vs_predicted.png

FINDINGS:
- ✓ Residuals centered around zero (mean $87) - no systematic bias
- ✓ Distribution roughly normal
- ✓ No funnel pattern - homoscedasticity holds

================================================================================
EXPORTED ARTIFACTS - PDF #04
================================================================================

Files saved to: notebooks/exports/

| File                    | Size     | Purpose                                    |
|-------------------------|----------|--------------------------------------------|
| model.joblib            | 11.95 MB | Trained Random Forest model                |
| preprocessor.joblib     | 5.3 KB   | Fitted ColumnTransformer for new data      |
| feature_columns.json    | 1.1 KB   | Feature names in order for inference       |
| training_stats.json     | 1.8 KB   | Median, quartiles from TRAIN for Stage 2   |

training_stats.json contents:
{
  "median_price": 160000,
  "mean_price": 178641,
  "std_price": 78030,
  "min_price": 12789,
  "max_price": 755000,
  "q1_price": 129500,
  "q3_price": 210500,
  "model_type": "Random Forest",
  "test_rmse": 32361,
  "test_r2": 0.8547
}

================================================================================
PDF REQUIREMENTS VERIFICATION
================================================================================

| # | Requirement                          | Status | Evidence                          |
|---|--------------------------------------|--------|-----------------------------------|
|01 | Three-way split (70/15/15)          | ✓ PASS | 2051/439/440 rows, no overlap     |
|02 | Missing values fit on train only    | ✓ PASS | Medians learned from train only   |
|03 | Encode and scale fit on train only  | ✓ PASS | StandardScaler, OneHotEncoder on train |
|04 | ColumnTransformer + 2 model types   | ✓ PASS | Linear Regression + Random Forest |
|05 | Train vs val scores + test once     | ✓ PASS | Comparison table, test ONCE       |

================================================================================
CONCLUSION
================================================================================

Phase 3 successfully:
1. Split data into train/validation/test with NO LEAKAGE
2. Created ColumnTransformer with imputation, encoding, scaling
3. Fitted all transformers on TRAIN data only
4. Trained Linear Regression (baseline) and Random Forest (primary)
5. Compared train vs validation scores
6. Evaluated best model (Random Forest) on test set ONCE
7. Exported all artifacts for deployment (Phase 4)

BEST MODEL: Random Forest
TEST RMSE: $32,361
TEST R²: 0.8547

Ready for Phase 4: Copy artifacts to backend/models/

================================================================================
