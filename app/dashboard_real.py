"""
FIRE SWARM - REAL DRONE CONTROL
================================
Actually connects to SITL and controls real simulated drones.
NO FAKE ANIMATIONS - Real MAVLink telemetry and commands.

Usage:
    1. Start SITL: python -m dronekit_sitl copter --home=44.8125,20.4612,0,0
    2. Run: streamlit run dashboard_real.py
    3. Click "Connect" then use controls

Features:
- Real SITL connection via MAVLink
- Manual waypoint input (click coordinates)
- ARM / TAKEOFF / RTL / GOTO commands
- Real telemetry display
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import time
import math
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import threading

# Page config
st.set_page_config(
    page_title="🔥 Real Drone Control",
    page_icon="🚁",
    layout="wide"
)

# Minimal CSS
st.markdown("""
<style>
    .stApp { background: #0d1117; }
    .big-metric { 
        font-size: 2.5rem; 
        font-weight: bold; 
        color: #00ff88; 
        font-family: monospace;
    }
    .status-online { color: #00ff88; }
    .status-offline { color: #ff4444; }
    .control-panel {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'master' not in st.session_state:
    st.session_state.master = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'drone_data' not in st.session_state:
    st.session_state.drone_data = {
        'lat': 44.8125,
        'lon': 20.4612,
        'alt': 0,
        'heading': 0,
        'speed': 0,
        'mode': 'UNKNOWN',
        'armed': False,
        'battery': 0,
        'gps_fix': 0
    }
if 'trail' not in st.session_state:
    st.session_state.trail = []
if 'target' not in st.session_state:
    st.session_state.target = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = 0

BASE_LAT = 44.8125
BASE_LON = 20.4612

# ============== MAVLINK FUNCTIONS ==============

def connect_sitl(port: int = 5760) -> bool:
    """Connect to SITL via MAVLink"""
    try:
        from pymavlink import mavutil
        
        st.session_state.master = mavutil.mavlink_connection(
            f'tcp:127.0.0.1:{port}', 
            timeout=10
        )
        
        # Wait for heartbeat
        msg = st.session_state.master.recv_match(type='HEARTBEAT', blocking=True, timeout=10)
        if msg:
            # Request data streams
            st.session_state.master.mav.request_data_stream_send(
                st.session_state.master.target_system,
                st.session_state.master.target_component,
                6,  # MAV_DATA_STREAM_POSITION
                10, 1
            )
            st.session_state.master.mav.request_data_stream_send(
                st.session_state.master.target_system,
                st.session_state.master.target_component,
                1,  # MAV_DATA_STREAM_ALL
                4, 1
            )
            st.session_state.connected = True
            return True
    except Exception as e:
        st.error(f"Connection failed: {e}")
    return False

def disconnect():
    """Disconnect from SITL"""
    if st.session_state.master:
        st.session_state.master.close()
    st.session_state.master = None
    st.session_state.connected = False

def get_telemetry() -> dict:
    """Get current telemetry from drone"""
    if not st.session_state.master:
        return st.session_state.drone_data
    
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        
        # Get position
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=0.5)
        if msg:
            st.session_state.drone_data['lat'] = msg.lat / 1e7
            st.session_state.drone_data['lon'] = msg.lon / 1e7
            st.session_state.drone_data['alt'] = msg.relative_alt / 1000
            st.session_state.drone_data['heading'] = msg.hdg / 100 if msg.hdg else 0
        
        # Get VFR HUD
        msg = master.recv_match(type='VFR_HUD', blocking=False)
        if msg:
            st.session_state.drone_data['speed'] = msg.groundspeed
            st.session_state.drone_data['alt'] = msg.alt
        
        # Get heartbeat for mode/armed
        msg = master.recv_match(type='HEARTBEAT', blocking=False)
        if msg:
            st.session_state.drone_data['armed'] = bool(
                msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
            )
            mode_map = {0: 'STABILIZE', 3: 'AUTO', 4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 9: 'LAND'}
            st.session_state.drone_data['mode'] = mode_map.get(msg.custom_mode, str(msg.custom_mode))
        
        # Get GPS
        msg = master.recv_match(type='GPS_RAW_INT', blocking=False)
        if msg:
            st.session_state.drone_data['gps_fix'] = msg.fix_type
        
        # Get battery
        msg = master.recv_match(type='SYS_STATUS', blocking=False)
        if msg:
            st.session_state.drone_data['battery'] = msg.battery_remaining
        
        # Update trail
        lat, lon = st.session_state.drone_data['lat'], st.session_state.drone_data['lon']
        if len(st.session_state.trail) == 0 or \
           (abs(lat - st.session_state.trail[-1][0]) > 0.00001 or 
            abs(lon - st.session_state.trail[-1][1]) > 0.00001):
            st.session_state.trail.append((lat, lon))
            if len(st.session_state.trail) > 500:
                st.session_state.trail = st.session_state.trail[-500:]
        
    except Exception as e:
        pass
    
    return st.session_state.drone_data

def send_arm():
    """Arm the drone"""
    if not st.session_state.master:
        return False
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        
        # Set GUIDED mode first
        master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4  # GUIDED
        )
        time.sleep(0.5)
        
        # Arm
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0
        )
        return True
    except:
        return False

def send_disarm():
    """Disarm the drone"""
    if not st.session_state.master:
        return False
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 0, 21196, 0, 0, 0, 0, 0  # Force disarm
        )
        return True
    except:
        return False

