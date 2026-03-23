# BSLO API Documentation

## Overview

The BSLO (Bengaluru Strategic Logistics Optimizer) API provides four core features for traffic congestion prediction and route optimization:

1. **Friction Score Predictor** - Predict congestion for individual roads
2. **Strategic Route Scoring** - Calculate cumulative friction for defined routes
3. **Route Comparison** - Compare multiple routes and recommend the best option
4. **Point-to-Point Route Planning** - Find optimal routes with interactive map visualization

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Option 1: Direct Python
python src/api.py

# Option 2: Using Uvicorn (recommended for development)
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 3. Access Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Run the Streamlit Dashboard

```bash
streamlit run app/streamlit_app.py
```

The dashboard will open in your browser at: `http://localhost:8501`

## API Endpoints

### Health Check

**GET** `/health`

Check if the API server and models are loaded.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "timestamp": "2024-11-25T10:30:00"
}
```

---

## Feature A: Friction Score Predictor

**POST** `/api/v1/friction-score`

Predicts congestion level (0-100) for a specific road on a target date.

### Request Body

```json
{
  "date": "2024-11-25",
  "area_name": "Indiranagar",
  "road_name": "100 Feet Road",
  "weather_condition": "Clear",
  "traffic_volume": 30000,
  "road_capacity_utilization": 92.0
}
```

### Parameters

| Field | Type | Required | Description | Options/Range |
|-------|------|----------|-------------|---------------|
| `date` | string | Yes | Target date (YYYY-MM-DD) | Future date |
| `area_name` | string | Yes | Area in Bengaluru | Indiranagar, Whitefield, Koramangala, M.G. Road, Jayanagar, Hebbal, Yeshwanthpur, Electronic City |
| `road_name` | string | Yes | Road/Intersection name | Varies by area |
| `weather_condition` | string | No | Weather condition (default: Clear) | Clear, Rain, Overcast, Fog, Windy |
| `traffic_volume` | integer | No | Expected traffic volume (default: 30000) | 5,000 - 70,000 vehicles/day |
| `road_capacity_utilization` | float | No | Road capacity utilization (default: 92.0) | 20.0 - 100.0 % |

### Response

```json
{
  "date": "2024-11-25",
  "area_name": "Indiranagar",
  "road_name": "100 Feet Road",
  "predicted_congestion": 78.45,
  "friction_category": "Very High",
  "weather_condition": "Clear",
  "traffic_volume": 30000,
  "road_capacity_utilization": 92.0
}
```

### Friction Categories

- **Low**: 0-25 (Green)
- **Medium**: 25-50 (Yellow)
- **High**: 50-75 (Orange)
- **Very High**: 75-100 (Red)

### Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/friction-score" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-11-25",
    "area_name": "Indiranagar",
    "road_name": "100 Feet Road",
    "weather_condition": "Clear",
    "traffic_volume": 30000,
    "road_capacity_utilization": 92.0
  }'
```

---

## Feature B: Strategic Route Scoring

**POST** `/api/v1/route-score`

Calculates cumulative friction score for a defined route (list of roads).

### Request Body

```json
{
  "date": "2024-11-25",
  "route_name": "City Center Route",
  "roads": [
    {"area_name": "M.G. Road", "road_name": "Brigade Road"},
    {"area_name": "Indiranagar", "road_name": "100 Feet Road"},
    {"area_name": "Koramangala", "road_name": "Hosur Road"}
  ],
  "weather_condition": "Clear"
}
```

### Response

```json
{
  "date": "2024-11-25",
  "route_name": "City Center Route",
  "total_friction_score": 234.56,
  "average_friction": 78.19,
  "road_count": 3,
  "road_details": [
    {
      "area_name": "M.G. Road",
      "road_name": "Brigade Road",
      "predicted_congestion": 82.34,
      "friction_category": "Very High"
    },
    {
      "area_name": "Indiranagar",
      "road_name": "100 Feet Road",
      "predicted_congestion": 76.45,
      "friction_category": "Very High"
    },
    {
      "area_name": "Koramangala",
      "road_name": "Hosur Road",
      "predicted_congestion": 75.77,
      "friction_category": "Very High"
    }
  ],
  "recommendation": "Not recommended - Very high congestion expected. Seek alternative routes"
}
```

### Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/route-score" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-11-25",
    "route_name": "City Center Route",
    "roads": [
      {"area_name": "M.G. Road", "road_name": "Brigade Road"},
      {"area_name": "Indiranagar", "road_name": "100 Feet Road"}
    ],
    "weather_condition": "Clear"
  }'
