# 🚀 PARALLEL TASKS FOR JUNIOR DEV AGENTS

> ⚠️ **DEPRECATED** - This file contains completed Phase 0 tasks.
> 
> 👉 **NEW ENGINEERS:** See [**COLLABORATION_GUIDE.md**](COLLABORATION_GUIDE.md) for current expert personas and prompts!

---

**Instructions:** Copy the relevant section to each agent. They can all work simultaneously.

---

## 📋 TASK STATUS

| Task # | Name | Status | Completed By |
|--------|------|--------|--------------|
| 1 | Multi-Drone Simulation Script | ✅ **COMPLETE** | Agent 1 |
| 2 | Multi-Drone Dashboard UI | ✅ **COMPLETE** | Agent 1 |
| 3 | FLAME Dataset Download Script | ✅ **COMPLETE** | Agent 3 |
| 4 | Recording & Sync System | ✅ **COMPLETE** | Agent 4 |
| 5 | Training Pipeline Script | ✅ **COMPLETE** | Agent 5 |

### 🎉 ALL TASKS COMPLETE!

### Completed Files:
- `multi_drone_launcher.py` - Launches 5 drone instances
- `dashboard_multi.py` - Multi-drone command center UI
- `simulation.py` - Updated with argparse for multi-drone support

### How to Test:
```bash
# Terminal 1
python multi_drone_launcher.py

# Terminal 2
streamlit run dashboard_multi.py
```

---

## 📋 REMAINING TASKS

| Task # | Name | Can Run In Parallel | Est. Time |
|--------|------|---------------------|-----------|
| 3 | FLAME Dataset Download Script | ✅ Yes | 10 min |
| 4 | Recording & Sync System | ✅ Yes | 15 min |
| 5 | Training Pipeline Script | ✅ Yes | 15 min |

---

# ═══════════════════════════════════════════════════════════
# TASK 1: MULTI-DRONE SIMULATION SCRIPT
# ═══════════════════════════════════════════════════════════

## COPY THIS TO AGENT 1:

```
PROJECT CONTEXT:
- Fire detection drone swarm project
- Currently have single-drone simulation (simulation.py)
- Need to support 5 drones running simultaneously
- Each drone should have unique ID, UDP port, and frame file

YOUR TASK:
Create a new file: multi_drone_launcher.py

REQUIREMENTS:
1. Launch 5 instances of simulation logic
2. Each drone has:
   - Unique ID: A1, A2, A3, A4, A5
   - Unique UDP port: 5001, 5002, 5003, 5004, 5005
   - Unique frame file: live_frame_A1.jpg, live_frame_A2.jpg, etc.
   - Different starting image index (spread across dataset)

3. Can be run with: python multi_drone_launcher.py
4. Should show status of all 5 drones in terminal
5. Press 'q' to quit all drones

REFERENCE THE EXISTING FILE:
- Read simulation.py to understand current structure
- Reuse the YOLO model loading and inference code
- Modify UDP port and frame file paths per drone

OUTPUT FILES TO CREATE:
1. multi_drone_launcher.py - Main launcher
2. drone_instance.py - Single drone class (optional, can be inline)

EXAMPLE STRUCTURE:
```python
# multi_drone_launcher.py
import multiprocessing
from drone_instance import DroneSimulator

DRONES = [
    {"id": "A1", "port": 5001, "start_idx": 0},
    {"id": "A2", "port": 5002, "start_idx": 800},
    {"id": "A3", "port": 5003, "start_idx": 1600},
    {"id": "A4", "port": 5004, "start_idx": 2400},
    {"id": "A5", "port": 5005, "start_idx": 3200},
]

def main():
    processes = []
    for drone in DRONES:
        p = multiprocessing.Process(target=run_drone, args=(drone,))
        processes.append(p)
        p.start()
    # Wait for all
    for p in processes:
        p.join()
```

TEST BY:
- Run: python multi_drone_launcher.py
- Should see 5 drone windows (or headless output)
- Check that 5 different frame files are created
```

---

# ═══════════════════════════════════════════════════════════
# TASK 2: MULTI-DRONE DASHBOARD UI
# ═══════════════════════════════════════════════════════════

## COPY THIS TO AGENT 2:

