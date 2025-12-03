# Data, Training & Multi-Drone Architecture

**Created:** November 2024  
**Status:** Planning Document for Phase 1+  
**Questions Addressed:**
1. Training on real drone videos?
2. Recording & telemetry storage for future training?
3. Thermal drone fire datasets to download?
4. Multi-drone UI showing all feeds centrally?

---

## 1. TRAINING STRATEGY: REAL DRONE VIDEOS

### Current State (Phase 0)
- Using **D-Fire dataset** (21,527 ground-based images)
- Model: YOLOv8n trained on COCO (not fire-specific)
- Works for simulation, NOT production

### Phase 1+ Training Plan

```
TRAINING DATA HIERARCHY:

┌─────────────────────────────────────────────────────────────┐
│  TIER 1: Public Aerial Fire Datasets (Download Now)        │
│  ├── FLAME Dataset (Arizona prescribed burns)              │
│  ├── D-Fire (already have - ground-based)                  │
│  └── FIRESENSE (European fire dataset)                     │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: Collected During Phase 3 Testing                  │
│  ├── Our own drone thermal recordings                      │
│  ├── Labeled by operator (CONFIRM/DISMISS decisions)       │
│  └── Various weather/terrain conditions                    │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: Continuous Learning (Production)                  │
│  ├── Every patrol adds new data                            │
│  ├── False positives → negative training examples          │
│  └── Confirmed fires → positive training examples          │
└─────────────────────────────────────────────────────────────┘
```

### Training Pipeline

```python
# PROPOSED TRAINING WORKFLOW

Phase 1A (Before Hardware):
├── Download FLAME dataset (aerial thermal)
├── Download additional fire datasets
├── Fine-tune YOLOv8n on combined dataset
├── Test on D-Fire validation set
└── Target: 90%+ fire detection, <10% false positives

Phase 3 (Field Testing):
├── Collect 100+ hours of patrol footage
├── Label operator decisions (CONFIRM/DISMISS)
├── Retrain model weekly with new data
└── Track accuracy improvement over time

Production:
├── Nightly sync of all drone recordings to base
├── Weekly model retraining with operator feedback
├── A/B testing of new models before deployment
└── Continuous accuracy monitoring
```

---

## 2. RECORDING & TELEMETRY STORAGE ARCHITECTURE

### The Problem
- Drones operate offline (no real-time cloud sync)
- Need to store ALL recordings for future training
- Need telemetry data for debugging and improvement

### Solution: Hierarchical Storage

```
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────┘

LEVEL 1: ON-DRONE STORAGE (During Flight)
┌──────────────────────────────────────────────────────────┐
│  Raspberry Pi 4                                          │
│  ├── SD Card (128GB minimum)                            │
│  │   ├── /recordings/                                    │
│  │   │   ├── 2024-11-28_patrol_001/                     │
│  │   │   │   ├── thermal_raw/  (160x120 frames, 16-bit) │
│  │   │   │   ├── thermal_video.mp4 (compressed)         │
│  │   │   │   ├── rgb_video.mp4 (if RGB camera attached) │
│  │   │   │   ├── telemetry.csv (GPS, altitude, heading) │
│  │   │   │   ├── detections.json (YOLO outputs)         │
│  │   │   │   └── metadata.json (start/end time, etc)    │
│  │   │   └── 2024-11-28_patrol_002/                     │
│  │   └── /models/                                        │
│  │       └── yolov8n_fire_v2.tflite (current model)     │
│  └── Retention: Last 7 days (auto-delete oldest)        │
└──────────────────────────────────────────────────────────┘
           │
           │ WiFi Sync (When Landed)
           ▼
LEVEL 2: BASE STATION STORAGE (Aggregation)
┌──────────────────────────────────────────────────────────┐
│  Operator Laptop / NAS                                   │
│  ├── External HDD (2TB minimum)                         │
│  │   ├── /drones/                                        │
│  │   │   ├── drone_01/                                   │
│  │   │   │   ├── 2024-11-28_patrol_001/                 │
│  │   │   │   └── 2024-11-28_patrol_002/                 │
│  │   │   ├── drone_02/                                   │
│  │   │   └── ... (all 5 drones)                         │
│  │   ├── /training_data/                                 │
│  │   │   ├── confirmed_fires/    (operator said YES)    │
│  │   │   ├── false_positives/    (operator said NO)     │
│  │   │   └── unlabeled/          (no operator decision) │
│  │   └── /models/                                        │
│  │       ├── yolov8n_fire_v1.tflite                     │
│  │       ├── yolov8n_fire_v2.tflite                     │
│  │       └── training_logs/                              │
│  └── SQLite Database                                     │
│      ├── detections (all fire alerts)                   │
│      ├── operator_decisions (CONFIRM/DISMISS)           │
│      ├── drone_flights (start, end, stats)              │
│      └── system_events (errors, warnings)               │
└──────────────────────────────────────────────────────────┘
           │
           │ Weekly/Monthly Backup (Optional Cloud)
           ▼
LEVEL 3: CLOUD ARCHIVE (Optional, for long-term)
┌──────────────────────────────────────────────────────────┐
│  Cloud Storage (AWS S3 / Google Drive / etc)            │
│  ├── Monthly archives of all recordings                 │
│  ├── Training datasets (curated)                        │
│  └── Model checkpoints                                   │
│  Note: NOT real-time. Batch upload when internet avail. │
└──────────────────────────────────────────────────────────┘
```

