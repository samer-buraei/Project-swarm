"""
FIRE SWARM COMMAND CENTER - SITL INTEGRATION
=============================================
Real-time dashboard showing drones from SITL on a live map.

Features:
- Live drone positions from SITL (MAVLink)
- Multiple drone support
- Flight path trails
- Fire detection markers
- Fleet commands (Arm, Takeoff, RTL)

Usage:
    1. Start SITL: python -m dronekit_sitl copter --home=44.8125,20.4612,0,0
    2. Run dashboard: streamlit run dashboard_sitl.py
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

# Page config
st.set_page_config(
    page_title="🔥 Fire Swarm Command",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%);
        color: #e0e0e0;
    }
    .drone-card {
        background: linear-gradient(135deg, #1e1e30 0%, #2d2d44 100%);
        border: 1px solid #3d3d5c;
        border-radius: 12px;
        padding: 15px;
        margin: 5px 0;
    }
    .drone-flying {
        border-left: 4px solid #00ff88;
    }
    .drone-armed {
        border-left: 4px solid #ffaa00;
    }
    .drone-offline {
        border-left: 4px solid #ff4444;
    }
    .fire-alert {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00ff88;
    }
    .command-btn {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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

# Base location (Belgrade)
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
    last_update: float = 0.0

def connect_to_sitl(port=5762):
    """Connect to SITL and start receiving telemetry"""
    try:
        from pymavlink import mavutil
        
        master = mavutil.mavlink_connection(f'tcp:127.0.0.1:{port}', timeout=5)
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
        
        if msg:
            # Request data streams
            master.mav.request_data_stream_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                4, 1
            )
            return master
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None

def get_drone_data(master) -> Optional[DroneData]:
    """Get current drone data from MAVLink connection"""
    if not master:
        return None
    
    try:
        from pymavlink import mavutil
        
        drone = DroneData(id="SITL-1")
        
        # Get position
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
        if msg:
            drone.lat = msg.lat / 1e7
            drone.lon = msg.lon / 1e7
            drone.alt = msg.relative_alt / 1000
            drone.heading = msg.hdg / 100 if msg.hdg else 0
        
        # Get heartbeat for mode/armed
        msg = master.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            drone.armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            mode_map = {0: 'STABILIZE', 3: 'AUTO', 4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 9: 'LAND'}
            drone.mode = mode_map.get(msg.custom_mode, str(msg.custom_mode))
        
        # Get VFR HUD for speed
        msg = master.recv_match(type='VFR_HUD', blocking=False)
        if msg:
            drone.speed = msg.groundspeed
        
        drone.connected = True
        drone.last_update = time.time()
        
        return drone
    except:
        return None

def send_command(master, command: str, **kwargs):
    """Send command to drone via MAVLink"""
    if not master:
        return False
    
    try:
        from pymavlink import mavutil
        
        if command == "ARM":
            master.mav.command_long_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 1, 0, 0, 0, 0, 0, 0
            )
        elif command == "DISARM":
            master.mav.command_long_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 0, 0, 0, 0, 0, 0, 0
            )
        elif command == "TAKEOFF":
            alt = kwargs.get('altitude', 50)
            master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4
            )
            time.sleep(0.5)
            master.mav.command_long_send(
                master.target_system, master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                0, 0, 0, 0, 0, 0, 0, alt
            )
        elif command == "RTL":
            master.mav.set_mode_send(
                master.target_system,
                mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6
            )
        elif command == "GOTO":
            lat = kwargs.get('lat', BASE_LAT)
            lon = kwargs.get('lon', BASE_LON)
            alt = kwargs.get('alt', 50)
            master.mav.set_position_target_global_int_send(
                0, master.target_system, master.target_component,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
                0b0000111111111000,
                int(lat * 1e7), int(lon * 1e7), alt,
                0, 0, 0, 0, 0, 0, 0, 0
            )
        
        return True
    except Exception as e:
        st.error(f"Command error: {e}")
        return False

# ============== UI LAYOUT ==============

# Header
col1, col2, col3 = st.columns([2, 4, 2])
with col1:
    st.markdown("# 🔥 FIRE SWARM")
with col2:
    st.markdown("### Command Center - SITL Integration")
with col3:
    if st.session_state.connected:
        st.success("🟢 SITL Connected")
    else:
        st.error("🔴 Disconnected")

st.markdown("---")

# Main layout
left_col, map_col, right_col = st.columns([1, 3, 1])

# Left panel - Connection & Commands
with left_col:
    st.markdown("### 🔌 Connection")
    
    port = st.number_input("SITL Port", value=5760, min_value=5760, max_value=5800)
    
    if st.button("🔗 Connect to SITL", use_container_width=True):
        with st.spinner("Connecting..."):
            master = connect_to_sitl(port)
            if master:
                st.session_state.mavlink = master
                st.session_state.connected = True
                st.success("Connected!")
            else:
                st.error("Failed to connect")
    
    if st.session_state.connected:
        if st.button("🔌 Disconnect", use_container_width=True):
            st.session_state.mavlink = None
            st.session_state.connected = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎮 Commands")
    
    if st.session_state.connected:
        if st.button("🔓 ARM", use_container_width=True, type="primary"):
            send_command(st.session_state.mavlink, "ARM")
            st.success("ARM sent!")
        
        if st.button("🛫 TAKEOFF 50m", use_container_width=True):
            send_command(st.session_state.mavlink, "ARM")
            time.sleep(1)
            send_command(st.session_state.mavlink, "TAKEOFF", altitude=50)
            st.success("Takeoff command sent!")
        
        if st.button("🏠 RTL", use_container_width=True):
            send_command(st.session_state.mavlink, "RTL")
            st.success("RTL sent!")
        
        if st.button("🔒 DISARM", use_container_width=True):
            send_command(st.session_state.mavlink, "DISARM")
            st.success("DISARM sent!")
        
        st.markdown("---")
        st.markdown("### 📍 Go To")
        goto_lat = st.number_input("Lat", value=44.815, format="%.5f")
        goto_lon = st.number_input("Lon", value=20.465, format="%.5f")
        if st.button("🎯 GO TO", use_container_width=True):
            send_command(st.session_state.mavlink, "GOTO", lat=goto_lat, lon=goto_lon)
            st.success(f"Going to ({goto_lat:.4f}, {goto_lon:.4f})")

# Center - Map
with map_col:
    st.markdown("### 🗺️ LIVE MAP")
    
    # Get drone data
    drone_data = None
    if st.session_state.connected and st.session_state.mavlink:
        drone_data = get_drone_data(st.session_state.mavlink)
        if drone_data:
            st.session_state.drones['SITL-1'] = drone_data
            
            # Update trail
            if 'SITL-1' not in st.session_state.trails:
                st.session_state.trails['SITL-1'] = deque(maxlen=100)
            st.session_state.trails['SITL-1'].append((drone_data.lat, drone_data.lon))
    
    # Create map
    center_lat = drone_data.lat if drone_data else BASE_LAT
    center_lon = drone_data.lon if drone_data else BASE_LON
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=16,
        tiles='cartodbdark_matter'
    )
    
    # Add base marker
    folium.Marker(
        [BASE_LAT, BASE_LON],
        popup='🏠 Home Base',
        icon=folium.Icon(color='green', icon='home', prefix='fa')
    ).add_to(m)
    
    # Add drone trails
    for drone_id, trail in st.session_state.trails.items():
        if len(trail) > 1:
            folium.PolyLine(
                list(trail),
                color='cyan',
                weight=2,
                opacity=0.7
            ).add_to(m)
    
    # Add drone markers
    for drone_id, drone in st.session_state.drones.items():
        if drone.connected:
            # Determine color based on state
            if drone.armed and drone.alt > 1:
                color = 'blue'  # Flying
                icon = 'plane'
            elif drone.armed:
                color = 'orange'  # Armed on ground
                icon = 'cog'
            else:
                color = 'gray'  # Disarmed
                icon = 'circle'
            
            popup_text = f"""
            <b>{drone_id}</b><br>
            Mode: {drone.mode}<br>
            Alt: {drone.alt:.1f}m<br>
            Speed: {drone.speed:.1f} m/s<br>
            Armed: {'Yes' if drone.armed else 'No'}
            """
            
            folium.Marker(
                [drone.lat, drone.lon],
                popup=popup_text,
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(m)
            
            # Altitude circle
            if drone.alt > 0:
                folium.Circle(
                    [drone.lat, drone.lon],
                    radius=drone.alt / 3,
                    color='cyan',
                    fill=True,
                    fillOpacity=0.2
                ).add_to(m)
    
    # Add fire markers
    for fire in st.session_state.fires:
        folium.Marker(
            fire,
            popup='🔥 Fire Detected!',
            icon=folium.Icon(color='red', icon='fire', prefix='fa')
        ).add_to(m)
    
    # Display map
    st_folium(m, width=700, height=500, returned_objects=[])

# Right panel - Drone Status
with right_col:
    st.markdown("### 📊 Drone Status")
    
    if st.session_state.drones:
        for drone_id, drone in st.session_state.drones.items():
            status_class = "drone-flying" if drone.armed and drone.alt > 1 else "drone-armed" if drone.armed else "drone-offline"
            
            st.markdown(f"""
            <div class="drone-card {status_class}">
                <h4>🚁 {drone_id}</h4>
                <p>
                <b>Mode:</b> {drone.mode}<br>
                <b>Position:</b><br>
                &nbsp;&nbsp;Lat: {drone.lat:.5f}<br>
                &nbsp;&nbsp;Lon: {drone.lon:.5f}<br>
                <b>Altitude:</b> {drone.alt:.1f}m<br>
                <b>Speed:</b> {drone.speed:.1f} m/s<br>
                <b>Heading:</b> {drone.heading:.0f}°<br>
                <b>Armed:</b> {'🟢 Yes' if drone.armed else '🔴 No'}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No drones connected")
    
    st.markdown("---")
    st.markdown("### 🔥 Fire Alerts")
    
    if st.session_state.fires:
        for i, fire in enumerate(st.session_state.fires):
            st.markdown(f"""
            <div class="fire-alert">
                🔥 FIRE #{i+1}<br>
                ({fire[0]:.5f}, {fire[1]:.5f})
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("✅ No fires detected")
    
    # Simulate fire button (for testing)
    if st.button("🔥 Simulate Fire", use_container_width=True):
        if drone_data:
            st.session_state.fires.append((drone_data.lat + 0.001, drone_data.lon + 0.001))
        else:
            st.session_state.fires.append((BASE_LAT + 0.002, BASE_LON + 0.002))
        st.rerun()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🕐 {time.strftime('%H:%M:%S')}")
with col2:
    drone_count = len([d for d in st.session_state.drones.values() if d.connected])
    st.caption(f"🚁 {drone_count} drone(s) online")
with col3:
    fire_count = len(st.session_state.fires)
    st.caption(f"🔥 {fire_count} fire(s) detected")

# Auto-refresh
time.sleep(0.5)
st.rerun()

