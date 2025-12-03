"""
FIRE SWARM FLEET COMMANDER
===========================
Multi-drone patrol planning with automatic pattern generation.

Features:
- Connect up to 5 drones
- Draw surveillance area on map
- Auto-generate patrol patterns (Grid, Perimeter, Spiral, Sector)
- Assign drones to patrol zones
- Real-time fleet tracking

Usage:
    streamlit run dashboard_fleet.py
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import json

# Page config
st.set_page_config(
    page_title="🔥 Fleet Commander",
    page_icon="🚁",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #161b22 100%);
    }
    
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff6b6b, #ffa502);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    .drone-card {
        background: linear-gradient(135deg, #1a1f26 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .drone-online {
        border-left: 4px solid #00ff88;
    }
    
    .drone-offline {
        border-left: 4px solid #666;
    }
    
    .pattern-card {
        background: rgba(30, 40, 50, 0.8);
        border: 2px solid #30363d;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .pattern-card:hover {
        border-color: #00ccff;
        transform: scale(1.02);
    }
    
    .pattern-selected {
        border-color: #00ff88 !important;
        background: rgba(0, 255, 136, 0.1);
    }
    
    .coverage-stat {
        font-family: 'Orbitron', monospace;
        font-size: 2rem;
        color: #00ff88;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============== SESSION STATE ==============
if 'drones' not in st.session_state:
    st.session_state.drones = {}
if 'area' not in st.session_state:
    # Default surveillance area (Belgrade park)
    st.session_state.area = {
        'lat_min': 44.810,
        'lat_max': 44.815,
        'lon_min': 20.458,
        'lon_max': 20.465
    }
if 'patrol_pattern' not in st.session_state:
    st.session_state.patrol_pattern = 'grid'
if 'num_drones' not in st.session_state:
    st.session_state.num_drones = 3
if 'waypoints' not in st.session_state:
    st.session_state.waypoints = {}
if 'trails' not in st.session_state:
    st.session_state.trails = {}

# Base location
BASE_LAT = 44.8125
BASE_LON = 20.4612

# ============== DRONE DATA ==============
@dataclass
class DroneData:
    id: str
    lat: float = BASE_LAT
    lon: float = BASE_LON
    alt: float = 0.0
    heading: float = 0.0
    speed: float = 0.0
    mode: str = "IDLE"
    armed: bool = False
    connected: bool = False
    battery: float = 100.0
    waypoint_idx: int = 0
    color: List[int] = field(default_factory=lambda: [0, 200, 255])

# Drone colors
DRONE_COLORS = [
    [255, 107, 107],  # Red
    [78, 205, 196],   # Cyan
    [255, 190, 11],   # Yellow
    [131, 56, 236],   # Purple
    [0, 255, 136],    # Green
]

# ============== PATROL PATTERNS ==============
def generate_grid_pattern(area: dict, num_drones: int, altitude: float = 50) -> Dict[str, List[Tuple]]:
    """Generate grid sweep pattern - each drone covers a column"""
    waypoints = {}
    
    lat_min, lat_max = area['lat_min'], area['lat_max']
    lon_min, lon_max = area['lon_min'], area['lon_max']
    
    # Divide longitude into columns for each drone
    lon_step = (lon_max - lon_min) / num_drones
    lat_steps = 5  # Number of horizontal passes
    
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        wps = []
        
        col_lon_start = lon_min + i * lon_step
        col_lon_end = lon_min + (i + 1) * lon_step
        col_lon_mid = (col_lon_start + col_lon_end) / 2
        
        # Create zigzag pattern
        for j in range(lat_steps + 1):
            lat = lat_min + (lat_max - lat_min) * j / lat_steps
            if j % 2 == 0:
                lon = col_lon_start
            else:
                lon = col_lon_end
            wps.append((lat, lon, altitude))
        
        waypoints[drone_id] = wps
    
    return waypoints

def generate_perimeter_pattern(area: dict, num_drones: int, altitude: float = 50) -> Dict[str, List[Tuple]]:
    """Generate perimeter patrol - drones circle the boundary"""
    waypoints = {}
    
    lat_min, lat_max = area['lat_min'], area['lat_max']
    lon_min, lon_max = area['lon_min'], area['lon_max']
    
    # Perimeter points (clockwise)
    perimeter = [
        (lat_max, lon_min),  # NW
        (lat_max, lon_max),  # NE
        (lat_min, lon_max),  # SE
        (lat_min, lon_min),  # SW
    ]
    
    # Offset each drone around the perimeter
    points_per_drone = len(perimeter)
    
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        offset = i * len(perimeter) // num_drones
        wps = []
        
        # Create continuous loop with offset starting point
        for j in range(len(perimeter) * 2):  # Double loop
            idx = (offset + j) % len(perimeter)
            lat, lon = perimeter[idx]
            wps.append((lat, lon, altitude))
        
        waypoints[drone_id] = wps
    
    return waypoints

def generate_spiral_pattern(area: dict, num_drones: int, altitude: float = 50) -> Dict[str, List[Tuple]]:
    """Generate spiral inward pattern - converge to center"""
    waypoints = {}
    
    lat_min, lat_max = area['lat_min'], area['lat_max']
    lon_min, lon_max = area['lon_min'], area['lon_max']
    
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    max_radius = min(lat_max - lat_min, lon_max - lon_min) / 2
    
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        wps = []
        
        # Each drone starts at different angle
        start_angle = (2 * math.pi * i) / num_drones
        
        # Spiral inward
        for step in range(20):
            radius = max_radius * (1 - step / 25)
            angle = start_angle + step * 0.5
            
            lat = center_lat + radius * math.cos(angle) * 1.0
            lon = center_lon + radius * math.sin(angle) * 1.5  # Adjust for lat/lon ratio
            wps.append((lat, lon, altitude))
        
        waypoints[drone_id] = wps
    
    return waypoints

def generate_sector_pattern(area: dict, num_drones: int, altitude: float = 50) -> Dict[str, List[Tuple]]:
    """Generate sector coverage - each drone covers a pie slice"""
    waypoints = {}
    
    lat_min, lat_max = area['lat_min'], area['lat_max']
    lon_min, lon_max = area['lon_min'], area['lon_max']
    
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    
    max_radius = min(lat_max - lat_min, lon_max - lon_min) / 2
    
    sector_angle = 2 * math.pi / num_drones
    
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        wps = []
        
        # Start from center
        wps.append((center_lat, center_lon, altitude))
        
        # Sector boundaries
        angle_start = i * sector_angle
        angle_end = (i + 1) * sector_angle
        
        # Radial sweep pattern within sector
        for r in [0.3, 0.6, 1.0]:
            radius = max_radius * r
            for a in np.linspace(angle_start, angle_end, 5):
                lat = center_lat + radius * math.cos(a)
                lon = center_lon + radius * math.sin(a) * 1.5
                wps.append((lat, lon, altitude))
        
        # Return to sector edge
        wps.append((center_lat, center_lon, altitude))
        
        waypoints[drone_id] = wps
    
    return waypoints

def generate_lawnmower_pattern(area: dict, num_drones: int, altitude: float = 50) -> Dict[str, List[Tuple]]:
    """Generate lawn mower pattern - horizontal sweeps"""
    waypoints = {}
    
    lat_min, lat_max = area['lat_min'], area['lat_max']
    lon_min, lon_max = area['lon_min'], area['lon_max']
    
    # Divide into horizontal strips
    lat_step = (lat_max - lat_min) / num_drones
    
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        wps = []
        
        strip_lat_start = lat_min + i * lat_step
        strip_lat_end = lat_min + (i + 1) * lat_step
        
        # Zigzag across the strip
        passes = 4
        for j in range(passes + 1):
            lat = strip_lat_start + (strip_lat_end - strip_lat_start) * j / passes
            if j % 2 == 0:
                wps.append((lat, lon_min, altitude))
                wps.append((lat, lon_max, altitude))
            else:
                wps.append((lat, lon_max, altitude))
                wps.append((lat, lon_min, altitude))
        
        waypoints[drone_id] = wps
    
    return waypoints

PATTERN_GENERATORS = {
    'grid': generate_grid_pattern,
    'perimeter': generate_perimeter_pattern,
    'spiral': generate_spiral_pattern,
    'sector': generate_sector_pattern,
    'lawnmower': generate_lawnmower_pattern,
}

PATTERN_INFO = {
    'grid': {'name': '⊞ Grid', 'desc': 'Column sweeps', 'icon': '⊞'},
    'perimeter': {'name': '◻️ Perimeter', 'desc': 'Boundary patrol', 'icon': '◻️'},
    'spiral': {'name': '🌀 Spiral', 'desc': 'Converge to center', 'icon': '🌀'},
    'sector': {'name': '◔ Sector', 'desc': 'Pie slice zones', 'icon': '◔'},
    'lawnmower': {'name': '☰ Lawnmower', 'desc': 'Horizontal sweeps', 'icon': '☰'},
}

# ============== MAP CREATION ==============
def create_fleet_map(drones: Dict, waypoints: Dict, area: dict, trails: Dict):
    """Create PyDeck map with drones, waypoints, and patrol paths"""
    
    layers = []
    
    # 1. Surveillance Area Box
    area_corners = [
        [area['lon_min'], area['lat_min']],
        [area['lon_max'], area['lat_min']],
        [area['lon_max'], area['lat_max']],
        [area['lon_min'], area['lat_max']],
        [area['lon_min'], area['lat_min']],  # Close the box
    ]
    
    area_df = pd.DataFrame([{'path': area_corners, 'color': [255, 255, 255, 100]}])
    layers.append(pdk.Layer(
        'PathLayer',
        data=area_df,
        get_path='path',
        get_color='color',
        width_scale=3,
        width_min_pixels=3,
    ))
    
    # 2. Base station
    base_df = pd.DataFrame([{
        'lat': BASE_LAT,
        'lon': BASE_LON,
        'color': [0, 255, 136, 255],
        'size': 150
    }])
    layers.append(pdk.Layer(
        'ScatterplotLayer',
        data=base_df,
        get_position=['lon', 'lat'],
        get_fill_color='color',
        get_radius='size',
    ))
    
    # 3. Waypoint paths for each drone
    for drone_id, wps in waypoints.items():
        if not wps:
            continue
        
        # Get drone color
        drone_idx = int(drone_id[1]) - 1 if drone_id.startswith('D') else 0
        color = DRONE_COLORS[drone_idx % len(DRONE_COLORS)]
        
        path = [[wp[1], wp[0]] for wp in wps]  # [lon, lat]
        
        path_df = pd.DataFrame([{
            'path': path,
            'color': color + [150]  # Add alpha
        }])
        
        layers.append(pdk.Layer(
            'PathLayer',
            data=path_df,
            get_path='path',
            get_color='color',
            width_scale=2,
            width_min_pixels=2,
        ))
        
        # Waypoint markers
        wp_df = pd.DataFrame([{
            'lat': wp[0],
            'lon': wp[1],
            'color': color + [200]
        } for wp in wps])
        
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=wp_df,
            get_position=['lon', 'lat'],
            get_fill_color='color',
            get_radius=20,
        ))
    
    # 4. Drone markers (simulated positions)
    for drone_id, drone in drones.items():
        drone_idx = int(drone_id[1]) - 1 if drone_id.startswith('D') else 0
        color = DRONE_COLORS[drone_idx % len(DRONE_COLORS)]
        
        drone_df = pd.DataFrame([{
            'lat': drone.lat,
            'lon': drone.lon,
            'altitude': max(drone.alt, 10),
            'color': color + [255],
            'name': drone_id
        }])
        
        # Drone column (3D)
        layers.append(pdk.Layer(
            'ColumnLayer',
            data=drone_df,
            get_position=['lon', 'lat'],
            get_elevation='altitude',
            elevation_scale=1,
            get_fill_color='color',
            radius=25,
            pickable=True,
        ))
        
        # Drone top marker
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=drone_df,
            get_position=['lon', 'lat'],
            get_fill_color=[255, 255, 255, 255],
            get_radius=15,
        ))
    
    # Create view
    center_lat = (area['lat_min'] + area['lat_max']) / 2
    center_lon = (area['lon_min'] + area['lon_max']) / 2
    
    view = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=14,
        pitch=45,
        bearing=0
    )
    
    # Add satellite tile layer at the bottom
    satellite_layer = pdk.Layer(
        "TileLayer",
        data="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        min_zoom=0,
        max_zoom=19,
        tile_size=256
    )
    
    # Insert satellite at the beginning (bottom layer)
    layers.insert(0, satellite_layer)
    
    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style=None,  # No base map, we use TileLayer
        tooltip={"text": "{name}"}
    )

# ============== SIMULATED DRONES ==============
def simulate_drone_movement(drones: Dict, waypoints: Dict) -> Dict:
    """Simulate drones moving along their waypoint paths"""
    for drone_id, drone in drones.items():
        if drone_id not in waypoints or not waypoints[drone_id]:
            continue
        
        wps = waypoints[drone_id]
        
        # Move towards current waypoint
        target_wp = wps[drone.waypoint_idx % len(wps)]
        target_lat, target_lon, target_alt = target_wp
        
        # Simple movement (lerp)
        move_speed = 0.0001
        
        dlat = target_lat - drone.lat
        dlon = target_lon - drone.lon
        dist = math.sqrt(dlat**2 + dlon**2)
        
        if dist > 0.00005:  # Not at waypoint yet
            drone.lat += (dlat / dist) * move_speed
            drone.lon += (dlon / dist) * move_speed
            drone.alt = target_alt
            drone.mode = "PATROL"
            drone.armed = True
        else:
            # Reached waypoint, go to next
            drone.waypoint_idx = (drone.waypoint_idx + 1) % len(wps)
        
        # Calculate heading
        if dist > 0:
            drone.heading = math.degrees(math.atan2(dlon, dlat)) % 360
        
        drone.speed = move_speed * 111000  # Approx m/s
    
    return drones

# ============== UI LAYOUT ==============

# Header
st.markdown('<h1 class="main-title">🔥 FIRE SWARM FLEET COMMANDER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #8b949e;">Multi-Drone Patrol Planning & Surveillance</p>', unsafe_allow_html=True)

# Layout
col_left, col_map, col_right = st.columns([1.2, 3, 1.2])

# ============== LEFT PANEL ==============
with col_left:
    st.markdown("### 🚁 Fleet Setup")
    
    # Number of drones
    num_drones = st.slider("Active Drones", 1, 5, st.session_state.num_drones)
    st.session_state.num_drones = num_drones
    
    # Initialize drones
    for i in range(num_drones):
        drone_id = f"D{i+1}"
        if drone_id not in st.session_state.drones:
            st.session_state.drones[drone_id] = DroneData(
                id=drone_id,
                lat=BASE_LAT + (i - 2) * 0.001,
                lon=BASE_LON,
                color=DRONE_COLORS[i]
            )
    
    # Remove excess drones
    st.session_state.drones = {k: v for k, v in st.session_state.drones.items() 
                               if int(k[1]) <= num_drones}
    
    st.markdown("---")
    
    # Surveillance Area
    st.markdown("### 📍 Surveillance Area")
    
    with st.expander("📐 Set Boundaries", expanded=False):
        area = st.session_state.area
        area['lat_min'] = st.number_input("South (Lat)", value=area['lat_min'], format="%.4f", step=0.001)
        area['lat_max'] = st.number_input("North (Lat)", value=area['lat_max'], format="%.4f", step=0.001)
        area['lon_min'] = st.number_input("West (Lon)", value=area['lon_min'], format="%.4f", step=0.001)
        area['lon_max'] = st.number_input("East (Lon)", value=area['lon_max'], format="%.4f", step=0.001)
    
    # Calculate area size
    lat_km = (area['lat_max'] - area['lat_min']) * 111
    lon_km = (area['lon_max'] - area['lon_min']) * 111 * math.cos(math.radians(BASE_LAT))
    area_km2 = lat_km * lon_km
    
    st.markdown(f"""
    <div style="background: rgba(0,255,136,0.1); padding: 10px; border-radius: 8px; text-align: center;">
        <div style="color: #8b949e; font-size: 0.8rem;">COVERAGE AREA</div>
        <div class="coverage-stat">{area_km2:.2f} km²</div>
        <div style="color: #8b949e;">{lat_km:.1f} × {lon_km:.1f} km</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Altitude
    patrol_alt = st.slider("Patrol Altitude (m)", 20, 120, 50)

