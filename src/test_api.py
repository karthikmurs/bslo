"""
Test script for BSLO API
Demonstrates all three core features with example requests
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_health_check():
    """Test health check endpoint"""
    print_section("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_friction_score():
    """Test Feature A: Friction Score Predictor"""
    print_section("Feature A: Friction Score Predictor")
    
    # Test case 1: Indiranagar on a weekday
    payload = {
        "date": "2024-11-25",
        "area_name": "Indiranagar",
        "road_name": "100 Feet Road",
        "weather_condition": "Clear",
        "roadwork": "No"
    }
    
    print("\nRequest:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/v1/friction-score", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))
    
    # Test case 2: M.G. Road with rain
    payload2 = {
        "date": "2024-11-25",
        "area_name": "M.G. Road",
        "road_name": "Brigade Road",
        "weather_condition": "Rain",
        "roadwork": "Yes"
    }
    
    print("\n" + "-" * 70)
    print("\nRequest (Rain + Roadwork):")
    print(json.dumps(payload2, indent=2))
    
    response2 = requests.post(f"{BASE_URL}/api/v1/friction-score", json=payload2)
    print(f"\nStatus Code: {response2.status_code}")
    print("\nResponse:")
    print(json.dumps(response2.json(), indent=2))

def test_route_scoring():
    """Test Feature B: Strategic Route Scoring"""
    print_section("Feature B: Strategic Route Scoring")
    
    # City Center Route
    payload = {
        "date": "2024-11-25",
        "route_name": "City Center Route",
        "roads": [
            {"area_name": "M.G. Road", "road_name": "Brigade Road"},
            {"area_name": "Indiranagar", "road_name": "100 Feet Road"},
            {"area_name": "Koramangala", "road_name": "Hosur Road"}
        ],
        "weather_condition": "Clear"
    }
    
    print("\nRequest:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/v1/route-score", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))

def test_route_comparison():
    """Test Feature B Extended: Route Comparison"""
    print_section("Feature B Extended: Route Comparison")
    
    payload = {
        "date": "2024-11-25",
        "routes": [
            {
                "route_name": "City Center Route",
                "roads": [
                    {"area_name": "M.G. Road", "road_name": "Brigade Road"},
                    {"area_name": "Indiranagar", "road_name": "100 Feet Road"},
                    {"area_name": "Koramangala", "road_name": "Hosur Road"}
                ]
            },
            {
                "route_name": "Ring Road Route",
                "roads": [
                    {"area_name": "Hebbal", "road_name": "Hebbal Flyover"},
                    {"area_name": "Whitefield", "road_name": "ITPL Main Road"},
                    {"area_name": "Koramangala", "road_name": "Silk Board Junction"}
                ]
            },
            {
                "route_name": "Outer Route",
                "roads": [
                    {"area_name": "Yeshwanthpur", "road_name": "Tumkur Road"},
                    {"area_name": "Hebbal", "road_name": "Ballari Road"},
                    {"area_name": "Whitefield", "road_name": "Marathahalli Bridge"}
                ]
            }
        ],
        "weather_condition": "Clear"
    }
    
    print("\nRequest:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/v1/route-comparison", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))

def main():
    """Run all API tests"""
    print("\n" + "=" * 70)
    print("  BSLO API Test Suite")
    print("  Bengaluru Strategic Logistics Optimizer")
    print("=" * 70)
    
    try:
        # Test health check
        test_health_check()
        
        # Test Feature A: Friction Score Predictor
        test_friction_score()
        
        # Test Feature B: Strategic Route Scoring
        test_route_scoring()
        
        # Test Route Comparison
        test_route_comparison()
        
        print("\n" + "=" * 70)
        print("  All tests completed successfully!")
        print("=" * 70 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Please ensure the API server is running:")
        print("  python src/api.py")
        print("  or")
        print("  uvicorn src.api:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
