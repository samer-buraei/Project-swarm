# 🔥 FIRE DETECTION DRONE SWARM - PROJECT STATE

**Last Updated:** December 3, 2025  
**Current Phase:** Phase 0 COMPLETE | Phase 1A Ready  
**Overall Progress:** ✅ Fleet Simulation Working, Mission Planning Working, Models Ready  
**GitHub:** https://github.com/samer-buraei/Project-swarm

---

## 📊 EXECUTIVE SUMMARY

```
┌─────────────────────────────────────────────────────────────────────┐
│  🎉 CURRENT STATUS: FULLY OPERATIONAL SIMULATION                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ 5-Drone SITL Fleet    - Connect, control, monitor via MAVLink  │
│  ✅ Fleet Control UI      - Streamlit dashboard on port 8506       │
│  ✅ Mission Planner       - Draw patrol grids on port 8507         │
│  ✅ Mission Integration   - Load JSON → Execute patrol patterns    │
│  ✅ Fire Detection        - 6 models (best: 85% mAP)               │
│  ✅ GitHub Repository     - Clean, no personal data, ~8 MB         │
│  ✅ Config System         - Private path overrides via config_local│
│                                                                     │
│  NEXT: Order €598 hardware for Phase 1A desk testing               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 QUICK START FOR NEW AGENTS/DEVELOPERS

### Prerequisites
```powershell
# Clone the repo
git clone https://github.com/samer-buraei/Project-swarm.git
cd "Project swarm"

# Install dependencies
pip install -r requirements.txt

