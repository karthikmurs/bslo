# Bengaluru Strategic Logistics Optimizer (BSLO)
## Technical Documentation

> **📖 For a comprehensive project overview with detailed explanations, see [README.md](README.md)**  
> This document contains technical implementation details for developers.

A Predictive AI System for Day-Ahead Route Planning and Infrastructure Simulation

## Project Overview

BSLO is an AI-powered planning tool designed for logistics managers and urban planners. Leveraging historical daily traffic data from the Preetham Gouda Bangalore Dataset, it predicts future congestion "Friction Scores" for specific dates. It aligns with the B-TRAC and ASTraM (Actionable Intelligence for Sustainable Traffic Management) initiatives by introducing a "Green Logistics" component that optimizes routes not just for speed, but for minimal environmental impact.

### Problem Statement

**The Gap:** Logistics companies in Bangalore suffer from unpredictable delivery windows. Current tools rely on real-time data, which is too late for resource planning (e.g., deciding fleet allocation 24 hours in advance).

**The Data Constraint:** Publicly available sensor data is aggregated at a Daily level, making minute-by-minute navigation impossible.

**The Opportunity:** Use this daily aggregation to build a Macro-Level Planner that predicts the "Total Stress" of a route for a future date, allowing for proactive rather than reactive decision-making.

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
bslo/
├── data/
│   ├── Banglore_traffic_Dataset.csv    # Raw dataset
│   └── traffic_data_cleaned.csv        # Processed dataset
├── notebooks/
│   ├── 01_eda_data_cleaning.ipynb      # EDA and data cleaning
│   ├── 02_baseline_modeling.ipynb      # Baseline model
│   └── 03_xgboost_modeling.ipynb       # XGBoost model
├── src/
│   ├── __init__.py                     # Package initialization
│   ├── api.py                          # FastAPI application
│   ├── geospatial.py                   # Geospatial routing utilities
│   └── test_api.py                     # API test script
├── app/
│   ├── streamlit_app.py                # Interactive dashboard
│   └── map_routing.py                  # Map-based routing page
├── models/
│   ├── xgboost_tuned.pkl               # Trained XGBoost model
│   ├── preprocessor.pkl                # Feature preprocessor
│   ├── baseline_results.csv            # Baseline metrics
│   ├── xgboost_results.csv             # XGBoost metrics
│   └── feature_importance.csv          # Feature importance analysis
├── .gitignore                          # Git ignore rules
├── API_DOCUMENTATION.md                # API documentation
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
└── start_bslo.sh                       # Startup script
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

### [03_xgboost_modeling.ipynb](notebooks/03_xgboost_modeling.ipynb)
XGBoost Model Development and Optimization:
- Initial XGBoost model with default parameters
- Hyperparameter tuning using GridSearchCV (3-fold CV)
- Comprehensive model evaluation and comparison with baseline
- Feature importance analysis
- Model and preprocessor saved for deployment
- **Expected Performance:** 50-60% improvement over baseline

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
- **API Framework:** FastAPI, Uvicorn
- **Dashboard:** Streamlit

## Getting Started

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd bslo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Notebooks (Model Training)

```bash
# Start Jupyter
jupyter notebook

# Run notebooks in order:
# 1. notebooks/01_eda_data_cleaning.ipynb
# 2. notebooks/02_baseline_modeling.ipynb
# 3. notebooks/03_xgboost_modeling.ipynb
```

### 3. Deploy API and Dashboard

#### Option A: Quick Start (Recommended)

```bash
# Start both API and dashboard with one command
./start_bslo.sh
```

#### Option B: Manual Start

```bash
# Terminal 1: Start API Server
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Streamlit Dashboard
streamlit run app/streamlit_app.py
```

### 4. Access the Application

- **API Documentation:** http://localhost:8000/docs
- **Interactive Dashboard:** http://localhost:8501
- **API Health Check:** http://localhost:8000/health

## API Features

### Feature A: Friction Score Predictor
Predict congestion level (0-100) for a specific road on a target date.

**Endpoint:** `POST /api/v1/friction-score`

**Key Parameters:**
- Traffic Volume (vehicles/day): 5,000 - 70,000
- Road Capacity Utilization (%): 20% - 100%
- Weather Condition: Clear, Rain, Overcast, Fog, Windy

### Feature B: Strategic Route Scoring
Calculate cumulative friction score for a defined route.

**Endpoint:** `POST /api/v1/route-score`

### Feature C: Route Comparison
Compare multiple routes and recommend the best option.

**Endpoint:** `POST /api/v1/route-comparison`

### Feature D: Point-to-Point Route Planning
Find optimal route from point A to point B with congestion predictions and interactive map visualization.

**Endpoint:** `POST /api/v1/point-to-point`

**Features:**
- Graph-based routing using NetworkX (Dijkstra's algorithm)
- Real-time congestion prediction for each road segment
- Interactive Folium map with color-coded congestion levels
- Distance calculation using Haversine formula
- Road-by-road breakdown with coordinates

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## Testing

```bash
# Run API tests
python src/test_api.py
```

## Contact and Further Information

**Project Repository:** [GitHub - BSLO](https://github.com/karthikmurs/bslo)

**Author:** Karthik Mahendra Raje Urs  
**Email:** [karthik.urs.m@gmail.com](mailto:karthik.urs.m@gmail.com)  
**LinkedIn:** [LinkedIn Profile](https://www.linkedin.com/in/karthikurs/)

**Dataset Source:** [Bangalore City Traffic Dataset on Kaggle](https://www.kaggle.com/datasets/preethamgouda/banglore-city-traffic-dataset)

**Technologies Used:**
- Python 3.12, Pandas, NumPy, Scikit-Learn, XGBoost
- FastAPI, Streamlit, Folium, NetworkX
- Plotly, Matplotlib, Seaborn

**License:** Educational/Research Use

**Acknowledgments:**
- Preetham Gouda for the Bangalore traffic dataset
- B-TRAC and ASTraM initiatives for inspiration
- Open-source community for excellent tools and libraries

---

**Last Updated:** March 2026  
**Version:** 1.0
