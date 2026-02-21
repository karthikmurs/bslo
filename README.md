# Bengaluru Strategic Logistics Optimizer (BSLO)

A Predictive AI System for Day-Ahead Route Planning and Infrastructure Simulation

## Project Overview

BSLO is an AI-powered planning tool designed for logistics managers and urban planners. Leveraging historical daily traffic data from the Preetham Gouda Bangalore Dataset, it predicts future congestion "Friction Scores" for specific dates. It aligns with the B-TRAC and ASTraM (Actionable Intelligence for Sustainable Traffic Management) initiatives by introducing a "Green Logistics" component that optimizes routes not just for speed, but for minimal environmental impact.

**Problem Statement**
•	The Gap: Logistics companies in Bangalore suffer from unpredictable delivery windows. Current tools rely on real-time data, which is too late for resource planning (e.g., deciding fleet allocation 24 hours in advance).
•	The Data Constraint: Publicly available sensor data is aggregated at a Daily level, making minute-by-minute navigation impossible.
•	The Opportunity: Use this daily aggregation to build a Macro-Level Planner that predicts the "Total Stress" of a route for a future date, allowing for proactive rather than reactive decision-making.

**Key Differentiator:** While real-time navigation apps solve "Where do I turn right now?", BSLO solves "Which route should our delivery fleet take next Tuesday?"


## Dataset

**Source:** [Bangalore City Traffic Dataset](https://www.kaggle.com/datasets/preethamgouda/banglore-city-traffic-dataset)

| Attribute | Value |
|-----------|-------|
| Records | 8,936 |
| Date Range | Jan 2022 - Aug 2024 |
| Areas | 8 (Indiranagar, Whitefield, Koramangala, M.G. Road, Jayanagar, Hebbal, Yeshwanthpur, Electronic City) |
| Roads/Intersections | 16 |
| Features | 16 columns |

## Key Findings

### Data Quality
- ✓ No missing values
- ✓ No duplicate records
- ✓ All values within expected ranges

### Traffic Patterns Discovered
1. **Temporal Patterns:** Clear day-of-week and monthly seasonality
2. **Geographic Variation:** Significant congestion differences across areas
3. **Weather Impact:** Weather conditions correlate with traffic patterns
4. **Strong Predictors:** Traffic Volume, Road Capacity Utilization, and lag features

### Target Variables
| Variable | Range | Purpose |
|----------|-------|---------|
| Congestion Level | 0-100 | Primary target (Friction Score) |
| Environmental Impact | ~60-180 | Green Corridor optimization |

## Project Structure

```
bslo_scratch/
├── data/
│   ├── Banglore_traffic_Dataset.csv    # Raw dataset
│   └── traffic_data_cleaned.csv        # Processed dataset
├── notebooks/
│   └── 01_eda_data_cleaning.ipynb      # EDA and data cleaning
│   └── 02_baseline_modeling.ipynb      # Baseline Model
├── src/                                 # Source code (future)
├── models/                              # Trained models (future)
└── README.md
```

## Notebooks

### [01_eda_data_cleaning.ipynb](notebooks/01_eda_data_cleaning.ipynb)
Exploratory Data Analysis and Data Cleaning notebook covering:
- Initial data inspection
- Missing values and duplicate analysis
- Univariate and bivariate analysis
- Temporal pattern analysis
- Outlier detection
- Feature engineering (lag features, derived metrics)
- Correlation analysis

### [02_baseline_modeling.ipynb](notebooks/02_baseline_modeling.ipynb)
Baseline Model Development and Evaluation:
- Feature preparation (26 features including temporal, traffic, and lag variables)
- Temporal train-test split (70/30) preserving time-series order
- Preprocessing pipeline (StandardScaler for numerical, OneHotEncoder for categorical)
- DummyRegressor baseline model (mean strategy)
- **Baseline Results:**
  - Test MAE: 19.96
  - Test RMSE: 23.49
  - Test R²: -0.00
- Error analysis by congestion level bins
- Establishes performance benchmark for advanced models

## Modeling Approach

**Algorithm:** XGBoost Regressor
- Handles tabular data effectively
- Captures non-linear relationships
- Provides feature importance for interpretability

**Evaluation Metrics:**
- **RMSE** (Root Mean Squared Error) - Primary metric, penalizes large prediction errors
- **MAE** (Mean Absolute Error) - Interpretable in congestion level units
- **R² Score** - Measures variance explained by the model

**Validation Strategy:** Time-Series Split (train on historical data, test on future dates)

## Tech Stack

- **Language:** Python 3.9+
- **Data Manipulation:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn, Plotly
- **Machine Learning:** Scikit-Learn, XGBoost
- **App Framework:** Streamlit (planned)

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install pandas numpy matplotlib seaborn plotly scikit-learn xgboost
   ```
3. Open the EDA notebook:
   ```bash
   jupyter notebook notebooks/01_eda_data_cleaning.ipynb
   ```


## License

This project is for educational purposes as part of a capstone project.