# First-time SITL setup (downloads ArduPilot firmware ~100MB)
pip install dronekit-sitl
```

### Run the System (3 Terminals)

**Terminal 1: Launch 5 Simulated Drones**
```powershell
cd app
py launch_fleet.py
# Wait for "All instances ready"
```

**Terminal 2: Fleet Control Dashboard**
```powershell
cd app
streamlit run dashboard_fleet_real.py --server.port 8506
```

**Terminal 3: Mission Planner (Optional)**
```powershell
cd app
streamlit run dashboard_mission.py --server.port 8507
```

### Access Dashboards
- **Fleet Control:** http://localhost:8506 - Control drones, execute missions
- **Mission Planner:** http://localhost:8507 - Draw patrol areas, generate grids

---

## 🎯 WHAT THE SYSTEM DOES

### Core Capability
A **fire detection drone swarm** for early wildfire detection:
- 5 autonomous drones with thermal cameras
- Real-time YOLO fire detection (on-drone AI, no cloud)
- LoRa radio communication (offline, 20km range)
- Human operator orchestration via Streamlit dashboard
- Draw patrol areas → Auto-generate grid → Execute mission

### Current Working Features

| Feature | Status | Location |
|---------|--------|----------|
| Fleet simulation (5 SITL drones) | ✅ Working | `app/launch_fleet.py` |
| Fleet control dashboard | ✅ Working | `app/dashboard_fleet_real.py` |
| Manual Control (Click-to-Fly) | ✅ Working | Integrated in fleet dashboard |
| Mission planner (draw areas) | ✅ Working | `app/dashboard_mission.py` |
| Mission execution | ✅ Working | Integrated in fleet dashboard |
| Fire detection models | ✅ 6 models ready | `data/models/pretrained/` |
| Thermal simulation | ✅ Working | `app/thermal_simulation.py` |
| Model comparison tool | ✅ Working | `app/test_all_models.py` |
| Config system | ✅ Working | `app/config.py` |

---

## 📁 PROJECT STRUCTURE

```
Project swarm/                     # GitHub Repository (~8 MB)
├── app/                           # Core application code
│   ├── launch_fleet.py            # 🚁 Start 5 SITL drones
│   ├── dashboard_fleet_real.py    # 🎮 Fleet Control UI (port 8506)
│   ├── dashboard_mission.py       # 🗺️ Mission Planner UI (port 8507)
│   ├── fire_detector_unified.py   # 🔥 Fire detection engine
│   ├── config.py                  # ⚙️ Central path configuration
│   ├── config_local.example.py    # 📝 Template for private paths
│   ├── drone_control.py           # MAVLink drone control
│   ├── simulation.py              # Drone simulation
│   ├── thermal_simulation.py      # Thermal camera simulation
│   ├── test_all_models.py         # Compare all fire models
│   ├── train_fire_quick.py        # Train custom models
│   └── ... (50+ scripts)
│
├── docs/                          # Documentation (24 files)
│   ├── PROJECT_STATE.md           # 📖 THIS FILE - Start here!
│   ├── DEVELOPER_GUIDE.md         # How to extend the system
│   ├── START_HERE_DOCUMENT_INDEX.md
│   └── ...
│
├── models/                        # Base YOLO model only
│   └── yolov8n.pt                # 6 MB base model
│
├── scripts/                       # Utility scripts
│   ├── train_fire_model.py
│   ├── evaluate_model.py
│   └── ...
│
├── P2Pro-Viewer/                 # InfiRay thermal camera driver
│
├── data/ → fire-drone-data/      # Symlink to large data (not in git)
│
├── .gitignore                    # Ignores large data, config_local.py
├── README.md                     # Quick overview
├── QUICKSTART.md                 # Getting started guide
├── LIVE_PROGRESS.md              # Current status dashboard
└── requirements.txt              # Python dependencies
```

### External Data (Not in Git)
```
fire-drone-data/                   # ~141 GB - Keep locally
├── datasets/
│   ├── Combined/                  # D-Fire (21K images)
│   ├── Kaggle_Combined/           # Kaggle (221K images)
│   └── FLAME/                     # Aerial thermal
├── models/
│   └── pretrained/               # 6 fire detection models
└── runs/                         # Training outputs
```

---

## 🤖 AVAILABLE MODELS

| Model | Accuracy | Size | Pi-Ready | Best For |
|-------|----------|------|----------|----------|
| **yolov10_fire_smoke.pt** | **85% mAP** ⭐ | 61 MB | ❌ | Desktop/testing |
| **yolov5s_dfire.pt** | **80% mAP** | 14 MB | ✅ | Pi deployment |
| **dfire_trained_72pct.pt** | **72% mAP** | 5.9 MB | ✅ | Pi (small) |
| yolov10n_forest_fire.pt | Good | 5.5 MB | ✅ | Pi (smallest) |
| yolov8s_forest_fire.pt | Good | 22 MB | ⚠️ | Pi (borderline) |
| yolov8n.pt | Base | 6.2 MB | ✅ | Training base |

### Test Models
```powershell
cd app
py test_all_models.py  # Compare all models on test images
```

---

## ⚙️ CONFIGURATION SYSTEM

The project uses a flexible configuration system for managing paths.

### For Default Setup (Symlink)
```powershell
# Run as Admin - Creates symlink from data/ to your data folder
New-Item -ItemType Junction -Path ".\data" -Target "<YOUR_DATA_PATH>\fire-drone-data"
```

### For Custom Paths (Private Config)
1. Copy template: `app/config_local.example.py` → `app/config_local.py`
2. Edit your paths:
```python
from pathlib import Path
DATA_PATH = Path("D:/my_custom_data/fire-drone-data")
```
3. `config_local.py` is gitignored - your paths stay private

### Verify Configuration
```powershell
cd app
py config.py  # Shows all paths, models, and datasets
```

---

## 🎮 DASHBOARD REFERENCE

### Fleet Control (port 8506)
**Purpose:** Control 5 drones, execute missions, monitor telemetry

**Features:**
- Real-time drone positions on interactive map (Folium)
- **Click-to-Fly:** Click anywhere on map to send drone
- **Manual Nudge:** Directional buttons for precise control
- Fleet status: battery, altitude, mode, heading
- Fleet commands: ARM ALL, TAKEOFF ALL, RTL ALL, DISARM ALL
- Individual drone control
- Mission loading and execution
- Detection log

**Key UI Elements:**
- Top: Fleet status cards (green=connected, red=offline)
- Left: Interactive map with flight trails
- Right: Control panel with **Manual Nudge Pad** and mission control

### Mission Planner (port 8507)
**Purpose:** Draw patrol areas, generate grid waypoints

**Features:**
- Satellite map view (Folium)
- Draw rectangle or polygon search areas
- Configure: altitude, grid spacing, angle
- Preview waypoints before saving
- Export to JSON for fleet execution

**Workflow:**
1. Navigate to area on map
2. Draw search boundary
3. Adjust settings (altitude, spacing)
4. Click "Generate Waypoints"
5. Click "Save Mission"
6. Load in Fleet Control → Execute

---

## 🔄 COMPLETE WORKFLOW

### Step 1: Plan a Patrol Mission
```
1. Open Mission Planner (http://localhost:8507)
2. Pan/zoom to your patrol area
3. Draw a search area (rectangle or polygon)
4. Set altitude (e.g., 50m) and grid spacing (e.g., 25m)
5. Click "Generate Waypoints" → See preview
6. Click "Save Mission" → Creates Search_Sector_XXX.json
```

### Step 2: Launch Fleet
```powershell
cd app
py launch_fleet.py
# Wait for "All instances ready" (5 drones on ports 5760-5764)
```

### Step 3: Execute Mission
```
1. Open Fleet Control (http://localhost:8506)
2. Click "Connect All Drones" → Wait for green status
3. Select mission from dropdown
4. Click "Load Mission" → Waypoints appear on map
5. Click "🚀 EXECUTE MISSION"
6. Watch drones fly the patrol pattern!
```

---

## 📋 KEY SCRIPTS REFERENCE

### Fleet & Control
| Script | Purpose | Command |
|--------|---------|---------|
| `launch_fleet.py` | Start 5 SITL drones | `py launch_fleet.py` |
| `dashboard_fleet_real.py` | Fleet control UI | `streamlit run dashboard_fleet_real.py --server.port 8506` |
| `dashboard_mission.py` | Mission planner | `streamlit run dashboard_mission.py --server.port 8507` |
| `drone_control.py` | MAVLink utilities | Library (imported) |

### Fire Detection
| Script | Purpose | Command |
|--------|---------|---------|
| `fire_detector_unified.py` | Main detector | `py fire_detector_unified.py --mode thermal` |
| `test_all_models.py` | Compare models | `py test_all_models.py` |
| `thermal_simulation.py` | Thermal sim | `py thermal_simulation.py` |

### Configuration & Setup
| Script | Purpose | Command |
|--------|---------|---------|
| `config.py` | Path configuration | `py config.py` (verify) |
| `download_pretrained_fire.py` | Get models | `py download_pretrained_fire.py` |
| `organize_kaggle_downloads.py` | Organize data | `py organize_kaggle_downloads.py` |

### Training
| Script | Purpose | Command |
|--------|---------|---------|
| `train_fire_quick.py` | Quick training | `py train_fire_quick.py` |
| `train_kaggle_finetune.py` | Kaggle fine-tune | `py train_kaggle_finetune.py` |
| `check_training_status.py` | Monitor training | `py check_training_status.py` |

---

## 🚁 DRONE SIMULATION DETAILS

### SITL Configuration
- **Simulator:** DroneKit-SITL (ArduCopter)
- **Ports:** 5760-5764 (one per drone)
- **Drone IDs:** A1, A2, A3, A4, A5
- **Initial Location:** Belgrade area (configurable)

### MAVLink Communication
```python
# Connect to drone
from dronekit import connect
vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)

# Arm and takeoff
vehicle.arm()
vehicle.simple_takeoff(50)  # 50m altitude
```

### Fleet Launcher
```python
# launch_fleet.py creates 5 instances:
DRONE_CONFIG = [
    {'id': 'A1', 'port': 5760, 'lat': 44.8176, 'lon': 20.4633},
    {'id': 'A2', 'port': 5761, 'lat': 44.8196, 'lon': 20.4653},
    {'id': 'A3', 'port': 5762, 'lat': 44.8186, 'lon': 20.4613},
    {'id': 'A4', 'port': 5763, 'lat': 44.8166, 'lon': 20.4643},
    {'id': 'A5', 'port': 5764, 'lat': 44.8206, 'lon': 20.4623},
]
```

---

## 🎯 PHASE STATUS

| Phase | Status | Description | Cost |
|-------|--------|-------------|------|
| **Phase 0** | ✅ **COMPLETE** | Software validation, simulation working | €0 |
| **Phase 1A** | ⏳ Ready | Hardware desk test (Pi, thermal, LoRa) | €598 |
| **Phase 1B** | ⏳ Waiting | First drone build | €1,200 |
| **Phase 2** | ⏳ Waiting | 5-drone fleet | €5,000 |
| **Phase 3** | ⏳ Waiting | Forest deployment & fire chief demo | €0 |

### Phase 1A Hardware Shopping List
| Part | Cost |
|------|------|
| Raspberry Pi 4 8GB | €60 |
| InfiRay P2Pro thermal camera | €250 |
| Heltec ESP32 LoRa modules ×2 | €100 |
| USB Hub, cables, power | €45 |
| Misc (SD card, etc) | €123 |
| **TOTAL** | **€598** |

---

## 🏗️ ARCHITECTURE

### System Layers
```
LAYER 1: THE DRONE (Edge AI)
├─ Hardware: Tarot 650 frame, Pixhawk 6C flight controller
├─ Sensors: InfiRay P2Pro thermal camera, GPS
├─ Brain: Raspberry Pi 4 (8GB RAM)
├─ AI: YOLOv8n fire detection (~756ms on Pi)
└─ Communication: Heltec ESP32 LoRa module

LAYER 2: THE LINK (Offline Communication)
├─ Protocol: LoRa radio (868 MHz, 20km range)
├─ Message: "FIRE lat lon temp" (21 bytes)
└─ Latency: <200ms air time

LAYER 3: THE BASE (Human Control)
├─ Hardware: Operator laptop + LoRa receiver
├─ Software: Streamlit dashboard
├─ Display: Fleet positions, detections, telemetry
└─ Database: SQLite (local, offline)

LAYER 4: THE HUMAN (Final Decision)
├─ Role: Confirm/dismiss AI fire detections
├─ Action: Call fire chief if confirmed
└─ Authority: Human always decides, not AI
```

### Why Offline Architecture?
```
Cloud (REJECTED):
  ❌ No 4G in remote forests
  ❌ Latency unacceptable
  ❌ Cloud costs 24/7

LoRa Offline (CHOSEN):
  ✅ Works anywhere (no internet)
  ✅ Low latency (<2 sec)
  ✅ No cloud cost
  ✅ Works in forest
```

---

## 🔧 TROUBLESHOOTING

### SITL Drones Not Connecting
```powershell
# First-time setup downloads firmware (~100MB)
pip install dronekit-sitl
# Run launch_fleet.py and wait 30-60 seconds
```

### Streamlit Port Already in Use
```powershell
# Kill existing streamlit processes
taskkill /F /IM streamlit.exe
# Restart
streamlit run dashboard_fleet_real.py --server.port 8506
```

### Models Not Found
```powershell
# Verify data symlink exists
ls data/models/pretrained/

# Or check config
cd app
py config.py
```

### ImportError for dronekit
```powershell
pip install dronekit pymavlink
```

---

## 📚 DOCUMENTATION INDEX

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **PROJECT_STATE.md** (this) | Complete system overview | First! Always! |
| LIVE_PROGRESS.md | Current status dashboard | Check status |
| QUICKSTART.md | Get running fast | First time setup |
| DEVELOPER_GUIDE.md | Extend the system | Adding features |
| START_HERE_DOCUMENT_INDEX.md | Doc navigation | Finding docs |
| COMPLETE_PLAN.md | Full project plan | Understanding scope |
| SITL_SETUP_GUIDE.md | Drone simulation | SITL issues |

---

## 🎓 FOR NEW AGENTS/COLLABORATORS

### First 10 Minutes
1. Read this file (PROJECT_STATE.md)
2. Run `py config.py` to verify setup
3. Run `py launch_fleet.py` to start drones
4. Open http://localhost:8506 to see fleet dashboard

### Understanding the Code
- All core code is in `app/`
- Configuration is in `app/config.py`
- Dashboards use Streamlit
- Drone control uses DroneKit/MAVLink
- Maps use PyDeck (3D) and Folium (2D)

### Making Changes
1. Check `app/config.py` for path management
2. Check `dashboard_fleet_real.py` for fleet UI
3. Check `dashboard_mission.py` for mission planning
4. All fire detection models are in `fire_detector_unified.py`

### Key Design Decisions
- **Offline-first:** No cloud, LoRa communication
- **Human-in-loop:** AI suggests, human confirms
- **Modular:** Each component can be tested independently
- **Config system:** Private paths via config_local.py

---

## ✅ WHAT'S DONE

- [x] 5-drone SITL simulation
- [x] Fleet control dashboard (Streamlit)
- [x] Mission planner (draw areas → generate grids)
- [x] Mission integration (load → execute)
- [x] Fire detection models (6 pretrained)
- [x] Configuration system (private paths)
- [x] GitHub repository (clean, no personal data)
- [x] Documentation (comprehensive)

## ⏳ WHAT'S NEXT

- [ ] Order Phase 1A hardware (€598)
- [ ] Test P2Pro thermal camera on real Pi 4
- [ ] Test LoRa communication range
- [ ] Test YOLO inference speed on Pi 4
- [ ] Build first drone (Phase 1B)

---

## 🤝 HANDOFF CHECKLIST

Before handing off to another agent/developer:

- [ ] Verify `py config.py` runs without errors
- [ ] Verify `py launch_fleet.py` starts 5 drones
- [ ] Verify dashboards load (ports 8506, 8507)
- [ ] Update this PROJECT_STATE.md with any changes
- [ ] Document any new features or fixes
- [ ] Push changes to GitHub

---

**Last Updated:** December 3, 2025  
**Maintained By:** Development Team  
**GitHub:** https://github.com/samer-buraei/Project-swarm
