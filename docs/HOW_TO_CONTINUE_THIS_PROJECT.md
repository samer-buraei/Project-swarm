# 🔄 HOW TO CONTINUE THIS PROJECT

**Instructions for resuming work after any break.**

Last Updated: December 3, 2025

---

## ⚡ QUICK RESUME (5 Minutes)

### 1. Check Current Status
```bash
# Open the live progress file
cat LIVE_PROGRESS.md
```

### 2. Verify Setup
```bash
cd app
py config.py  # Shows all paths and model status
```

### 3. Start the System
```bash
# Terminal 1: Start drones
cd app
py launch_fleet.py

# Terminal 2: Start dashboard
cd app
streamlit run dashboard_fleet_real.py --server.port 8506
```

### 4. Open Dashboard
- http://localhost:8506

---

## 📖 FULL CONTEXT RECOVERY

### For a New Agent or Developer

Read these documents in order:

1. **[PROJECT_STATE.md](PROJECT_STATE.md)** (15 min)
   - Complete system overview
   - What's built, what works
   - Architecture and design decisions

2. **[QUICKSTART.md](../QUICKSTART.md)** (5 min)
   - How to run the system

3. **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** (20 min)
   - How the code works
   - How to extend it

4. **[LIVE_PROGRESS.md](../LIVE_PROGRESS.md)** (2 min)
   - Current status dashboard

---

## 🎯 COMMON SCENARIOS

### "I need to understand what this project does"

```
Read: PROJECT_STATE.md (Section: Executive Summary)

TL;DR: Multi-drone wildfire detection system
- 5 drones with thermal cameras
- YOLO AI for fire detection
- Offline LoRa communication
- Human operator makes final decisions
```

### "I need to run the system"

```bash
# Three terminals:

# 1. Start drones
cd app && py launch_fleet.py

# 2. Fleet control
streamlit run dashboard_fleet_real.py --server.port 8506

# 3. Mission planner (optional)
streamlit run dashboard_mission.py --server.port 8507
```

### "I need to add a feature"

```
Read: DEVELOPER_GUIDE.md (Section: How to Extend)

Key files:
- app/dashboard_fleet_real.py  - Fleet UI
- app/dashboard_mission.py     - Mission planning
- app/fire_detector_unified.py - Fire detection
- app/config.py               - Path configuration
```

### "I need to understand the architecture"

```
Read: PROJECT_STATE.md (Section: Architecture)

Summary:
- Layer 1: Drone (Pi 4 + thermal camera + YOLO)
- Layer 2: Link (LoRa radio, offline)
- Layer 3: Base (Operator laptop + dashboard)
- Layer 4: Human (Confirms fire, calls fire chief)
```

### "I need to train/test fire detection"

```bash
# Test with models
cd app
py fire_detector_unified.py --mode thermal
py test_all_models.py

# Models are in: data/models/pretrained/
# Best model: yolov10_fire_smoke.pt (85% mAP)
```

### "I need to fix drone simulation issues"

```
Read: SITL_SETUP_GUIDE.md

Quick fixes:
- First run downloads firmware: pip install dronekit-sitl
- Port already in use: taskkill /F /IM python.exe
- Drones not connecting: Wait 30-60 seconds
```

---

## 📋 STATUS CHECK TEMPLATE

Use this when resuming:

```
=== PROJECT STATUS CHECK ===

1. Configuration OK?
   cd app && py config.py
   Expected: Shows paths, models ✅ or ❌

2. Fleet can launch?
   py launch_fleet.py
   Expected: "All 5 SITL instances ready!"

3. Dashboard loads?
   streamlit run dashboard_fleet_real.py --server.port 8506
   Expected: Opens at http://localhost:8506

4. Drones connect?
   Click "Connect All Drones"
   Expected: 5 green status cards

5. Mission works?
   Load mission → Execute Mission
   Expected: Drones fly to waypoints
```

---

## 🔧 TROUBLESHOOTING RESUME ISSUES

### "pip packages missing"
```bash
pip install -r requirements.txt
pip install dronekit-sitl
```

### "Ports already in use"
```bash
taskkill /F /IM streamlit.exe
taskkill /F /IM python.exe
```

### "Models not found"
```bash
# Check symlink
ls data/models/pretrained/

# Or create config_local.py with your paths
copy app\config_local.example.py app\config_local.py
```

### "SITL won't start"
```bash
# Remove old SITL data
rmdir /s /q %LOCALAPPDATA%\dronekit-sitl

# Reinstall
pip uninstall dronekit-sitl
pip install dronekit-sitl
```

---

## 📊 WHAT'S COMPLETED

✅ **Working Now:**
- 5-drone SITL fleet simulation
- Fleet Control Dashboard (port 8506)
- Mission Planner (port 8507)
- Mission Integration (load & execute)
- Fire Detection (6 models, 85% mAP best)
- Configuration System (private paths)
- GitHub Repository (clean)

⏳ **Next Steps:**
- Order Phase 1A hardware (€598)
- Test on real Raspberry Pi 4
- Test InfiRay P2Pro thermal camera
- Test LoRa communication

---

## 🤖 FOR AI AGENTS

### Context Prompt Template

Copy this to give a new AI agent context:

```
I'm working on a Fire Drone Swarm project for wildfire detection.

Current State:
- 5-drone simulation working (DroneKit-SITL)
- Fleet Control Dashboard (Streamlit on port 8506)
- Mission Planner (Streamlit on port 8507)
- Fire Detection (YOLOv8, best model 85% mAP)
- Phase 0 complete, Phase 1A ready

Key Files:
- app/launch_fleet.py - Start drones
- app/dashboard_fleet_real.py - Fleet UI
- app/dashboard_mission.py - Mission planner
- app/config.py - Configuration
- docs/PROJECT_STATE.md - Full documentation

GitHub: https://github.com/samer-buraei/Project-swarm

To run:
1. cd app && py launch_fleet.py
2. streamlit run dashboard_fleet_real.py --server.port 8506
3. Open http://localhost:8506

Read docs/PROJECT_STATE.md for complete context.
```

---

## 📚 DOCUMENT HIERARCHY

```
Most Important (Read First)
├── PROJECT_STATE.md      - Everything about the system
├── QUICKSTART.md         - How to run it
└── LIVE_PROGRESS.md      - Current status

Development
├── DEVELOPER_GUIDE.md    - How to code
└── config.py             - Path management

Reference
├── SITL_SETUP_GUIDE.md   - Drone simulation
├── COMPLETE_PLAN.md      - Full project plan
└── Historical docs       - Past decisions
```

---

## ✅ BEFORE HANDING OFF

Checklist before giving this to another agent/developer:

- [ ] Update PROJECT_STATE.md if you made changes
- [ ] Update LIVE_PROGRESS.md with current status
- [ ] Verify `py config.py` runs without errors
- [ ] Verify `py launch_fleet.py` starts 5 drones
- [ ] Verify dashboards load (ports 8506, 8507)
- [ ] Push any changes to GitHub
- [ ] Note any issues encountered in docs

---

**When in doubt, read PROJECT_STATE.md** 📖
