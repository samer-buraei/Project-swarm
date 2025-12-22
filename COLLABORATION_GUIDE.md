# 🤝 FireSwarm Collaboration Guide

## For AI Agents & Engineers Joining the Project

**Last Updated:** December 22, 2025  
**Project Status:** Phase 1A - Hardware Testing & Core Development

---

## 📋 QUICK PROJECT SUMMARY

**What is this?** A fleet of 5 autonomous drones with thermal cameras that detect wildfires in real-time using AI, streaming video to a human operator who makes final decisions.

**Key Numbers:**
| Metric | Target |
|--------|--------|
| Drones | 5 autonomous units |
| Flight Time | **60 minutes** per battery |
| Detection | YOLOv8-nano on-drone (2 FPS) |
| Connectivity | 4G/LTE primary + LoRa backup |
| Cost | ~$1,285/drone, ~$6,775 total |

**Hardware Stack (Confirmed):**
- **Compute:** Raspberry Pi 5 (8GB)
- **Thermal Camera:** InfiRay P2 Pro (256×192, 25Hz, radiometric)
- **Flight Controller:** Pixhawk 6C + ArduPilot
- **Frame:** GEPRC Mark4 10"
- **Battery:** Li-Ion 6S 8000mAh (Molicel P42A)
- **Connectivity:** Sixfab 4G/LTE + Heltec LoRa V3 (Meshtastic)

---

## 🗂️ PROJECT STRUCTURE

```
Project swarm 2/
├── 📁 app/                          # Main application code
│   ├── simulation.py                # Single drone simulator
│   ├── multi_drone_launcher.py      # 5-drone launcher
│   ├── fire_detector_unified.py     # YOLO fire detection
│   ├── thermal_simulation.py        # Thermal camera simulator
│   ├── drone_control.py             # MAVLink drone control
│   ├── dashboard.py                 # Single drone UI
│   ├── dashboard_multi.py           # Fleet command center UI
│   ├── dashboard_fleet.py           # Fleet overview
│   ├── recorder.py                  # Recording system
│   ├── sync_to_base.py              # Ground station sync
│   ├── export_for_pi.py             # Model export for edge
│   └── *.py                         # Other utilities
│
├── 📁 scripts/                      # Utility scripts
│   ├── train_fire_model.py          # YOLO training
│   ├── export_model.py              # Model export
│   ├── evaluate_model.py            # Model evaluation
│   └── *.py                         # Dataset tools
│
├── 📁 models/                       # AI models
│   └── yolov8n.pt                   # Base YOLO model
│
├── 📁 P2Pro-Viewer/                 # Thermal camera driver
│   ├── main.py                      # P2 Pro viewer
│   └── P2Pro/                       # Driver modules
│
├── 📁 docs/                         # Documentation (30+ files)
│   ├── PROJECT_STATE.md             # Master overview
│   ├── HARDWARE_BOM.md              # Complete parts list
│   ├── P2PRO_INTEGRATION_GUIDE.md   # Thermal camera setup
│   ├── CONNECTIVITY_ARCHITECTURE.md # 4G/LoRa networking
│   ├── DEVELOPMENT_PHASES.md        # 10-week plan
│   ├── START_HERE_DOCUMENT_INDEX.md # Document navigation
│   └── *.md                         # Other docs
│
├── README.md                        # Project overview
├── COLLABORATION_GUIDE.md           # THIS FILE
├── requirements.txt                 # Python dependencies
└── run_demo.bat                     # Quick demo launcher
```

---

## 📚 KEY DOCUMENTS TO READ FIRST

| Priority | Document | What You'll Learn |
|----------|----------|-------------------|
| 1️⃣ | [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) | Full system overview, architecture |
| 2️⃣ | [`docs/HARDWARE_BOM.md`](docs/HARDWARE_BOM.md) | All components, vendors, prices |
| 3️⃣ | [`docs/DEVELOPMENT_PHASES.md`](docs/DEVELOPMENT_PHASES.md) | 10-week MVP roadmap |
| 4️⃣ | [`docs/P2PRO_INTEGRATION_GUIDE.md`](docs/P2PRO_INTEGRATION_GUIDE.md) | Thermal camera code |
| 5️⃣ | [`docs/CONNECTIVITY_ARCHITECTURE.md`](docs/CONNECTIVITY_ARCHITECTURE.md) | 4G + LoRa networking |
| 6️⃣ | [`docs/PROPOSAL_ANALYSIS.md`](docs/PROPOSAL_ANALYSIS.md) | Tech decisions & trade-offs |

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                           GROUND STATION                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │   React/        │  │   FastAPI       │  │   SQLite/           │  │
│  │   Streamlit UI  │◄─┤   Backend       │◄─┤   PostgreSQL        │  │
│  │   (Operator)    │  │                 │  │                     │  │
│  └────────▲────────┘  └────────▲────────┘  └─────────────────────┘  │
│           │                    │                                     │
│           │         ┌─────────┴──────────┐                          │
│           │         │ MediaMTX (Video)   │                          │
│           │         │ Tailscale (VPN)    │                          │
│           │         └─────────┬──────────┘                          │
└───────────┼───────────────────┼─────────────────────────────────────┘
            │                   │
     ┌──────┴───────┐   ┌──────┴───────┐   NETWORK
     │   4G/LTE     │   │   LoRa       │   (hybrid)
     │   (primary)  │   │   (backup)   │
     └──────┬───────┘   └──────┬───────┘
            │                   │