# ============== CENTER - MAP ==============
with col_map:
    st.markdown("### 🗺️ Patrol Map")
    
    # Pattern Selection
    st.markdown("#### Select Patrol Pattern:")
    pattern_cols = st.columns(5)
    
    for idx, (pattern_key, info) in enumerate(PATTERN_INFO.items()):
        with pattern_cols[idx]:
            if st.button(f"{info['icon']}\n{info['name'].split()[1]}", 
                        key=f"pat_{pattern_key}",
                        use_container_width=True,
                        type="primary" if st.session_state.patrol_pattern == pattern_key else "secondary"):
                st.session_state.patrol_pattern = pattern_key
    
    # Generate waypoints for selected pattern
    pattern_gen = PATTERN_GENERATORS[st.session_state.patrol_pattern]
    st.session_state.waypoints = pattern_gen(
        st.session_state.area, 
        st.session_state.num_drones,
        patrol_alt
    )
    
    # Simulate drone movement
    st.session_state.drones = simulate_drone_movement(
        st.session_state.drones,
        st.session_state.waypoints
    )
    
    # Create and display map
    fleet_map = create_fleet_map(
        st.session_state.drones,
        st.session_state.waypoints,
        st.session_state.area,
        st.session_state.trails
    )
    
    st.pydeck_chart(fleet_map, use_container_width=True, height=500)
    
    # Pattern info
    pattern_info = PATTERN_INFO[st.session_state.patrol_pattern]
    st.info(f"**{pattern_info['name']}**: {pattern_info['desc']} - Each drone covers its assigned zone")

