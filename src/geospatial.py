"""
Geospatial utilities for BSLO
Handles geocoding, mapping, and route visualization for Bangalore traffic data
"""

import requests
import time
from typing import Dict, List, Tuple, Optional
import networkx as nx
import folium
from folium import plugins
import json

# Bangalore city center coordinates
BANGALORE_CENTER = (12.9716, 77.5946)

# Known coordinates for major Bangalore areas and roads
# These are approximate coordinates for the areas/roads in the dataset
AREA_COORDINATES = {
    "Indiranagar": (12.9716, 77.6412),
    "Whitefield": (12.9698, 77.7499),
    "Koramangala": (12.9352, 77.6245),
    "M.G. Road": (12.9756, 77.6069),
    "Jayanagar": (12.9250, 77.5838),
    "Hebbal": (13.0358, 77.5970),
    "Yeshwanthpur": (13.0280, 77.5380),
    "Electronic City": (12.8456, 77.6603)
}

ROAD_COORDINATES = {
    # Indiranagar
    "100 Feet Road": (12.9698, 77.6410),
    "CMH Road": (12.9850, 77.6380),
    
    # Whitefield
    "ITPL Main Road": (12.9850, 77.7280),
    "Marathahalli Bridge": (12.9591, 77.7010),
    
    # Koramangala
    "Sarjapur Road": (12.9121, 77.6446),
    "Sony World Junction": (12.9343, 77.6270),
    
    # M.G. Road
    "Trinity Circle": (12.9756, 77.6220),
    "Anil Kumble Circle": (12.9740, 77.6050),
    
    # Jayanagar
    "Jayanagar 4th Block": (12.9250, 77.5950),
    "South End Circle": (12.9400, 77.5870),
    
    # Hebbal
    "Hebbal Flyover": (13.0358, 77.5970),
    "Ballari Road": (13.0500, 77.6000),
    
    # Yeshwanthpur
    "Tumkur Road": (13.0280, 77.5200),
    "Yeshwanthpur Circle": (13.0280, 77.5380),
    
    # Electronic City
    "Hosur Road": (12.8900, 77.6500),
    "Silk Board Junction": (12.9180, 77.6220)
}

# Define road network connections (which roads connect to which)
ROAD_NETWORK = {
    "100 Feet Road": ["CMH Road", "Sony World Junction"],
    "CMH Road": ["100 Feet Road", "Trinity Circle"],
    "ITPL Main Road": ["Marathahalli Bridge"],
    "Marathahalli Bridge": ["ITPL Main Road", "Sony World Junction"],
    "Sarjapur Road": ["Sony World Junction", "Hosur Road"],
    "Sony World Junction": ["100 Feet Road", "Marathahalli Bridge", "Sarjapur Road", "Silk Board Junction"],
    "Trinity Circle": ["CMH Road", "Anil Kumble Circle"],
    "Anil Kumble Circle": ["Trinity Circle", "South End Circle"],
    "Jayanagar 4th Block": ["South End Circle"],
    "South End Circle": ["Anil Kumble Circle", "Jayanagar 4th Block", "Silk Board Junction"],
    "Hebbal Flyover": ["Ballari Road", "Yeshwanthpur Circle"],
    "Ballari Road": ["Hebbal Flyover"],
    "Tumkur Road": ["Yeshwanthpur Circle"],
    "Yeshwanthpur Circle": ["Tumkur Road", "Hebbal Flyover"],
    "Hosur Road": ["Sarjapur Road", "Silk Board Junction"],
    "Silk Board Junction": ["Sony World Junction", "South End Circle", "Hosur Road"]
}


