"""
Map-based routing page for BSLO Streamlit dashboard
Provides interactive point-to-point route planning with map visualization
"""

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import geospatial module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from geospatial import create_route_map, ROAD_COORDINATES, BANGALORE_CENTER

API_BASE_URL = "http://localhost:8000"

def get_available_roads():
    """Get list of available roads from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/available-roads")
        if response.status_code == 200:
            return response.json()["roads"]
        return list(ROAD_COORDINATES.keys())
    except:
        return list(ROAD_COORDINATES.keys())

def plan_route(date, start_road, end_road, weather, traffic_volume, road_capacity):
    """Call point-to-point routing API"""
    payload = {
        "date": date,
        "start_road": start_road,
        "end_road": end_road,
        "weather_condition": weather,
        "traffic_volume": traffic_volume,
        "road_capacity_utilization": road_capacity
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/point-to-point", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def show_map_routing_page():
    """Display the map-based routing page"""
    
    st.header("🗺️ Point-to-Point Route Planning")
    st.markdown("Plan your route from point A to point B with real-time congestion predictions")
    
    # Check API health
    api_available = False
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health.status_code == 200:
            api_available = True
            st.success("✅ API Server Connected")
        else:
            st.warning("⚠️ API Server is not responding properly")
    except Exception as e:
        st.warning("⚠️ API Server is not running. Start it to enable route planning.")
        st.code("uvicorn src.api:app --reload", language="bash")
    
    try:
        # Get available roads
        available_roads = get_available_roads()
        
        if not available_roads:
            st.error("No roads available. Check if ROAD_COORDINATES is loaded properly.")
            return
        
        st.write(f"Debug: {len(available_roads)} roads loaded")  # Debug line
        
        # Input section
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📍 Route Details")
            
            target_date = st.date_input(
                "Target Date",
                value=datetime.now() + timedelta(days=1),
                min_value=datetime.now().date()
            )
            
            start_road = st.selectbox(
                "Starting Point (Road)",
                available_roads,
                index=available_roads.index("100 Feet Road") if "100 Feet Road" in available_roads else 0,
                help="Select your starting road"
            )
            
            end_road = st.selectbox(
                "Destination (Road)",
                available_roads,
                index=available_roads.index("Hosur Road") if "Hosur Road" in available_roads else min(5, len(available_roads)-1),
                help="Select your destination road"
            )
            
            weather = st.selectbox(
                "Weather Condition",
                ["Clear", "Rain", "Overcast", "Fog", "Windy"]
            )
        
        with col2:
            st.subheader("🚗 Traffic Conditions")
            
            traffic_volume = st.slider(
                "Expected Traffic Volume (vehicles/day)",
                min_value=5000,
                max_value=70000,
                value=29000,
                step=5000,
                help="Adjust expected traffic volume"
            )
            
            road_capacity = st.slider(
                "Road Capacity Utilization (%)",
                min_value=20.0,
                max_value=100.0,
                value=92.0,
                step=5.0,
                help="Adjust road capacity utilization"
            )
            
            st.info(f"📊 **Route Info**\n\n"
                    f"From: {start_road}\n\n"
                    f"To: {end_road}\n\n"
                    f"Date: {target_date.strftime('%Y-%m-%d')}")
        
        # Initialize session state for results
        if 'route_result' not in st.session_state:
            st.session_state.route_result = None
        
        # Plan route button
        if st.button("🔍 Find Best Route", type="primary", use_container_width=True):
            if start_road == end_road:
                st.warning("⚠️ Start and end roads must be different!")
                st.session_state.route_result = None
            else:
                with st.spinner("Planning route and predicting congestion..."):
                    result = plan_route(
                        date=target_date.strftime("%Y-%m-%d"),
                        start_road=start_road,
                        end_road=end_road,
                        weather=weather,
                        traffic_volume=traffic_volume,
                        road_capacity=road_capacity
                    )
                    st.session_state.route_result = result
        
        # Display results from session state
        if st.session_state.route_result:
            result = st.session_state.route_result
            if not result['route_found']:
                st.error(f"❌ {result['recommendation']}")
                st.info("💡 Try selecting different start/end points that are connected in the road network.")
            else:
                # Success - show results
                st.success("✅ Route found!")
                
                # Display recommendation
                avg_cong = result['average_congestion']
                if avg_cong < 40:
                    st.success(f"🟢 {result['recommendation']}")
                elif avg_cong < 60:
                    st.info(f"🟡 {result['recommendation']}")
                elif avg_cong < 80:
                    st.warning(f"🟠 {result['recommendation']}")
                else:
                    st.error(f"🔴 {result['recommendation']}")
                
                # Route summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Roads in Route", result['road_count'])
                
                with col2:
                    st.metric("Total Distance", f"{result['total_distance_km']} km")
                
                with col3:
                    st.metric("Avg Congestion", f"{result['average_congestion']:.1f}")
                
                with col4:
                    category = "Low" if avg_cong < 25 else "Medium" if avg_cong < 50 else "High" if avg_cong < 75 else "Very High"
                    st.metric("Category", category)
                
                # Create and display map
                st.subheader("🗺️ Route Visualization")
                
                # Extract congestion data for map
                congestion_data = {
                    road['road_name']: road['predicted_congestion']
                    for road in result['road_details']
                }
                
                # Create map
                route_map = create_route_map(
                    route=result['route'],
                    congestion_data=congestion_data,
                    center=BANGALORE_CENTER
                )
                
                # Display map in Streamlit
                st_folium(route_map, width=800, height=500)
                            
                # Road-by-road breakdown
                st.subheader("📋 Road-by-Road Breakdown")
                
                for i, road_detail in enumerate(result['road_details'], 1):
                    with st.expander(f"Stop {i}: {road_detail['road_name']} ({road_detail['area_name']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Predicted Congestion:** {road_detail['predicted_congestion']:.1f}")
                            st.write(f"**Category:** {road_detail['friction_category']}")
                        
                        with col2:
                            coords = road_detail.get('coordinates', (0, 0))
                            st.write(f"**Coordinates:** {coords[0]:.4f}, {coords[1]:.4f}")
                            st.write(f"**Area:** {road_detail['area_name']}")
                            
                # Export option
                st.subheader("💾 Export Route")
                
                route_text = f"""
BSLO Route Plan
===============
Date: {result['date']}
From: {result['start_road']}
To: {result['end_road']}

Route Summary:
- Total Roads: {result['road_count']}
- Total Distance: {result['total_distance_km']} km
- Average Congestion: {result['average_congestion']:.1f}
- Recommendation: {result['recommendation']}

Route Path:
{' → '.join(result['route'])}

Detailed Breakdown:
"""
                for i, road in enumerate(result['road_details'], 1):
                    route_text += f"\n{i}. {road['road_name']} ({road['area_name']})"
                    route_text += f"\n   Congestion: {road['predicted_congestion']:.1f} - {road['friction_category']}"
                
                st.download_button(
                    label="📥 Download Route Plan",
                    data=route_text,
                    file_name=f"bslo_route_{target_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

    except Exception as e:
        st.error(f"Error rendering page: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    show_map_routing_page()
