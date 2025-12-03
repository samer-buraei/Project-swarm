import streamlit as st
import pydeck as pdk
import socket
import threading
import json
import time
import os
import glob

# --- CONFIGURATION ---
UDP_PORTS = [5001, 5002, 5003, 5004, 5005]
DRONE_IDS = ["A1", "A2", "A3", "A4", "A5"]
UDP_IP = "127.0.0.1"

st.set_page_config(
    page_title="FIRE SWARM COMMAND (MULTI-DRONE)", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if 'drones' not in st.session_state:
    st.session_state.drones = {}
    for did in DRONE_IDS:
        st.session_state.drones[did] = {
            "gps": [44.8125, 20.4612], # Default Belgrade
            "fire": False,
            "conf": 0.0,
            "fps": 0.0,
            "last_update": 0
        }

if 'event_log' not in st.session_state:
    st.session_state.event_log = []

# --- UDP LISTENER (Multi-Port) ---
def udp_listener(port, drone_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((UDP_IP, port))
    except OSError:
        return # Already bound

    sock.settimeout(0.1)
    
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode())
            
            # Update global state file (simple IPC)
            # In production, use a proper database or shared memory
            state_file = f"drone_state_{drone_id}.json"
            with open(state_file, "w") as f:
                json.dump(message, f)
                
        except socket.timeout:
            continue
        except Exception:
            pass

# Start listeners
if 'listeners_started' not in st.session_state:
    for i, port in enumerate(UDP_PORTS):
        did = DRONE_IDS[i]
        t = threading.Thread(target=udp_listener, args=(port, did), daemon=True)
        t.start()
    st.session_state.listeners_started = True

# --- READ STATES ---
for did in DRONE_IDS:
    try:
        with open(f"drone_state_{did}.json", "r") as f:
            data = json.load(f)
            
            # Check for new fire event
            if data.get("fire") and not st.session_state.drones[did]["fire"]:
                timestamp = time.strftime("%H:%M:%S")
                pos = data.get("gps")
                conf = data.get("conf", 0)
                log_entry = f"[{timestamp}] 🦅 {did}: 🔥 FIRE DETECTED at {pos} ({conf:.0%})"
                st.session_state.event_log.insert(0, log_entry)
            
            st.session_state.drones[did] = data
            st.session_state.drones[did]["last_update"] = time.time()
    except:
        pass # No state yet

# --- UI STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .drone-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    .status-ok { color: #00ff88; font-weight: bold; }
    .status-alert { color: #ff4444; font-weight: bold; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .metric-val { font-size: 1.2rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("## 🦅 FIRE SWARM COMMAND <span style='font-size:1rem; color:#888'>| MULTI-DRONE FLEET VIEW</span>", unsafe_allow_html=True)

# --- FLEET STATUS BAR ---
cols = st.columns(len(DRONE_IDS))
for i, did in enumerate(DRONE_IDS):
    d = st.session_state.drones[did]
    status_color = "🔴" if d["fire"] else "🟢"
    with cols[i]:
        st.markdown(f"""
        <div class="drone-card">
            <div>{status_color} <strong>{did}</strong></div>
            <div style="font-size:0.8rem">FPS: {d.get('fps', 0):.1f}</div>
        </div>
        """, unsafe_allow_html=True)

# --- MAIN GRID ---
c_map, c_logs = st.columns([2, 1])

with c_map:
    st.markdown("### 🗺️ TACTICAL MAP")
    
    layers = []
    
    # Satellite
    layers.append(pdk.Layer(
        "TileLayer",
        data="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        min_zoom=0, max_zoom=19, tileSize=256
    ))
    
    # Drones
    drone_data = []
    for did in DRONE_IDS:
        d = st.session_state.drones[did]
        color = [255, 0, 0, 200] if d["fire"] else [0, 100, 255, 200]
        radius = 80 if d["fire"] else 30
        drone_data.append({
            "name": did,
            "pos": [d["gps"][1], d["gps"][0]], # Lon, Lat
            "color": color,
            "radius": radius
        })
        
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=drone_data,
        get_position="pos",
        get_color="color",
        get_radius="radius",
        pickable=True,
    ))
    
    # View State (Center on A1 or average)
    center = st.session_state.drones["A1"]["gps"]
    view_state = pdk.ViewState(latitude=center[0], longitude=center[1], zoom=14)
    
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=layers,
        tooltip={"text": "{name}"}
    ), height=400)