### Data Formats

| Data Type | Format | Size Estimate | Retention |
|-----------|--------|---------------|-----------|
| Thermal Raw | 16-bit PNG per frame | ~50KB/frame | 7 days on drone |
| Thermal Video | H.264 MP4 | ~10MB/min | 30 days on base |
| RGB Video | H.264 MP4 | ~50MB/min | 30 days on base |
| Telemetry | CSV | ~100KB/hour | Forever |
| Detections | JSON | ~1KB/detection | Forever |
| Operator Decisions | SQLite | ~1KB/decision | Forever |

### Sync Protocol

```
WIFI SYNC WORKFLOW (When Drone Lands):

1. Drone connects to base station WiFi (5GHz, dedicated)
2. rsync new files to base station HDD
3. Verify checksums
4. Mark synced files on drone (don't re-sync)
5. Delete files >7 days old on drone SD card
6. Download new model if available

Estimated sync time: 5-10 min for 1 hour of patrol
```

---

## 3. THERMAL DRONE FIRE DATASETS TO DOWNLOAD

### Recommended Datasets

| Dataset | Type | Size | Source | Priority |
|---------|------|------|--------|----------|
| **FLAME** | Aerial thermal+RGB | 2.3GB | IEEE/Arizona | ⭐⭐⭐⭐⭐ |
| **D-Fire** | Ground thermal | 2.8GB | Already have | ⭐⭐⭐⭐ |
| **FIRESENSE** | Multi-sensor | 1.5GB | EU Project | ⭐⭐⭐ |
| **ForestFire** | Aerial RGB | 500MB | Kaggle | ⭐⭐ |

### FLAME Dataset Details

```
FLAME (Fire Luminosity Airborne-based Machine learning Evaluation)

Source: IEEE DataPort / University of Arizona
Content:
├── 2,003 aerial images from prescribed burns
├── Both RGB and thermal (IR) images
├── Captured by DJI drones at various altitudes
├── Labeled fire/smoke/background regions
├── Real pine forest fires (controlled burns)

Why it's critical:
├── AERIAL perspective (matches our drones)
├── THERMAL data (matches our P2Pro camera)
├── Real fires (not synthetic)
├── Diverse conditions (smoke, flames, embers)

Download: https://ieee-dataport.org/open-access/flame-dataset
Paper: https://arxiv.org/abs/2012.14036
```

### Download Commands

```bash
# Create datasets directory
mkdir -p datasets/FLAME
mkdir -p datasets/FIRESENSE

# FLAME Dataset (need IEEE account - free)
# Download from: https://ieee-dataport.org/open-access/flame-dataset
# Extract to: datasets/FLAME/

# Alternative: Kaggle mirror
# pip install kaggle
# kaggle datasets download -d phylake1337/fire-dataset

# D-Fire (already have)
# Located at: DFireDataset/
```