┌───────────┼───────────────────┼─────────────────────────────────────┐
│           ▼                   ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    DRONE (x5)                                │    │
│  │                                                              │    │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐              │    │
│  │  │ P2 Pro   │───▶│ Pi 5     │───▶│ Pixhawk  │              │    │
│  │  │ Thermal  │    │ YOLOv8n  │    │ 6C       │              │    │
│  │  │ 256×192  │    │ ~2 FPS   │    │ ArduPilot│              │    │
│  │  └──────────┘    └─────┬────┘    └──────────┘              │    │
│  │                        │                                    │    │
│  │                   Fire?│                                    │    │
│  │                   Temp>80°C                                 │    │
│  │                   Conf>0.7                                  │    │
│  │                        │                                    │    │
│  │                        ▼                                    │    │
│  │  ┌──────────────────────────────────────────────────┐      │    │
│  │  │ Alert: GPS + Temp + Confidence + Video Frame     │      │    │
│  │  └──────────────────────────────────────────────────┘      │    │
│  │                                                              │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                           DRONE                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 🔌 DATA FLOW

```
1. P2 Pro captures thermal frame (256×192 @ 25Hz)
2. P2Pro-Viewer extracts raw radiometric data
3. Temperature conversion: T = (raw × 0.0625) - 273.15
4. Frame resized for YOLO input
5. YOLOv8-nano inference (~500ms on Pi 5)
6. Fire check: (Temp > 80°C) AND (Confidence > 0.7)
7. If fire: Send alert via 4G/LTE (or LoRa if offline)
8. Ground station receives alert + video stream
9. Human operator CONFIRMS or DISMISSES
10. If CONFIRMED: Alert fire department
```

---

## 👷 EXPERT PERSONAS & PROMPTS

Use these prompts to spin up AI agents or brief human engineers on specific roles.

---

### 🔥 PERSONA 1: THERMAL CAMERA ENGINEER

**Role:** Integrate InfiRay P2 Pro with Raspberry Pi 5 for fire detection

**Context Prompt:**
```
You are a Thermal Camera Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm using thermal cameras
YOUR FOCUS: InfiRay P2 Pro thermal camera integration

HARDWARE:
- InfiRay P2 Pro: 256×192, 25Hz, -20°C to 550°C, radiometric
- Raspberry Pi 5 (8GB)
- USB Type-C connection (UVC compatible)

KEY FILES TO READ:
1. docs/P2PRO_INTEGRATION_GUIDE.md - Full integration guide
2. P2Pro-Viewer/ - Open source driver (clone of github.com/LeoDJ/P2Pro-Viewer)
3. app/thermal_simulation.py - Current thermal simulation

YOUR TASKS:
1. Get P2 Pro streaming on Pi 5 using P2Pro-Viewer
2. Extract radiometric temperature data (not just visual)
3. Implement temperature-to-Celsius conversion
4. Create fire threshold detection (>80°C)
5. Output frames for YOLO pipeline

TEMPERATURE CONVERSION FORMULA:
  celsius = (raw_value * 0.0625) - 273.15

SUCCESS CRITERIA:
- Pi 5 displays 256×192 thermal video
- Console shows max temperature per frame
- Fire alert triggers when temp > 80°C
```

---

### 🧠 PERSONA 2: AI/ML ENGINEER

**Role:** Optimize YOLO fire detection for Raspberry Pi 5 edge deployment

