# 🔥 Fire Swarm - Drone Wildfire Detection System

**Multi-drone swarm for early wildfire detection using thermal imaging and AI.**

[![Phase](https://img.shields.io/badge/Phase-0%20Complete-green)]()
[![Drones](https://img.shields.io/badge/Simulated%20Drones-5-blue)]()
[![Detection](https://img.shields.io/badge/Detection-YOLOv8-orange)]()
[![Model](https://img.shields.io/badge/Model%20Accuracy-72%25%20mAP-brightgreen)]()

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch 5 Simulated Drones
```bash
cd app
python launch_fleet.py
```

### 3. Start Fleet Control Dashboard
```bash
cd app
streamlit run dashboard_fleet_real.py --server.port 8506
```

### 4. Open Browser
```
http://localhost:8506
```

### 5. Click "Connect All Drones" → Control your fleet! 🎮

---

## 📸 Screenshots

### Fleet Control Dashboard
- 5 drones connected via MAVLink
- Real-time telemetry (altitude, heading, speed)
- Fleet commands (ARM ALL, TAKEOFF ALL, RTL ALL)
- Individual drone control
- 3D map with flight trails

---

## 🗂️ Project Structure

```
fire-drone-swarm/                # GitHub Repo (~20 MB)
├── app/                         # Core application code
│   ├── simulation.py            # Drone simulation
│   ├── dashboard.py             # Main dashboard
│   ├── dashboard_fleet_real.py  # Fleet control UI
│   ├── fire_detector_unified.py # Fire detection
│   ├── drone_control.py         # MAVLink controller
│   ├── launch_fleet.py          # Start 5 SITL drones
│   └── ... (50+ scripts)
│
├── docs/                        # Documentation (24 files)
│   ├── PROJECT_STATE.md         # Current status
│   ├── SYSTEM_ARCHITECTURE.md   # Technical design
│   └── ...
│
├── scripts/                     # Utility scripts
│   ├── train_fire_model.py
│   ├── export_model.py
│   └── ...
│
├── models/                      # Base model only
│   └── yolov8n.pt              # 6 MB base model
│
├── P2Pro-Viewer/               # Thermal camera driver
│
├── .gitignore
├── README.md
├── requirements.txt
└── QUICKSTART.md

fire-drone-data/                 # Local Only (~141 GB) - NOT on GitHub
├── datasets/                    # Training datasets
│   ├── Combined/               # D-Fire (21K images)
│   ├── Kaggle_Combined/        # Kaggle (221K images)
│   └── FLAME/                  # Aerial thermal (pending)
├── models/
│   └── pretrained/             # Trained models (6 models, 85% mAP best)
└── runs/                       # Training outputs
```

---

## 🎯 Features

### Multi-Drone Fleet Control
- Connect and control 5 drones simultaneously
- Real MAVLink communication (same as real hardware)
- ARM / TAKEOFF / RTL / GOTO commands
- Individual or fleet-wide control

### Patrol Patterns
- Grid sweep
- Perimeter patrol
- Spiral search
- Sector coverage
- Lawnmower pattern

### Fire Detection
- YOLOv8 neural network
- 18.9ms inference time (PC)
- ~7 FPS on Raspberry Pi 4 (simulated)
- Thermal camera ready

### Visualization
- 3D PyDeck maps
- Real-time flight trails
- Drone altitude columns
- Fire alert markers

---

## ⚙️ Configuration

### Change Location (Belgrade → Your Area)
```python
# In dashboard_fleet_real.py (line 58):
BASE_LAT = 44.8125  # Your latitude
BASE_LON = 20.4612  # Your longitude
```

### Change Number of Drones
```python
# In launch_fleet.py and dashboard_fleet_real.py:
DRONES = [
    {"id": "D1", "port": 5760, "lat": 44.8125, "lon": 20.4612},
    # Add more drones here...
]
```

### Change Takeoff Altitude
```python
# In dashboard_fleet_real.py, send_command():
elif cmd == "TAKEOFF":
    alt = kwargs.get('alt', 50)  # Change 50 to desired altitude
```

---

## 📡 Ports Reference

| Port | Service |
|------|---------|
| 5760-5800 | SITL Drones (D1-D5) |
| 8501-8506 | Streamlit Dashboards |

---

## 🔧 Requirements

- Python 3.10+
- Windows/Linux/Mac
- ~2GB RAM
- No GPU required (CPU inference)

### Key Dependencies
```
streamlit>=1.28.0
ultralytics>=8.0.0
pymavlink>=2.4.0
dronekit-sitl>=3.3.0
pydeck>=0.8.0
folium>=0.14.0
opencv-python>=4.8.0
```

---

## 📈 Performance

| Metric | PC | Raspberry Pi 4 (simulated) |
|--------|----|-----------------------------|
| Inference | 18.9ms | ~115ms |
| FPS | 50+ | 7-8 |
| Drones | 5 | 5 |

---

## 🗺️ Roadmap

- [x] Phase 0: PC Simulation ✅
- [x] Model Training: D-Fire 72% mAP ✅
- [x] Pretrained Models: 6 models collected ✅
- [ ] Phase 1: Hardware Integration
- [ ] Phase 2: Field Testing
- [ ] Phase 3: Deployment

---

## 🔥 Fire Detection Models

| Model | Accuracy | Size | For |
|-------|----------|------|-----|
| yolov10_fire_smoke.pt | **85% mAP** | 61 MB | Desktop |
| yolov5s_dfire.pt | **80% mAP** | 14 MB | Pi |
| D-Fire Trained | **72% mAP** | 5.9 MB | Pi |
| yolov10n_forest_fire.pt | Good | 5.5 MB | Pi |

*Models stored in `fire-drone-data/models/pretrained/` (not in GitHub)*

---

## 📚 Documentation

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [SITL Setup Guide](docs/SITL_SETUP_GUIDE.md)
- [Project State](docs/PROJECT_STATE.md)
- [Progress Review](docs/PROGRESS_REVIEW_20251201.md)

---

## 💾 Data & Models (Not on GitHub)

Training data and large models are stored separately (~141 GB).

### Option 1: Symlink (Recommended)
```powershell
# Run as Admin - creates symlink to your data folder
New-Item -ItemType Junction -Path ".\data" -Target "D:\your-path\fire-drone-data"
```

### Option 2: Config File (Alternative)
```powershell
# Copy the example config
cp app/config_local.example.py app/config_local.py

# Edit with your paths
notepad app/config_local.py
```

In `config_local.py`:
```python
DATA_PATH = "D:/your-path/fire-drone-data"
```

### Verify Setup
```bash
cd app
python config.py  # Shows path status
```

---

## 🤝 Contributing

This is an active development project. See `docs/` for detailed specifications.

### After Cloning:
1. `pip install -r requirements.txt`
2. Download training data separately (if needed)
3. Link data folder (see above)
4. `cd app && python launch_fleet.py`

---

## 📄 License

MIT License - See LICENSE file.

---

**Built with 🔥 for wildfire prevention**