# ============== RIGHT PANEL ==============
with col_right:
    st.markdown("### 📊 Fleet Status")
    
    # Fleet summary
    active_count = len([d for d in st.session_state.drones.values() if d.armed])
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-around; margin-bottom: 15px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; color: #00ff88;">{num_drones}</div>
            <div style="color: #8b949e; font-size: 0.8rem;">DRONES</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 2rem; color: #00ccff;">{active_count}</div>
            <div style="color: #8b949e; font-size: 0.8rem;">ACTIVE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Individual drone cards
    for drone_id, drone in st.session_state.drones.items():
        drone_idx = int(drone_id[1]) - 1
        color = DRONE_COLORS[drone_idx]
        color_hex = f"rgb({color[0]}, {color[1]}, {color[2]})"
        
        wps = st.session_state.waypoints.get(drone_id, [])
        wp_count = len(wps)
        current_wp = drone.waypoint_idx % wp_count if wp_count > 0 else 0
        
        st.markdown(f"""
        <div class="drone-card {'drone-online' if drone.armed else 'drone-offline'}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.2rem; font-weight: bold; color: {color_hex};">🚁 {drone_id}</span>
                <span style="color: {'#00ff88' if drone.armed else '#666'};">{'● ACTIVE' if drone.armed else '○ IDLE'}</span>
            </div>
            <div style="margin-top: 8px; font-size: 0.9rem; color: #aaa;">
                📍 ({drone.lat:.4f}, {drone.lon:.4f})<br>
                🎯 WP: {current_wp + 1}/{wp_count} | Alt: {drone.alt:.0f}m<br>
                🧭 Heading: {drone.heading:.0f}°
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Fleet commands
    st.markdown("### 🎮 Commands")
    
    col_cmd1, col_cmd2 = st.columns(2)
    with col_cmd1:
        if st.button("▶️ START", use_container_width=True, type="primary"):
            for d in st.session_state.drones.values():
                d.armed = True
                d.mode = "PATROL"
    
    with col_cmd2:
        if st.button("⏹️ STOP", use_container_width=True):
            for d in st.session_state.drones.values():
                d.armed = False
                d.mode = "IDLE"
    
    if st.button("🏠 RTL ALL", use_container_width=True):
        for d in st.session_state.drones.values():
            d.lat = BASE_LAT
            d.lon = BASE_LON
            d.alt = 0
            d.armed = False
            d.mode = "RTL"
            d.waypoint_idx = 0

# Footer stats
st.markdown("---")
footer_cols = st.columns(4)
with footer_cols[0]:
    total_wps = sum(len(wps) for wps in st.session_state.waypoints.values())
    st.metric("Total Waypoints", total_wps)
with footer_cols[1]:
    st.metric("Coverage", f"{area_km2:.2f} km²")
with footer_cols[2]:
    st.metric("Pattern", PATTERN_INFO[st.session_state.patrol_pattern]['name'])
with footer_cols[3]:
    overlap = max(0, 20 - num_drones * 3)
    st.metric("Est. Coverage %", f"{min(100, 70 + num_drones * 6)}%")

# Auto-refresh for animation
time.sleep(0.2)
st.rerun()

