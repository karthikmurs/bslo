"""
BSLO API - Bengaluru Strategic Logistics Optimizer
FastAPI application for traffic congestion prediction and route optimization
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, date
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from geospatial import find_route, get_route_summary, ROAD_COORDINATES

app = FastAPI(
    title="BSLO API",
    description="Bengaluru Strategic Logistics Optimizer - Predictive AI for Day-Ahead Route Planning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models and preprocessor
MODEL_DIR = Path(__file__).parent.parent / "models"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"
XGBOOST_MODEL_PATH = MODEL_DIR / "xgboost_tuned.pkl"

# Global variables for loaded models
preprocessor = None
xgboost_model = None

def load_models():
    """Load trained models and preprocessor"""
    global preprocessor, xgboost_model
    
    try:
        with open(PREPROCESSOR_PATH, 'rb') as f:
            preprocessor = pickle.load(f)
        
        with open(XGBOOST_MODEL_PATH, 'rb') as f:
            xgboost_model = pickle.load(f)
        
        print("[OK] Models loaded successfully")
    except Exception as e:
        print(f"Error loading models: {e}")
        raise

# Pydantic models for request/response
class FrictionScoreRequest(BaseModel):
    """Request model for friction score prediction"""
    date: str = Field(..., description="Target date in YYYY-MM-DD format", example="2024-11-25")
    area_name: str = Field(..., description="Area name in Bengaluru", example="Indiranagar")
    road_name: str = Field(..., description="Road/Intersection name", example="100 Feet Road")
    weather_condition: Optional[str] = Field("Clear", description="Weather condition", example="Clear")
    traffic_volume: Optional[int] = Field(30000, description="Expected traffic volume (vehicles/day)", example=30000)
    road_capacity_utilization: Optional[float] = Field(75.0, description="Road capacity utilization (%)", example=75.0)
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-11-25",
                "area_name": "Indiranagar",
                "road_name": "100 Feet Road",
                "weather_condition": "Clear",
                "traffic_volume": 30000,
                "road_capacity_utilization": 75.0
            }
        }

class FrictionScoreResponse(BaseModel):
    """Response model for friction score prediction"""
    date: str
    area_name: str
    road_name: str
    predicted_congestion: float = Field(..., description="Predicted congestion level (0-100)")
    friction_category: str = Field(..., description="Friction category (Low/Medium/High/Very High)")
    weather_condition: str
    traffic_volume: int
    road_capacity_utilization: float
    
class RouteRequest(BaseModel):
    """Request model for route scoring"""
    date: str = Field(..., description="Target date in YYYY-MM-DD format", example="2024-11-25")
    route_name: str = Field(..., description="Route identifier", example="Route 1")
    roads: List[Dict[str, str]] = Field(..., description="List of roads with area and road name")
    weather_condition: Optional[str] = Field("Clear", description="Weather condition")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-11-25",
                "route_name": "City Center Route",
                "roads": [
                    {"area_name": "M.G. Road", "road_name": "Brigade Road"},
                    {"area_name": "Indiranagar", "road_name": "100 Feet Road"},
                    {"area_name": "Koramangala", "road_name": "Hosur Road"}
                ],
                "weather_condition": "Clear"
            }
        }

class RouteResponse(BaseModel):
    """Response model for route scoring"""
    date: str
    route_name: str
    total_friction_score: float
    average_friction: float
    road_count: int
    road_details: List[Dict]
    recommendation: str

class RouteComparisonRequest(BaseModel):
    """Request model for comparing multiple routes"""
    date: str
    routes: List[Dict] = Field(..., description="List of routes to compare")
    weather_condition: Optional[str] = Field("Clear")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-11-25",
                "routes": [
                    {
                        "route_name": "City Center",
                        "roads": [
                            {"area_name": "M.G. Road", "road_name": "Brigade Road"},
                            {"area_name": "Indiranagar", "road_name": "100 Feet Road"}
                        ]
                    },
                    {
                        "route_name": "Ring Road",
                        "roads": [
                            {"area_name": "Hebbal", "road_name": "Hebbal Flyover"},
                            {"area_name": "Whitefield", "road_name": "ITPL Main Road"}
                        ]
                    }
                ],
                "weather_condition": "Clear"
            }
        }

class RouteComparisonResponse(BaseModel):
    """Response model for route comparison"""
    date: str
    routes: List[Dict]
    best_route: str
    worst_route: str
    recommendation: str

# Helper functions
def get_friction_category(congestion: float) -> str:
    """Categorize congestion level into friction categories"""
    if congestion < 25:
        return "Low"
    elif congestion < 50:
        return "Medium"
    elif congestion < 75:
        return "High"
    else:
        return "Very High"

def extract_date_features(date_str: str) -> Dict:
    """Extract temporal features from date string"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return {
        'Month': dt.month,
        'Day_of_Week': dt.weekday(),
        'Is_Weekend': 1 if dt.weekday() >= 5 else 0,
        'Quarter': (dt.month - 1) // 3 + 1,
        'Day_of_Month': dt.day
    }