### Combined Training Dataset Structure

```
datasets/
├── D-Fire/                    # Ground-based (already have)
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   └── test/
├── FLAME/                     # Aerial thermal (download)
│   ├── RGB/
│   ├── Thermal/
│   └── Labels/
├── FIRESENSE/                 # European (download)
├── OurData/                   # Collected during testing
│   ├── confirmed_fires/
│   └── false_positives/
└── Combined/                  # Merged for training
    ├── train/
    ├── val/
    └── test/
```

---

## 4. MULTI-DRONE UI ARCHITECTURE

### Current State
- Dashboard shows **1 drone only**
- Single video feed
- Single map marker

### Target State: 5-Drone Command Center

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🦅 FIRE SWARM COMMAND                                      ● 5 ONLINE │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │                                 │  │  📡 FLEET STATUS             │ │
│  │                                 │  │  ┌────┬────┬────┬────┬────┐  │ │
│  │                                 │  │  │ A1 │ A2 │ A3 │ A4 │ A5 │  │ │
│  │        🗺️ TACTICAL MAP         │  │  │ ✓  │ ✓  │ 🔋 │ ✓  │ ⚠️ │  │ │
│  │                                 │  │  └────┴────┴────┴────┴────┘  │ │
│  │     🔵 A1   🔵 A2              │  │                               │ │
│  │              🔴 FIRE!          │  │  Selected: Drone A2           │ │
│  │     🔵 A4                      │  │  Battery: 73%                 │ │
│  │              🔵 A5             │  │  Altitude: 85m                │ │
│  │                                 │  │  Signal: -42 dBm             │ │
│  │     ⚪ A3 (charging)           │  │                               │ │
│  └─────────────────────────────────┘  └──────────────────────────────┘ │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  📹 DRONE FEEDS                                                      ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       ││
│  │  │  A1     │ │  A2 🔥  │ │  A3     │ │  A4     │ │  A5     │       ││
│  │  │ [feed]  │ │ [feed]  │ │ OFFLINE │ │ [feed]  │ │ [feed]  │       ││
│  │  │ 84% ✓   │ │ 73% ⚠️  │ │ CHARGING│ │ 91% ✓   │ │ 45% ⚠️  │       ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       ││
│  │                                                                      ││
│  │  Click any feed to expand | Double-click for full screen            ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  📜 GLOBAL EVENT LOG            │  │  🎮 FLEET COMMANDS           │ │
│  │  [11:45:23] A2: 🔥 FIRE 95%    │  │  [RTL ALL] [PAUSE ALL]       │ │
│  │  [11:44:12] A5: Low battery    │  │  [RESUME]  [EMERGENCY]       │ │
│  │  [11:43:01] A3: Landed         │  │                               │ │
│  │  [11:42:45] A1: Patrol start   │  │  Individual: [Select Drone ▼]│ │
│  └─────────────────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### UI Components

| Component | Description | Implementation |
|-----------|-------------|----------------|
| **Fleet Status Bar** | All 5 drones at a glance | Horizontal status indicators |
| **Tactical Map** | All drone positions + fire markers | PyDeck with 5 layers |
| **Video Grid** | 5 thumbnail feeds | Streamlit columns + images |
| **Expanded View** | Click to enlarge one feed | Modal or tab |
| **Global Event Log** | Aggregated from all drones | Merged, sorted by time |
| **Fleet Commands** | RTL ALL, PAUSE ALL, etc. | Button panel |