def send_takeoff(altitude: float = 50):
    """Takeoff to specified altitude"""
    if not st.session_state.master:
        return False
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, altitude
        )
        return True
    except:
        return False

def send_rtl():
    """Return to launch"""
    if not st.session_state.master:
        return False
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            6  # RTL
        )
        return True
    except:
        return False

def send_goto(lat: float, lon: float, alt: float = 50):
    """Go to specified location"""
    if not st.session_state.master:
        return False
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        
        # Make sure we're in GUIDED mode
        master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4  # GUIDED
        )
        time.sleep(0.2)
        
        # Send position target
        master.mav.set_position_target_global_int_send(
            0,  # time_boot_ms
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b0000111111111000,  # type_mask (position only)
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
            0, 0, 0,  # velocity
            0, 0, 0,  # acceleration
            0, 0  # yaw, yaw_rate
        )
        st.session_state.target = (lat, lon, alt)
        return True
    except Exception as e:
        st.error(f"GOTO failed: {e}")
        return False

def send_land():
    """Land at current position"""
    if not st.session_state.master:
        return False
    try:
        from pymavlink import mavutil
        master = st.session_state.master
        master.mav.set_mode_send(
            master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            9  # LAND
        )
        return True
    except:
        return False

# ============== MAP ==============

def create_map(drone_data: dict, trail: list, target: Optional[Tuple] = None):
    """Create PyDeck map with drone position"""
    layers = []
    
    # Base marker
    base_df = pd.DataFrame([{
        'lat': BASE_LAT, 'lon': BASE_LON,
        'color': [0, 255, 136, 200]
    }])
    layers.append(pdk.Layer(
        'ScatterplotLayer',
        data=base_df,
        get_position=['lon', 'lat'],
        get_fill_color='color',
        get_radius=50,
    ))
    
    # Trail
    if len(trail) > 1:
        path = [[p[1], p[0]] for p in trail]
        trail_df = pd.DataFrame([{'path': path, 'color': [0, 200, 255, 150]}])
        layers.append(pdk.Layer(
            'PathLayer',
            data=trail_df,
            get_path='path',
            get_color='color',
            width_scale=2,
            width_min_pixels=2,
        ))
    
    # Target marker
    if target:
        target_df = pd.DataFrame([{
            'lat': target[0], 'lon': target[1],
            'color': [255, 200, 0, 255]
        }])
        layers.append(pdk.Layer(
            'ScatterplotLayer',
            data=target_df,
            get_position=['lon', 'lat'],
            get_fill_color='color',
            get_radius=40,
        ))
    
    # Drone marker (3D column)
    if drone_data['alt'] > 0:
        drone_df = pd.DataFrame([{
            'lat': drone_data['lat'],
            'lon': drone_data['lon'],
            'altitude': drone_data['alt'],
            'color': [255, 100, 100, 255] if drone_data['armed'] else [100, 100, 100, 255]
        }])
        layers.append(pdk.Layer(
            'ColumnLayer',
            data=drone_df,
            get_position=['lon', 'lat'],
            get_elevation='altitude',
            elevation_scale=1,
            get_fill_color='color',
            radius=20,
        ))
    
    # Drone top marker
    drone_top_df = pd.DataFrame([{
        'lat': drone_data['lat'],
        'lon': drone_data['lon'],
        'color': [255, 255, 255, 255]
    }])
    layers.append(pdk.Layer(
        'ScatterplotLayer',
        data=drone_top_df,
        get_position=['lon', 'lat'],
        get_fill_color='color',
        get_radius=25,
    ))
    
    view = pdk.ViewState(
        latitude=drone_data['lat'],
        longitude=drone_data['lon'],
        zoom=15,
        pitch=50,
        bearing=0
    )
    
    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    )

# ============== UI ==============

st.markdown("# 🚁 REAL DRONE CONTROL")
st.markdown("*Connected to SITL via MAVLink - No fake animations!*")

# Layout
col_left, col_map, col_right = st.columns([1.2, 3, 1.2])

