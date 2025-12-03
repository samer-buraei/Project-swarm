# 🔥 Fire Swarm - System Architecture

**Last Updated:** November 28, 2024  
**Status:** Phase 0 Complete - Full PC Simulation Working

---

## 📋 What We Built

A complete **multi-drone wildfire detection system** that can be fully tested on PC before deploying to real hardware.

### Capabilities
- ✅ 5 simulated drones with real Pixhawk firmware (SITL)
- ✅ Real MAVLink communication (same protocol as real hardware)
- ✅ Fire detection with YOLOv8
- ✅ Multi-drone fleet control dashboard
- ✅ Patrol pattern generation
- ✅ 3D map visualization
- ✅ Individual and fleet commands

---

## 🗂️ File Architecture

```
Project swarm/
│
├── 🚀 LAUNCHERS
│   ├── launch_fleet.py          # Start 5 SITL drones
│   ├── run_demo.bat             # Quick start script
│   └── multi_drone_launcher.py  # Legacy multi-drone launcher
│
├── 🎮 DASHBOARDS
│   ├── dashboard_fleet_real.py  # ⭐ MAIN: Real 5-drone control
│   ├── dashboard_real.py        # Single drone real control
│   ├── dashboard_fleet.py       # Patrol pattern planner (demo)
│   ├── dashboard_3d.py          # 3D PyDeck visualization
│   ├── dashboard_sitl.py        # SITL + Folium map
│   ├── dashboard_multi.py       # Multi-drone UDP dashboard
│   └── dashboard.py             # Original single-drone dashboard
│
├── 🔥 DETECTION
│   ├── simulation.py            # YOLO fire detection simulation
│   ├── yolo_benchmark.py        # Model performance testing
│   └── yolov8n.pt              # Pre-trained YOLO model
│
├── 🚁 DRONE CONTROL
│   ├── drone_control.py         # MAVLink drone controller class
│   ├── patrol_simulator.py      # Patrol pattern simulation
│   ├── test_sitl.py            # DroneKit SITL test (legacy)
│   ├── test_sitl_mavlink.py    # PyMAVLink SITL test
│   └── full_simulation_test.py  # Complete mission test
│
├── 📊 UTILITIES
│   ├── recorder.py              # Recording system for training data
│   ├── test_video.py           # Test detection on video files
│   └── live_map.py             # Live map generation
│
├── 📁 scripts/
│   ├── test_fire_detection.py   # Benchmark on D-Fire dataset
│   ├── simulate_pi4.py          # Pi 4 performance simulation
│   ├── prepare_training_data.py # Dataset preparation
│   ├── train_fire_model.py      # Model training
│   ├── export_model.py          # Export to TFLite
│   └── evaluate_model.py        # Model evaluation
│
├── 📚 docs/
│   ├── SYSTEM_ARCHITECTURE.md   # ⭐ THIS FILE
│   ├── SITL_SETUP_GUIDE.md      # SITL installation guide
│   ├── SESSION_FLIGHT_SIMULATION.md
│   ├── PROJECT_STATE.md         # Master project status
│   └── ...other docs
│
└── 📦 CONFIG
    ├── requirements.txt         # Python dependencies
    └── README.md               # Project overview
```

---

## 🎯 Key Files Explained

### 1. `launch_fleet.py` - Fleet Launcher
**Purpose:** Starts 5 ArduPilot SITL instances on different ports.

```python
# Configuration (lines 15-21)
DRONES = [
    {"id": "D1", "port": 5760, "lat": 44.8125, "lon": 20.4612},
    {"id": "D2", "port": 5770, "lat": 44.8135, "lon": 20.4622},
    {"id": "D3", "port": 5780, "lat": 44.8115, "lon": 20.4602},
    {"id": "D4", "port": 5790, "lat": 44.8140, "lon": 20.4592},
    {"id": "D5", "port": 5800, "lat": 44.8110, "lon": 20.4632},
]
```

**Configurable:**
- Number of drones (add/remove from list)
- Port numbers (must be unique, 5760+ recommended)
- Home positions (lat/lon for each drone)

---

### 2. `dashboard_fleet_real.py` - Main Fleet Control
**Purpose:** Real-time control of all 5 drones via MAVLink.

```python
# Drone configuration (lines 50-56)
DRONE_CONFIG = [
    {"id": "D1", "port": 5760, "color": [255, 107, 107], "name": "Alpha"},
    {"id": "D2", "port": 5770, "color": [78, 205, 196], "name": "Bravo"},
    ...
]

# Base location (line 58)
BASE_LAT = 44.8125
BASE_LON = 20.4612
```

**Configurable:**
- Drone names and colors
- Base station location
- Takeoff altitude (in `send_command()`)
- Trail length (`maxlen=200` in deque)

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `connect_drone(port)` | Connect to SITL via MAVLink |
| `get_telemetry(master, drone)` | Read position, mode, armed status |
| `send_command(master, cmd)` | Send ARM, TAKEOFF, RTL, GOTO |
| `create_fleet_map()` | Generate PyDeck 3D map |

