### Bengaluru Strategic Logistics Optimizer (BSLO)
**Predicting Traffic Congestion for Smarter Delivery Planning**

**Author:** Karthik Mahendra Raje Urs

---

## Executive Summary

BSLO is a traffic prediction system that helps delivery companies and city planners in Bangalore make smarter decisions about route planning. Instead of reacting to traffic in real-time, BSLO predicts congestion levels for tomorrow or next week, allowing businesses to plan ahead. Using 2.5 years of historical traffic data and machine learning, the system achieves high accuracy in predicting congestion levels and provides an interactive dashboard for route planning with visual maps.

**Key Achievement:** The system can predict traffic congestion with 60% better accuracy than simple baseline methods, helping logistics managers choose the best routes before vehicles even leave the depot.

---

## Rationale: Why This Matters

### The Problem
Delivery companies in Bangalore face a daily challenge: **unpredictable traffic makes delivery times unreliable**. Current navigation apps like Google Maps only show traffic conditions *right now*, but logistics managers need to plan their fleet allocation 24 hours in advance. By the time a driver sees heavy traffic on their phone, it's too late to choose a different route or reassign deliveries.

### The Impact
- **For Businesses:** Missed delivery windows mean unhappy customers, wasted fuel, and overtime costs
- **For Cities:** Inefficient routing increases congestion and pollution
- **For Drivers:** Unpredictable schedules and stressful working conditions

### Why Daily Predictions Work
While real-time apps need minute-by-minute data, publicly available traffic sensors in Bangalore only provide daily summaries. Rather than seeing this as a limitation, BSLO turns it into an advantage: **daily predictions are perfect for day-ahead planning**, which is exactly what logistics managers need.

---

## Research Question

**Can we predict tomorrow's traffic congestion on specific roads in Bangalore using historical daily traffic patterns, weather conditions, and road characteristics?**

More specifically:
1. Which roads will have high congestion next Tuesday?
2. If I have to deliver packages from Indiranagar to Electronic City, which route will have the least traffic tomorrow?
3. How do weather conditions (like rain) affect traffic on different roads?
4. Can we provide route recommendations that minimize both travel time and environmental impact?

---

## Data Sources

### Primary Dataset
**Bangalore City Traffic Dataset** (Preetham Gouda, Kaggle)
- **Size:** 8,936 daily traffic records
- **Time Period:** January 2022 to August 2024 (2.5 years)
- **Coverage:** 8 major areas in Bangalore, 16 key roads/intersections
- **Quality:** No missing values, no duplicates, clean and well-structured

### What the Data Contains
Each record represents one day's traffic on one specific road, including:
- **Location:** Which area and road (e.g., "100 Feet Road in Indiranagar")
- **Date & Time:** Day of week, month, whether it's a holiday
- **Traffic Metrics:** Vehicle count, road capacity usage, congestion level (0-100)
- **Conditions:** Weather (Clear, Rain, Fog, etc.), roadwork activity
- **Environmental:** Air quality index, environmental impact score

### Data Visualization
The data was thoroughly analyzed to understand traffic patterns:
- **Temporal patterns:** Traffic varies by day of week and month
- **Geographic variation:** Some areas consistently have higher congestion
- **Weather impact:** Rain significantly increases congestion
- **Capacity relationship:** Roads operating above 90% capacity show exponential congestion increase

---

## Methodology

### 1. Data Preparation
**What we did:** Cleaned and organized the data to make it suitable for machine learning
- Verified data quality (no missing values, no errors)
- Created additional useful features (e.g., "traffic from 7 days ago" to capture weekly patterns)
- Split data into training set (70% - to teach the model) and test set (30% - to evaluate accuracy)

**Why it matters:** Clean data is the foundation of accurate predictions. We preserved the time order (train on past, test on future) to simulate real-world usage.

### 2. Model Selection
**What we chose:** XGBoost (eXtreme Gradient Boosting) - a powerful machine learning algorithm

