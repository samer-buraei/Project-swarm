"""
FIRE SWARM - FULL COMMAND CENTER
=================================
Complete mission control with:
- Mission planning (draw areas)
- Fleet control
- Individual drone info
- Live video feeds
- QGroundControl compatible

Usage:
    1. Start SITL: python launch_fleet.py
    2. Run: streamlit run dashboard_command.py
    3. Optional: Connect QGroundControl to tcp:127.0.0.1:5760
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
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from PIL import Image

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
    .video-feed {
        border: 2px solid #2a3a4a;
        border-radius: 8px;
        overflow: hidden;
    }
    .drone-detail {
        background: linear-gradient(135deg, #1a1f28 0%, #252a35 100%);
        border: 1px solid #3a4a5a;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    .tel-item {
        background: #0d1117;
        padding: 10px;
        border-radius: 6px;
        text-align: center;
    }
    .tel-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00ff88;
        font-family: monospace;
    }
    .tel-label {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
    }
    .status-bar {
        display: flex;
        justify-content: space-between;
        background: #161b22;
        padding: 8px 15px;
        border-radius: 6px;
        margin: 5px 0;
    }
    .fire-alert {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        padding: 10px;
        border-radius: 8px;
        color: white;
        text-align: center;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
DRONE_CONFIG = [
    {"id": "D1", "name": "Alpha", "port": 5760, "color": "red", "frame": "live_frame_A1.jpg"},
    {"id": "D2", "name": "Bravo", "port": 5770, "color": "blue", "frame": "live_frame_A2.jpg"},
    {"id": "D3", "name": "Charlie", "port": 5780, "color": "green", "frame": "live_frame_A3.jpg"},
    {"id": "D4", "name": "Delta", "port": 5790, "color": "purple", "frame": "live_frame_A4.jpg"},
    {"id": "D5", "name": "Echo", "port": 5800, "color": "orange", "frame": "live_frame_A5.jpg"},
]

BASE_LAT = 44.8125
BASE_LON = 20.4612

# Session state
if 'selected_drone' not in st.session_state:
    st.session_state.selected_drone = "D1"
if 'connections' not in st.session_state:
    st.session_state.connections = {}
if 'fleet_data' not in st.session_state:
    st.session_state.fleet_data = {}
if 'fires' not in st.session_state:
    st.session_state.fires = []
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "fleet"  # fleet, drone, video

@dataclass
class DroneData:
    id: str
    name: str
    lat: float = BASE_LAT
    lon: float = BASE_LON
    alt: float = 0
    heading: float = 0
    speed: float = 0
    mode: str = "UNKNOWN"
    armed: bool = False
    battery: float = 100
    gps_fix: int = 0
    connected: bool = False
    fire_detected: bool = False
    confidence: float = 0

def connect_drone(port: int):
    """Connect to SITL drone"""
    try:
        from pymavlink import mavutil
        master = mavutil.mavlink_connection(f'tcp:127.0.0.1:{port}', timeout=5)
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
        if msg:
            master.mav.request_data_stream_send(
                master.target_system, master.target_component, 6, 10, 1)
            return master
    except:
        pass
    return None

def get_telemetry(master, drone: DroneData) -> DroneData:
    """Get drone telemetry from MAVLink"""
    if not master:
        drone.connected = False
        return drone
    
    try:
        from pymavlink import mavutil
        
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=0.3)
        if msg:
            drone.lat = msg.lat / 1e7
            drone.lon = msg.lon / 1e7
            drone.alt = msg.relative_alt / 1000
            drone.heading = msg.hdg / 100 if msg.hdg else 0
        
        msg = master.recv_match(type='VFR_HUD', blocking=False)
        if msg:
            drone.speed = msg.groundspeed
        
        msg = master.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            drone.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            mode_map = {0: 'STAB', 3: 'AUTO', 4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 9: 'LAND'}
            drone.mode = mode_map.get(msg.custom_mode, str(msg.custom_mode))
        
        drone.connected = True
    except:
        drone.connected = False
    
    return drone

def send_command(master, cmd: str, **kwargs):
    """Send MAVLink command"""
    if not master:
        return False
    try:
        from pymavlink import mavutil
        if cmd == "ARM":
            master.mav.set_mode_send(master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4)
            time.sleep(0.3)
            master.mav.command_long_send(master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
        elif cmd == "TAKEOFF":
            master.mav.command_long_send(master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, kwargs.get('alt', 50))
        elif cmd == "RTL":
            master.mav.set_mode_send(master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6)
        elif cmd == "GOTO":
            master.mav.set_position_target_global_int_send(
                0, master.target_system, master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, 0b0000111111111000,
                int(kwargs['lat'] * 1e7), int(kwargs['lon'] * 1e7), kwargs.get('alt', 50),
                0,0,0,0,0,0,0,0)
        return True
    except:
        return False

def load_video_frame(frame_path: str):
    """Load video frame from file"""
    if os.path.exists(frame_path):
        try:
            return Image.open(frame_path)
        except:
            pass
    return None

# ============== HEADER ==============
col1, col2, col3 = st.columns([2, 4, 2])
with col1:
    st.markdown("# 🔥 FIRE SWARM")
with col2:
    # View mode selector
    view_cols = st.columns(3)
    with view_cols[0]:
        if st.button("🗺️ Fleet View", use_container_width=True, 
                    type="primary" if st.session_state.view_mode == "fleet" else "secondary"):
            st.session_state.view_mode = "fleet"
    with view_cols[1]:
        if st.button("🚁 Drone Detail", use_container_width=True,
                    type="primary" if st.session_state.view_mode == "drone" else "secondary"):
            st.session_state.view_mode = "drone"
    with view_cols[2]:
        if st.button("📹 Video Grid", use_container_width=True,
                    type="primary" if st.session_state.view_mode == "video" else "secondary"):
            st.session_state.view_mode = "video"
with col3:
    connected_count = len([d for d in st.session_state.fleet_data.values() if d.connected])
    st.metric("Connected", f"{connected_count}/5", label_visibility="collapsed")

st.markdown("---")

# ============== CONNECT BUTTON ==============
if st.button("🔗 Connect All Drones", type="primary"):
    for cfg in DRONE_CONFIG:
        master = connect_drone(cfg['port'])
        if master:
            st.session_state.connections[cfg['id']] = master
            st.session_state.fleet_data[cfg['id']] = DroneData(
                id=cfg['id'], name=cfg['name'], connected=True)

# Update telemetry
for cfg in DRONE_CONFIG:
    drone_id = cfg['id']
    if drone_id in st.session_state.connections:
        master = st.session_state.connections[drone_id]
        if drone_id not in st.session_state.fleet_data:
            st.session_state.fleet_data[drone_id] = DroneData(id=drone_id, name=cfg['name'])
        st.session_state.fleet_data[drone_id] = get_telemetry(master, st.session_state.fleet_data[drone_id])

# ============== FLEET VIEW ==============
if st.session_state.view_mode == "fleet":
    col_left, col_map, col_right = st.columns([1, 3, 1])
    
    with col_left:
        st.markdown("### 🚁 Fleet Status")
        
        for cfg in DRONE_CONFIG:
            drone_id = cfg['id']
            drone = st.session_state.fleet_data.get(drone_id)
            
            if drone and drone.connected:
                status = "🟢" if drone.armed else "🟡"
                alt_display = f"{drone.alt:.0f}m"
            else:
                status = "🔴"
                alt_display = "--"
            
            if st.button(f"{status} {drone_id} - {cfg['name']} | {alt_display}", 
                        key=f"sel_{drone_id}", use_container_width=True):
                st.session_state.selected_drone = drone_id
                st.session_state.view_mode = "drone"
                st.rerun()
    
    with col_map:
        st.markdown("### 🗺️ Fleet Map")
        
        # Create map
        m = folium.Map(location=[BASE_LAT, BASE_LON], zoom_start=15)
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri', name='Satellite'
        ).add_to(m)
        
        # Base
        folium.Marker([BASE_LAT, BASE_LON], popup='🏠 Base',
                     icon=folium.Icon(color='green', icon='home')).add_to(m)
        
        # Drones
        for cfg in DRONE_CONFIG:
            drone = st.session_state.fleet_data.get(cfg['id'])
            if drone and drone.connected:
                folium.Marker(
                    [drone.lat, drone.lon],
                    popup=f"🚁 {cfg['id']} - {cfg['name']}<br>Alt: {drone.alt:.0f}m<br>Mode: {drone.mode}",
                    icon=folium.Icon(color=cfg['color'], icon='plane')
                ).add_to(m)
        
        # Fires
        for fire in st.session_state.fires:
            folium.Marker(fire, popup='🔥 FIRE!',
                         icon=folium.Icon(color='red', icon='fire')).add_to(m)
        
        st_folium(m, width=700, height=450)
    
    with col_right:
        st.markdown("### 🎮 Fleet Commands")
        
        if st.button("🔓 ARM ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "ARM")
        
        if st.button("🛫 TAKEOFF ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "ARM")
                time.sleep(0.3)
                send_command(master, "TAKEOFF", alt=50)
        
        if st.button("🏠 RTL ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "RTL")
        
        st.markdown("---")
        st.markdown("### 🔥 Fire Alerts")
        
        if st.session_state.fires:
            for i, fire in enumerate(st.session_state.fires):
                st.markdown(f"""
                <div class="fire-alert">
                    🔥 FIRE #{i+1}<br>
                    ({fire[0]:.4f}, {fire[1]:.4f})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No fires detected")