```
PROJECT CONTEXT:
- Fire detection drone swarm project
- Currently have single-drone dashboard (dashboard.py)
- Need to show ALL 5 drones in one interface
- Each drone sends to different UDP port

YOUR TASK:
Create a new file: dashboard_multi.py

REQUIREMENTS:
1. Listen on 5 UDP ports (5001-5005) or read 5 state files
2. Display grid of 5 video feeds (thumbnails)
3. Show all 5 drones on the map
4. Aggregate event log from all drones
5. Fleet status bar at top

UI LAYOUT:
```
┌─────────────────────────────────────────────────────────────┐
│ 🦅 FIRE SWARM COMMAND              [A1 ✓][A2 ✓][A3][A4][A5]│
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐  ┌────────────────────────────────┐│
│ │   🗺️ TACTICAL MAP   │  │  📡 FLEET TELEMETRY           ││
│ │   (all 5 drones)    │  │  Click drone to select        ││
│ └─────────────────────┘  └────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│ 📹 DRONE FEEDS                                              │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │
│ │  A1  │ │  A2  │ │  A3  │ │  A4  │ │  A5  │              │
│ │[img] │ │[img] │ │[img] │ │[img] │ │[img] │              │
│ │ 84%  │ │ 72%  │ │ OFF  │ │ 91%  │ │ 45%  │              │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘              │
├─────────────────────────────────────────────────────────────┤
│ 📜 GLOBAL EVENT LOG                                         │
│ [12:34:56] A2: 🔥 Fire detected at [44.81, 20.46]          │
│ [12:34:45] A5: ⚠️ Low battery (45%)                         │
└─────────────────────────────────────────────────────────────┘
```

REFERENCE THE EXISTING FILE:
- Read dashboard.py to understand current structure
- Reuse the styling and PyDeck map code
- Extend state management for 5 drones

STATE FILE STRUCTURE:
```python
# Read from drone_states.json (or individual files)
{
    "A1": {"gps": [44.81, 20.46], "fire": false, "conf": 0.0, "fps": 10.2},
    "A2": {"gps": [44.82, 20.47], "fire": true, "conf": 0.95, "fps": 9.8},
    "A3": {"gps": [44.80, 20.45], "fire": false, "conf": 0.0, "fps": 0},
    "A4": {"gps": [44.83, 20.48], "fire": false, "conf": 0.12, "fps": 10.1},
    "A5": {"gps": [44.79, 20.44], "fire": false, "conf": 0.0, "fps": 9.5}
}
```

KEY COMPONENTS:
1. Fleet status bar (5 indicators)
2. Map with 5 drone markers (different colors for fire)
3. 5-column grid for video feeds
4. Merged event log
5. Selected drone detail panel

TEST BY:
- Run: streamlit run dashboard_multi.py
- Should see 5 feed placeholders
- Should see 5 markers on map when drones running
```

---

# ═══════════════════════════════════════════════════════════
# TASK 3: FLAME DATASET DOWNLOAD SCRIPT
# ═══════════════════════════════════════════════════════════

## COPY THIS TO AGENT 3:

```
PROJECT CONTEXT:
- Fire detection drone swarm project
- Need FLAME dataset for aerial thermal fire images
- Dataset is on IEEE DataPort (requires free account)
- Alternative: Kaggle mirrors or direct links

YOUR TASK:
Create files for dataset management

REQUIREMENTS:
1. Create download instructions document
2. Create dataset organization script
3. Create dataset verification script

OUTPUT FILES TO CREATE:

1. docs/DATASET_DOWNLOAD_INSTRUCTIONS.md
```markdown
# Dataset Download Instructions

## FLAME Dataset (Priority: Critical)

### Option 1: IEEE DataPort (Official)
1. Create free account at https://ieee-dataport.org
2. Go to: https://ieee-dataport.org/open-access/flame-dataset
3. Download all files (~2.3GB)
4. Extract to: datasets/FLAME/

### Option 2: Kaggle (Mirror)
```bash
pip install kaggle
kaggle datasets download -d phylake1337/fire-dataset
unzip fire-dataset.zip -d datasets/FLAME/
```

### Option 3: Direct Links (if available)
[List any direct download links found]