```

---

## Feature B Extended: Route Comparison

**POST** `/api/v1/route-comparison`

Compare multiple routes and recommend the best option.

### Request Body

```json
{
  "date": "2024-11-25",
  "routes": [
    {
      "route_name": "City Center Route",
      "roads": [
        {"area_name": "M.G. Road", "road_name": "Brigade Road"},
        {"area_name": "Indiranagar", "road_name": "100 Feet Road"}
      ]
    },
    {
      "route_name": "Ring Road Route",
      "roads": [
        {"area_name": "Hebbal", "road_name": "Hebbal Flyover"},
        {"area_name": "Whitefield", "road_name": "ITPL Main Road"}
      ]
    }
  ],
  "weather_condition": "Clear"
}
```

### Response

```json
{
  "date": "2024-11-25",
  "routes": [
    {
      "route_name": "City Center Route",
      "total_friction": 158.79,
      "average_friction": 79.40,
      "road_count": 2,
      "roads": [...]
    },
    {
      "route_name": "Ring Road Route",
      "total_friction": 145.23,
      "average_friction": 72.62,
      "road_count": 2,
      "roads": [...]
    }
  ],
  "best_route": "Ring Road Route",
  "worst_route": "City Center Route",
  "recommendation": "On 2024-11-25, Ring Road Route is recommended with 8.5% less congestion than City Center Route. Average friction: 72.6 vs 79.4"
}
```

---

## Testing the API

### Using the Test Script

```bash
python src/test_api.py
```

This will run comprehensive tests for all three features.

### Using Python Requests

```python
import requests

# Feature A: Friction Score
response = requests.post(
    "http://localhost:8000/api/v1/friction-score",
    json={
        "date": "2024-11-25",
        "area_name": "Indiranagar",
        "road_name": "100 Feet Road",
        "weather_condition": "Clear",
        "traffic_volume": 30000,
        "road_capacity_utilization": 92.0
    }
)
print(response.json())
```

---

## Available Areas and Roads

### Areas
- Indiranagar
- Whitefield
- Koramangala
- M.G. Road
- Jayanagar
- Hebbal
- Yeshwanthpur
- Electronic City

### Roads by Area

**Indiranagar:**
- 100 Feet Road
- CMH Road

**Whitefield:**
- ITPL Main Road
- Marathahalli Bridge

**Koramangala:**
- Sarjapur Road
- Sony World Junction

**M.G. Road:**
- Trinity Circle
- Anil Kumble Circle

**Jayanagar:**
- Jayanagar 4th Block
- South End Circle

**Hebbal:**
- Hebbal Flyover
- Ballari Road

**Yeshwanthpur:**
- Tumkur Road
- Yeshwanthpur Circle

**Electronic City:**
- Hosur Road
- Silk Board Junction

---

## Feature D: Point-to-Point Route Planning

**POST** `/api/v1/point-to-point`

Find the optimal route from point A to point B using graph-based routing with congestion predictions.

### Request Body

```json
{
  "date": "2024-11-25",
  "start_road": "100 Feet Road",
  "end_road": "Hosur Road",
  "weather_condition": "Clear",
  "traffic_volume": 30000,
  "road_capacity_utilization": 92.0
}
```

### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | Yes | Target date (YYYY-MM-DD) |
| `start_road` | string | Yes | Starting road name |
| `end_road` | string | Yes | Destination road name |
| `weather_condition` | string | No | Weather condition (default: Clear) |
| `traffic_volume` | integer | No | Expected traffic volume (default: 30000) |
| `road_capacity_utilization` | float | No | Road capacity utilization (default: 92.0) |

### Response

```json
{
  "date": "2024-11-25",
  "start_road": "100 Feet Road",
  "end_road": "Hosur Road",
  "route_found": true,
  "route": ["100 Feet Road", "Sony World Junction", "Silk Board Junction", "Hosur Road"],
  "road_count": 4,
  "total_distance_km": 12.5,
  "average_congestion": 65.3,
  "total_congestion_score": 261.2,
  "road_details": [
    {
      "road_name": "100 Feet Road",
      "area_name": "Indiranagar",
      "predicted_congestion": 68.2,
      "friction_category": "High",
      "coordinates": [12.9698, 77.6410]
    },
    {
      "road_name": "Sony World Junction",
      "area_name": "Koramangala",
      "predicted_congestion": 72.1,
      "friction_category": "High",
      "coordinates": [12.9343, 77.6270]
    }
  ],
  "recommendation": "Good route with moderate congestion. Estimated distance: 12.5 km"
}
```

### Features

- **Graph-Based Routing:** Uses NetworkX with Dijkstra's algorithm to find shortest path
- **Congestion Prediction:** Predicts congestion for each road segment in the route
- **Distance Calculation:** Uses Haversine formula for accurate distance measurement
- **Interactive Visualization:** Returns coordinates for map rendering
- **Color-Coded Categories:** Low (Green), Medium (Yellow), High (Orange), Very High (Red)

### Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/point-to-point" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-11-25",
    "start_road": "100 Feet Road",
    "end_road": "Hosur Road",
    "weather_condition": "Clear",
    "traffic_volume": 30000,
    "road_capacity_utilization": 92.0
  }'
```