# ============== DRONE DETAIL VIEW ==============
elif st.session_state.view_mode == "drone":
    drone_id = st.session_state.selected_drone
    cfg = next((c for c in DRONE_CONFIG if c['id'] == drone_id), DRONE_CONFIG[0])
    drone = st.session_state.fleet_data.get(drone_id)
    master = st.session_state.connections.get(drone_id)
    
    col_left, col_center, col_right = st.columns([1.2, 2, 1.2])
    
    with col_left:
        st.markdown(f"### 🚁 {drone_id} - {cfg['name']}")
        
        # Drone selector
        drone_options = [f"{c['id']} - {c['name']}" for c in DRONE_CONFIG]
        selected = st.selectbox("Select Drone", drone_options, 
                               index=[c['id'] for c in DRONE_CONFIG].index(drone_id))
        new_id = selected.split(" - ")[0]
        if new_id != drone_id:
            st.session_state.selected_drone = new_id
            st.rerun()
        
        st.markdown("---")
        
        if drone and drone.connected:
            # Telemetry grid
            st.markdown(f"""
            <div class="drone-detail">
                <div class="telemetry-grid">
                    <div class="tel-item">
                        <div class="tel-value">{drone.alt:.1f}m</div>
                        <div class="tel-label">Altitude</div>
                    </div>
                    <div class="tel-item">
                        <div class="tel-value">{drone.speed:.1f}</div>
                        <div class="tel-label">Speed (m/s)</div>
                    </div>
                    <div class="tel-item">
                        <div class="tel-value">{drone.heading:.0f}°</div>
                        <div class="tel-label">Heading</div>
                    </div>
                    <div class="tel-item">
                        <div class="tel-value">{drone.mode}</div>
                        <div class="tel-label">Mode</div>
                    </div>
                </div>
                <div class="status-bar">
                    <span>Armed: {'✅' if drone.armed else '❌'}</span>
                    <span>GPS: {'✅' if drone.gps_fix > 2 else '⚠️'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📍 Position")
            st.code(f"Lat: {drone.lat:.6f}\nLon: {drone.lon:.6f}")
        else:
            st.warning("Drone not connected")
    
    with col_center:
        st.markdown("### 📹 Live Video Feed")
        
        frame = load_video_frame(cfg['frame'])
        if frame:
            st.image(frame, use_container_width=True, caption=f"{drone_id} Camera")
        else:
            st.info(f"No video feed from {drone_id}")
            st.caption(f"Looking for: {cfg['frame']}")
    
    with col_right:
        st.markdown("### 🎮 Drone Commands")
        
        if master:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔓 ARM", use_container_width=True):
                    send_command(master, "ARM")
                if st.button("🛫 TAKEOFF", use_container_width=True):
                    send_command(master, "TAKEOFF", alt=50)
            with col2:
                if st.button("🔒 DISARM", use_container_width=True):
                    send_command(master, "DISARM")
                if st.button("🏠 RTL", use_container_width=True):
                    send_command(master, "RTL")
            
            st.markdown("---")
            st.markdown("### 📍 Go To")
            goto_lat = st.number_input("Lat", value=drone.lat + 0.002 if drone else BASE_LAT, format="%.5f")
            goto_lon = st.number_input("Lon", value=drone.lon + 0.002 if drone else BASE_LON, format="%.5f")
            if st.button("🎯 FLY TO", use_container_width=True, type="primary"):
                send_command(master, "GOTO", lat=goto_lat, lon=goto_lon, alt=50)
        else:
            st.warning("Connect drone first")

# ============== VIDEO GRID VIEW ==============
elif st.session_state.view_mode == "video":
    st.markdown("### 📹 All Video Feeds")
    
    # 2x3 grid for 5 drones + overview
    row1 = st.columns(3)
    row2 = st.columns(3)
    
    all_cols = row1 + row2
    
    for i, cfg in enumerate(DRONE_CONFIG):
        with all_cols[i]:
            drone = st.session_state.fleet_data.get(cfg['id'])
            
            st.markdown(f"**{cfg['id']} - {cfg['name']}**")
            
            frame = load_video_frame(cfg['frame'])
            if frame:
                st.image(frame, use_container_width=True)
            else:
                st.info("No feed")
            
            if drone and drone.connected:
                st.caption(f"Alt: {drone.alt:.0f}m | Mode: {drone.mode}")
            else:
                st.caption("Offline")
    
    # 6th slot for overview
    with all_cols[5]:
        st.markdown("**🗺️ Overview**")
        st.metric("Connected", f"{connected_count}/5")
        st.metric("Flying", len([d for d in st.session_state.fleet_data.values() if d.connected and d.armed]))
        
        if st.button("🔗 Refresh All", use_container_width=True):
            st.rerun()

# ============== FOOTER ==============
st.markdown("---")
cols = st.columns(4)
with cols[0]:
    st.caption(f"🕐 {time.strftime('%H:%M:%S')}")
with cols[1]:
    st.caption(f"🚁 {connected_count}/5 connected")
with cols[2]:
    st.caption(f"🔥 {len(st.session_state.fires)} fires")
with cols[3]:
    st.caption("📡 QGC: tcp:127.0.0.1:5760")

# Auto-refresh
if connected_count > 0:
    time.sleep(0.5)
    st.rerun()

