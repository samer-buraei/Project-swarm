"""
LIVE DRONE MAP VISUALIZATION
============================
Shows the drone flying on a real map in real-time!

Connects to SITL and displays:
- Drone position (moving marker)
- Flight path (trail)
- Home base
- Fire detections

Usage:
    1. Start SITL: python -m dronekit_sitl copter --home=44.8125,20.4612,0,0
    2. Run this: streamlit run live_map.py
    3. In another terminal: python full_simulation_test.py
"""

import streamlit as st
import time
import json
import folium
from streamlit_folium import st_folium
from collections import deque
import threading

# Page config
st.set_page_config(
    page_title="🚁 Live Drone Map",
    page_icon="🚁",
    layout="wide"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .status-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .fire-alert {
        background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        font-weight: bold;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'positions' not in st.session_state:
    st.session_state.positions = deque(maxlen=100)  # Trail of last 100 positions
if 'fire_locations' not in st.session_state:
    st.session_state.fire_locations = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'drone_data' not in st.session_state:
    st.session_state.drone_data = {
        'lat': 44.8125,
        'lon': 20.4612,
        'alt': 0,
        'heading': 0,
        'mode': 'UNKNOWN',
        'armed': False
    }

# Header
st.markdown("# 🚁 LIVE DRONE MAP")
st.markdown("Real-time visualization of drone flight from SITL")

# Layout
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("### 📊 Drone Status")
    
    # Connection status
    status_placeholder = st.empty()
    
    # Drone data display
    data_placeholder = st.empty()
    
    # Fire alerts
    fire_placeholder = st.empty()
    
    # Controls
    st.markdown("### 🎮 Controls")
    if st.button("🔄 Refresh Connection", use_container_width=True):
        st.session_state.connected = False
        st.rerun()
    
    if st.button("🗑️ Clear Trail", use_container_width=True):
        st.session_state.positions.clear()
        st.session_state.fire_locations.clear()
        st.rerun()

with col1:
    map_placeholder = st.empty()

# Try to connect to SITL
def get_drone_position():
    """Get current drone position from SITL"""
    try:
        from pymavlink import mavutil
        
        if not hasattr(st.session_state, 'mavlink_conn') or st.session_state.mavlink_conn is None:
            st.session_state.mavlink_conn = mavutil.mavlink_connection('tcp:127.0.0.1:5760', timeout=2)
            # Wait for heartbeat
            msg = st.session_state.mavlink_conn.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
            if msg:
                st.session_state.connected = True
                # Request data streams
                st.session_state.mavlink_conn.mav.request_data_stream_send(
                    st.session_state.mavlink_conn.target_system,
                    st.session_state.mavlink_conn.target_component,
                    mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1
                )
        
        if st.session_state.connected:
            master = st.session_state.mavlink_conn
            
            # Get position
            msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=1)
            if msg:
                st.session_state.drone_data['lat'] = msg.lat / 1e7
                st.session_state.drone_data['lon'] = msg.lon / 1e7
                st.session_state.drone_data['alt'] = msg.relative_alt / 1000
                st.session_state.drone_data['heading'] = msg.hdg / 100 if msg.hdg else 0
            
            # Get heartbeat for mode/armed
            msg = master.recv_match(type='HEARTBEAT', blocking=False)
            if msg:
                st.session_state.drone_data['armed'] = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                # Decode mode
                mode_map = {0: 'STABILIZE', 3: 'AUTO', 4: 'GUIDED', 5: 'LOITER', 6: 'RTL', 9: 'LAND'}
                st.session_state.drone_data['mode'] = mode_map.get(msg.custom_mode, str(msg.custom_mode))
            
            return True
    except Exception as e:
        st.session_state.connected = False
        st.session_state.mavlink_conn = None
        return False
    
    return False

# Main loop
def update_display():
    # Try to get drone position
    connected = get_drone_position()
    
    # Update status
    with status_placeholder.container():
        if connected:
            st.success("🟢 Connected to SITL")
        else:
            st.error("🔴 Not connected to SITL")
            st.caption("Start SITL: `python -m dronekit_sitl copter`")
    
    # Update drone data display
    with data_placeholder.container():
        d = st.session_state.drone_data
        
        armed_icon = "🟢" if d['armed'] else "🔴"
        
        st.markdown(f"""
        <div class="status-box">
            <b>📍 Position</b><br>
            Lat: {d['lat']:.6f}<br>
            Lon: {d['lon']:.6f}<br>
            Alt: {d['alt']:.1f}m<br>
            <br>
            <b>🎚️ Status</b><br>
            Mode: {d['mode']}<br>
            Armed: {armed_icon} {'YES' if d['armed'] else 'NO'}<br>
            Heading: {d['heading']:.0f}°
        </div>
        """, unsafe_allow_html=True)
    
    # Add position to trail
    if connected:
        pos = (st.session_state.drone_data['lat'], st.session_state.drone_data['lon'])
        if not st.session_state.positions or st.session_state.positions[-1] != pos:
            st.session_state.positions.append(pos)
    
    # Update fire alerts
    with fire_placeholder.container():
        if st.session_state.fire_locations:
            st.markdown("""
            <div class="fire-alert">
                🔥 FIRE DETECTED!<br>
                {} location(s)
            </div>
            """.format(len(st.session_state.fire_locations)), unsafe_allow_html=True)
    
    # Create map
    d = st.session_state.drone_data
    
    # Center on drone or default location
    m = folium.Map(
        location=[d['lat'], d['lon']],
        zoom_start=16,
        tiles='cartodbdark_matter'
    )
    
    # Add home marker
    folium.Marker(
        [44.8125, 20.4612],
        popup='🏠 Home Base',
        icon=folium.Icon(color='green', icon='home', prefix='fa')
    ).add_to(m)
    
    # Add flight trail
    if len(st.session_state.positions) > 1:
        trail = list(st.session_state.positions)
        folium.PolyLine(
            trail,
            color='cyan',
            weight=3,
            opacity=0.8
        ).add_to(m)
    
    # Add drone marker
    drone_color = 'red' if d['armed'] else 'blue'
    folium.Marker(
        [d['lat'], d['lon']],
        popup=f"🚁 Drone\nAlt: {d['alt']:.1f}m\nMode: {d['mode']}",
        icon=folium.Icon(color=drone_color, icon='plane', prefix='fa')
    ).add_to(m)
    
    # Add altitude circle (visual indicator)
    if d['alt'] > 0:
        folium.Circle(
            [d['lat'], d['lon']],
            radius=d['alt'] / 2,  # Scale altitude to radius
            color='cyan',
            fill=True,
            fillOpacity=0.2
        ).add_to(m)
    
    # Add fire markers
    for fire_loc in st.session_state.fire_locations:
        folium.Marker(
            fire_loc,
            popup='🔥 Fire Detected!',
            icon=folium.Icon(color='red', icon='fire', prefix='fa')
        ).add_to(m)
    
    # Display map
    with map_placeholder:
        st_folium(m, width=800, height=600, returned_objects=[])

# Run update loop
update_display()

# Auto-refresh
time.sleep(0.5)
st.rerun()

