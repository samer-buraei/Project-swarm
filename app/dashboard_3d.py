"""
FIRE SWARM COMMAND CENTER - 3D MAP VERSION
===========================================
Professional 3D map visualization using PyDeck.
Shows drones flying in 3D with altitude, trails, and fire markers.

Usage:
    1. Start SITL: python -m dronekit_sitl copter --home=44.8125,20.4612,0,0
    2. Run: streamlit run dashboard_3d.py
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import numpy as np

# Page config
st.set_page_config(
    page_title="🔥 Fire Swarm 3D",
    page_icon="🔥",
    layout="wide"
)

# Custom CSS - QGroundControl inspired dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #161b22 100%);
    }
    
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00ff88, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        color: #8b949e;
        text-align: center;
        font-size: 1.1rem;
    }
    
    .status-panel {
        background: rgba(22, 27, 34, 0.9);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    .drone-card {
        background: linear-gradient(135deg, #1a1f26 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-left: 4px solid #00ff88;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    .drone-card.armed {
        border-left-color: #ff9500;
        animation: pulse-border 2s infinite;
    }
    
    .drone-card.flying {
        border-left-color: #00ccff;
    }
    
    .metric-label {
        color: #8b949e;
        font-size: 0.8rem;
        text-transform: uppercase;
    }
    
    .metric-value {
        color: #00ff88;
        font-size: 1.5rem;
        font-weight: 600;
        font-family: 'Orbitron', monospace;
    }
    
    .fire-alert {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
        animation: pulse 1s infinite;
        font-family: 'Orbitron', monospace;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(255,68,68,0.5); }
        50% { transform: scale(1.02); box-shadow: 0 0 40px rgba(255,68,68,0.8); }
    }
    
    @keyframes pulse-border {
        0%, 100% { border-left-color: #ff9500; }
        50% { border-left-color: #ffcc00; }
    }
    
    .command-btn {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .hud-overlay {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.7);
        padding: 10px 30px;
        border-radius: 20px;
        border: 1px solid #00ff88;
        font-family: 'Orbitron', monospace;
        color: #00ff88;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'drones' not in st.session_state:
    st.session_state.drones = {}
if 'trails' not in st.session_state:
    st.session_state.trails = {}
if 'fires' not in st.session_state:
    st.session_state.fires = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'mavlink' not in st.session_state:
    st.session_state.mavlink = None
if 'view_state' not in st.session_state:
    st.session_state.view_state = {
        'latitude': 44.8125,
        'longitude': 20.4612,
        'zoom': 15,
        'pitch': 60,
        'bearing': 0
    }

# Base location
BASE_LAT = 44.8125
BASE_LON = 20.4612

@dataclass
class DroneData:
    id: str
    lat: float = BASE_LAT
    lon: float = BASE_LON
    alt: float = 0.0
    heading: float = 0.0
    speed: float = 0.0
    battery: float = 100.0
    mode: str = "UNKNOWN"
    armed: bool = False
    connected: bool = False

def connect_to_sitl(port=5762):
    try:
        from pymavlink import mavutil
        master = mavutil.mavlink_connection(f'tcp:127.0.0.1:{port}', timeout=5)
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
        if msg:
            master.mav.request_data_stream_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1
            )
            return master
    except Exception as e:
        pass
    return None

def get_drone_data(master) -> Optional[DroneData]:
    if not master:
        return None
    try:
        from pymavlink import mavutil
        drone = DroneData(id="DRONE-1")
        
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
        if msg:
            drone.lat = msg.lat / 1e7
            drone.lon = msg.lon / 1e7
            drone.alt = msg.relative_alt / 1000
            drone.heading = msg.hdg / 100 if msg.hdg else 0
        
        msg = master.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            drone.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            mode_map = {0: 'STABILIZE', 3: 'AUTO', 4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 9: 'LAND'}
            drone.mode = mode_map.get(msg.custom_mode, str(msg.custom_mode))
        
        msg = master.recv_match(type='VFR_HUD', blocking=False)
        if msg:
            drone.speed = msg.groundspeed
        
        drone.connected = True
        return drone
    except:
        return None

def send_command(master, command: str, **kwargs):
    if not master:
        return False
    try:
        from pymavlink import mavutil
        if command == "ARM":
            master.mav.set_mode_send(master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4)
            time.sleep(0.5)
            master.mav.command_long_send(master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
        elif command == "TAKEOFF":
            master.mav.command_long_send(master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, kwargs.get('altitude', 50))
        elif command == "RTL":
            master.mav.set_mode_send(master.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6)
        elif command == "GOTO":
            master.mav.set_position_target_global_int_send(0, master.target_system, master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, 0b0000111111111000,
                int(kwargs['lat'] * 1e7), int(kwargs['lon'] * 1e7), kwargs.get('alt', 50), 0,0,0,0,0,0,0,0)
        return True
    except:
        return False

def create_3d_map(drones: Dict, trails: Dict, fires: List, view_state: dict):
    """Create PyDeck 3D map with drones, trails, and fires"""
    
    layers = []
    
    # Base station layer
    base_data = pd.DataFrame([{
        'lat': BASE_LAT,
        'lon': BASE_LON,
        'altitude': 5,
        'color': [0, 255, 136, 200],
        'size': 100
    }])
    
    layers.append(pdk.Layer(
        'ColumnLayer',
        data=base_data,
        get_position=['lon', 'lat'],
        get_elevation='altitude',
        elevation_scale=1,
        get_fill_color='color',
        radius=20,
        pickable=True
    ))
    
    # Drone layers
    for drone_id, drone in drones.items():
        if not drone.connected:
            continue
        
        # Drone marker (3D column)
        drone_color = [0, 200, 255, 255] if drone.armed and drone.alt > 1 else [255, 150, 0, 255] if drone.armed else [150, 150, 150, 255]
        
        drone_data = pd.DataFrame([{
            'lat': drone.lat,
            'lon': drone.lon,
            'altitude': max(drone.alt, 5),
            'color': drone_color,
            'name': drone_id
        }])
        
        # Drone column
        layers.append(pdk.Layer(
            'ColumnLayer',
            data=drone_data,
            get_position=['lon', 'lat'],
            get_elevation='altitude',
            elevation_scale=1,
            get_fill_color='color',
            radius=15,
            pickable=True
        ))
        
        # Drone icon on top
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=drone_data,
            get_position=['lon', 'lat'],
            get_fill_color=[0, 255, 200, 255],
            get_radius=25,
            pickable=True
        ))
        
        # Altitude shadow on ground
        shadow_data = pd.DataFrame([{
            'lat': drone.lat,
            'lon': drone.lon,
        }])
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=shadow_data,
            get_position=['lon', 'lat'],
            get_fill_color=[100, 100, 100, 100],
            get_radius=drone.alt + 10,
        ))
    
    # Trail layers
    for drone_id, trail in trails.items():
        if len(trail) > 1:
            trail_list = list(trail)
            path_data = pd.DataFrame([{
                'path': [[p[1], p[0]] for p in trail_list],  # [lon, lat] for pydeck
                'color': [0, 255, 255, 150]
            }])
            
            layers.append(pdk.Layer(
                'PathLayer',
                data=path_data,
                get_path='path',
                get_color='color',
                width_scale=2,
                width_min_pixels=2,
                pickable=True
            ))
    
    # Fire layers
    if fires:
        fire_data = pd.DataFrame([{
            'lat': f[0],
            'lon': f[1],
            'altitude': 100,
            'color': [255, 68, 68, 255]
        } for f in fires])
        
        # Fire columns
        layers.append(pdk.Layer(
            'ColumnLayer',
            data=fire_data,
            get_position=['lon', 'lat'],
            get_elevation='altitude',
            elevation_scale=1,
            get_fill_color='color',
            radius=30,
            pickable=True
        ))
        
        # Fire pulse effect
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=fire_data,
            get_position=['lon', 'lat'],
            get_fill_color=[255, 100, 100, 100],
            get_radius=80,
        ))
    
    # Create deck
    view = pdk.ViewState(
        latitude=view_state['latitude'],
        longitude=view_state['longitude'],
        zoom=view_state['zoom'],
        pitch=view_state['pitch'],
        bearing=view_state['bearing']
    )
    
    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        tooltip={"text": "{name}"}
    )
    
    return deck

# ================== UI ==================

# Header
st.markdown('<h1 class="main-title">🔥 FIRE SWARM COMMAND</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">3D Tactical Visualization • Real-Time Drone Tracking</p>', unsafe_allow_html=True)

# Layout
col_left, col_map, col_right = st.columns([1, 4, 1])

# Left panel - Connection & Commands
with col_left:
    st.markdown("### 🔌 SITL")
    
    port = st.number_input("Port", value=5760, min_value=5760, max_value=5800, label_visibility="collapsed")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔗 Connect", use_container_width=True):
            master = connect_to_sitl(port)
            if master:
                st.session_state.mavlink = master
                st.session_state.connected = True
    with col_btn2:
        if st.button("🔌 Disconnect" if st.session_state.connected else "---", use_container_width=True):
            if st.session_state.connected:
                st.session_state.mavlink = None
                st.session_state.connected = False
    
    if st.session_state.connected:
        st.success("🟢 Online")
    else:
        st.error("🔴 Offline")
    
    st.markdown("---")
    st.markdown("### 🎮 COMMANDS")
    
    if st.session_state.connected:
        if st.button("🔓 ARM", use_container_width=True, type="primary"):
            send_command(st.session_state.mavlink, "ARM")
        
        if st.button("🛫 TAKEOFF", use_container_width=True):
            send_command(st.session_state.mavlink, "TAKEOFF", altitude=50)
        
        if st.button("🏠 RTL", use_container_width=True):
            send_command(st.session_state.mavlink, "RTL")
        
        st.markdown("---")
        st.markdown("### 📍 GOTO")
        lat = st.number_input("Lat", value=44.815, format="%.5f", label_visibility="collapsed")
        lon = st.number_input("Lon", value=20.465, format="%.5f", label_visibility="collapsed")
        if st.button("🎯 FLY TO", use_container_width=True):
            send_command(st.session_state.mavlink, "GOTO", lat=lat, lon=lon)
    
    st.markdown("---")
    st.markdown("### 🎥 VIEW")
    pitch = st.slider("Pitch", 0, 85, 60)
    st.session_state.view_state['pitch'] = pitch

# Center - 3D Map
with col_map:
    # Get drone data
    drone = None
    if st.session_state.connected and st.session_state.mavlink:
        drone = get_drone_data(st.session_state.mavlink)
        if drone:
            st.session_state.drones['DRONE-1'] = drone
            if 'DRONE-1' not in st.session_state.trails:
                st.session_state.trails['DRONE-1'] = deque(maxlen=200)
            st.session_state.trails['DRONE-1'].append((drone.lat, drone.lon))
            
            # Center on drone
            st.session_state.view_state['latitude'] = drone.lat
            st.session_state.view_state['longitude'] = drone.lon
    
    # Create and display 3D map
    deck = create_3d_map(
        st.session_state.drones,
        st.session_state.trails,
        st.session_state.fires,
        st.session_state.view_state
    )
    
    st.pydeck_chart(deck, use_container_width=True, height=600)

# Right panel - Status
with col_right:
    st.markdown("### 📊 STATUS")
    
    for drone_id, d in st.session_state.drones.items():
        if d.connected:
            status = "flying" if d.armed and d.alt > 1 else "armed" if d.armed else ""
            st.markdown(f"""
            <div class="drone-card {status}">
                <div style="font-size: 1.2rem; font-weight: bold; color: #00ccff;">🚁 {drone_id}</div>
                <div class="metric-label">MODE</div>
                <div class="metric-value">{d.mode}</div>
                <div class="metric-label">ALTITUDE</div>
                <div class="metric-value">{d.alt:.1f}m</div>
                <div class="metric-label">SPEED</div>
                <div class="metric-value">{d.speed:.1f}m/s</div>
                <div class="metric-label">HEADING</div>
                <div class="metric-value">{d.heading:.0f}°</div>
                <div class="metric-label">ARMED</div>
                <div style="color: {'#00ff88' if d.armed else '#ff4444'}">{'● YES' if d.armed else '○ NO'}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if not st.session_state.drones:
        st.info("No drones")
    
    st.markdown("---")
    st.markdown("### 🔥 ALERTS")
    
    if st.session_state.fires:
        for i, fire in enumerate(st.session_state.fires):
            st.markdown(f"""
            <div class="fire-alert">
                🔥 FIRE #{i+1}<br>
                <small>({fire[0]:.4f}, {fire[1]:.4f})</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Clear")
    
    if st.button("🔥 Test Fire", use_container_width=True):
        if drone:
            st.session_state.fires.append((drone.lat + 0.002, drone.lon + 0.002))
        else:
            st.session_state.fires.append((BASE_LAT + 0.003, BASE_LON + 0.003))

# Footer HUD
if st.session_state.drones:
    d = list(st.session_state.drones.values())[0]
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 10px; margin-top: 20px;">
        <span style="color: #00ff88; font-family: 'Orbitron', monospace;">
            ALT: {d.alt:.0f}m | SPD: {d.speed:.1f}m/s | HDG: {d.heading:.0f}° | MODE: {d.mode}
        </span>
    </div>
    """, unsafe_allow_html=True)

# Auto-refresh
time.sleep(0.3)
st.rerun()

