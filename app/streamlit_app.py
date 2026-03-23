"""
BSLO Streamlit Dashboard
Interactive "What-If" Simulator for Traffic Congestion Prediction
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add map routing module path
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="BSLO - Traffic Optimizer",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Predefined routes based on capstone document
PREDEFINED_ROUTES = {
    "City Center Route": [
        {"area_name": "M.G. Road", "road_name": "Brigade Road"},
        {"area_name": "Indiranagar", "road_name": "100 Feet Road"},
        {"area_name": "Koramangala", "road_name": "Hosur Road"}
    ],
    "Ring Road Route": [
        {"area_name": "Hebbal", "road_name": "Hebbal Flyover"},
        {"area_name": "Whitefield", "road_name": "ITPL Main Road"},
        {"area_name": "Koramangala", "road_name": "Silk Board Junction"}
    ],
    "Outer Route": [
        {"area_name": "Yeshwanthpur", "road_name": "Tumkur Road"},
        {"area_name": "Hebbal", "road_name": "Ballari Road"},
        {"area_name": "Whitefield", "road_name": "Marathahalli Bridge"}
    ]
}

AREAS = [
    "Indiranagar", "Whitefield", "Koramangala", "M.G. Road", 
    "Jayanagar", "Hebbal", "Yeshwanthpur", "Electronic City"
]

ROADS = {
    "Indiranagar": ["100 Feet Road", "CMH Road"],
    "Whitefield": ["ITPL Main Road", "Marathahalli Bridge"],
    "Koramangala": ["Hosur Road", "Sarjapur Road", "Silk Board Junction"],
    "M.G. Road": ["Brigade Road", "Trinity Circle"],
    "Jayanagar": ["Jayanagar 4th Block", "South End Circle"],
    "Hebbal": ["Hebbal Flyover", "Ballari Road"],
    "Yeshwanthpur": ["Tumkur Road", "Yeshwanthpur Circle"],
    "Electronic City": ["Hosur Road"]
}

WEATHER_CONDITIONS = ["Clear", "Rain", "Overcast", "Fog", "Windy"]

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .friction-low {
        color: #28a745;
        font-weight: bold;
    }
    .friction-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .friction-high {
        color: #fd7e14;
        font-weight: bold;
    }
    .friction-very-high {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_friction_color(friction):
    """Get color based on friction level"""
    if friction < 25:
        return "#28a745"  # Green
    elif friction < 50:
        return "#ffc107"  # Yellow
    elif friction < 75:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red

def predict_friction_score(date, area, road, weather, traffic_volume, road_capacity):
    """Call friction score API"""
    payload = {
        "date": date,
        "area_name": area,
        "road_name": road,
        "weather_condition": weather,
        "traffic_volume": traffic_volume,
        "road_capacity_utilization": road_capacity
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/friction-score", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def compare_routes(date, routes, weather):
    """Call route comparison API"""
    payload = {
        "date": date,
        "routes": routes,
        "weather_condition": weather
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/v1/route-comparison", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">🚦 BSLO - Bengaluru Strategic Logistics Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Predictive AI for Day-Ahead Route Planning</div>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ API Server is not running. Please start the API server first:")
        st.code("python src/api.py", language="bash")
        st.stop()
    
    st.success("✅ API Server Connected")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Feature",
        ["Friction Score Predictor", "Route Comparison", "Map-Based Routing", "What-If Simulator"]
    )
    
    # Feature A: Friction Score Predictor
    if page == "Friction Score Predictor":
        st.header("Feature A: Friction Score Predictor")
        st.markdown("Predict congestion level (0-100) for a specific road on a target date")
        st.info("💡 **Tip:** Adjust Traffic Volume and Road Capacity to see how congestion changes!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_date = st.date_input(
                "Target Date",
                value=datetime.now() + timedelta(days=1),
                min_value=datetime.now().date()
            )
            
            area = st.selectbox("Select Area", AREAS)
            road = st.selectbox("Select Road", ROADS.get(area, []))
            
            weather = st.selectbox("Weather Condition", WEATHER_CONDITIONS)
        
        with col2:
            st.subheader("Traffic Conditions")
            
            traffic_volume = st.slider(
                "Expected Traffic Volume (vehicles/day)",
                min_value=5000,
                max_value=70000,
                value=29000,
                step=5000,
                help="Higher traffic volume increases congestion (49% model importance). Range: 5k-70k"
            )
            
            road_capacity = st.slider(
                "Road Capacity Utilization (%)",
                min_value=20.0,
                max_value=100.0,
                value=92.0,
                step=5.0,
                help="Higher capacity utilization means more congestion (33% model importance). Typical: 92%"
            )
        
        if st.button("Predict Friction Score", type="primary"):
            with st.spinner("Predicting..."):
                result = predict_friction_score(
                    date=target_date.strftime("%Y-%m-%d"),
                    area=area,
                    road=road,
                    weather=weather,
                    traffic_volume=traffic_volume,
                    road_capacity=road_capacity
                )
                
                if result:
                    st.success("Prediction Complete!")
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Predicted Congestion",
                            f"{result['predicted_congestion']:.1f}",
                            delta=None
                        )
                    
                    with col2:
                        category = result['friction_category']
                        st.metric("Friction Category", category)
                    
                    with col3:
                        st.metric("Date", result['date'])
                    
                    # Gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=result['predicted_congestion'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Congestion Level"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': get_friction_color(result['predicted_congestion'])},
                            'steps': [
                                {'range': [0, 25], 'color': "lightgreen"},
                                {'range': [25, 50], 'color': "lightyellow"},
                                {'range': [50, 75], 'color': "orange"},
                                {'range': [75, 100], 'color': "lightcoral"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Recommendation
                    if result['predicted_congestion'] < 40:
                        st.success("✅ Excellent conditions - Low congestion expected")
                    elif result['predicted_congestion'] < 60:
                        st.info("ℹ️ Moderate conditions - Plan accordingly")
                    elif result['predicted_congestion'] < 80:
                        st.warning("⚠️ High congestion expected - Consider alternatives")
                    else:
                        st.error("🚫 Very high congestion - Avoid if possible")
    
    # Feature B: Route Comparison
    elif page == "Route Comparison":
        st.header("Feature B: Strategic Route Scoring")
        st.markdown("Compare multiple routes and find the optimal path for your delivery fleet")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            target_date = st.date_input(
                "Target Date",
                value=datetime.now() + timedelta(days=1),
                min_value=datetime.now().date()
            )
            
            weather = st.selectbox("Weather Condition", WEATHER_CONDITIONS)
            
            selected_routes = st.multiselect(
                "Select Routes to Compare",
                list(PREDEFINED_ROUTES.keys()),
                default=list(PREDEFINED_ROUTES.keys())[:2]
            )
        
        with col2:
            st.subheader("Route Details")
            for route_name in selected_routes:
                with st.expander(f"📍 {route_name}"):
                    roads = PREDEFINED_ROUTES[route_name]
                    for i, road in enumerate(roads, 1):
                        st.write(f"{i}. {road['area_name']} - {road['road_name']}")
        
        if st.button("Compare Routes", type="primary"):
            if len(selected_routes) < 2:
                st.warning("Please select at least 2 routes to compare")
            else:
                with st.spinner("Analyzing routes..."):
                    routes_payload = [
                        {
                            "route_name": name,
                            "roads": PREDEFINED_ROUTES[name]
                        }
                        for name in selected_routes
                    ]
                    
                    result = compare_routes(
                        date=target_date.strftime("%Y-%m-%d"),
                        routes=routes_payload,
                        weather=weather
                    )
                    
                    if result:
                        st.success("Analysis Complete!")
                        
                        # Display recommendation
                        st.info(f"📊 {result['recommendation']}")
                        
                        # Create comparison chart
                        route_data = pd.DataFrame(result['routes'])
                        
                        fig = go.Figure()
                        
                        colors = [get_friction_color(row['average_friction']) for _, row in route_data.iterrows()]
                        
                        fig.add_trace(go.Bar(
                            x=route_data['route_name'],
                            y=route_data['average_friction'],
                            marker_color=colors,
                            text=route_data['average_friction'].round(1),
                            textposition='auto',
                        ))
                        
                        fig.update_layout(
                            title="Average Friction Score by Route",
                            xaxis_title="Route",
                            yaxis_title="Average Friction Score",
                            yaxis_range=[0, 100],
                            showlegend=False,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Detailed breakdown
                        st.subheader("Detailed Route Analysis")
                        
                        for route in result['routes']:
                            with st.expander(f"📍 {route['route_name']} - Avg Friction: {route['average_friction']:.1f}"):
                                road_df = pd.DataFrame(route['roads'])
                                st.dataframe(road_df, use_container_width=True)
                                
                                # Mini chart for this route
                                fig_mini = px.bar(
                                    road_df,
                                    x='road_name',
                                    y='predicted_congestion',
                                    color='predicted_congestion',
                                    color_continuous_scale=['green', 'yellow', 'orange', 'red'],
                                    range_color=[0, 100],
                                    title=f"Congestion by Road Segment"
                                )
                                st.plotly_chart(fig_mini, use_container_width=True)
    
    # Feature: Map-Based Routing
    elif page == "Map-Based Routing":
        # Dynamic import to ensure latest code is loaded
        import importlib
        import map_routing
        importlib.reload(map_routing)
        map_routing.show_map_routing_page()
    
    # Feature C: What-If Simulator
    elif page == "What-If Simulator":
        st.header("What-If Simulator")
        st.markdown("Explore how different traffic conditions affect congestion predictions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_date = st.date_input(
                "Target Date",
                value=datetime.now() + timedelta(days=1),
                min_value=datetime.now().date()
            )
            
            area = st.selectbox("Select Area", AREAS, key="sim_area")
            road = st.selectbox("Select Road", ROADS.get(area, []), key="sim_road")
            
            weather = st.selectbox("Weather Condition", WEATHER_CONDITIONS, key="sim_weather")
        
        with col2:
            st.subheader("Scenario Variables")
            
            st.markdown("**Traffic Volume Scenarios**")
            traffic_scenarios = st.multiselect(
                "Select Traffic Volumes to Test",
                ["Very Low (10k)", "Low (20k)", "Normal (29k)", "High (45k)", "Peak (65k)"],
                default=["Low (20k)", "Normal (29k)", "High (45k)"]
            )
            
            st.markdown("**Road Capacity Scenarios**")
            capacity_scenarios = st.multiselect(
                "Select Capacity Levels to Test",
                ["Low (50%)", "Medium (75%)", "High (92%)", "Critical (100%)"],
                default=["Medium (75%)", "High (92%)"]
            )
        
        if st.button("Run Simulation", type="primary"):
            if not traffic_scenarios or not capacity_scenarios:
                st.warning("Please select at least one scenario for both Traffic Volume and Road Capacity")
            else:
                with st.spinner("Running scenarios..."):
                    scenarios = []
                    
                    # Map scenario labels to values
                    traffic_map = {
                        "Very Low (10k)": 10000,
                        "Low (20k)": 20000,
                        "Normal (29k)": 29000,
                        "High (45k)": 45000,
                        "Peak (65k)": 65000
                    }
                    
                    capacity_map = {
                        "Low (50%)": 50.0,
                        "Medium (75%)": 75.0,
                        "High (92%)": 92.0,
                        "Critical (100%)": 100.0
                    }
                    
                    for traffic_label in traffic_scenarios:
                        for capacity_label in capacity_scenarios:
                            traffic_vol = traffic_map[traffic_label]
                            capacity_val = capacity_map[capacity_label]
                            
                            result = predict_friction_score(
                                date=target_date.strftime("%Y-%m-%d"),
                                area=area,
                                road=road,
                                weather=weather,
                                traffic_volume=traffic_vol,
                                road_capacity=capacity_val
                            )
                            
                            if result:
                                scenarios.append({
                                    'Traffic Volume': traffic_label,
                                    'Road Capacity': capacity_label,
                                    'Predicted Congestion': result['predicted_congestion'],
                                    'Category': result['friction_category']
                                })
                
                if scenarios:
                    st.success("Simulation Complete!")
                    
                    df = pd.DataFrame(scenarios)
                    
                    # Heatmap
                    pivot_df = df.pivot(index='Traffic Volume', columns='Road Capacity', values='Predicted Congestion')
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_df.values,
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        colorscale='RdYlGn_r',
                        text=pivot_df.values.round(1),
                        texttemplate='%{text}',
                        textfont={"size": 14},
                        colorbar=dict(title="Congestion")
                    ))
                    
                    fig.update_layout(
                        title="Congestion Heatmap: Traffic Volume vs Road Capacity",
                        xaxis_title="Road Capacity Utilization",
                        yaxis_title="Traffic Volume",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Data table
                    st.subheader("Scenario Results")
                    st.dataframe(df, use_container_width=True)
                    
                    # Insights
                    st.subheader("Key Insights")
                    max_scenario = df.loc[df['Predicted Congestion'].idxmax()]
                    min_scenario = df.loc[df['Predicted Congestion'].idxmin()]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.error(f"**Worst Case Scenario**")
                        st.write(f"Traffic Volume: {max_scenario['Traffic Volume']}")
                        st.write(f"Road Capacity: {max_scenario['Road Capacity']}")
                        st.write(f"Congestion: {max_scenario['Predicted Congestion']:.1f}")
                    
                    with col2:
                        st.success(f"**Best Case Scenario**")
                        st.write(f"Traffic Volume: {min_scenario['Traffic Volume']}")
                        st.write(f"Road Capacity: {min_scenario['Road Capacity']}")
                        st.write(f"Congestion: {min_scenario['Predicted Congestion']:.1f}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "BSLO - Bengaluru Strategic Logistics Optimizer | "
        "Powered by XGBoost & FastAPI"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