### Data Flow for Multi-Drone

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Drone A1 │  │ Drone A2 │  │ Drone A3 │  │ Drone A4 │  │ Drone A5 │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │             │
     │ UDP:5001    │ UDP:5002    │ UDP:5003    │ UDP:5004    │ UDP:5005
     │             │             │             │             │
     └──────────────────────┬────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │       BASE STATION          │
              │  ┌───────────────────────┐  │
              │  │ Multi-Drone Listener  │  │
              │  │ (5 UDP ports)         │  │
              │  └───────────┬───────────┘  │
              │              │              │
              │  ┌───────────▼───────────┐  │
              │  │ drone_states.json     │  │
              │  │ {                     │  │
              │  │   "A1": {...},        │  │
              │  │   "A2": {...},        │  │
              │  │   "A3": {...},        │  │
              │  │   "A4": {...},        │  │
              │  │   "A5": {...}         │  │
              │  │ }                     │  │
              │  └───────────┬───────────┘  │
              │              │              │
              │  ┌───────────▼───────────┐  │
              │  │ Streamlit Dashboard   │  │
              │  │ (Multi-Drone View)    │  │
              │  └───────────────────────┘  │
              └─────────────────────────────┘
```

### Implementation Plan

```
PHASE 0 (Current):
✅ Single drone simulation
✅ Single feed in dashboard
✅ Basic telemetry

PHASE 1A (Add Multi-Drone Support):
├── [ ] Modify simulation.py to accept --drone-id parameter
├── [ ] Each drone uses different UDP port (5001-5005)
├── [ ] Each drone saves to different frame file
├── [ ] Dashboard reads all 5 states
├── [ ] Dashboard displays 5-drone grid

PHASE 1B (Polish):
├── [ ] Click-to-expand video feed
├── [ ] Drone selection for detailed view
├── [ ] Fleet-wide commands
├── [ ] Global alert aggregation

PHASE 2 (Production):
├── [ ] Real LoRa communication
├── [ ] Battery monitoring per drone
├── [ ] Automated rotation scheduling
├── [ ] Historical playback
```

---

## 5. IMPLEMENTATION CHECKLIST

### Immediate Actions (Tonight)

- [ ] Download FLAME dataset from IEEE DataPort
- [ ] Organize datasets folder structure
- [ ] Create multi-drone simulation script

### This Week

- [ ] Update dashboard for multi-drone support
- [ ] Test 5-drone simulation locally
- [ ] Document sync protocol
- [ ] Create training data pipeline script

### Before Phase 1A Hardware

- [ ] Fine-tune YOLOv8n on FLAME + D-Fire combined
- [ ] Benchmark new model accuracy
- [ ] Test model on Pi 4 (or simulate latency)

---

## 6. SUMMARY ANSWERS

### Q1: Are we going to train on real drone videos?
**YES.** We will:
1. Download FLAME dataset (aerial thermal drone footage)
2. Combine with D-Fire (ground thermal)
3. Fine-tune YOLOv8n on combined dataset
4. Continuously improve with our own footage from Phase 3

### Q2: How do we store recordings for future training?
**Hierarchical storage:**
1. On-drone SD card (7 days)
2. Base station HDD (30 days)
3. Optional cloud archive (forever)
4. Operator decisions automatically label training data

### Q3: What thermal drone fire datasets should we download?
**Priority order:**
1. ⭐⭐⭐⭐⭐ FLAME Dataset (aerial thermal, 2.3GB)
2. ⭐⭐⭐⭐ D-Fire (already have)
3. ⭐⭐⭐ FIRESENSE (European multi-sensor)

### Q4: Will we have all drone feeds in one central UI?
**YES.** Multi-drone dashboard will show:
- 5 video thumbnails (click to expand)
- Single tactical map with all positions
- Fleet status bar
- Global event log
- Fleet-wide commands

---

## APPENDIX: File Naming Conventions

```
Recordings:
  {drone_id}_{date}_{patrol_number}/
  Example: A1_2024-11-28_patrol_003/

Frame files:
  thermal_{timestamp_ms}.png
  Example: thermal_1732789234567.png

Telemetry:
  telemetry_{date}.csv
  Columns: timestamp, lat, lon, altitude, heading, battery, temp_max, detection_conf

Detections:
  detections_{date}.json
  Format: [{timestamp, lat, lon, conf, bbox, operator_decision}, ...]
```

---

**Document Version:** 1.0  
**Last Updated:** November 28, 2024  
**Next Review:** Before Phase 1A hardware purchase