**Why XGBoost:**
- Excellent at finding complex patterns in tabular data
- Handles non-linear relationships (e.g., congestion doesn't increase linearly with traffic volume)
- Provides "feature importance" - tells us which factors matter most for predictions
- Industry-proven for similar prediction tasks

**Alternatives considered:** We first tested a simple baseline model (just predicting the average congestion) to establish a performance benchmark.

### 3. Model Training & Tuning
**What we did:** 
- Trained the model on historical data (2022-2023)
- Fine-tuned 50+ different parameter combinations to find the best settings
- Used cross-validation to ensure the model works well on different time periods

**Key parameters optimized:**
- Learning rate (how fast the model learns)
- Tree depth (how complex patterns it can capture)
- Number of trees (how many decision points to use)

### 4. Evaluation Metrics
**How we measure success:**
- **RMSE (Root Mean Squared Error):** Measures average prediction error - lower is better
- **MAE (Mean Absolute Error):** Average difference between predicted and actual congestion
- **R² Score:** How much of the congestion variation the model explains (0-100%)

**Comparison:** We compared XGBoost against the baseline to quantify improvement.

### 5. Feature Importance Analysis
**What we discovered:** The model revealed which factors most influence traffic congestion:
1. **Traffic Volume** (49% importance) - Number of vehicles on the road
2. **Road Capacity Utilization** (31% importance) - How full the road is
3. **Historical patterns** (lag features) - Traffic from previous days/weeks

**Surprising finding:** Weather and roadwork had less impact than expected, suggesting that traffic volume and capacity are the dominant factors.

---

## Results

### Model Performance
**XGBoost achieved 60% improvement over baseline predictions**

| Metric | Baseline Model | XGBoost Model | Improvement |
|--------|---------------|---------------|-------------|
| RMSE | 23.49 | ~9.4 | 60% better |
| MAE | 19.96 | ~7.8 | 61% better |
| R² Score | -0.00 | ~0.84 | Explains 84% of variance |

**What this means in practice:** 
- Baseline: "Tomorrow's congestion will be around 65 ± 20" (very uncertain)
- XGBoost: "Tomorrow's congestion will be around 68 ± 8" (much more precise)

### Key Insights

#### 1. Traffic Volume is King
The single most important factor for predicting congestion is the number of vehicles on the road. This validates the intuitive understanding that more cars = more traffic.

#### 2. Capacity Matters More Than You Think
Roads operating above 90% capacity show exponential congestion increases. A road at 85% capacity might have moderate congestion (50), but at 95% capacity, congestion jumps to 80+.

#### 3. Temporal Patterns are Predictable
Weekly patterns are strong - if a road was congested last Monday, it's likely to be congested this Monday. This makes day-ahead predictions reliable.

#### 4. Geographic Hotspots
Certain areas (like Silk Board Junction, Marathahalli Bridge) consistently show higher congestion, making them prime targets for infrastructure improvements.

### Deployed System Features

The trained model powers a complete application with:

1. **API Endpoints** (for developers/systems):
   - Predict congestion for any road on any future date
   - Compare multiple routes and recommend the best option
   - Find optimal point-to-point routes using graph algorithms

2. **Interactive Dashboard** (for end users):
   - Visual map showing predicted congestion with color coding (green = low, red = high)
   - Sliders to adjust traffic conditions and see "what-if" scenarios
   - Route comparison tool showing distance, congestion, and recommendations
   - Download route plans for fleet managers

3. **Real-World Usability**:
   - Predictions available in under 100 milliseconds
   - Handles 16 roads across 8 major Bangalore areas
   - Supports multiple weather conditions and traffic scenarios

---

## Next Steps

### Immediate Enhancements
1. **Expand Coverage:** Add more roads and areas beyond the current 16 roads
2. **Real-Time Integration:** Combine daily predictions with real-time traffic feeds for hybrid approach
3. **Mobile App:** Create a mobile interface for drivers to check routes on-the-go
4. **Green Routing:** Fully implement environmental impact optimization (currently in beta)

### Future Research Directions
1. **Event Detection:** Incorporate special events (concerts, sports, festivals) that cause unusual traffic
2. **Multi-Modal Transport:** Include public transit, bike lanes, and pedestrian routes
3. **Dynamic Rerouting:** Automatically suggest alternative routes when predictions indicate high congestion
4. **Historical Trend Analysis:** Identify long-term traffic pattern changes to inform infrastructure planning

### Scaling Opportunities
1. **Other Cities:** Adapt the model for other Indian cities with similar data
2. **Fleet Management Integration:** Build APIs for logistics companies to integrate with their dispatch systems
3. **Government Partnership:** Work with Bangalore Traffic Police for official adoption
4. **Commercial Deployment:** Offer as a service to delivery companies, ride-sharing platforms

---

## Outline of Project

### Jupyter Notebooks (Analysis & Model Development)

1. **[Data Exploration & Cleaning](notebooks/01_eda_data_cleaning.ipynb)**
   - Initial data inspection and quality checks
   - Visualization of traffic patterns across time and geography
   - Feature engineering (creating lag features, derived metrics)
   - Correlation analysis to identify key predictors

2. **[Baseline Model Development](notebooks/02_baseline_modeling.ipynb)**
   - Simple baseline model using mean prediction
   - Establishes performance benchmark (RMSE: 23.49, MAE: 19.96)
   - Error analysis by congestion level
   - Sets the bar for improvement

3. **[XGBoost Model Training & Evaluation](notebooks/03_xgboost_modeling.ipynb)**
   - XGBoost model implementation
   - Hyperparameter tuning (50 iterations, 3-fold cross-validation)
   - Performance comparison with baseline (60% improvement)
   - Feature importance analysis
   - Model export for deployment

### Application Code

- **[API Server](src/api.py)** - FastAPI backend serving predictions
- **[Geospatial Routing](src/geospatial.py)** - Graph-based route finding with NetworkX
- **[Interactive Dashboard](app/streamlit_app.py)** - Streamlit web interface
- **[Map Routing Page](app/map_routing.py)** - Visual route planning with Folium maps

### Documentation

- **[Technical README](README_TECHNICAL.md)** - Complete technical documentation
- **[API Documentation](API_DOCUMENTATION.md)** - API endpoints and usage examples

---

## How to Use This Project

### For Non-Technical Users
1. **Access the Dashboard:** Open http://localhost:8501 in your web browser
2. **Select Your Route:** Choose starting point and destination from dropdown menus
3. **Adjust Conditions:** Use sliders to set expected traffic volume and weather
4. **Get Predictions:** Click "Find Best Route" to see congestion predictions and map
5. **Download Plan:** Export the route plan for your delivery team

### For Developers
1. **Install Dependencies:** `pip install -r requirements.txt`
2. **Start Services:** Run `./start_bslo.sh` to launch API and dashboard
3. **API Access:** Use http://localhost:8000/docs for interactive API documentation
4. **Integrate:** Call API endpoints from your logistics management system

### For Researchers
1. **Explore Notebooks:** Review the Jupyter notebooks for methodology details
2. **Reproduce Results:** Run notebooks in order (01 → 02 → 03)
3. **Extend Analysis:** Modify hyperparameters or try different algorithms
4. **Contribute:** Suggest improvements or additional features

---

## Quick Start for Developers

### Installation
```bash
git clone https://github.com/karthikmurs/bslo
cd bslo
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Application
```bash
# Start both API and dashboard with one command
./start_bslo.sh

# Or start manually:
# Terminal 1: uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
# Terminal 2: streamlit run app/streamlit_app.py
```

### Access Points
- **API Documentation:** http://localhost:8000/docs
- **Interactive Dashboard:** http://localhost:8501
- **API Health Check:** http://localhost:8000/health

### Testing
```bash
python src/test_api.py
```

For detailed technical documentation, see [README_TECHNICAL.md](README_TECHNICAL.md).

---

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