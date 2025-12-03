"""
FIRE SWARM - REAL MULTI-DRONE CONTROL
======================================
Controls 5 real SITL drones simultaneously.

Prerequisites:
    python launch_fleet.py  (in another terminal)

Then run:
    streamlit run dashboard_fleet_real.py
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import deque

# Page config
st.set_page_config(
    page_title="🔥 Fleet Control",
    page_icon="🚁",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .stApp { background: #0a0f14; }
    .drone-panel {
        background: linear-gradient(135deg, #141a20 0%, #1a2028 100%);
        border: 1px solid #2a3a4a;
        border-radius: 8px;
        padding: 12px;
        margin: 5px 0;
    }
    .drone-connected { border-left: 3px solid #00ff88; }
    .drone-armed { border-left: 3px solid #ff9500; }
    .drone-flying { border-left: 3px solid #00ccff; }
    .drone-offline { border-left: 3px solid #444; opacity: 0.6; }
    .big-alt {
        font-size: 1.8rem;
        font-weight: bold;
        font-family: monospace;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    .badge-armed { background: #ff9500; color: black; }
    .badge-flying { background: #00ccff; color: black; }
    .badge-idle { background: #444; color: white; }
</style>
""", unsafe_allow_html=True)

# Drone configuration
DRONE_CONFIG = [
    {"id": "D1", "port": 5760, "color": [255, 107, 107], "name": "Alpha"},
    {"id": "D2", "port": 5770, "color": [78, 205, 196], "name": "Bravo"},
    {"id": "D3", "port": 5780, "color": [255, 190, 11], "name": "Charlie"},
    {"id": "D4", "port": 5790, "color": [131, 56, 236], "name": "Delta"},
    {"id": "D5", "port": 5800, "color": [0, 255, 136], "name": "Echo"},
]

BASE_LAT = 44.8125
BASE_LON = 20.4612

# Session state
if 'fleet' not in st.session_state:
    st.session_state.fleet = {}
if 'connections' not in st.session_state:
    st.session_state.connections = {}
if 'trails' not in st.session_state:
    st.session_state.trails = {d['id']: deque(maxlen=200) for d in DRONE_CONFIG}
if 'selected_drone' not in st.session_state:
    st.session_state.selected_drone = "D1"

@dataclass
class DroneState:
    id: str
    name: str
    port: int
    color: List[int]
    lat: float = BASE_LAT
    lon: float = BASE_LON
    alt: float = 0.0
    heading: float = 0.0
    speed: float = 0.0
    mode: str = "UNKNOWN"
    armed: bool = False
    connected: bool = False
    battery: float = 100.0

# ============== MAVLINK FUNCTIONS ==============

def connect_drone(port: int):
    """Connect to a SITL drone"""
    try:
        from pymavlink import mavutil
        master = mavutil.mavlink_connection(f'tcp:127.0.0.1:{port}', timeout=5)
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
        if msg:
            master.mav.request_data_stream_send(
                master.target_system, master.target_component,
                6, 10, 1  # Position stream
            )
            return master
    except:
        pass
    return None

def get_telemetry(master, drone: DroneState) -> DroneState:
    """Update drone state from MAVLink"""
    if not master:
        drone.connected = False
        return drone
    
    try:
        from pymavlink import mavutil
        
        # Position
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=0.3)
        if msg:
            drone.lat = msg.lat / 1e7
            drone.lon = msg.lon / 1e7
            drone.alt = msg.relative_alt / 1000
            drone.heading = msg.hdg / 100 if msg.hdg else 0
        
        # Speed
        msg = master.recv_match(type='VFR_HUD', blocking=False)
        if msg:
            drone.speed = msg.groundspeed
        
        # Mode/Armed
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
    """Send command to drone"""
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
        
        elif cmd == "DISARM":
            master.mav.command_long_send(master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 21196, 0, 0, 0, 0, 0)
        
        elif cmd == "TAKEOFF":
            alt = kwargs.get('alt', 50)
            master.mav.command_long_send(master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, alt)
        
        elif cmd == "RTL":
            master.mav.set_mode_send(master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6)
        
        elif cmd == "GOTO":
            master.mav.set_mode_send(master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4)
            time.sleep(0.2)
            master.mav.set_position_target_global_int_send(
                0, master.target_system, master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b0000111111111000,
                int(kwargs['lat'] * 1e7), int(kwargs['lon'] * 1e7), kwargs.get('alt', 50),
                0, 0, 0, 0, 0, 0, 0, 0)
        
        return True
    except:
        return False

# ============== MAP ==============