def create_prediction_input(
    area_name: str,
    road_name: str,
    date_str: str,
    weather: str = "Clear",
    traffic_volume: int = 30000,
    road_capacity_utilization: float = 75.0
) -> pd.DataFrame:
    """Create input DataFrame for prediction"""
    
    # Extract date features
    date_features = extract_date_features(date_str)
    
    # Calculate derived features based on traffic volume and capacity
    speed_volume_ratio = (35.0 / traffic_volume) * 1000  # Inverse relationship
    
    # Create base features
    features = {
        'Area Name': area_name,
        'Road/Intersection Name': road_name,
        'Weather Conditions': weather,
        'Roadwork and Construction Activity': 'No',  # Fixed as it has minimal impact
        'Traffic Volume': traffic_volume,
        'Road Capacity Utilization': road_capacity_utilization,
        'Incident Reports': 1,
        'Public Transport Usage': 50.0,
        'Traffic Signal Compliance': 80.0,
        'Parking Usage': 60.0,
        'Pedestrian and Cyclist Count': 150,
        'Month': date_features['Month'],
        'Day_of_Week': date_features['Day_of_Week'],
        'Is_Weekend': date_features['Is_Weekend'],
        'Quarter': date_features['Quarter'],
        'Day_of_Month': date_features['Day_of_Month'],
        # Lag features (use current values as proxy for historical patterns)
        'Traffic Volume_Lag1': traffic_volume,
        'Traffic Volume_Lag7': traffic_volume,
        'Traffic Volume_Rolling7': traffic_volume,
        'Congestion Level_Lag1': road_capacity_utilization,
        'Congestion Level_Lag7': road_capacity_utilization,
        'Congestion Level_Rolling7': road_capacity_utilization,
        'Average Speed_Lag1': 35.0,
        'Average Speed_Lag7': 35.0,
        'Average Speed_Rolling7': 35.0,
        'Speed_Volume_Ratio': speed_volume_ratio
    }
    
    return pd.DataFrame([features])

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    load_models()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "BSLO API",
        "version": "1.0.0",
        "description": "Bengaluru Strategic Logistics Optimizer",
        "endpoints": {
            "friction_score": "/api/v1/friction-score",
            "route_score": "/api/v1/route-score",
            "route_comparison": "/api/v1/route-comparison",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    models_loaded = preprocessor is not None and xgboost_model is not None
    return {
        "status": "healthy" if models_loaded else "unhealthy",
        "models_loaded": models_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/friction-score", response_model=FrictionScoreResponse)
async def predict_friction_score(request: FrictionScoreRequest):
    """
    Feature A: The "Friction Score" Predictor
    
    Predicts congestion level (0-100) for a specific road on a target date.
    This allows logistics managers to assess the "friction" or difficulty
    of using a particular road segment for future planning.
    
    Key Parameters:
    - Traffic Volume: Expected number of vehicles (20k-50k range)
    - Road Capacity Utilization: How full the road is (50-95% range)
    """
    
    if preprocessor is None or xgboost_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Validate date
        datetime.strptime(request.date, "%Y-%m-%d")
        
        # Create input features
        input_df = create_prediction_input(
            area_name=request.area_name,
            road_name=request.road_name,
            date_str=request.date,
            weather=request.weather_condition,
            traffic_volume=request.traffic_volume,
            road_capacity_utilization=request.road_capacity_utilization
        )
        
        # Preprocess and predict
        input_processed = preprocessor.transform(input_df)
        prediction = xgboost_model.predict(input_processed)[0]
        
        # Ensure prediction is within valid range
        prediction = np.clip(prediction, 0, 100)
        
        return FrictionScoreResponse(
            date=request.date,
            area_name=request.area_name,
            road_name=request.road_name,
            predicted_congestion=round(float(prediction), 2),
            friction_category=get_friction_category(prediction),
            weather_condition=request.weather_condition,
            traffic_volume=request.traffic_volume,
            road_capacity_utilization=request.road_capacity_utilization
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/v1/route-score", response_model=RouteResponse)
async def score_route(request: RouteRequest):
    """
    Feature B: Strategic Route Scoring
    
    Calculates cumulative friction score for a defined route (list of roads).
    Helps logistics managers compare different route options for a target date.
    """
    
    if preprocessor is None or xgboost_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Validate date
        datetime.strptime(request.date, "%Y-%m-%d")
        
        road_predictions = []
        total_friction = 0.0
        
        # Predict friction for each road in the route
        for road in request.roads:
            input_df = create_prediction_input(
                area_name=road['area_name'],
                road_name=road['road_name'],
                date_str=request.date,
                weather=request.weather_condition
            )
            
            input_processed = preprocessor.transform(input_df)
            prediction = float(xgboost_model.predict(input_processed)[0])
            prediction = float(np.clip(prediction, 0, 100))
            
            road_predictions.append({
                'area_name': road['area_name'],
                'road_name': road['road_name'],
                'predicted_congestion': round(prediction, 2),
                'friction_category': get_friction_category(prediction)
            })
            
            total_friction += prediction
        
        avg_friction = total_friction / len(request.roads)
        
        # Generate recommendation
        if avg_friction < 40:
            recommendation = "Excellent route - Low congestion expected"
        elif avg_friction < 60:
            recommendation = "Good route - Moderate congestion expected"
        elif avg_friction < 80:
            recommendation = "Caution - High congestion expected. Consider alternative routes"
        else:
            recommendation = "Not recommended - Very high congestion expected. Seek alternative routes"
        
        return RouteResponse(
            date=request.date,
            route_name=request.route_name,
            total_friction_score=round(total_friction, 2),
            average_friction=round(avg_friction, 2),
            road_count=len(request.roads),
            road_details=road_predictions,
            recommendation=recommendation
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route scoring error: {str(e)}")

@app.post("/api/v1/route-comparison", response_model=RouteComparisonResponse)
async def compare_routes(request: RouteComparisonRequest):
    """
    Compare multiple routes and recommend the best option
    
    Allows logistics managers to evaluate several route alternatives
    and make data-driven decisions about which route to use.
    """
    
    if preprocessor is None or xgboost_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        datetime.strptime(request.date, "%Y-%m-%d")
        
        route_scores = []
        
        # Score each route
        for route in request.routes:
            total_friction = 0.0
            road_details = []
            
            for road in route['roads']:
                input_df = create_prediction_input(
                    area_name=road['area_name'],
                    road_name=road['road_name'],
                    date_str=request.date,
                    weather=request.weather_condition
                )
                
                input_processed = preprocessor.transform(input_df)
                prediction = float(xgboost_model.predict(input_processed)[0])
                prediction = float(np.clip(prediction, 0, 100))
                
                road_details.append({
                    'area_name': road['area_name'],
                    'road_name': road['road_name'],
                    'predicted_congestion': round(prediction, 2)
                })
                
                total_friction += prediction
            
            avg_friction = total_friction / len(route['roads'])
            
            route_scores.append({
                'route_name': route['route_name'],
                'total_friction': round(float(total_friction), 2),
                'average_friction': round(float(avg_friction), 2),
                'road_count': len(route['roads']),
                'roads': road_details
            })
        
        # Find best and worst routes
        best_route = min(route_scores, key=lambda x: x['average_friction'])
        worst_route = max(route_scores, key=lambda x: x['average_friction'])
        
        # Generate recommendation
        friction_diff = worst_route['average_friction'] - best_route['average_friction']
        pct_diff = (friction_diff / worst_route['average_friction']) * 100
        
        recommendation = (
            f"On {request.date}, {best_route['route_name']} is recommended with "
            f"{pct_diff:.1f}% less congestion than {worst_route['route_name']}. "
            f"Average friction: {best_route['average_friction']:.1f} vs {worst_route['average_friction']:.1f}"
        )
        
        return RouteComparisonResponse(
            date=request.date,
            routes=route_scores,
            best_route=best_route['route_name'],
            worst_route=worst_route['route_name'],
            recommendation=recommendation
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

class PointToPointRequest(BaseModel):
    """Request model for point-to-point routing"""
    date: str = Field(..., description="Target date in YYYY-MM-DD format")
    start_road: str = Field(..., description="Starting road name")
    end_road: str = Field(..., description="Destination road name")
    weather_condition: Optional[str] = Field("Clear", description="Weather condition")
    traffic_volume: Optional[int] = Field(30000, description="Expected traffic volume")
    road_capacity_utilization: Optional[float] = Field(92.0, description="Road capacity utilization")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-11-25",
                "start_road": "100 Feet Road",
                "end_road": "Hosur Road",
                "weather_condition": "Clear",
                "traffic_volume": 30000,
                "road_capacity_utilization": 92.0
            }
        }

class PointToPointResponse(BaseModel):
    """Response model for point-to-point routing"""
    date: str
    start_road: str
    end_road: str
    route_found: bool
    route: List[str]
    road_count: int
    total_distance_km: float
    average_congestion: float
    total_congestion_score: float
    road_details: List[Dict]
    recommendation: str

@app.post("/api/v1/point-to-point", response_model=PointToPointResponse)
async def plan_point_to_point_route(request: PointToPointRequest):
    """
    Point-to-Point Route Planning
    
    Find the optimal route from point A to point B and predict congestion
    for each road segment. Uses graph-based routing with NetworkX.
    """
    
    if preprocessor is None or xgboost_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Validate date
        datetime.strptime(request.date, "%Y-%m-%d")
        
        # Find route using graph algorithm
        route = find_route(request.start_road, request.end_road)
        
        if route is None:
            return PointToPointResponse(
                date=request.date,
                start_road=request.start_road,
                end_road=request.end_road,
                route_found=False,
                route=[],
                road_count=0,
                total_distance_km=0.0,
                average_congestion=0.0,
                total_congestion_score=0.0,
                road_details=[],
                recommendation=f"No route found between {request.start_road} and {request.end_road}"
            )
        
        # Predict congestion for each road in the route
        road_details = []
        congestion_data = {}
        
        for road in route:
            # Find area for this road (from ROAD_COORDINATES mapping)
            area = None
            for area_name, roads in [
                ("Indiranagar", ["100 Feet Road", "CMH Road"]),
                ("Whitefield", ["ITPL Main Road", "Marathahalli Bridge"]),
                ("Koramangala", ["Sarjapur Road", "Sony World Junction"]),
                ("M.G. Road", ["Trinity Circle", "Anil Kumble Circle"]),
                ("Jayanagar", ["Jayanagar 4th Block", "South End Circle"]),
                ("Hebbal", ["Hebbal Flyover", "Ballari Road"]),
                ("Yeshwanthpur", ["Tumkur Road", "Yeshwanthpur Circle"]),
                ("Electronic City", ["Hosur Road", "Silk Board Junction"])
            ]:
                if road in roads:
                    area = area_name
                    break
            
            if area:
                # Predict congestion
                input_df = create_prediction_input(
                    area_name=area,
                    road_name=road,
                    date_str=request.date,
                    weather=request.weather_condition,
                    traffic_volume=request.traffic_volume,
                    road_capacity_utilization=request.road_capacity_utilization
                )
                
                input_processed = preprocessor.transform(input_df)
                prediction = float(xgboost_model.predict(input_processed)[0])
                prediction = float(np.clip(prediction, 0, 100))
                
                congestion_data[road] = prediction
                
                road_details.append({
                    'road_name': road,
                    'area_name': area,
                    'predicted_congestion': round(prediction, 2),
                    'friction_category': get_friction_category(prediction),
                    'coordinates': ROAD_COORDINATES.get(road, (0, 0))
                })
        
        # Get route summary
        summary = get_route_summary(route, congestion_data)
        
        # Generate recommendation
        avg_congestion = summary['average_congestion']
        if avg_congestion < 40:
            recommendation = f"Excellent route! Low congestion expected. Estimated distance: {summary['total_distance_km']} km"
        elif avg_congestion < 60:
            recommendation = f"Good route with moderate congestion. Estimated distance: {summary['total_distance_km']} km"
        elif avg_congestion < 80:
            recommendation = f"Caution: High congestion expected on this route. Consider alternative times or routes."
        else:
            recommendation = f"Warning: Very high congestion expected. Strongly recommend alternative route or time."
        
        return PointToPointResponse(
            date=request.date,
            start_road=request.start_road,
            end_road=request.end_road,
            route_found=True,
            route=route,
            road_count=summary['road_count'],
            total_distance_km=summary['total_distance_km'],
            average_congestion=summary['average_congestion'],
            total_congestion_score=summary['total_congestion_score'],
            road_details=road_details,
            recommendation=recommendation
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")

@app.get("/api/v1/available-roads")
async def get_available_roads():
    """Get list of all available roads for routing"""
    return {
        "roads": sorted(list(ROAD_COORDINATES.keys())),
        "total_count": len(ROAD_COORDINATES)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