**Context Prompt:**
```
You are an AI/ML Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm with on-device AI
YOUR FOCUS: YOLOv8-nano optimization for Raspberry Pi 5

HARDWARE:
- Raspberry Pi 5 (8GB) - Target device
- No GPU acceleration (CPU only on Pi)
- Optional: Coral USB Accelerator for future

CURRENT STATE:
- YOLOv8n base model exists (models/yolov8n.pt)
- Target: 2 FPS minimum (~500ms/frame)
- Fire datasets: D-Fire, FLAME (aerial thermal)

KEY FILES TO READ:
1. app/fire_detector_unified.py - Current detection code
2. scripts/train_fire_model.py - Training pipeline
3. scripts/export_model.py - Edge export (TFLite, ONNX)
4. docs/DATASET_DOWNLOAD_INSTRUCTIONS.md - Training data

YOUR TASKS:
1. Benchmark current model on Pi 5 (FPS, latency)
2. Quantize to INT8 for faster inference
3. Test TFLite export for Pi deployment
4. Fine-tune on D-Fire + FLAME datasets
5. Validate 80%+ mAP on fire detection

INFERENCE PIPELINE:
  Frame (256×192) → Resize (640×640) → YOLO → Boxes + Confidence

SUCCESS CRITERIA:
- Inference < 600ms on Pi 5 (CPU)
- Fire detection mAP > 80%
- Model size < 10MB (TFLite INT8)
```

---

### 🛩️ PERSONA 3: DRONE/FLIGHT ENGINEER

**Role:** ArduPilot integration and autonomous patrol implementation

**Context Prompt:**
```
You are a Drone/Flight Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm with 60-minute flight time
YOUR FOCUS: ArduPilot integration, autonomous patrol, MAVLink control

HARDWARE:
- Flight Controller: Pixhawk 6C
- Firmware: ArduPilot (Copter 4.5+)
- Frame: GEPRC Mark4 10"
- Motors: BrotherHobby 3115 900KV
- Battery: Li-Ion 6S 8000mAh (Molicel P42A)
- GPS: Matek M10-5883

KEY FILES TO READ:
1. docs/HARDWARE_BOM.md - Full parts list
2. app/drone_control.py - Current MAVLink code
3. docs/SITL_SETUP_GUIDE.md - Simulation setup
4. app/test_sitl_mavlink.py - SITL testing

YOUR TASKS:
1. Set up ArduPilot SITL for testing
2. Implement pymavlink connection (not MAVSDK)
3. Create autonomous patrol waypoint mission
4. Implement RTL (Return to Launch) failsafe
5. Monitor battery and trigger low-battery RTL

MAVLINK MESSAGES:
- GPS: GLOBAL_POSITION_INT
- Attitude: ATTITUDE
- Battery: SYS_STATUS
- Heartbeat: HEARTBEAT

SUCCESS CRITERIA:
- Drone follows patrol waypoints in SITL
- Auto-RTL when battery < 20%
- Auto-RTL when connectivity lost > 30s
- 60-minute flight simulation successful
```

---

### 📡 PERSONA 4: CONNECTIVITY ENGINEER

**Role:** 4G/LTE primary + LoRa backup hybrid networking

**Context Prompt:**
```
You are a Connectivity Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm with hybrid connectivity
YOUR FOCUS: 4G/LTE primary, LoRa/Meshtastic backup, failover logic

HARDWARE:
- 4G/LTE: Sixfab Cellular Modem Kit (for Pi 5)
- LoRa: Heltec ESP32 LoRa V3 (drones) + RAK WisBlock (ground station)
- VPN: Tailscale for secure tunnel

KEY FILES TO READ:
1. docs/CONNECTIVITY_ARCHITECTURE.md - Full architecture
2. docs/HARDWARE_BOM.md - Hardware specs

YOUR TASKS:
1. Set up Sixfab 4G modem on Pi 5
2. Configure Tailscale VPN for secure connection
3. Set up Meshtastic on Heltec LoRa devices
4. Implement ConnectivityManager class with failover
5. Test failover: 4G → LoRa → Auto-RTL

FAILOVER LOGIC:
  1. Check 4G ping every 5 seconds
  2. If 4G fails 3x: Switch to LoRa
  3. If LoRa fails 3x: Trigger RTL failsafe
  4. Heartbeat timeout: 30 seconds

DATA PRIORITIES (4G vs LoRa):
  4G: Video stream (500kbps+), full telemetry, commands
  LoRa: Fire alerts only (GPS, temp, confidence) - 256 bytes max

SUCCESS CRITERIA:
- 4G streams video at 720p/15fps
- LoRa delivers alert in < 2 seconds
- Failover happens within 15 seconds
- Auto-RTL triggers if both fail
```

---

### 🖥️ PERSONA 5: FRONTEND/UI ENGINEER

**Role:** Operator dashboard (React + Map visualization)

