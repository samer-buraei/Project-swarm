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
import folium
from streamlit_folium import st_folium
import pandas as pd
import time
import math
import json
import glob
import os
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
    
    /* Manual Control Pad */
    .control-pad {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 5px;
        max-width: 200px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Drone configuration
DRONE_CONFIG = [
    {"id": "D1", "port": 5760, "color": "red", "name": "Alpha"},
    {"id": "D2", "port": 5770, "color": "blue", "name": "Bravo"},
    {"id": "D3", "port": 5780, "color": "orange", "name": "Charlie"},
    {"id": "D4", "port": 5790, "color": "purple", "name": "Delta"},
    {"id": "D5", "port": 5800, "color": "green", "name": "Echo"},
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
if 'mission' not in st.session_state:
    st.session_state.mission = None
if 'mission_waypoints' not in st.session_state:
    st.session_state.mission_waypoints = []
if 'mission_executing' not in st.session_state:
    st.session_state.mission_executing = False
if 'last_click' not in st.session_state:
    st.session_state.last_click = None

@dataclass
class DroneState:
    id: str
    name: str
    port: int
    color: str
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
            # Request ALL data streams for full telemetry
            master.mav.request_data_stream_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1)
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
        
        # ArduCopter mode map (complete)
        COPTER_MODES = {
            0: 'STABILIZE', 1: 'ACRO', 2: 'ALT_HOLD', 3: 'AUTO',
            4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 7: 'CIRCLE',
            9: 'LAND', 11: 'DRIFT', 13: 'SPORT', 14: 'FLIP',
            15: 'AUTOTUNE', 16: 'POSHOLD', 17: 'BRAKE', 18: 'THROW',
            19: 'AVOID_ADSB', 20: 'GUIDED_NOGPS', 21: 'SMART_RTL',
            22: 'FLOWHOLD', 23: 'FOLLOW', 24: 'ZIGZAG', 25: 'SYSTEMID',
            26: 'AUTOROTATE', 27: 'AUTO_RTL'
        }
        
        # Position and velocity
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=0.3)
        if msg:
            drone.lat = msg.lat / 1e7
            drone.lon = msg.lon / 1e7
            drone.alt = msg.relative_alt / 1000
            drone.heading = msg.hdg / 100 if msg.hdg else 0
            # Calculate ground speed from velocity components
            vx = msg.vx / 100  # cm/s to m/s
            vy = msg.vy / 100
            drone.speed = math.sqrt(vx*vx + vy*vy)
        
        # Heartbeat for mode/armed
        msg = master.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            drone.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            drone.mode = COPTER_MODES.get(msg.custom_mode, f"MODE_{msg.custom_mode}")
        
        drone.connected = True
    except Exception as e:
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
        
        st.markdown(f"""
        <div class="drone-panel {status_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {drone.color}; font-weight: bold;">🚁 {drone_id} - {drone.name}</span>
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
    
    # Initialize Folium Map
    # Center on fleet or base
    connected_drones = [d for d in st.session_state.fleet.values() if d.connected]
    if connected_drones:
        avg_lat = sum(d.lat for d in connected_drones) / len(connected_drones)
        avg_lon = sum(d.lon for d in connected_drones) / len(connected_drones)
    else:
        avg_lat, avg_lon = BASE_LAT, BASE_LON
        
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=16, tiles="CartoDB dark_matter")
    
    # Add Base Station
    folium.Marker(
        [BASE_LAT, BASE_LON],
        popup="Base Station",
        icon=folium.Icon(color="white", icon="home")
    ).add_to(m)
    
    # Add Mission Waypoints
    if st.session_state.mission_waypoints:
        for i, wp in enumerate(st.session_state.mission_waypoints):
            folium.CircleMarker(
                location=[wp[0], wp[1]],
                radius=3,
                color="orange",
                fill=True
            ).add_to(m)
        
        # Draw path
        folium.PolyLine(
            st.session_state.mission_waypoints,
            color="orange",
            weight=2,
            opacity=0.5
        ).add_to(m)

    # Add Drones and Trails
    for drone_id, drone in st.session_state.fleet.items():
        if not drone.connected:
            continue
            
        # Trail
        trail = list(st.session_state.trails[drone_id])
        if len(trail) > 1:
            folium.PolyLine(
                trail,
                color=drone.color,
                weight=2,
                opacity=0.6
            ).add_to(m)
            
        # Drone Marker
        folium.Marker(
            [drone.lat, drone.lon],
            popup=f"{drone.id} ({drone.alt:.0f}m)",
            icon=folium.Icon(color=drone.color, icon="plane", prefix="fa")
        ).add_to(m)

    # Render Map with Click Events
    map_output = st_folium(m, height=500, width=800)
    
    # Handle Click-to-Fly
    if map_output.get("last_clicked"):
        click_data = map_output["last_clicked"]
        clicked_lat = click_data["lat"]
        clicked_lon = click_data["lng"]
        
        # Only trigger if click changed (simple debounce)
        if st.session_state.last_click != (clicked_lat, clicked_lon):
            st.session_state.last_click = (clicked_lat, clicked_lon)
            
            # Send selected drone to this location
            target_drone_id = st.session_state.selected_drone
            if target_drone_id in st.session_state.connections:
                master = st.session_state.connections[target_drone_id]
                drone = st.session_state.fleet[target_drone_id]
                
                # Command
                send_command(master, "GOTO", lat=clicked_lat, lon=clicked_lon, alt=max(20, drone.alt))
                st.toast(f"🚁 Sending {target_drone_id} to {clicked_lat:.5f}, {clicked_lon:.5f}")
            else:
                st.toast(f"⚠️ {target_drone_id} not connected!", icon="⚠️")

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
    st.session_state.selected_drone = selected_id
    
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
        
        # Manual Control Pad
        st.markdown("#### 🕹️ Manual Nudge")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("⬆️", key="n_north", use_container_width=True):
                send_command(master, "GOTO", lat=drone.lat + 0.0002, lon=drone.lon, alt=drone.alt)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("⬅️", key="n_west", use_container_width=True):
                send_command(master, "GOTO", lat=drone.lat, lon=drone.lon - 0.0002, alt=drone.alt)
        with c2:
            if st.button("⬇️", key="n_south", use_container_width=True):
                send_command(master, "GOTO", lat=drone.lat - 0.0002, lon=drone.lon, alt=drone.alt)
        with c3:
            if st.button("➡️", key="n_east", use_container_width=True):
                send_command(master, "GOTO", lat=drone.lat, lon=drone.lon + 0.0002, alt=drone.alt)
                
        st.caption("Nudges drone ~20m in direction")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mode", drone.mode)
            st.metric("Speed", f"{drone.speed:.1f} m/s")
        with col2:
            st.metric("Armed", "✅" if drone.armed else "❌")
            st.metric("Heading", f"{drone.heading:.0f}°")
        
        st.markdown("#### Commands")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🔓 ARM", use_container_width=True):
                send_command(master, "ARM")
            if st.button(f"🛫 TAKEOFF", use_container_width=True):
                send_command(master, "TAKEOFF", alt=50)
        with col2:
            if st.button(f"🔒 DISARM", use_container_width=True):
                send_command(master, "DISARM")
            if st.button(f"🏠 RTL", use_container_width=True):
                send_command(master, "RTL")
        
    else:
        st.info(f"Connect {selected_id} first")
    
    # ============== MISSION LOADER ==============
    st.markdown("---")
    st.markdown("### 📋 Mission Control")
    
    # Find mission files
    mission_files = glob.glob("*.json")
    mission_files = [f for f in mission_files if "drone_state" not in f and "fleet_command" not in f]
    
    if mission_files:
        selected_mission = st.selectbox("Select Mission", ["None"] + mission_files)
        
        if selected_mission != "None":
            # Load mission button
            if st.button("📂 Load Mission", use_container_width=True):
                try:
                    with open(selected_mission, 'r') as f:
                        mission_data = json.load(f)
                    st.session_state.mission = mission_data
                    
                    # Extract waypoints
                    if 'waypoints' in mission_data:
                        st.session_state.mission_waypoints = mission_data['waypoints']
                    st.success(f"✅ Loaded {len(st.session_state.mission_waypoints)} waypoints!")
                except Exception as e:
                    st.error(f"Error: {e}")
            
            # Show mission info
            if st.session_state.mission:
                st.info(f"📍 **{len(st.session_state.mission_waypoints)} waypoints** loaded")
                
                # Execute mission
                if st.button("🚀 EXECUTE MISSION", use_container_width=True, type="primary"):
                    if st.session_state.mission_waypoints:
                        st.session_state.mission_executing = True
                        
                        # Distribute waypoints among connected drones
                        connected_drones = [d for d in st.session_state.fleet.values() if d.connected]
                        waypoints = st.session_state.mission_waypoints
                        
                        if connected_drones:
                            # Simple: assign waypoints round-robin to drones
                            altitude = st.session_state.mission.get('altitude', 50)
                            
                            for i, wp in enumerate(waypoints[:len(connected_drones)]):
                                drone = connected_drones[i % len(connected_drones)]
                                master = st.session_state.connections.get(drone.id)
                                if master:
                                    # ARM and send to first waypoint
                                    send_command(master, "ARM")
                                    time.sleep(0.3)
                                    send_command(master, "TAKEOFF", alt=altitude)
                                    time.sleep(1)
                                    send_command(master, "GOTO", lat=wp[0], lon=wp[1], alt=altitude)
                            
                            st.success(f"🚁 Mission started! {len(connected_drones)} drones dispatched")
                        else:
                            st.error("No drones connected!")
                
                # Clear mission
                if st.button("🗑️ Clear Mission", use_container_width=True):
                    st.session_state.mission = None
                    st.session_state.mission_waypoints = []
                    st.session_state.mission_executing = False
    else:
        st.info("💡 Create a mission in Mission Planner (port 8507)")
        st.link_button("🗺️ Open Mission Planner", "http://localhost:8507", use_container_width=True)

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
    time.sleep(1)
    st.rerun()