## Folder Structure After Download
```
datasets/
├── FLAME/
│   ├── RGB/
│   ├── Thermal/
│   └── Labels/
├── DFireDataset/  (already have)
└── Combined/      (will create)
```
```

2. scripts/organize_datasets.py
```python
# Script to organize and merge datasets
# - Copy D-Fire to Combined/
# - Copy FLAME to Combined/
# - Create train/val/test splits
# - Convert labels to YOLO format if needed
```

3. scripts/verify_datasets.py
```python
# Script to verify dataset integrity
# - Count images per class
# - Check label format
# - Report statistics
```

TEST BY:
- Run: python scripts/verify_datasets.py
- Should report image counts and label format
```

---

# ═══════════════════════════════════════════════════════════
# TASK 4: RECORDING & SYNC SYSTEM
# ═══════════════════════════════════════════════════════════

## COPY THIS TO AGENT 4:

```
PROJECT CONTEXT:
- Fire detection drone swarm project
- Need to record all drone footage for future training
- Recordings should be organized by drone/date/patrol
- Telemetry (GPS, detections) saved alongside video

YOUR TASK:
Create recording and sync system

REQUIREMENTS:
1. Recording module for each drone
2. Organized file structure
3. Sync script for base station

OUTPUT FILES TO CREATE:

1. recorder.py - Recording module
```python
"""
Drone Recording Module

Records:
- Thermal frames (JPEG)
- Telemetry (CSV)
- Detections (JSON)

Organized by:
recordings/{drone_id}/{date}/{patrol_id}/
"""

class DroneRecorder:
    def __init__(self, drone_id, base_path="recordings"):
        self.drone_id = drone_id
        self.patrol_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = f"{base_path}/{drone_id}/{date}/{self.patrol_id}"
        os.makedirs(self.path, exist_ok=True)
        
    def save_frame(self, frame, timestamp):
        # Save thermal frame as JPEG
        pass
        
    def log_telemetry(self, gps, altitude, heading, battery):
        # Append to telemetry.csv
        pass
        
    def log_detection(self, detection):
        # Append to detections.json
        pass
        
    def finalize(self):
        # Create metadata.json with patrol summary
        pass
```

2. sync_to_base.py - Sync script
```python
"""
Sync drone recordings to base station

Usage: python sync_to_base.py --drone A1 --dest /mnt/hdd/drones/

Features:
- rsync-like incremental sync
- Verify checksums
- Delete old files on drone after sync
"""
```

3. training_data_extractor.py
```python
"""
Extract labeled training data from recordings

Uses operator decisions to label:
- CONFIRM -> positive examples (fire)
- DISMISS -> negative examples (false positive)
"""
```

FILE STRUCTURE:
```
recordings/
├── A1/
│   └── 2024-11-28/
│       └── 143025/  (patrol started at 14:30:25)
│           ├── frames/
│           │   ├── 0001.jpg
│           │   ├── 0002.jpg
│           │   └── ...
│           ├── telemetry.csv
│           ├── detections.json
│           └── metadata.json
```

TEST BY:
- Import recorder in simulation.py
- Run simulation for 1 minute
- Check recordings/ folder has files
```

---

# ═══════════════════════════════════════════════════════════
# TASK 5: TRAINING PIPELINE SCRIPT
# ═══════════════════════════════════════════════════════════

## COPY THIS TO AGENT 5:

```
PROJECT CONTEXT:
- Fire detection drone swarm project
- Need to train/fine-tune YOLOv8 on fire datasets
- Combine D-Fire + FLAME datasets
- Export model for edge deployment (TFLite)

YOUR TASK:
Create training pipeline scripts

REQUIREMENTS:
1. Dataset preparation script
2. Training script with config
3. Model export script
4. Evaluation script

OUTPUT FILES TO CREATE:

1. scripts/prepare_training_data.py
```python
"""
Prepare combined dataset for YOLO training

Steps:
1. Load D-Fire dataset
2. Load FLAME dataset
3. Convert all to YOLO format
4. Create train/val/test splits (70/20/10)
5. Create data.yaml config file
"""

def create_data_yaml():
    yaml_content = """
    path: datasets/Combined
    train: train/images
    val: val/images
    test: test/images
    
    names:
      0: fire
      1: smoke
    """
    # Write to datasets/Combined/data.yaml
