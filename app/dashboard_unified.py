"""
FIRE SWARM - UNIFIED COMMAND CENTER
====================================
Combined mission planning + fleet control in one dashboard.

Features:
- Draw search areas on satellite map
- Auto-generate grid patterns inside drawn areas
- Control fleet to execute the mission
- Real-time drone tracking

Usage:
    streamlit run dashboard_unified.py
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import json
import numpy as np
import pandas as pd
import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# Page config
st.set_page_config(
    page_title="🔥 Fire Swarm Command",
    page_icon="🔥",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stApp { background: #0a0f14; }
    .step-header {
        background: linear-gradient(90deg, #1a2030 0%, #2a3040 100%);
        padding: 10px 20px;
        border-radius: 8px;
        border-left: 4px solid #00ff88;
        margin: 10px 0;
    }
    .drone-card {
        background: #1a1f28;
        border: 1px solid #2a3a4a;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }
    .active { border-left: 3px solid #00ff88; }
    .idle { border-left: 3px solid #666; }
</style>
""", unsafe_allow_html=True)

# Session state
if 'mission_waypoints' not in st.session_state:
    st.session_state.mission_waypoints = []
if 'mission_polygon' not in st.session_state:
    st.session_state.mission_polygon = None
if 'drones' not in st.session_state:
    st.session_state.drones = {}
if 'mission_started' not in st.session_state:
    st.session_state.mission_started = False
if 'step' not in st.session_state:
    st.session_state.step = 1

# Config
BASE_LAT = 44.8125
BASE_LON = 20.4612
DRONE_COLORS = ['red', 'blue', 'green', 'purple', 'orange']

@dataclass
class Drone:
    id: str
    lat: float = BASE_LAT
    lon: float = BASE_LON
    alt: float = 0
    waypoint_idx: int = 0
    active: bool = False
    color: str = 'blue'

# ============== HEADER ==============
st.markdown("# 🔥 FIRE SWARM UNIFIED COMMAND")

# Progress indicator
cols = st.columns(4)
steps = ["1️⃣ Draw Area", "2️⃣ Generate Grid", "3️⃣ Assign Drones", "4️⃣ Execute"]
for i, (col, step) in enumerate(zip(cols, steps)):
    with col:
        if i + 1 < st.session_state.step:
            st.success(step)
        elif i + 1 == st.session_state.step:
            st.info(step)
        else:
            st.markdown(f"<span style='color:#666'>{step}</span>", unsafe_allow_html=True)

st.markdown("---")

# ============== MAIN LAYOUT ==============
col_left, col_map, col_right = st.columns([1, 2.5, 1])

# ============== LEFT: SETTINGS ==============
with col_left:
    st.markdown("### ⚙️ Mission Settings")
    
    num_drones = st.slider("Number of Drones", 1, 5, 3)
    altitude = st.slider("Flight Altitude (m)", 20, 100, 50)
    grid_spacing = st.slider("Grid Spacing (m)", 10, 100, 30)
    
    st.markdown("---")
    
    # Initialize drones
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        if drone_id not in st.session_state.drones:
            st.session_state.drones[drone_id] = Drone(
                id=drone_id,
                lat=BASE_LAT + (i - num_drones//2) * 0.0005,
                lon=BASE_LON - 0.002,
                color=DRONE_COLORS[i]
            )
    
    # Remove extra drones
    st.session_state.drones = {k: v for k, v in st.session_state.drones.items() 
                               if int(k[1]) <= num_drones}
    
    st.markdown("### 🚁 Fleet")
    for drone_id, drone in st.session_state.drones.items():
        status = "ACTIVE" if drone.active else "IDLE"
        status_class = "active" if drone.active else "idle"
        st.markdown(f"""
        <div class="drone-card {status_class}">
            <b style="color:{drone.color}">🚁 {drone_id}</b> - {status}<br>
            <small>WP: {drone.waypoint_idx + 1}/{len(st.session_state.mission_waypoints) // num_drones if st.session_state.mission_waypoints else 0}</small>
        </div>
        """, unsafe_allow_html=True)

# ============== CENTER: MAP ==============
with col_map:
    st.markdown("### 🗺️ Mission Map")
    st.caption("Draw a polygon or rectangle to define search area")
    
    # Create map with satellite
    m = folium.Map(location=[BASE_LAT, BASE_LON], zoom_start=15)
    
    # Satellite layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        overlay=False
    ).add_to(m)
    
    # Base marker
    folium.Marker(
        [BASE_LAT, BASE_LON],
        popup='🏠 Base Station',
        icon=folium.Icon(color='green', icon='home')
    ).add_to(m)
    
    # Add existing waypoints
    if st.session_state.mission_waypoints:
        for i, wp in enumerate(st.session_state.mission_waypoints):
            folium.CircleMarker(
                [wp[0], wp[1]],
                radius=4,
                color='yellow',
                fill=True,
                popup=f'WP {i+1}'
            ).add_to(m)
        
        # Draw path
        if len(st.session_state.mission_waypoints) > 1:
            folium.PolyLine(
                st.session_state.mission_waypoints,
                color='cyan',
                weight=2,
                opacity=0.8
            ).add_to(m)
    
    # Add drone markers
    for drone_id, drone in st.session_state.drones.items():
        folium.Marker(
            [drone.lat, drone.lon],
            popup=f'🚁 {drone_id}',
            icon=folium.Icon(color=drone.color, icon='plane')
        ).add_to(m)
    
    # Draw control
    draw = Draw(
        export=False,
        position='topleft',
        draw_options={
            'polyline': False,
            'rectangle': True,
            'polygon': True,
            'circle': False,
            'marker': False,
            'circlemarker': False
        }
    )
    draw.add_to(m)
    
    # Display map
    output = st_folium(m, width=700, height=500, returned_objects=["all_drawings"])
    
    # Process drawings
    if output and output.get('all_drawings'):
        last_draw = output['all_drawings'][-1]
        if last_draw and last_draw.get('geometry'):
            geom_type = last_draw['geometry']['type']
            coords = last_draw['geometry']['coordinates']
            
            if geom_type == 'Polygon':
                st.session_state.mission_polygon = coords[0] if len(coords) == 1 else coords
                st.session_state.step = max(st.session_state.step, 2)

