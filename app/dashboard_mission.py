"""
FIRE SWARM - MISSION PLANNER
============================
Interactive mission planning with map drawing tools.

Features:
- Draw search areas on the map
- Auto-generate grid patterns
- Export missions to JSON

Usage:
    streamlit run dashboard_mission.py
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import json
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, Point

st.set_page_config(page_title="Mission Planner", layout="wide")

st.title("🗺️ Interactive Mission Planner")

# Sidebar
with st.sidebar:
    st.header("Mission Settings")
    altitude = st.slider("Altitude (m)", 20, 100, 50)
    spacing = st.slider("Grid Spacing (m)", 10, 100, 30)
    angle = st.slider("Grid Angle", 0, 180, 0)
    
    st.divider()
    st.markdown("### 📤 Export")
    mission_name = st.text_input("Mission Name", "Search_Sector_Alpha")
    if st.button("Save Mission"):
        if 'generated_waypoints' in st.session_state:
            with open(f"{mission_name}.json", "w") as f:
                json.dump({
                    "name": mission_name,
                    "altitude": altitude,
                    "waypoints": st.session_state.generated_waypoints
                }, f)
            st.success(f"Saved to {mission_name}.json")
        else:
            st.error("No waypoints generated yet")

# Map
m = folium.Map(location=[44.8125, 20.4612], zoom_start=15)

# Add Satellite
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite',
    overlay=False,
    control=True
).add_to(m)

# Draw Control
draw = Draw(
    export=True,
    position='topleft',
    draw_options={'polyline': False, 'rectangle': True, 'polygon': True, 'circle': False, 'marker': False, 'circlemarker': False},
    edit_options={'edit': True}
)
draw.add_to(m)

# Display Map
output = st_folium(m, width="100%", height=600)

# Process Drawing
if output['all_drawings']:
    last_draw = output['all_drawings'][-1]
    geom_type = last_draw['geometry']['type']
    coords = last_draw['geometry']['coordinates']
    
    if geom_type == 'Polygon':
        # Flatten coords if needed (Folium sometimes nests them)
        if len(coords) == 1:
            poly_coords = coords[0]
        else:
            poly_coords = coords
            
        # Create Shapely polygon
        poly = Polygon(poly_coords)
        
        st.success(f"✅ Area defined: {poly.area*1e10:.0f} m² (approx)")
        
        # Generate Grid (Simple Bounding Box Grid)
        min_x, min_y, max_x, max_y = poly.bounds
        
        # Convert spacing to degrees (approx)
        deg_spacing = spacing / 111000
        
        waypoints = []
        x = min_x
        direction = 1
        
        while x < max_x:
            y_range = np.arange(min_y, max_y, deg_spacing)
            if direction == -1:
                y_range = y_range[::-1]
                
            for y in y_range:
                p = Point(x, y)
                if poly.contains(p):
                    waypoints.append([y, x]) # Lat, Lon
            
            x += deg_spacing
            direction *= -1
            
        st.session_state.generated_waypoints = waypoints
        st.info(f"📍 Generated {len(waypoints)} waypoints")
        
        # Show waypoints table
        if waypoints:
            st.dataframe(pd.DataFrame(waypoints, columns=["Lat", "Lon"]))

else:
    st.info("👆 Use the drawing tools on the left of the map to define a search area.")
