# 🚀 FIRE DRONE SWARM - QUICKSTART

**Get the system running in 5 minutes.**

---

## Prerequisites

```powershell
# Install Python dependencies
pip install -r requirements.txt

# First-time SITL setup (downloads ArduPilot firmware ~100MB)
pip install dronekit-sitl
```

---

## Launch the System (3 Terminals)

### Terminal 1: Start 5 Simulated Drones
```powershell
cd app
py launch_fleet.py
```
Wait for: `"All 5 SITL instances ready!"`

### Terminal 2: Fleet Control Dashboard
```powershell
cd app
streamlit run dashboard_fleet_real.py --server.port 8506
```

### Terminal 3: Mission Planner (Optional)
```powershell
cd app
streamlit run dashboard_mission.py --server.port 8507
```

---

## Open Dashboards

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| **Fleet Control** | http://localhost:8506 | Control drones, execute missions |
| **Mission Planner** | http://localhost:8507 | Draw patrol areas, generate grids |

---

## Quick Workflow

### 1. Plan a Mission
1. Open Mission Planner (port 8507)
2. Draw a search area on the map
3. Set altitude and grid spacing
4. Click "Save Mission"

### 2. Execute Mission
1. Open Fleet Control (port 8506)
2. Click **"Connect All Drones"**
3. Select your mission from dropdown
4. Click **"Load Mission"**
5. Click **"🚀 EXECUTE MISSION"**
6. Watch drones fly the patrol pattern!

---

## Fire Detection Testing

### Test with Best Model (85% mAP)
```powershell
cd app
py fire_detector_unified.py --model data/models/pretrained/yolov10_fire_smoke.pt --mode thermal
```

### Compare All Models
```powershell
cd app
py test_all_models.py
```

### Test Thermal Simulation
```powershell
cd app
py thermal_simulation.py
```

**Controls:**
- `Q` - Quit
- `M` - Cycle mode (RGB → Thermal → Dual)
- `T` - Change thermal colormap
- `S` - Save screenshot

---

## Verify Configuration

```powershell
cd app
py config.py
```

This shows:
- Project root path
- Data directory path
- Available models (✅ or ❌)
- Available datasets

---

## Configuration (Optional)

### Method 1: Symlink (Recommended)
```powershell
# Run as Admin
New-Item -ItemType Junction -Path ".\data" -Target "<YOUR_DATA_PATH>\fire-drone-data"
```

### Method 2: Private Config File
```powershell
# Copy template
copy app\config_local.example.py app\config_local.py

# Edit with your paths
notepad app\config_local.py
```

Example `config_local.py`:
```python
from pathlib import Path
DATA_PATH = Path("D:/my_fire_data")
```

---

## Available Models

| Model | Accuracy | Size | Pi-Ready |
|-------|----------|------|----------|
| **yolov10_fire_smoke.pt** | **85%** ⭐ | 61 MB | ❌ |
| **yolov5s_dfire.pt** | **80%** | 14 MB | ✅ |
| **dfire_trained_72pct.pt** | **72%** | 5.9 MB | ✅ |
| yolov10n_forest_fire.pt | Good | 5.5 MB | ✅ |

---

## Troubleshooting

### Drones Not Connecting?
```powershell
# First-time SITL downloads firmware (~100MB)
# Wait 30-60 seconds after starting launch_fleet.py
```

### Port Already in Use?
```powershell
taskkill /F /IM streamlit.exe
```

### Models Not Found?
```powershell
cd app
py config.py  # Check paths
```

---

## Need More Help?

- **Full Documentation:** `docs/PROJECT_STATE.md`
- **Developer Guide:** `docs/DEVELOPER_GUIDE.md`
- **Live Status:** `LIVE_PROGRESS.md`

---

**Ready to fly! 🚁**