# ============== RIGHT: CONTROLS ==============
with col_right:
    st.markdown("### 🎮 Mission Control")
    
    # Step 2: Generate Grid
    if st.session_state.mission_polygon:
        poly_coords = st.session_state.mission_polygon
        
        # Calculate bounds
        lons = [c[0] for c in poly_coords]
        lats = [c[1] for c in poly_coords]
        
        area_width = (max(lons) - min(lons)) * 111000 * math.cos(math.radians(BASE_LAT))
        area_height = (max(lats) - min(lats)) * 111000
        
        st.success(f"✅ Area defined: {area_width:.0f}m × {area_height:.0f}m")
        
        if st.button("🔲 Generate Grid", type="primary", use_container_width=True):
            # Generate lawnmower pattern
            deg_spacing = grid_spacing / 111000
            
            waypoints = []
            x = min(lons)
            direction = 1
            
            while x <= max(lons):
                y_range = np.arange(min(lats), max(lats), deg_spacing)
                if direction == -1:
                    y_range = y_range[::-1]
                
                for y in y_range:
                    waypoints.append([y, x])  # [lat, lon]
                
                x += deg_spacing
                direction *= -1
            
            st.session_state.mission_waypoints = waypoints
            st.session_state.step = 3
            st.rerun()
    else:
        st.warning("👆 Draw an area on the map first")
    
    st.markdown("---")
    
    # Step 3: Show waypoints
    if st.session_state.mission_waypoints:
        wp_count = len(st.session_state.mission_waypoints)
        st.info(f"📍 {wp_count} waypoints generated")
        
        # Assign to drones
        wps_per_drone = wp_count // num_drones
        st.caption(f"~{wps_per_drone} waypoints per drone")
        
        st.markdown("---")
        
        # Step 4: Execute
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ START", type="primary", use_container_width=True):
                st.session_state.mission_started = True
                st.session_state.step = 4
                for drone in st.session_state.drones.values():
                    drone.active = True
                st.rerun()
        
        with col2:
            if st.button("⏹️ STOP", use_container_width=True):
                st.session_state.mission_started = False
                for drone in st.session_state.drones.values():
                    drone.active = False
                st.rerun()
        
        if st.button("🏠 RTL ALL", use_container_width=True):
            st.session_state.mission_started = False
            for drone in st.session_state.drones.values():
                drone.active = False
                drone.lat = BASE_LAT
                drone.lon = BASE_LON
                drone.waypoint_idx = 0
            st.rerun()
        
        if st.button("🗑️ Clear Mission", use_container_width=True):
            st.session_state.mission_waypoints = []
            st.session_state.mission_polygon = None
            st.session_state.step = 1
            st.rerun()
    
    st.markdown("---")
    
    # Mission stats
    if st.session_state.mission_waypoints:
        st.markdown("### 📊 Mission Stats")
        total_dist = 0
        wps = st.session_state.mission_waypoints
        for i in range(1, len(wps)):
            dlat = (wps[i][0] - wps[i-1][0]) * 111000
            dlon = (wps[i][1] - wps[i-1][1]) * 111000 * math.cos(math.radians(BASE_LAT))
            total_dist += math.sqrt(dlat**2 + dlon**2)
        
        flight_time = total_dist / 10  # Assume 10 m/s
        
        st.metric("Total Distance", f"{total_dist/1000:.1f} km")
        st.metric("Est. Flight Time", f"{flight_time/60:.0f} min")
        st.metric("Waypoints", len(wps))

# ============== SIMULATION ==============
if st.session_state.mission_started and st.session_state.mission_waypoints:
    wps = st.session_state.mission_waypoints
    wps_per_drone = len(wps) // num_drones
    
    for i, (drone_id, drone) in enumerate(st.session_state.drones.items()):
        if not drone.active:
            continue
        
        # Get this drone's waypoints
        start_idx = i * wps_per_drone
        end_idx = start_idx + wps_per_drone
        drone_wps = wps[start_idx:end_idx]
        
        if not drone_wps:
            continue
        
        # Move towards current waypoint
        wp_idx = drone.waypoint_idx % len(drone_wps)
        target = drone_wps[wp_idx]
        
        dlat = target[0] - drone.lat
        dlon = target[1] - drone.lon
        dist = math.sqrt(dlat**2 + dlon**2)
        
        if dist > 0.00005:
            drone.lat += (dlat / dist) * 0.0001
            drone.lon += (dlon / dist) * 0.0001
        else:
            drone.waypoint_idx += 1
    
    time.sleep(0.2)
    st.rerun()

# Footer
st.markdown("---")
st.caption(f"🕐 {time.strftime('%H:%M:%S')} | Drones: {num_drones} | WPs: {len(st.session_state.mission_waypoints)} | {'🟢 RUNNING' if st.session_state.mission_started else '🔴 STOPPED'}")