**Context Prompt:**
```
You are a Frontend/UI Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm command center
YOUR FOCUS: Operator dashboard with map, video feeds, fleet control

CURRENT STATE:
- Streamlit prototypes exist (dashboard.py, dashboard_multi.py)
- Need production React app

KEY FILES TO READ:
1. app/dashboard_multi.py - Current multi-drone UI (Streamlit)
2. app/dashboard_fleet.py - Fleet overview
3. docs/PROPOSAL_ANALYSIS.md - UI design decisions
4. docs/DEVELOPMENT_PHASES.md - Phase 1-5 UI requirements

YOUR TASKS:
1. Design tactical operator interface
2. Implement 5-drone video matrix (WebRTC)
3. Add interactive map with drone positions
4. Create fire alert workflow (CONFIRM/DISMISS)
5. Show fleet telemetry (battery, GPS, status)

UI REQUIREMENTS:
- 5 video feeds in grid (thumbnail + expand)
- Map: Leaflet or Mapbox with 5 drone markers
- Fire alert: Red flash + sound + action buttons
- Battery warnings: Yellow < 30%, Red < 15%
- Connection status: Green/Yellow/Red per drone

TECH STACK:
- Frontend: React + TypeScript
- Video: WebRTC (via MediaMTX)
- Map: Leaflet or react-map-gl
- State: React Query or Zustand
- Backend API: FastAPI (Python)

SUCCESS CRITERIA:
- All 5 drones visible on map
- Video matrix updates in real-time
- Fire alert to operator response < 5 seconds
- Works on tablet (responsive design)
```

---

### ⚙️ PERSONA 6: BACKEND ENGINEER

**Role:** FastAPI backend, database, ground station services

**Context Prompt:**
```
You are a Backend Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm ground station
YOUR FOCUS: FastAPI backend, database, alert management

KEY FILES TO READ:
1. docs/CONNECTIVITY_ARCHITECTURE.md - Data flow
2. app/dashboard_*.py - Current backend logic (embedded in Streamlit)
3. docs/DEVELOPMENT_PHASES.md - Backend requirements by phase

YOUR TASKS:
1. Create FastAPI application structure
2. Design database schema (SQLite → PostgreSQL)
3. Implement WebSocket for real-time telemetry
4. Create REST API for drone commands
5. Build alert management system

API ENDPOINTS:
  GET  /api/drones              - List all drones
  GET  /api/drones/{id}         - Single drone status
  POST /api/drones/{id}/command - Send command (RTL, PATROL, etc.)
  GET  /api/alerts              - List alerts
  POST /api/alerts/{id}/confirm - Confirm fire alert
  POST /api/alerts/{id}/dismiss - Dismiss false positive
  WS   /ws/telemetry            - Real-time telemetry stream

DATABASE SCHEMA:
  drones: id, name, status, last_seen, battery, gps_lat, gps_lon
  alerts: id, drone_id, timestamp, gps, temp, confidence, status, video_url
  missions: id, drone_id, waypoints[], status, start_time, end_time

TECH STACK:
- FastAPI + Pydantic
- SQLAlchemy + Alembic (migrations)
- SQLite (dev) → PostgreSQL (prod)
- WebSocket for streaming
- MediaMTX integration for video

SUCCESS CRITERIA:
- API handles 5 drones at 2 updates/second each
- Alert latency < 100ms (receive to broadcast)
- Database persists all telemetry and alerts
```

---

### 🔧 PERSONA 7: DEVOPS/INTEGRATION ENGINEER

**Role:** System integration, testing, deployment pipelines

**Context Prompt:**
```
You are a DevOps/Integration Engineer for the FireSwarm drone project.

PROJECT: Fire detection drone swarm deployment
YOUR FOCUS: CI/CD, testing, Raspberry Pi deployment, ground station setup

KEY FILES TO READ:
1. docs/DEVELOPMENT_PHASES.md - Phase milestones
2. requirements.txt - Python dependencies
3. docs/SITL_SETUP_GUIDE.md - Simulation testing

YOUR TASKS:
1. Create CI/CD pipeline (GitHub Actions)
2. Set up automated testing (pytest)
3. Create Pi 5 deployment scripts
4. Document ground station setup
5. Create Docker containers for ground station

TESTING REQUIREMENTS:
- Unit tests for fire detection
- Integration tests for MAVLink
- SITL simulation tests (5 drones)
- Performance benchmarks (FPS, latency)

DEPLOYMENT TARGETS:
- Raspberry Pi 5: Python 3.11, opencv, ultralytics, pymavlink
- Ground Station: Docker Compose (FastAPI, MediaMTX, PostgreSQL)

PI 5 SETUP SCRIPT:
  1. Flash Raspberry Pi OS (64-bit)
  2. Install dependencies
  3. Clone repo
  4. Set up systemd services
  5. Configure 4G modem
  6. Configure camera

SUCCESS CRITERIA:
- One-command Pi 5 setup
- All tests pass in CI
- Ground station deploys via docker-compose up
```