def geocode_location(location_name: str, city: str = "Bangalore") -> Optional[Tuple[float, float]]:
    """
    Geocode a location using Nominatim (OpenStreetMap)
    
    Args:
        location_name: Name of the location
        city: City name (default: Bangalore)
    
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Check if we have hardcoded coordinates first
    if location_name in AREA_COORDINATES:
        return AREA_COORDINATES[location_name]
    if location_name in ROAD_COORDINATES:
        return ROAD_COORDINATES[location_name]
    
    # Try geocoding via Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"{location_name}, {city}, Karnataka, India",
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "BSLO-Traffic-Optimizer/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        time.sleep(1)  # Rate limiting
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception as e:
        print(f"Geocoding error for {location_name}: {e}")
    
    return None


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate approximate distance between two coordinates in km using Haversine formula
    
    Args:
        coord1: (lat, lon) tuple
        coord2: (lat, lon) tuple
    
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth radius in km
    R = 6371.0
    
    return R * c


def build_road_graph() -> nx.Graph:
    """
    Build a NetworkX graph representing the road network
    
    Returns:
        NetworkX Graph with roads as nodes and connections as edges
    """
    G = nx.Graph()
    
    # Add all roads as nodes with their coordinates
    for road, coords in ROAD_COORDINATES.items():
        G.add_node(road, pos=coords, lat=coords[0], lon=coords[1])
    
    # Add edges based on road network connections
    for road, connections in ROAD_NETWORK.items():
        for connected_road in connections:
            if road in ROAD_COORDINATES and connected_road in ROAD_COORDINATES:
                # Calculate distance for edge weight
                dist = calculate_distance(
                    ROAD_COORDINATES[road],
                    ROAD_COORDINATES[connected_road]
                )
                G.add_edge(road, connected_road, weight=dist)
    
    return G


def find_route(start_road: str, end_road: str, graph: nx.Graph = None) -> Optional[List[str]]:
    """
    Find the shortest path between two roads using NetworkX
    
    Args:
        start_road: Starting road name
        end_road: Destination road name
        graph: NetworkX graph (if None, will build new one)
    
    Returns:
        List of road names representing the route, or None if no path exists
    """
    if graph is None:
        graph = build_road_graph()
    
    try:
        # Use Dijkstra's algorithm to find shortest path
        path = nx.shortest_path(graph, start_road, end_road, weight='weight')
        return path
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None


def create_route_map(
    route: List[str],
    congestion_data: Dict[str, float] = None,
    center: Tuple[float, float] = BANGALORE_CENTER
) -> folium.Map:
    """
    Create an interactive Folium map showing the route with congestion levels
    
    Args:
        route: List of road names in the route
        congestion_data: Dictionary mapping road names to congestion levels (0-100)
        center: Map center coordinates
    
    Returns:
        Folium Map object
    """
    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add route markers and lines
    route_coords = []
    
    for i, road in enumerate(route):
        if road in ROAD_COORDINATES:
            coords = ROAD_COORDINATES[road]
            route_coords.append(coords)
            
            # Determine marker color based on congestion
            congestion = congestion_data.get(road, 50) if congestion_data else 50
            
            if congestion < 25:
                color = 'green'
                icon = 'ok-sign'
            elif congestion < 50:
                color = 'lightgreen'
                icon = 'info-sign'
            elif congestion < 75:
                color = 'orange'
                icon = 'warning-sign'
            else:
                color = 'red'
                icon = 'exclamation-sign'
            
            # Add marker
            marker_label = f"{'START' if i == 0 else 'END' if i == len(route)-1 else f'Stop {i}'}"
            popup_text = f"""
            <b>{marker_label}: {road}</b><br>
            Congestion: {congestion:.1f}<br>
            Category: {'Low' if congestion < 25 else 'Medium' if congestion < 50 else 'High' if congestion < 75 else 'Very High'}
            """
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_text, max_width=200),
                tooltip=road,
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
    
    # Draw route line
    if len(route_coords) > 1:
        folium.PolyLine(
            route_coords,
            color='blue',
            weight=4,
            opacity=0.7,
            popup='Route Path'
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p style="margin: 0;"><b>Congestion Levels</b></p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:green"></i> Low (0-25)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:lightgreen"></i> Medium (25-50)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:orange"></i> High (50-75)</p>
    <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:red"></i> Very High (75-100)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m


def get_route_summary(route: List[str], congestion_data: Dict[str, float] = None) -> Dict:
    """
    Generate a summary of the route
    
    Args:
        route: List of road names
        congestion_data: Dictionary mapping road names to congestion levels
    
    Returns:
        Dictionary with route summary statistics
    """
    total_distance = 0.0
    total_congestion = 0.0
    road_count = len(route)
    
    # Calculate total distance
    for i in range(len(route) - 1):
        if route[i] in ROAD_COORDINATES and route[i+1] in ROAD_COORDINATES:
            dist = calculate_distance(
                ROAD_COORDINATES[route[i]],
                ROAD_COORDINATES[route[i+1]]
            )
            total_distance += dist
    
    # Calculate average congestion
    if congestion_data:
        congestion_values = [congestion_data.get(road, 50) for road in route]
        total_congestion = sum(congestion_values)
        avg_congestion = total_congestion / road_count
    else:
        avg_congestion = 50.0
    
    return {
        'route': route,
        'road_count': road_count,
        'total_distance_km': round(total_distance, 2),
        'average_congestion': round(avg_congestion, 2),
        'total_congestion_score': round(total_congestion, 2)
    }