---

### 3. `dashboard_fleet.py` - Patrol Planner
**Purpose:** Generate and visualize patrol patterns (demo mode).

```python
# Surveillance area (session state)
st.session_state.area = {
    'lat_min': 44.810,
    'lat_max': 44.815,
    'lon_min': 20.458,
    'lon_max': 20.465
}
```

**Patrol Patterns:**
| Pattern | Function | Description |
|---------|----------|-------------|
| Grid | `generate_grid_pattern()` | Column sweeps |
| Perimeter | `generate_perimeter_pattern()` | Boundary patrol |
| Spiral | `generate_spiral_pattern()` | Converge to center |
| Sector | `generate_sector_pattern()` | Pie slice zones |
| Lawnmower | `generate_lawnmower_pattern()` | Horizontal sweeps |

---

### 4. `simulation.py` - Fire Detection
**Purpose:** Run YOLO inference on video/images, send telemetry.

```python
# Configuration (top of file)
MODEL_PATH = "yolov8n.pt"
CONF_THRESHOLD = 0.5
UDP_IP = "127.0.0.1"
UDP_PORT = 5001
```

**Configurable:**
- Model path (can use custom trained model)
- Confidence threshold for detections
- UDP port for telemetry
- Frame save path for dashboard

---

### 5. `scripts/simulate_pi4.py` - Pi 4 Simulator
**Purpose:** Throttle inference to match Raspberry Pi 4 performance.

```python
# Configuration
THROTTLE_FACTOR = 6.0  # PC is ~6x faster than Pi 4
TELEMETRY_INTERVAL = 2.0  # Send data every 2 seconds
```

---

## 🔧 Configuration Quick Reference

### Change Base Location (Belgrade → Your Location)
```python
# In any dashboard file:
BASE_LAT = 44.8125  # Change to your latitude
BASE_LON = 20.4612  # Change to your longitude
```

### Change Number of Drones
```python
# In launch_fleet.py and dashboard_fleet_real.py:
# Add/remove entries from DRONES list
DRONES = [
    {"id": "D1", "port": 5760, ...},
    {"id": "D2", "port": 5770, ...},
    # Add more here
]
```

### Change Takeoff Altitude
```python
# In dashboard_fleet_real.py, send_command function:
elif cmd == "TAKEOFF":
    alt = kwargs.get('alt', 50)  # Default 50m, change here
```

### Change Map Style
```python
# In any dashboard with PyDeck:
map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'

# Alternatives:
# 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'  # Light
# 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json'   # Color
```

### Change YOLO Model
```python
# In simulation.py:
MODEL_PATH = "yolov8n.pt"  # Pre-trained
# Or use custom:
MODEL_PATH = "models/fire_detector_v1.pt"
```

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start 5 simulated drones
python launch_fleet.py

# 3. Start fleet control (new terminal)
streamlit run dashboard_fleet_real.py --server.port 8506

# 4. Open browser
# http://localhost:8506
```

---

## 📡 Port Reference

| Port | Service |
|------|---------|
| 5760 | SITL Drone 1 (D1-Alpha) |
| 5770 | SITL Drone 2 (D2-Bravo) |
| 5780 | SITL Drone 3 (D3-Charlie) |
| 5790 | SITL Drone 4 (D4-Delta) |
| 5800 | SITL Drone 5 (D5-Echo) |
| 8501-8506 | Streamlit dashboards |

---

## 🔗 Dashboard URLs

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| Fleet Control | http://localhost:8506 | **Main** - 5 drone control |
| Single Drone | http://localhost:8505 | Single drone testing |
| 3D Map | http://localhost:8503 | 3D visualization |
| Patrol Planner | http://localhost:8504 | Pattern generation |

---

## 📈 What's Next (Phase 1)

1. **Hardware Acquisition**
   - Raspberry Pi 4 (×5)
   - Pixhawk flight controllers (×5)
   - Thermal cameras (×5)
   - LoRa radios

2. **Real Hardware Testing**
   - Flash ArduCopter to Pixhawks
   - Connect Pi 4 to Pixhawk via MAVLink
   - Test fire detection with thermal camera
   - Deploy to actual drones

3. **Training**
   - Download FLAME dataset
   - Train fire-specific YOLO model
   - Export to TFLite for Pi 4

---

## 🏆 Phase 0 Achievements

| Test | Status | Result |
|------|--------|--------|
| Fire Detection | ✅ | 18.9ms inference |
| Pi 4 Simulation | ✅ | 7+ FPS validated |
| SITL Connection | ✅ | MAVLink working |
| Multi-Drone | ✅ | 5 drones controlled |
| Fleet Commands | ✅ | ARM/TAKEOFF/RTL/GOTO |
| 3D Visualization | ✅ | PyDeck maps |
| Patrol Patterns | ✅ | 5 patterns available |

**Verdict: Ready for hardware! 🎉**

