# 📚 DOCUMENT INDEX & NAVIGATION

**Complete guide to all project documentation.**

Last Updated: December 3, 2025

---

## 🎯 START HERE

### New Agent / Developer?
Read these in order:

| Order | Document | Time | Purpose |
|-------|----------|------|---------|
| 1️⃣ | **[PROJECT_STATE.md](PROJECT_STATE.md)** | 15 min | Complete system overview |
| 2️⃣ | **[../QUICKSTART.md](../QUICKSTART.md)** | 5 min | Get running fast |
| 3️⃣ | **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** | 20 min | How the code works |

### Just Want to Run It?
```bash
# Start drones
cd app && py launch_fleet.py

# Start dashboard
streamlit run dashboard_fleet_real.py --server.port 8506

# Open browser: http://localhost:8506
```

---

## 📁 DOCUMENT CATEGORIES

### Core Documentation

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[PROJECT_STATE.md](PROJECT_STATE.md)** | Full system overview, architecture, status | First! Always! |
| **[../QUICKSTART.md](../QUICKSTART.md)** | Quick start guide | First time setup |
| **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** | Code tour, how to extend | Before coding |
| **[../LIVE_PROGRESS.md](../LIVE_PROGRESS.md)** | Current status dashboard | Check progress |

### Architecture & Design

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** | Technical architecture | Understanding design |
| **[PHASE_1_ARCHITECTURE_OFFLINE_FIRST.md](PHASE_1_ARCHITECTURE_OFFLINE_FIRST.md)** | Why offline, LoRa design | Hardware planning |
| **[fire_drone_system_diagrams.md](fire_drone_system_diagrams.md)** | Wiring diagrams, block diagrams | Building hardware |

### Phase Execution

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[COMPLETE_PLAN.md](COMPLETE_PLAN.md)** | Full 12-week project plan | Understanding scope |
| **[MASTER_EXECUTION_CHECKLIST_FINAL_CORRECTED.md](MASTER_EXECUTION_CHECKLIST_FINAL_CORRECTED.md)** | Day-by-day execution plan | During execution |
| **[PHASE_0_COMPLETE.md](PHASE_0_COMPLETE.md)** | Phase 0 completion status | After Phase 0 |
| **[HOW_TO_CONTINUE_THIS_PROJECT.md](HOW_TO_CONTINUE_THIS_PROJECT.md)** | How to resume work | After breaks |

### Simulation & Testing

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[SITL_SETUP_GUIDE.md](SITL_SETUP_GUIDE.md)** | DroneKit-SITL setup | SITL issues |
| **[PC_SIMULATION_TESTING_PLAN.md](PC_SIMULATION_TESTING_PLAN.md)** | Testing strategy | Testing phase |
| **[SESSION_REPORT_PC_SIMULATION.md](SESSION_REPORT_PC_SIMULATION.md)** | Simulation test results | Review results |

### Data & Training

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[DATA_TRAINING_AND_MULTI_DRONE_ARCHITECTURE.md](DATA_TRAINING_AND_MULTI_DRONE_ARCHITECTURE.md)** | Training data strategy | Model training |
| **[DATASET_DOWNLOAD_INSTRUCTIONS.md](DATASET_DOWNLOAD_INSTRUCTIONS.md)** | How to get datasets | Dataset setup |

### Historical / Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[THE_HONEST_RECKONING_WHAT_WAS_WRONG.md](THE_HONEST_RECKONING_WHAT_WAS_WRONG.md)** | Why we chose offline architecture | Understanding decisions |
| **[SESSION_SUMMARY_20251130.md](SESSION_SUMMARY_20251130.md)** | Nov 30 session notes | Historical |
| **[SESSION_SUMMARY_20251201.md](SESSION_SUMMARY_20251201.md)** | Dec 1 session notes | Historical |
| **[PROGRESS_REVIEW_20251201.md](PROGRESS_REVIEW_20251201.md)** | Dec 1 progress review | Historical |

---

## 🗺️ DECISION TREE: Which Document?

```
"I'm new to this project"
└── Read: PROJECT_STATE.md → QUICKSTART.md → DEVELOPER_GUIDE.md

"I want to run the system"
└── Read: QUICKSTART.md

"I want to add features"
└── Read: DEVELOPER_GUIDE.md

"I want to understand the architecture"
└── Read: PROJECT_STATE.md → SYSTEM_ARCHITECTURE.md

"I'm debugging drone simulation"
└── Read: SITL_SETUP_GUIDE.md

"I'm resuming after a break"
└── Read: HOW_TO_CONTINUE_THIS_PROJECT.md → LIVE_PROGRESS.md

"I want to train fire detection models"
└── Read: DATA_TRAINING_AND_MULTI_DRONE_ARCHITECTURE.md

"I want to build the hardware"
└── Read: PHASE_1_ARCHITECTURE_OFFLINE_FIRST.md → fire_drone_system_diagrams.md
```

---

## 📊 KEY FILES IN CODEBASE

### Must-Know Scripts

| Script | Purpose | Run Command |
|--------|---------|-------------|
| `app/launch_fleet.py` | Start 5 SITL drones | `py launch_fleet.py` |
| `app/dashboard_fleet_real.py` | Fleet control UI | `streamlit run dashboard_fleet_real.py --server.port 8506` |
| `app/dashboard_mission.py` | Mission planner | `streamlit run dashboard_mission.py --server.port 8507` |
| `app/config.py` | Path configuration | `py config.py` (verify) |
| `app/fire_detector_unified.py` | Fire detection | `py fire_detector_unified.py --mode thermal` |
| `app/test_all_models.py` | Compare models | `py test_all_models.py` |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files to exclude from Git |
| `app/config.py` | Central path configuration |
| `app/config_local.example.py` | Template for private paths |
| `app/config_local.py` | Your private paths (gitignored) |

---

## 🎯 QUICK LINKS BY TASK

### Setup & Running
- [QUICKSTART.md](../QUICKSTART.md) - Get running in 5 minutes
- [requirements.txt](../requirements.txt) - Python packages needed

### Understanding the System
- [PROJECT_STATE.md](PROJECT_STATE.md) - Complete overview
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Code walkthrough

### Simulation
- [SITL_SETUP_GUIDE.md](SITL_SETUP_GUIDE.md) - Drone simulation setup

### Current Status
- [LIVE_PROGRESS.md](../LIVE_PROGRESS.md) - What's working now

---

## ✅ DOCUMENT FRESHNESS

| Document | Last Updated | Status |
|----------|--------------|--------|
| PROJECT_STATE.md | Dec 3, 2025 | ✅ Current |
| QUICKSTART.md | Dec 3, 2025 | ✅ Current |
| DEVELOPER_GUIDE.md | Dec 3, 2025 | ✅ Current |
| LIVE_PROGRESS.md | Dec 3, 2025 | ✅ Current |
| README.md | Dec 3, 2025 | ✅ Current |
| Others | Various | ⚠️ May be older |

---

## 📋 HANDOFF CHECKLIST

Before handing off to another agent:

- [ ] Update PROJECT_STATE.md with any changes
- [ ] Update LIVE_PROGRESS.md with current status
- [ ] Verify all quick start commands work
- [ ] Document any new features or fixes
- [ ] Push to GitHub

---

**Start with PROJECT_STATE.md - it explains everything.** 📖
