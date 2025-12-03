# 👩‍💻 Developer Guide & Code Tour

**A comprehensive guide to the Fire Drone Swarm codebase.**

Last Updated: December 3, 2025

---

## 📖 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Key Components](#key-components)
4. [Configuration System](#configuration-system)
5. [Fleet Control System](#fleet-control-system)
6. [Mission Planning System](#mission-planning-system)
7. [Fire Detection System](#fire-detection-system)
8. [How to Extend](#how-to-extend)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ System Overview

The Fire Drone Swarm is a multi-drone wildfire detection system with:

- **5 simulated drones** using DroneKit-SITL (ArduCopter)
- **Fleet Control Dashboard** (Streamlit + PyDeck 3D maps)
- **Mission Planner** (Streamlit + Folium drawing tools)
- **Fire Detection** (YOLOv8 with thermal simulation)
- **Offline architecture** (designed for LoRa, no cloud needed)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FIRE DRONE SWARM SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ launch_     │    │ dashboard_  │    │ dashboard_  │         │
│  │ fleet.py    │    │ fleet_      │    │ mission.py  │         │
│  │             │    │ real.py     │    │             │         │
│  │ Starts 5    │◄──►│ Fleet       │◄───│ Mission     │         │
│  │ SITL drones │    │ Control UI  │    │ Planner UI  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                  │                   │                 │
│        │                  │                   │                 │
│        ▼                  ▼                   ▼                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              MAVLink Protocol (TCP)                 │       │
│  │         Ports: 5760, 5761, 5762, 5763, 5764         │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Architecture

### Communication Flow

```
1. launch_fleet.py
   └─ Spawns 5 SITL (Software-In-The-Loop) drone instances
   └─ Each drone listens on TCP port 5760-5764

2. dashboard_fleet_real.py
   └─ Connects to drones via DroneKit
   └─ Reads telemetry: position, altitude, battery, mode
   └─ Sends commands: ARM, TAKEOFF, GOTO, RTL, LAND
   └─ Displays 3D map with PyDeck

3. dashboard_mission.py
   └─ User draws search areas on Folium map
   └─ Generates grid waypoints using Shapely
   └─ Exports mission JSON files

4. Mission Execution
   └─ Fleet dashboard loads mission JSON
   └─ Sends GOTO commands to drones sequentially
   └─ Tracks progress through waypoints
```

### File Organization

```
app/
├── FLEET CONTROL
│   ├── launch_fleet.py           # Start SITL instances
│   ├── dashboard_fleet_real.py   # Fleet UI (port 8506)
│   └── drone_control.py          # MAVLink utilities
│
├── MISSION PLANNING  
│   └── dashboard_mission.py      # Mission planner (port 8507)
│
├── FIRE DETECTION
│   ├── fire_detector_unified.py  # Main detection engine
│   ├── thermal_simulation.py     # Thermal camera simulation
│   └── test_all_models.py        # Model comparison
│
├── TRAINING
│   ├── train_fire_quick.py       # Quick training script
│   ├── train_kaggle_finetune.py  # Kaggle fine-tuning
│   └── check_training_status.py  # Monitor training
│
├── CONFIGURATION
│   ├── config.py                 # Central path management
│   └── config_local.example.py   # Template for private paths
│
└── UTILITIES
    ├── download_pretrained_fire.py
    ├── organize_kaggle_downloads.py
    └── ... (many more)
```

---

## 🔧 Key Components

### 1. Fleet Launcher (`launch_fleet.py`)

**Purpose:** Start 5 SITL drone simulators

**How it works:**
```python
from dronekit_sitl import SITL

DRONE_CONFIG = [
    {'id': 'A1', 'port': 5760, 'lat': 44.8176, 'lon': 20.4633},
    {'id': 'A2', 'port': 5761, 'lat': 44.8196, 'lon': 20.4653},
    # ... more drones
]

for drone in DRONE_CONFIG:
    sitl = SITL()
    sitl.download('copter', '4.3')  # Downloads ArduCopter firmware
    sitl.launch(['--home=' + home_location, '--instance=' + instance])
```

**Key Points:**
- First run downloads ~100MB of ArduCopter firmware
- Each drone gets a unique port (5760-5764)
- Each drone has a unique starting GPS position

---

### 2. Fleet Control Dashboard (`dashboard_fleet_real.py`)

**Purpose:** Real-time fleet management UI

**Key Features:**
- Connect to 5 drones via DroneKit
- Display telemetry in real-time
- Fleet commands (ARM ALL, TAKEOFF ALL, RTL ALL)
- Individual drone control
- 3D map with altitude columns
- Mission loading and execution

**Core Connection Logic:**
```python
from dronekit import connect, VehicleMode

def connect_drone(port):
    vehicle = connect(f'tcp:127.0.0.1:{port}', wait_ready=True)
    return vehicle

# Read telemetry
lat = vehicle.location.global_frame.lat
lon = vehicle.location.global_frame.lon
alt = vehicle.location.global_relative_frame.alt
battery = vehicle.battery.level
mode = vehicle.mode.name
```

**Command Sending:**
```python
def send_command(vehicle, cmd, **kwargs):
    if cmd == "ARM":
        vehicle.arm(wait=False)
    elif cmd == "TAKEOFF":
        vehicle.simple_takeoff(kwargs.get('alt', 50))
    elif cmd == "GOTO":
        target = LocationGlobalRelative(lat, lon, alt)
        vehicle.simple_goto(target)
    elif cmd == "RTL":
        vehicle.mode = VehicleMode("RTL")
```

**3D Map (PyDeck):**
```python
import pydeck as pdk

# Altitude columns for each drone
column_layer = pdk.Layer(
    "ColumnLayer",
    data=drone_df,
    get_position=["lon", "lat"],
    get_elevation="alt",
    get_fill_color=["r", "g", "b"],
    radius=20,
)
```

---

### 3. Mission Planner (`dashboard_mission.py`)

**Purpose:** Draw patrol areas and generate grid waypoints

**Key Features:**
- Folium map with drawing tools
- Rectangle or polygon selection
- Grid waypoint generation
- Mission export to JSON

**Grid Generation Logic:**
```python
from shapely.geometry import Polygon, box
from shapely.affinity import rotate

def generate_grid_waypoints(polygon, spacing, altitude, angle=0):
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    
    waypoints = []
    y = miny
    row = 0
    while y <= maxy:
        x = minx if row % 2 == 0 else maxx
        step = spacing if row % 2 == 0 else -spacing
        while (step > 0 and x <= maxx) or (step < 0 and x >= minx):
            point = Point(x, y)
            if polygon.contains(point):
                waypoints.append((y, x))  # lat, lon
            x += step
        y += spacing
        row += 1
    
    return waypoints
```

**Mission JSON Format:**
```json
{
    "name": "Search_Sector_Alpha",
    "timestamp": "2025-12-03T14:30:00",
    "altitude": 50,
    "waypoints": [
        [44.8176, 20.4633],
        [44.8186, 20.4643],
        ...
    ],
    "area_polygon": [[lat, lon], ...],
    "grid_spacing": 25
}
```

---

### 4. Fire Detection (`fire_detector_unified.py`)

**Purpose:** Detect fire in images/video using YOLO

**Modes:**
- `rgb` - Standard RGB detection
- `thermal` - Simulated thermal camera
- `dual` - Side-by-side RGB + Thermal

**Usage:**
```python
from ultralytics import YOLO

model = YOLO('yolov10_fire_smoke.pt')
results = model(frame)

for detection in results[0].boxes:
    confidence = detection.conf[0]
    class_name = model.names[int(detection.cls[0])]
    if class_name in ['fire', 'smoke'] and confidence > 0.7:
        # Fire detected!
        x1, y1, x2, y2 = detection.xyxy[0]
```

**Thermal Simulation:**
```python
def simulate_thermal(rgb_frame):
    # Convert to grayscale
    gray = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2GRAY)
    # Apply thermal colormap
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
    return thermal
```

---

### 5. Configuration System (`config.py`)

**Purpose:** Centralized path management with private overrides

**How it works:**
```python
from pathlib import Path

# Core paths (auto-detected)
BASE_DIR = Path(__file__).resolve().parent.parent  # Project root
DATA_DIR = BASE_DIR / "data"  # Default: symlink to fire-drone-data

# Try to load private config overrides
try:
    import config_local
    if hasattr(config_local, 'DATA_PATH'):
        DATA_DIR = config_local.DATA_PATH
except ImportError:
    pass  # No local config, use defaults

# Derived paths
MODELS_DIR = DATA_DIR / "models"
DATASETS_DIR = DATA_DIR / "datasets"
```

**Creating a local config:**
```python
# app/config_local.py (gitignored)
from pathlib import Path
DATA_PATH = Path("D:/my_fire_data")
```

---

## 🚀 How to Extend

### Add a New Drone Sensor (e.g., Wind Speed)

1. **Update telemetry reading in `dashboard_fleet_real.py`:**
```python
# In update_fleet_status()
drone_state.wind_speed = vehicle.wind.speed  # If available
```

2. **Display in UI:**
```python
st.metric("Wind", f"{drone_state.wind_speed:.1f} m/s")
```

### Add a New Fleet Command

1. **Add to `send_command()` function:**
```python
elif cmd == "SPIRAL":
    # Generate spiral waypoints
    waypoints = generate_spiral(center_lat, center_lon, radius)
    for wp in waypoints:
        vehicle.simple_goto(wp)
```

2. **Add button in UI:**
```python
if st.button("🌀 SPIRAL"):
    send_command(vehicle, "SPIRAL", lat=lat, lon=lon, radius=100)
```

### Add a New Map Layer

```python
# In create_fleet_map()
new_layer = pdk.Layer(
    "ScatterplotLayer",
    data=my_data,
    get_position=["lon", "lat"],
    get_fill_color=[255, 0, 0],
    get_radius=50,
)
layers.append(new_layer)
```

### Add a New Fire Detection Model

1. **Place model in `data/models/pretrained/`**

2. **Register in `config.py`:**
```python
FIRE_MODELS["my_model"] = PRETRAINED_MODELS_DIR / "my_model.pt"
```

3. **Use in detection:**
```python
model = YOLO(config.get_model_path("my_model"))
```

---

## 🧪 Testing

### Manual Testing Checklist

```bash
# 1. Test configuration
cd app
py config.py  # Should show all paths

# 2. Test fleet launch
py launch_fleet.py  # Wait for "All instances ready"

# 3. Test fleet dashboard
streamlit run dashboard_fleet_real.py --server.port 8506
# Open http://localhost:8506
# Click "Connect All Drones" - should show 5 green statuses

# 4. Test mission planner
streamlit run dashboard_mission.py --server.port 8507
# Draw area, save mission

# 5. Test fire detection
py fire_detector_unified.py --mode thermal

# 6. Compare models
py test_all_models.py
```

### Automated Checks

```bash
# Verify imports work
python -c "from app.config import DATA_DIR; print(DATA_DIR)"

# Verify DroneKit
python -c "from dronekit import connect; print('DroneKit OK')"

# Verify YOLO
python -c "from ultralytics import YOLO; print('YOLO OK')"
```

---

## ❓ Troubleshooting

### "Address already in use"
```bash
# Kill existing Streamlit processes
taskkill /F /IM streamlit.exe
```

### SITL Drones Not Connecting
```bash
# First-time downloads firmware (~100MB)
pip install dronekit-sitl
# Wait 30-60 seconds after starting launch_fleet.py
```

### Models Not Found
```bash
# Check data symlink
ls data/models/pretrained/

# Or check config
cd app
py config.py
```

### "Module not found: config"
```bash
# Run from app/ directory
cd app
py config.py
```

### Mission Not Loading
- Ensure mission JSON file is in `app/` directory
- Check file format matches expected schema
- Look at console for error messages

---

## 📚 Additional Resources

| Document | Purpose |
|----------|---------|
| `PROJECT_STATE.md` | Full system overview |
| `QUICKSTART.md` | Get running fast |
| `LIVE_PROGRESS.md` | Current status |
| `SITL_SETUP_GUIDE.md` | Drone simulation details |

---

## 🤝 Contributing Guidelines

1. **Test before committing** - Run manual testing checklist
2. **Update docs** - If adding features, update relevant docs
3. **Use config system** - Don't hardcode paths
4. **Follow existing patterns** - Match code style
5. **Keep personal data out** - Use `config_local.py` for private paths

---

**Happy coding! 🚁🔥**