```

2. scripts/train_fire_model.py
```python
"""
Train YOLOv8 on fire detection dataset

Usage: python train_fire_model.py --epochs 100 --batch 16

Saves to: models/yolov8n_fire_v1/
"""

from ultralytics import YOLO

def train():
    model = YOLO('yolov8n.pt')  # Start from pretrained
    
    results = model.train(
        data='datasets/Combined/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        name='fire_detection_v1',
        project='models'
    )
    
    return results
```

3. scripts/export_model.py
```python
"""
Export trained model for edge deployment

Exports:
- TFLite (for Raspberry Pi)
- ONNX (for flexibility)
- TensorRT (if NVIDIA available)
"""

from ultralytics import YOLO

def export_for_edge(model_path):
    model = YOLO(model_path)
    
    # Export to TFLite (INT8 quantized)
    model.export(format='tflite', int8=True)
    
    # Export to ONNX
    model.export(format='onnx')
```

4. scripts/evaluate_model.py
```python
"""
Evaluate model on test set

Reports:
- Precision, Recall, F1
- Confusion matrix
- Per-class accuracy
- Inference speed
"""
```

TEST BY:
- Run: python scripts/prepare_training_data.py
- Should create datasets/Combined/ folder
- Run: python scripts/train_fire_model.py --epochs 1
- Should start training (even 1 epoch is OK for test)
```

---

# ═══════════════════════════════════════════════════════════
# AGENT COORDINATION
# ═══════════════════════════════════════════════════════════

## Dependencies Between Tasks

```
TASK 1 (Multi-Drone Sim) ──┐
                           ├──► Can test together
TASK 2 (Multi-Drone UI)  ──┘

TASK 3 (Dataset Download) ──► TASK 5 (Training Pipeline)

TASK 4 (Recording) ──► Independent, integrate later
```

## After All Tasks Complete

1. Test multi-drone: Run Task 1 + Task 2 together
2. Download datasets: Follow Task 3 instructions
3. Train model: Run Task 5 scripts
4. Integrate recording: Add Task 4 to simulation

## File Checklist

After all agents finish, you should have:

```
Project swarm/
├── multi_drone_launcher.py      (Task 1)
├── drone_instance.py            (Task 1)
├── dashboard_multi.py           (Task 2)
├── recorder.py                  (Task 4)
├── sync_to_base.py              (Task 4)
├── docs/
│   └── DATASET_DOWNLOAD_INSTRUCTIONS.md  (Task 3)
├── scripts/
│   ├── organize_datasets.py     (Task 3)
│   ├── verify_datasets.py       (Task 3)
│   ├── prepare_training_data.py (Task 5)
│   ├── train_fire_model.py      (Task 5)
│   ├── export_model.py          (Task 5)
│   └── evaluate_model.py        (Task 5)
```

---

# 🎯 QUICK COPY-PASTE FOR EACH AGENT

## Agent 1 Prompt:
```
Read PARALLEL_TASKS_FOR_AGENTS.md, find TASK 1, and implement the multi-drone simulation launcher. Create multi_drone_launcher.py and drone_instance.py.
```

## Agent 2 Prompt:
```
Read PARALLEL_TASKS_FOR_AGENTS.md, find TASK 2, and implement the multi-drone dashboard. Create dashboard_multi.py with 5-drone grid view.
```

## Agent 3 Prompt:
```
Read PARALLEL_TASKS_FOR_AGENTS.md, find TASK 3, and create the dataset download documentation and scripts. Create docs/DATASET_DOWNLOAD_INSTRUCTIONS.md and scripts for organizing datasets.
```

## Agent 4 Prompt:
```
Read PARALLEL_TASKS_FOR_AGENTS.md, find TASK 4, and implement the recording system. Create recorder.py and sync_to_base.py.
```

## Agent 5 Prompt:
```
Read PARALLEL_TASKS_FOR_AGENTS.md, find TASK 5, and implement the training pipeline. Create scripts for data preparation, training, export, and evaluation.
```

---

**Created:** November 28, 2024
**For:** Fire Detection Drone Swarm - Phase 0/1A

