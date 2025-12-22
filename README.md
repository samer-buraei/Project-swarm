# 🔥 Project Swarm v2 - Drone Wildfire Detection System

**Multi-drone swarm for early wildfire detection using thermal imaging and AI.**

[![Phase](https://img.shields.io/badge/Phase-0%20Complete-green)]()
[![Drones](https://img.shields.io/badge/Simulated%20Drones-5-blue)]()
[![Detection](https://img.shields.io/badge/Detection-YOLOv8-orange)]()
[![Model](https://img.shields.io/badge/Model%20Accuracy-85%25%20mAP-brightgreen)]()
[![Flight](https://img.shields.io/badge/Flight%20Time-60%20min-blue)]()
[![Connectivity](https://img.shields.io/badge/Connectivity-4G%2FLora-purple)]()

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
- **60-minute flight time** per battery (Li-Ion)

### Connectivity (Hybrid)
- **Primary:** 4G/LTE cellular (video + telemetry)
- **Backup:** LoRa mesh (20km range, offline)
- Automatic failover between connections
- Works in remote forests without infrastructure

### Patrol Patterns
- Grid sweep
- Perimeter patrol
- Spiral search
- Sector coverage
- Lawnmower pattern

### Fire Detection
- YOLOv8 neural network (85% mAP best model)
- 18.9ms inference time (PC)
- ~500ms on Raspberry Pi 5 (~2 FPS)
- **InfiRay P2 Pro** thermal camera (256×192, 25Hz, radiometric)

### Visualization
- 3D PyDeck maps
- Real-time flight trails
- Drone altitude columns
- Fire alert markers

---

## 🛠️ Hardware Specifications

> 📋 **Full BOM:** See [`docs/HARDWARE_BOM.md`](docs/HARDWARE_BOM.md) for complete parts list.

### Per Drone (~$1,285)

| Component | Model | Price |
|-----------|-------|-------|
| Flight Controller | Pixhawk 6C | $141 |
| Compute | Raspberry Pi 5 8GB | $105 |
| **Thermal Camera** | **InfiRay P2 Pro** ⭐ | $350 |
| Frame | GEPRC Mark4 10" | $100 |
| Motors | BrotherHobby 3115 900KV (x5) | $125 |
| ESC | Holybro Tekko32 50A 4in1 | $70 |
| Battery | Li-Ion 6S 8000mAh (Molicel) | $160 |
| Connectivity | Sixfab 4G/LTE Kit | $100 |
| GPS | Matek M10-5883 | $30 |
| Props + Accessories | Various | $104 |

**P2 Pro Specs:** 256×192 resolution, 25Hz, -20°C to 550°C, 9.5g weight, radiometric output

### Flight Time: 60 Minutes
- **Battery:** Li-Ion 6S 8000mAh (Molicel P42A cells)
- **Motors:** 900KV efficiency-optimized
- **Props:** 10x5x3 for maximum efficiency

### Connectivity
- **Primary:** Sixfab 4G/LTE Modem (video streaming)
- **Backup:** Heltec LoRa 868MHz (20km range)

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

### Software
- Python 3.10+
- Windows/Linux/Mac
- ~2GB RAM
- No GPU required (CPU inference)

### Hardware (for deployment)
- See [`docs/HARDWARE_BOM.md`](docs/HARDWARE_BOM.md) for complete list
- Budget: **~$1,285 per drone** + ~$350 one-time costs
- **5 Drones Total:** ~$6,775

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

| Metric | PC | Raspberry Pi 5 | Jetson Nano |
|--------|----|--------------------|-------------|
| Inference | 18.9ms | ~500ms | ~100ms |
| FPS | 50+ | ~2 | ~10 |
| Drones | 5 | 5 | 5 |
| Flight Time | - | 60 min (Li-Ion) | 60 min (Li-Ion) |

---

## 🗺️ Roadmap

### Completed
- [x] Phase 0: PC Simulation ✅
- [x] Model Training: D-Fire 72% mAP ✅
- [x] Pretrained Models: 6 models (best: 85% mAP) ✅
- [x] Hardware BOM: 60-min flight specs finalized ✅
- [x] Connectivity: 4G/LTE + LoRa architecture ✅

### In Progress
- [ ] Phase 1A: Hardware Desk Testing
  - [ ] Pi 5 + **InfiRay P2 Pro** thermal camera
  - [ ] Sixfab 4G/LTE modem
  - [ ] LoRa communication backup

### Upcoming
- [ ] Phase 1B: First Drone Build (~$1,176)
- [ ] Phase 2: 5-Drone Fleet (~$6,000)
- [ ] Phase 3: Forest Deployment & Fire Chief Demo

---

## 🔥 Fire Detection Models

| Model | Accuracy | Size | Recommended For |
|-------|----------|------|-----------------|
| **yolov10_fire_smoke.pt** | **85% mAP** ⭐ | 61 MB | Desktop/Jetson |
| **yolov5s_dfire.pt** | **80% mAP** | 14 MB | Pi 5 |
| D-Fire Trained | **72% mAP** | 5.9 MB | Pi 5 (lightweight) |
| yolov10n_forest_fire.pt | Good | 5.5 MB | Pi 5 (fast) |

*Models stored in `fire-drone-data/models/pretrained/` (not in GitHub repo)*

---

## 📚 Documentation

### 🆕 Start Here
- [**🤝 Collaboration Guide**](COLLABORATION_GUIDE.md) - **FOR NEW ENGINEERS** - Expert personas & prompts

### Core Documents
- [**Hardware BOM**](docs/HARDWARE_BOM.md) - Complete parts list with vendors
- [**Project State**](docs/PROJECT_STATE.md) - Current status & decisions
- [**P2 Pro Integration**](docs/P2PRO_INTEGRATION_GUIDE.md) - Thermal camera setup & code
- [**Connectivity Architecture**](docs/CONNECTIVITY_ARCHITECTURE.md) - 4G/LTE + LoRa setup
- [**Development Phases**](docs/DEVELOPMENT_PHASES.md) - 10-week MVP plan
- [**Master Links**](docs/MASTER_LINKS.md) - All resources & references

### Technical Guides
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Proposal Analysis](docs/PROPOSAL_ANALYSIS.md) - Tech decisions
- [SITL Setup Guide](docs/SITL_SETUP_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)

---

## 💾 Data & Models (Not on GitHub)

Training data and large models are stored separately:
- **Location:** `fire-drone-data/` (sibling folder)
- **Size:** ~141 GB
- **Contents:** Datasets, pretrained models, training outputs

To link for local development (run as Admin):
```powershell
New-Item -ItemType Junction -Path ".\data" -Target "C:\Users\sam\Downloads\fire-drone-data"
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