# LEFT PANEL - Connection & Commands
with col_left:
    st.markdown("### 🔌 Connection")
    
    port = st.number_input("SITL Port", value=5760, min_value=5760, max_value=5800)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔗 Connect", use_container_width=True, disabled=st.session_state.connected):
            with st.spinner("Connecting..."):
                if connect_sitl(port):
                    st.success("Connected!")
                    st.rerun()
    with col2:
        if st.button("🔌 Disconnect", use_container_width=True, disabled=not st.session_state.connected):
            disconnect()
            st.rerun()
    
    if st.session_state.connected:
        st.markdown('<p class="status-online">● CONNECTED</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-offline">● DISCONNECTED</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎮 Flight Commands")
    
    if st.session_state.connected:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 ARM", use_container_width=True, type="primary"):
                if send_arm():
                    st.success("Armed!")
        with col2:
            if st.button("🔒 DISARM", use_container_width=True):
                if send_disarm():
                    st.success("Disarmed!")
        
        takeoff_alt = st.slider("Takeoff Altitude", 10, 100, 50)
        if st.button("🛫 TAKEOFF", use_container_width=True):
            if send_takeoff(takeoff_alt):
                st.success(f"Taking off to {takeoff_alt}m!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 RTL", use_container_width=True):
                if send_rtl():
                    st.success("Returning home!")
        with col2:
            if st.button("🛬 LAND", use_container_width=True):
                if send_land():
                    st.success("Landing!")
        
        st.markdown("---")
        st.markdown("### 📍 GO TO Location")
        
        goto_lat = st.number_input("Target Latitude", value=44.815, format="%.5f", step=0.001)
        goto_lon = st.number_input("Target Longitude", value=20.465, format="%.5f", step=0.001)
        goto_alt = st.number_input("Target Altitude", value=50, min_value=10, max_value=120)
        
        if st.button("🎯 FLY TO TARGET", use_container_width=True, type="primary"):
            if send_goto(goto_lat, goto_lon, goto_alt):
                st.success(f"Flying to ({goto_lat:.4f}, {goto_lon:.4f})!")
        
        # Quick waypoints
        st.markdown("#### Quick Waypoints")
        wp_col1, wp_col2 = st.columns(2)
        with wp_col1:
            if st.button("📍 NE", use_container_width=True):
                send_goto(BASE_LAT + 0.003, BASE_LON + 0.003, 50)
            if st.button("📍 SE", use_container_width=True):
                send_goto(BASE_LAT - 0.003, BASE_LON + 0.003, 50)
        with wp_col2:
            if st.button("📍 NW", use_container_width=True):
                send_goto(BASE_LAT + 0.003, BASE_LON - 0.003, 50)
            if st.button("📍 SW", use_container_width=True):
                send_goto(BASE_LAT - 0.003, BASE_LON - 0.003, 50)

# CENTER - Map
with col_map:
    st.markdown("### 🗺️ Live Map")
    
    # Get telemetry
    if st.session_state.connected:
        drone_data = get_telemetry()
    else:
        drone_data = st.session_state.drone_data
    
    # Create map
    deck = create_map(drone_data, st.session_state.trail, st.session_state.target)
    st.pydeck_chart(deck, use_container_width=True, height=500)
    
    # Legend
    st.markdown("""
    **Legend:** 🟢 Base | ⚪ Drone | 🟡 Target | 🔵 Trail
    """)

# RIGHT PANEL - Telemetry
with col_right:
    st.markdown("### 📊 Telemetry")
    
    if st.session_state.connected:
        data = st.session_state.drone_data
        
        # Big altitude display
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #161b22; border-radius: 8px; margin-bottom: 15px;">
            <div style="color: #8b949e; font-size: 0.8rem;">ALTITUDE</div>
            <div class="big-metric">{data['alt']:.1f}m</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status grid
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mode", data['mode'])
            st.metric("Speed", f"{data['speed']:.1f} m/s")
            st.metric("GPS Fix", f"Type {data['gps_fix']}")
        with col2:
            st.metric("Armed", "✅ YES" if data['armed'] else "❌ NO")
            st.metric("Heading", f"{data['heading']:.0f}°")
            st.metric("Battery", f"{data['battery']}%")
        
        st.markdown("---")
        st.markdown("### 📍 Position")
        st.code(f"""
Latitude:  {data['lat']:.6f}
Longitude: {data['lon']:.6f}
Altitude:  {data['alt']:.1f} m
        """)
        
        # Target info
        if st.session_state.target:
            t = st.session_state.target
            st.markdown("### 🎯 Current Target")
            st.code(f"({t[0]:.5f}, {t[1]:.5f}) @ {t[2]}m")
            
            # Distance to target
            dlat = (t[0] - data['lat']) * 111000
            dlon = (t[1] - data['lon']) * 111000 * math.cos(math.radians(data['lat']))
            dist = math.sqrt(dlat**2 + dlon**2)
            st.metric("Distance to Target", f"{dist:.0f} m")
        
        # Clear trail button
        if st.button("🗑️ Clear Trail", use_container_width=True):
            st.session_state.trail = []
            st.session_state.target = None
    else:
        st.info("Connect to SITL to see telemetry")

# Footer
st.markdown("---")
if st.session_state.connected:
    st.caption(f"🔗 Connected to SITL on port {port} | Last update: {time.strftime('%H:%M:%S')}")
else:
    st.caption("⚠️ Not connected - Start SITL with: `python -m dronekit_sitl copter --home=44.8125,20.4612,0,0`")

# Auto-refresh when connected
if st.session_state.connected:
    time.sleep(0.3)
    st.rerun()