---

## 🚀 CURRENT PHASE: 1A (DESK TESTING)

### What's Happening Now

| Task | Status | Owner |
|------|--------|-------|
| Order P2 Pro thermal camera | ⏳ Pending | Hardware lead |
| Order Raspberry Pi 5 | ⏳ Pending | Hardware lead |
| Order Sixfab 4G modem | ⏳ Pending | Hardware lead |
| Test P2Pro-Viewer on Pi 5 | 🔲 Blocked | Thermal Camera Engineer |
| Test YOLO on Pi 5 | 🔲 Blocked | AI/ML Engineer |
| Test 4G connectivity | 🔲 Blocked | Connectivity Engineer |

### Parallel Tasks Available NOW

These can start immediately (SITL/simulation, no hardware needed):

| Task | Persona | Files to Create/Modify |
|------|---------|------------------------|
| ArduPilot SITL testing | Drone Engineer | app/drone_control.py |
| YOLO optimization research | AI/ML Engineer | scripts/train_fire_model.py |
| FastAPI backend scaffold | Backend Engineer | app/api/ (new) |
| React dashboard prototype | Frontend Engineer | app/frontend/ (new) |
| CI/CD pipeline setup | DevOps Engineer | .github/workflows/ |

---

## 📝 HOW TO ONBOARD A NEW AGENT/ENGINEER

### Step 1: Share This File
Copy `COLLABORATION_GUIDE.md` and share with the new team member.

### Step 2: Assign Persona
Choose the relevant persona from the list above based on their expertise.

### Step 3: Provide Context Prompt
Copy the **Context Prompt** section for their persona and paste it as their initial briefing.

### Step 4: Point to Key Files
Direct them to the specific files listed in their persona.

### Step 5: Define Deliverables
Specify exactly what files they should create or modify.

---

## 🔄 TASK COORDINATION

### Dependencies Between Personas

```
Thermal Camera Engineer ──┐
                          ├──► AI/ML Engineer (needs thermal frames)
                          │
Drone Engineer ───────────┤
                          ├──► Backend Engineer (needs telemetry format)
                          │
Connectivity Engineer ────┤
                          ├──► DevOps (needs deployment config)
                          │
Frontend Engineer ◄───────┴──► Backend Engineer (API contract)
```

### Communication Protocol

1. **Thermal → AI:** Frame format, resolution, color space
2. **Drone → Backend:** Telemetry JSON schema, MAVLink message types
3. **Connectivity → Backend:** Alert message format, latency requirements
4. **Frontend ↔ Backend:** API contract (OpenAPI spec)

---

## 📂 DELIVERABLES CHECKLIST

After all personas complete their initial tasks:

```
Project swarm 2/
├── app/
│   ├── api/                        # (Backend Engineer)
│   │   ├── main.py                 # FastAPI app
│   │   ├── routes/
│   │   └── models/
│   ├── p2pro_capture.py            # (Thermal Camera Engineer)
│   ├── fire_detector_optimized.py  # (AI/ML Engineer)
│   ├── drone_controller.py         # (Drone Engineer)
│   └── connectivity_manager.py     # (Connectivity Engineer)
│
├── app/frontend/                   # (Frontend Engineer)
│   ├── src/
│   └── package.json
│
├── tests/                          # (DevOps Engineer)
│   ├── test_detection.py
│   ├── test_mavlink.py
│   └── test_connectivity.py
│
├── .github/workflows/              # (DevOps Engineer)
│   └── ci.yml
│
└── docker-compose.yml              # (DevOps Engineer)
```

---

## 📞 QUICK REFERENCE

| Question | Answer |
|----------|--------|
| **Thermal Camera?** | InfiRay P2 Pro, 256×192, 25Hz |
| **Compute?** | Raspberry Pi 5 (8GB) |
| **AI Model?** | YOLOv8-nano, ~500ms on Pi 5 |
| **Flight Time?** | 60 minutes (Li-Ion 6S 8000mAh) |
| **Primary Connectivity?** | 4G/LTE (Sixfab) |
| **Backup Connectivity?** | LoRa/Meshtastic |
| **Ground Station UI?** | React (production), Streamlit (prototype) |
| **Backend?** | FastAPI + SQLite/PostgreSQL |
| **Total Budget?** | ~$6,775 for 5 drones |

---

**Document Version:** 1.0  
**Created:** December 22, 2025  
**Maintainer:** Project Lead
