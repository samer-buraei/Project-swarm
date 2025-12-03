import streamlit as st
import folium
from streamlit_folium import st_folium
import time
import socket
import threading
import json
import pydeck as pdk
import os
import csv

# --- CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
FRAME_PATH = "live_frame.jpg"  # Shared frame from simulation

st.set_page_config(
    page_title="FIRE SWARM COMMAND", 
    layout="wide", 
    page_icon="🔥",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if 'fire_detected' not in st.session_state:
    st.session_state.fire_detected = False
if 'drone_pos' not in st.session_state:
    st.session_state.drone_pos = [44.8125, 20.4612]
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'event_log' not in st.session_state:
    st.session_state.event_log = []
if 'confidence' not in st.session_state:
    st.session_state.confidence = 0.0
if 'fps' not in st.session_state:
    st.session_state.fps = 0.0
if 'inference_ms' not in st.session_state:
    st.session_state.inference_ms = 0.0
if 'detections' not in st.session_state:
    st.session_state.detections = 0
if 'drone_timestamp' not in st.session_state:
    st.session_state.drone_timestamp = "--:--:--"

# --- UDP LISTENER (Background Thread) ---
def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((UDP_IP, UDP_PORT))
    except OSError:
        print("⚠️ Socket already bound. Assuming previous listener is active.")
        return

    sock.settimeout(0.1)
    
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode())
            
            # Save state to file (Streamlit workaround)
            with open("drone_state.json", "w") as f:
                json.dump(message, f)
                
        except socket.timeout:
            continue
        except Exception as e:
            pass  # Silently ignore errors

# Start listener once
if 'listener_started' not in st.session_state:
    t = threading.Thread(target=udp_listener, daemon=True)
    t.start()
    st.session_state.listener_started = True

# --- LOGGING FUNCTION ---
def log_detection(pos, conf):
    file_exists = os.path.isfile('detection_log.csv')
    with open('detection_log.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Confidence'])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), pos[0], pos[1], conf])

# --- LOAD HISTORY FROM CSV ---
if not st.session_state.event_log and os.path.isfile('detection_log.csv'):
    try:
        with open('detection_log.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            rows = list(reader)
            for row in reversed(rows[-10:]):  # Last 10 entries
                if len(row) >= 4:
                    st.session_state.event_log.append(
                        f"[{row[0].split(' ')[1]}] 🔥 Fire at [{float(row[1]):.4f}, {float(row[2]):.4f}] ({float(row[3]):.0%})"
                    )
    except Exception as e:
        pass

# --- READ STATE FROM FILE ---
try:
    with open("drone_state.json", "r") as f:
        state = json.load(f)
        new_pos = state.get("gps", [44.8125, 20.4612])
        new_fire = state.get("fire", False)
        new_conf = state.get("conf", 0.0)
        
        # Update extended telemetry
        st.session_state.fps = state.get("fps", 0.0)
        st.session_state.inference_ms = state.get("inference_ms", 0.0)
        st.session_state.detections = state.get("detections", 0)
        st.session_state.drone_timestamp = state.get("timestamp", "--:--:--")
        
        # Log new fire detections
        if new_fire and not st.session_state.fire_detected:
            timestamp = time.strftime("%H:%M:%S")
            st.session_state.event_log.insert(0, 
                f"[{timestamp}] 🔥 Fire at [{new_pos[0]:.4f}, {new_pos[1]:.4f}] ({new_conf:.0%})"
            )
            log_detection(new_pos, new_conf)
            # Keep only last 20 events
            st.session_state.event_log = st.session_state.event_log[:20]
            
        st.session_state.drone_pos = new_pos
        st.session_state.fire_detected = new_fire
        st.session_state.confidence = new_conf
        
except FileNotFoundError:
    pass
except json.JSONDecodeError:
    pass
except Exception as e:
    pass

# --- UI STYLING ---
st.markdown("""
<style>
    /* Dark tactical theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
    }
    
    /* Glass panel effect */
    .glass-panel {
        background: rgba(20, 20, 40, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(100, 100, 150, 0.3);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* Fire alert styling */
    .fire-alert {
        background: linear-gradient(135deg, rgba(255, 50, 50, 0.3) 0%, rgba(255, 100, 50, 0.2) 100%);
        border: 2px solid #ff4444;
        color: #ff6666 !important;
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        animation: pulse-fire 1.5s ease-in-out infinite;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    @keyframes pulse-fire {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 50, 50, 0.5); }
        50% { box-shadow: 0 0 30px rgba(255, 50, 50, 0.8); }
    }
    
    /* Status indicator */
    .status-ok {
        color: #00ff88 !important;
        font-weight: bold;
    }
    .status-alert {
        color: #ff4444 !important;
        font-weight: bold;
    }
    
    /* Text colors */
    h1, h2, h3, h4, p, div, span {
        color: #e0e0e0 !important;
    }
    
    /* Metric styling */
    .metric-box {
        text-align: center;
        padding: 10px;
        background: rgba(0, 100, 255, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(0, 100, 255, 0.3);
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00ff88 !important;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #888 !important;
        text-transform: uppercase;
    }
    
    /* Event log styling */
    .event-item {
        border-bottom: 1px solid rgba(100, 100, 150, 0.2);
        padding: 8px 0;
        font-size: 0.85rem;
        font-family: 'Consolas', 'Monaco', monospace;
    }
    
    /* Video feed container */
    .video-container {
        border: 2px solid rgba(0, 100, 255, 0.5);
        border-radius: 8px;
        overflow: hidden;
        background: #000;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
status_class = "status-alert" if st.session_state.fire_detected else "status-ok"
status_text = "⚠️ ALERT" if st.session_state.fire_detected else "● ONLINE"

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <h1 style="margin: 0;">🦅 FIRE SWARM COMMAND</h1>
    <span class="{status_class}" style="font-size: 1.2rem;">{status_text}</span>
</div>
""", unsafe_allow_html=True)

# --- MAIN LAYOUT ---
col_left, col_right = st.columns([2, 1])

# === LEFT COLUMN: MAP + VIDEO ===
with col_left:
    # --- TACTICAL MAP ---
    st.markdown("### 🗺️ TACTICAL MAP")
    
    layers = []
    
    # Satellite background
    satellite_layer = pdk.Layer(
        "TileLayer",
        data="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        id="satellite-layer",
        min_zoom=0,
        max_zoom=19,
        tileSize=256,
    )
    layers.append(satellite_layer)
    
    # Drone position (blue dot)
    drone_layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"pos": [st.session_state.drone_pos[1], st.session_state.drone_pos[0]], "name": "Drone A-1"}],
        get_position="pos",
        get_color=[0, 150, 255, 220],
        get_radius=25,
        pickable=True,
    )
    layers.append(drone_layer)
    
    # Fire marker (red pulsing)
    if st.session_state.fire_detected:
        fire_layer = pdk.Layer(
            "ScatterplotLayer",
            data=[{"pos": [st.session_state.drone_pos[1], st.session_state.drone_pos[0]]}],
            get_position="pos",
            get_color=[255, 50, 50, 180],
            get_radius=80,
            pickable=True,
        )
        layers.append(fire_layer)

    view_state = pdk.ViewState(
        latitude=st.session_state.drone_pos[0],
        longitude=st.session_state.drone_pos[1],
        zoom=15,
        pitch=0,
    )

    st.pydeck_chart(pdk.Deck(
        map_provider=None,
        map_style=None,
        initial_view_state=view_state,
        layers=layers,
        tooltip={"text": "{name}"}
    ), height=350)
    
    # Fire alert banner
    if st.session_state.fire_detected:
        st.markdown(f"""
        <div class='fire-alert'>
            🔥 FIRE DETECTED — Lat: {st.session_state.drone_pos[0]:.5f}, Lon: {st.session_state.drone_pos[1]:.5f}
        </div>
        """, unsafe_allow_html=True)

    # --- LIVE VIDEO FEED ---
    st.markdown("### 📹 LIVE DRONE FEED")
    
    # Check if frame exists
    if os.path.exists(FRAME_PATH):
        try:
            # Read and display the live frame
            st.image(FRAME_PATH, caption=f"Drone Camera — {st.session_state.drone_timestamp}", use_container_width=True)
        except Exception as e:
            st.warning("⏳ Waiting for drone feed...")
    else:
        st.info("📡 Waiting for drone connection... Make sure `simulation.py` is running.")