with c_logs:
    st.markdown("### 📜 FLEET LOGS")
    log_html = ""
    for event in st.session_state.event_log[:10]:
        color = "#ff4444" if "FIRE" in event else "#cccccc"
        log_html += f"<div style='color:{color}; border-bottom:1px solid #333; padding:4px; font-size:0.85rem'>{event}</div>"
    st.markdown(f"<div style='background:#111; padding:10px; border-radius:10px; height:400px; overflow-y:auto'>{log_html}</div>", unsafe_allow_html=True)

# --- VIDEO GRID ---
st.markdown("### 📹 LIVE FEEDS")
v_cols = st.columns(5)
for i, did in enumerate(DRONE_IDS):
    with v_cols[i]:
        st.markdown(f"**{did}**")
        frame_file = f"live_frame_{did}.jpg"
        if os.path.exists(frame_file):
            try:
                st.image(frame_file, use_container_width=True)
            except:
                st.info("Signal Lost")
        else:
            st.image("https://placehold.co/320x240/1a1a1a/444444?text=OFFLINE", use_container_width=True)

# --- FLEET COMMANDS ---
st.markdown("### 🎮 FLEET COMMANDS")
cmd_cols = st.columns([1, 1, 1, 1, 2])

with cmd_cols[0]:
    if st.button("🏠 RTL ALL", use_container_width=True, type="secondary"):
        # Save command to file for patrol simulator
        with open("fleet_command.json", "w") as f:
            json.dump({"command": "RTL_ALL", "timestamp": time.time()}, f)
        st.session_state.event_log.insert(0, f"[{time.strftime('%H:%M:%S')}] 📤 RTL ALL command sent")

with cmd_cols[1]:
    if st.button("⏸️ PAUSE ALL", use_container_width=True, type="secondary"):
        with open("fleet_command.json", "w") as f:
            json.dump({"command": "PAUSE_ALL", "timestamp": time.time()}, f)
        st.session_state.event_log.insert(0, f"[{time.strftime('%H:%M:%S')}] 📤 PAUSE ALL command sent")

with cmd_cols[2]:
    if st.button("▶️ RESUME ALL", use_container_width=True, type="secondary"):
        with open("fleet_command.json", "w") as f:
            json.dump({"command": "RESUME_ALL", "timestamp": time.time()}, f)
        st.session_state.event_log.insert(0, f"[{time.strftime('%H:%M:%S')}] 📤 RESUME ALL command sent")

with cmd_cols[3]:
    if st.button("🚨 EMERGENCY", use_container_width=True, type="primary"):
        with open("fleet_command.json", "w") as f:
            json.dump({"command": "EMERGENCY", "timestamp": time.time()}, f)
        st.session_state.event_log.insert(0, f"[{time.strftime('%H:%M:%S')}] 🚨 EMERGENCY LAND command sent")

with cmd_cols[4]:
    selected_drone = st.selectbox("Select Drone", DRONE_IDS, key="cmd_drone", label_visibility="collapsed")
    sub_cols = st.columns(2)
    with sub_cols[0]:
        if st.button(f"RTL {selected_drone}", use_container_width=True):
            with open("fleet_command.json", "w") as f:
                json.dump({"command": "RTL", "drone": selected_drone, "timestamp": time.time()}, f)
            st.session_state.event_log.insert(0, f"[{time.strftime('%H:%M:%S')}] 📤 RTL {selected_drone}")
    with sub_cols[1]:
        if st.button(f"VALIDATE", use_container_width=True):
            # Send nearest drone to validate fire location
            st.session_state.event_log.insert(0, f"[{time.strftime('%H:%M:%S')}] 📤 VALIDATE sent to {selected_drone}")

# --- FOOTER ---
st.markdown(f"""
<div style='text-align:center; color:#444; padding:10px; font-size:0.8rem'>
    Fire Swarm Command v0.2 | {len([d for d in st.session_state.drones.values() if d.get('fps', 0) > 0])}/{len(DRONE_IDS)} drones online | 
    Last update: {time.strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# Auto-refresh
time.sleep(0.5)
st.rerun()