def create_fleet_map(fleet: Dict[str, DroneState], trails: Dict):
    """Create map with all drones"""
    layers = []
    
    # Base
    base_df = pd.DataFrame([{'lat': BASE_LAT, 'lon': BASE_LON, 'color': [0, 255, 136, 200]}])
    layers.append(pdk.Layer('ScatterplotLayer', data=base_df,
        get_position=['lon', 'lat'], get_fill_color='color', get_radius=60))
    
    # Trails
    for drone_id, trail in trails.items():
        if len(trail) > 1 and drone_id in fleet:
            color = fleet[drone_id].color
            path = [[p[1], p[0]] for p in trail]
            trail_df = pd.DataFrame([{'path': path, 'color': color + [120]}])
            layers.append(pdk.Layer('PathLayer', data=trail_df,
                get_path='path', get_color='color', width_scale=2, width_min_pixels=2))
    
    # Drones
    for drone_id, drone in fleet.items():
        if not drone.connected:
            continue
        
        # Column for altitude
        if drone.alt > 1:
            drone_df = pd.DataFrame([{
                'lat': drone.lat, 'lon': drone.lon,
                'altitude': drone.alt,
                'color': drone.color + [255]
            }])
            layers.append(pdk.Layer('ColumnLayer', data=drone_df,
                get_position=['lon', 'lat'], get_elevation='altitude',
                elevation_scale=1, get_fill_color='color', radius=20))
        
        # Top marker
        top_df = pd.DataFrame([{
            'lat': drone.lat, 'lon': drone.lon,
            'color': [255, 255, 255, 255]
        }])
        layers.append(pdk.Layer('ScatterplotLayer', data=top_df,
            get_position=['lon', 'lat'], get_fill_color='color', get_radius=15))
    
    # Center on fleet
    if fleet:
        connected = [d for d in fleet.values() if d.connected]
        if connected:
            avg_lat = sum(d.lat for d in connected) / len(connected)
            avg_lon = sum(d.lon for d in connected) / len(connected)
        else:
            avg_lat, avg_lon = BASE_LAT, BASE_LON
    else:
        avg_lat, avg_lon = BASE_LAT, BASE_LON
    
    view = pdk.ViewState(latitude=avg_lat, longitude=avg_lon, zoom=15, pitch=50)
    
    return pdk.Deck(layers=layers, initial_view_state=view,
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json')

# ============== UI ==============

st.markdown("# 🔥 FIRE SWARM FLEET CONTROL")
st.markdown("*Real MAVLink connection to 5 SITL drones*")

# Layout
col_left, col_map, col_right = st.columns([1.5, 3, 1.5])

# LEFT - Fleet Status
with col_left:
    st.markdown("### 🚁 Fleet")
    
    # Connect All button
    if st.button("🔗 Connect All Drones", use_container_width=True, type="primary"):
        for cfg in DRONE_CONFIG:
            with st.spinner(f"Connecting {cfg['id']}..."):
                master = connect_drone(cfg['port'])
                if master:
                    st.session_state.connections[cfg['id']] = master
                    st.session_state.fleet[cfg['id']] = DroneState(
                        id=cfg['id'], name=cfg['name'], port=cfg['port'],
                        color=cfg['color'], connected=True
                    )
    
    st.markdown("---")
    
    # Individual drone cards
    for cfg in DRONE_CONFIG:
        drone_id = cfg['id']
        
        # Get/update state
        if drone_id in st.session_state.fleet:
            drone = st.session_state.fleet[drone_id]
            master = st.session_state.connections.get(drone_id)
            if master:
                drone = get_telemetry(master, drone)
                st.session_state.fleet[drone_id] = drone
                
                # Update trail
                if drone.connected:
                    trail = st.session_state.trails[drone_id]
                    if len(trail) == 0 or (abs(drone.lat - trail[-1][0]) > 0.00001):
                        trail.append((drone.lat, drone.lon))
        else:
            drone = DroneState(id=drone_id, name=cfg['name'], port=cfg['port'], 
                             color=cfg['color'], connected=False)
        
        # Status class
        if not drone.connected:
            status_class = "drone-offline"
            badge = '<span class="status-badge badge-idle">OFFLINE</span>'
        elif drone.armed and drone.alt > 1:
            status_class = "drone-flying"
            badge = '<span class="status-badge badge-flying">FLYING</span>'
        elif drone.armed:
            status_class = "drone-armed"
            badge = '<span class="status-badge badge-armed">ARMED</span>'
        else:
            status_class = "drone-connected"
            badge = '<span class="status-badge badge-idle">IDLE</span>'
        
        color_hex = f"rgb({cfg['color'][0]}, {cfg['color'][1]}, {cfg['color'][2]})"
        
        st.markdown(f"""
        <div class="drone-panel {status_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {color_hex}; font-weight: bold;">🚁 {drone_id} - {drone.name}</span>
                {badge}
            </div>
            <div style="font-size: 0.85rem; color: #888; margin-top: 5px;">
                Alt: <span class="big-alt" style="color: #00ff88;">{drone.alt:.0f}m</span> | 
                Mode: {drone.mode} | 
                Spd: {drone.speed:.1f}m/s
            </div>
        </div>
        """, unsafe_allow_html=True)

# CENTER - Map
with col_map:
    st.markdown("### 🗺️ Fleet Map")
    
    # Create map
    fleet_map = create_fleet_map(st.session_state.fleet, st.session_state.trails)
    st.pydeck_chart(fleet_map, use_container_width=True, height=450)
    
    # Quick fleet commands
    st.markdown("### 🎮 Fleet Commands")
    cmd_cols = st.columns(5)
    
    with cmd_cols[0]:
        if st.button("🔓 ARM ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "ARM")
    
    with cmd_cols[1]:
        if st.button("🛫 TAKEOFF ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "ARM")
                time.sleep(0.5)
                send_command(master, "TAKEOFF", alt=50)
    
    with cmd_cols[2]:
        if st.button("🏠 RTL ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "RTL")
    
    with cmd_cols[3]:
        if st.button("🔒 DISARM ALL", use_container_width=True):
            for drone_id, master in st.session_state.connections.items():
                send_command(master, "DISARM")
    
    with cmd_cols[4]:
        if st.button("🗑️ Clear Trails", use_container_width=True):
            for k in st.session_state.trails:
                st.session_state.trails[k] = deque(maxlen=200)

# RIGHT - Individual Control
with col_right:
    st.markdown("### 🎯 Individual Control")
    
    # Drone selector
    drone_options = [f"{cfg['id']} - {cfg['name']}" for cfg in DRONE_CONFIG]
    selected = st.selectbox("Select Drone", drone_options, label_visibility="collapsed")
    selected_id = selected.split(" - ")[0]
    
    if selected_id in st.session_state.fleet:
        drone = st.session_state.fleet[selected_id]
        master = st.session_state.connections.get(selected_id)
        
        st.markdown(f"""
        <div style="background: #1a2028; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <div style="font-size: 1.5rem; color: #00ff88; font-family: monospace; text-align: center;">
                {drone.alt:.1f}m
            </div>
            <div style="text-align: center; color: #888; font-size: 0.8rem;">ALTITUDE</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mode", drone.mode)
            st.metric("Speed", f"{drone.speed:.1f} m/s")
        with col2:
            st.metric("Armed", "✅" if drone.armed else "❌")
            st.metric("Heading", f"{drone.heading:.0f}°")
        
        st.markdown("---")
        st.markdown("#### Commands")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🔓 ARM {selected_id}", use_container_width=True):
                send_command(master, "ARM")
            if st.button(f"🛫 TAKEOFF", use_container_width=True):
                send_command(master, "TAKEOFF", alt=50)
        with col2:
            if st.button(f"🔒 DISARM", use_container_width=True):
                send_command(master, "DISARM")
            if st.button(f"🏠 RTL", use_container_width=True):
                send_command(master, "RTL")
        
        st.markdown("---")
        st.markdown("#### Go To")
        goto_lat = st.number_input("Lat", value=drone.lat + 0.002, format="%.5f", key="goto_lat")
        goto_lon = st.number_input("Lon", value=drone.lon + 0.002, format="%.5f", key="goto_lon")
        if st.button(f"🎯 FLY {selected_id} TO TARGET", use_container_width=True, type="primary"):
            send_command(master, "GOTO", lat=goto_lat, lon=goto_lon, alt=50)
    else:
        st.info(f"Connect {selected_id} first")

# Footer
st.markdown("---")
connected_count = len([d for d in st.session_state.fleet.values() if d.connected])
flying_count = len([d for d in st.session_state.fleet.values() if d.connected and d.armed and d.alt > 1])

cols = st.columns(4)
with cols[0]:
    st.metric("Connected", f"{connected_count}/5")
with cols[1]:
    st.metric("Flying", flying_count)
with cols[2]:
    st.metric("Trails", sum(len(t) for t in st.session_state.trails.values()))
with cols[3]:
    st.caption(f"Updated: {time.strftime('%H:%M:%S')}")

# Auto-refresh
if connected_count > 0:
    time.sleep(0.3)
    st.rerun()