# === RIGHT COLUMN: TELEMETRY + LOGS ===
with col_right:
    # --- LIVE TELEMETRY ---
    st.markdown("### 📡 TELEMETRY")
    
    # Detection status
    if st.session_state.fire_detected:
        st.markdown(f"""
        <div class="glass-panel" style="border-color: #ff4444; background: rgba(255, 50, 50, 0.1);">
            <h3 style="color: #ff4444 !important; margin: 0; text-align: center;">⚠️ FIRE ALERT</h3>
            <p style="text-align: center; margin: 5px 0; font-size: 1.5rem; color: #ff6666 !important;">
                {st.session_state.confidence:.0%} CONFIDENCE
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-panel">
            <h4 style="color: #00ff88 !important; margin: 0;">✓ STATUS: PATROL</h4>
            <p style="margin: 5px 0; font-size: 0.9rem;">All sensors nominal</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics grid
    st.markdown(f"""
    <div class="glass-panel">
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
            <div class="metric-box">
                <div class="metric-label">Drone ID</div>
                <div class="metric-value">A-1</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">FPS</div>
                <div class="metric-value">{st.session_state.fps:.1f}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Inference</div>
                <div class="metric-value">{st.session_state.inference_ms:.0f}ms</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Detections</div>
                <div class="metric-value">{st.session_state.detections}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # GPS coordinates
    st.markdown(f"""
    <div class="glass-panel">
        <div class="metric-label">GPS POSITION</div>
        <div style="font-family: monospace; font-size: 0.9rem;">
            LAT: {st.session_state.drone_pos[0]:.6f}<br>
            LON: {st.session_state.drone_pos[1]:.6f}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- EVENT LOG ---
    st.markdown("### 📜 EVENT LOG")
    
    if st.session_state.event_log:
        log_html = ""
        for event in st.session_state.event_log[:8]:
            log_html += f'<div class="event-item">{event}</div>'
        st.markdown(f'<div class="glass-panel">{log_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-panel">
            <p style="color: #666 !important; text-align: center; margin: 0;">No events yet</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- CONTROLS ---
    st.markdown("### 🎮 CONTROLS")
    st.markdown("""
    <div class="glass-panel">
        <p style="font-size: 0.85rem; margin: 0;">
            <strong>Simulation Controls:</strong><br>
            • Press <code>f</code> in drone window → Trigger fire<br>
            • Press <code>q</code> in drone window → Quit
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
<div style="text-align: center; padding: 20px; color: #444 !important; font-size: 0.8rem;">
    Last Update: {time.strftime("%H:%M:%S")} | Fire Swarm Command v0.1
</div>
""", unsafe_allow_html=True)

# --- AUTO REFRESH ---
time.sleep(0.5)  # Faster refresh for smoother video
st.rerun()