### Available Roads Endpoint

**GET** `/api/v1/available-roads`

Get list of all available roads for routing.

**Response:**
```json
{
  "roads": [
    "100 Feet Road",
    "Anil Kumble Circle",
    "Ballari Road",
    "CMH Road",
    "Hebbal Flyover",
    "Hosur Road",
    "ITPL Main Road",
    "Jayanagar 4th Block",
    "Marathahalli Bridge",
    "Sarjapur Road",
    "Silk Board Junction",
    "Sony World Junction",
    "South End Circle",
    "Trinity Circle",
    "Tumkur Road",
    "Yeshwanthpur Circle"
  ],
  "total_count": 16
}
```

---

## Predefined Routes

### Route 1: City Center
- M.G. Road - Trinity Circle
- Indiranagar - 100 Feet Road
- Electronic City - Hosur Road

### Route 2: Ring Road
- Hebbal - Hebbal Flyover
- Whitefield - ITPL Main Road
- Electronic City - Silk Board Junction

### Route 3: Outer Route
- Yeshwanthpur - Tumkur Road
- Hebbal - Ballari Road
- Whitefield - Marathahalli Bridge

---

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid input (e.g., wrong date format)
- **500 Internal Server Error**: Prediction error
- **503 Service Unavailable**: Models not loaded

### Example Error Response

```json
{
  "detail": "Invalid date format: Date must be in YYYY-MM-DD format"
}
```

---

## Use Cases

### 1. Day-Ahead Fleet Planning
Logistics managers can predict congestion for tomorrow and allocate vehicles accordingly.

```bash
# Check if Route A is better than Route B for tomorrow
curl -X POST "http://localhost:8000/api/v1/route-comparison" \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-11-26", "routes": [...]}'
```

### 2. Weather Impact Analysis
Understand how rain affects specific roads.

```bash
# Compare Clear vs Rain conditions
curl -X POST "http://localhost:8000/api/v1/friction-score" \
  -d '{"date": "2024-11-25", "weather_condition": "Rain", ...}'
```

### 3. Infrastructure Planning
Urban planners can identify high-congestion areas for infrastructure improvements.

---

## Architecture

```
BSLO System Architecture
│
├── FastAPI Server (src/api.py)
│   ├── Load XGBoost Model
│   ├── Load Preprocessor
│   └── Serve Predictions
│
├── Streamlit Dashboard (app/streamlit_app.py)
│   ├── Interactive UI
│   ├── What-If Simulator
│   └── Route Visualization
│
└── Models (models/)
    ├── xgboost_tuned.pkl
    └── preprocessor.pkl
```

---

## Performance

- **Prediction Latency**: < 100ms per road
- **Route Scoring**: < 500ms for 3-road route
- **Concurrent Requests**: Supports multiple simultaneous predictions

---

## Future Enhancements

1. **Feature C: Green Corridor Selector** (Environmental Impact optimization)
2. **Real-time Traffic Integration**
3. **Historical Trend Analysis**
4. **Mobile App Integration**
5. **Fleet Management Dashboard**

---

## Dashboard Features

The Streamlit dashboard (`http://localhost:8501`) provides:

1. **Friction Score Predictor** - Interactive form for single road predictions
2. **Route Comparison** - Compare multiple predefined routes
3. **Map-Based Routing** - Visual point-to-point route planning with interactive maps
4. **What-If Simulator** - Explore how traffic conditions affect predictions

### Map-Based Routing Features

- **Interactive Map:** Folium-based visualization with color-coded congestion
- **Route Planning:** Select start and end points from dropdown menus
- **Traffic Conditions:** Adjust traffic volume and road capacity with sliders
- **Real-time Predictions:** See congestion predictions for each road segment
- **Export:** Download route plans as text files

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

**Quick Links:**
- **API Documentation:** http://localhost:8000/docs
- **Interactive Dashboard:** http://localhost:8501
- **Project Overview:** [README.md](README.md)
- **Technical Documentation:** [README_TECHNICAL.md](README_TECHNICAL.md)

---

**Last Updated:** March 2026  
**Version:** 1.0
