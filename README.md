# 🔥 Fire Swarm - Drone Wildfire Detection System

**Multi-drone swarm for early wildfire detection using thermal imaging and AI.**

[![Phase](https://img.shields.io/badge/Phase-0%20Complete-green)]()
[![Drones](https://img.shields.io/badge/Simulated%20Drones-5-blue)]()
[![Detection](https://img.shields.io/badge/Detection-YOLOv8-orange)]()
[![Best Model](https://img.shields.io/badge/Best%20Model-85%25%20mAP-brightgreen)]()

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install dronekit-sitl  # First-time: downloads ArduPilot firmware
```

### 2. Launch 5 Simulated Drones (Terminal 1)
```bash
cd app
python launch_fleet.py
# Wait for "All 5 SITL instances ready!"
```

### 3. Start Fleet Control Dashboard (Terminal 2)
```bash
cd app
streamlit run dashboard_fleet_real.py --server.port 8506
```

### 4. Start Mission Planner (Terminal 3, Optional)
```bash
cd app
streamlit run dashboard_mission.py --server.port 8507
```

### 5. Open Dashboards
- **Fleet Control:** http://localhost:8506
- **Mission Planner:** http://localhost:8507

### 6. Connect & Fly! 🎮
1. Click **"Connect All Drones"**
2. Click **"TAKEOFF ALL"**
3. Watch your fleet take off!

---

## 🗺️ Mission Planning & Execution

### Plan a Patrol
1. Open **Mission Planner** (http://localhost:8507)
2. Draw a search area on the map
3. Set altitude (e.g., 50m) and grid spacing (e.g., 25m)
4. Click **"Save Mission"**

### Execute the Mission
1. Open **Fleet Control** (http://localhost:8506)
2. Click **"Connect All Drones"**
3. Select mission from dropdown → Click **"Load Mission"**
4. Click **"🚀 EXECUTE MISSION"**
5. Watch drones fly the patrol pattern!

---

## 🎯 Features

### Multi-Drone Fleet Control
- ✅ Connect and control 5 drones simultaneously
- ✅ Real MAVLink communication (same as real hardware)
- ✅ ARM / TAKEOFF / RTL / GOTO / LAND commands
- ✅ Individual or fleet-wide control
- ✅ 3D map with altitude columns and flight trails

### Mission Planning
- ✅ Draw search areas (rectangle or polygon)
- ✅ Auto-generate grid waypoints
- ✅ Configure altitude, spacing, angle
- ✅ Export missions to JSON
- ✅ Load & execute in Fleet Control

### Fire Detection
- ✅ 6 pretrained YOLO models (best: 85% mAP)
- ✅ Thermal camera simulation
- ✅ RGB + Thermal + Dual modes
- ✅ ~756ms inference on Raspberry Pi 4

---

## 🗂️ Project Structure

```
Project swarm/                    # GitHub Repo (~8 MB)
├── app/                          # Core application code
│   ├── launch_fleet.py           # 🚁 Start 5 SITL drones
│   ├── dashboard_fleet_real.py   # 🎮 Fleet Control UI
│   ├── dashboard_mission.py      # 🗺️ Mission Planner
│   ├── fire_detector_unified.py  # 🔥 Fire detection
│   ├── config.py                 # ⚙️ Path configuration
│   └── ... (50+ scripts)
│
├── docs/                         # Documentation
│   ├── PROJECT_STATE.md          # 📖 Full system overview
│   └── ...
│
├── models/                       # Base model only
│   └── yolov8n.pt
│
├── P2Pro-Viewer/                # Thermal camera driver
├── .gitignore
├── README.md
└── requirements.txt

fire-drone-data/                  # Local Only (~141 GB)
├── datasets/                     # Training data
├── models/pretrained/           # 6 fire detection models
└── runs/                        # Training outputs
```

---

## 🔥 Fire Detection Models

| Model | Accuracy | Size | Pi-Ready |
|-------|----------|------|----------|
| **yolov10_fire_smoke.pt** | **85% mAP** ⭐ | 61 MB | ❌ |
| **yolov5s_dfire.pt** | **80% mAP** | 14 MB | ✅ |
| **dfire_trained_72pct.pt** | **72% mAP** | 5.9 MB | ✅ |
| yolov10n_forest_fire.pt | Good | 5.5 MB | ✅ |

### Test Fire Detection
```bash
cd app
python fire_detector_unified.py --mode thermal
python test_all_models.py  # Compare all models
```

---

## ⚙️ Configuration

### Option 1: Symlink (Recommended)
```powershell
# Run as Admin - creates symlink to your data folder
New-Item -ItemType Junction -Path ".\data" -Target "<YOUR_PATH>\fire-drone-data"
```

### Option 2: Private Config File
```powershell
# Copy template
copy app\config_local.example.py app\config_local.py

# Edit with your paths
notepad app\config_local.py
```

In `config_local.py`:
```python
from pathlib import Path
DATA_PATH = Path("D:/my_fire_data")
```

### Verify Setup
```bash
cd app
python config.py  # Shows all paths and models
```

---

## 📡 Ports Reference

| Port | Service |
|------|---------|
| 5760-5764 | SITL Drones (A1-A5) |
| 8506 | Fleet Control Dashboard |
| 8507 | Mission Planner |

---

## 🔧 Requirements

- Python 3.10+
- Windows/Linux/Mac
- ~2GB RAM
- No GPU required

### Key Dependencies
```
streamlit>=1.28.0
ultralytics>=8.0.0
pymavlink>=2.4.0
dronekit-sitl>=3.3.0
pydeck>=0.8.0
folium>=0.14.0
opencv-python>=4.8.0
shapely>=2.0.0
streamlit-folium>=0.15.0
```

---

## 📈 Performance

| Metric | Desktop | Raspberry Pi 4 |
|--------|---------|----------------|
| YOLO Inference | 18.9ms | ~756ms |
| Detection FPS | 50+ | ~1.3 |
| Drones Supported | 5+ | 5 |

---

## 🗺️ Roadmap

- [x] Phase 0: PC Simulation ✅
- [x] Fleet Control Dashboard ✅
- [x] Mission Planner ✅
- [x] Mission Integration ✅
- [x] Fire Detection Models (85% mAP) ✅
- [ ] Phase 1A: Hardware Integration (€598)
- [ ] Phase 1B: First Drone Build
- [ ] Phase 2: 5-Drone Fleet
- [ ] Phase 3: Forest Deployment

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [PROJECT_STATE.md](docs/PROJECT_STATE.md) | Complete system overview |
| [QUICKSTART.md](QUICKSTART.md) | Get running fast |
| [LIVE_PROGRESS.md](LIVE_PROGRESS.md) | Current status |
| [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) | Extend the system |
| [SITL_SETUP_GUIDE.md](docs/SITL_SETUP_GUIDE.md) | Drone simulation |

---

## 🤝 Contributing

### After Cloning:
1. `pip install -r requirements.txt`
2. `pip install dronekit-sitl`
3. Link data folder (see Configuration above)
4. `cd app && python launch_fleet.py`
5. `streamlit run dashboard_fleet_real.py --server.port 8506`

### For New Agents/Developers:
Start by reading `docs/PROJECT_STATE.md` - it explains everything.

---

## 📄 License

MIT License - See LICENSE file.

---

**Built with 🔥 for wildfire prevention**
