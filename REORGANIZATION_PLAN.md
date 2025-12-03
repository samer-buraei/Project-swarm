# 🔄 PROJECT REORGANIZATION PLAN

## Current Problem
- Project is **141+ GB** (mostly training data)
- Cannot upload to GitHub (100 MB file limit)
- Too large for LLMs to understand
- Mixing flight code with training data

## Solution: Split Into Two Folders

### 📁 fire-drone-swarm/ (GitHub Repo - ~5 MB)
**Purpose:** Clean, uploadable codebase for drone swarm control

```
fire-drone-swarm/
├── app/                          # Core application code
│   ├── simulation.py             # Drone simulation
│   ├── dashboard.py              # Main dashboard
│   ├── dashboard_*.py            # Other dashboards
│   ├── drone_control.py          # Flight control
│   ├── fire_detector_unified.py  # Fire detection
│   ├── thermal_simulation.py     # Thermal camera sim
│   └── ... (other core scripts)
│
├── config/                       # Configuration files
│   └── (move from app/config/)
│
├── scripts/                      # Utility scripts
│   ├── evaluate_model.py
│   ├── export_model.py
│   └── ... (training utilities)
│
├── docs/                         # Documentation
│   ├── PROJECT_STATE.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── ... (all .md files)
│
├── P2Pro-Viewer/                 # Thermal camera driver
│
├── models/                       # Small base models ONLY
│   └── yolov8n.pt               # 6 MB base model
│
├── .gitignore
├── README.md
├── requirements.txt
├── run_demo.bat
└── QUICKSTART.md
```

### 📁 fire-drone-data/ (Local Only - 141+ GB)
**Purpose:** Training data, large models, datasets (NOT on GitHub)

```
fire-drone-data/
├── datasets/
│   ├── Combined/                 # D-Fire organized
│   ├── Kaggle_Combined/          # Kaggle 221K images
│   └── FLAME/                    # Thermal aerial (when downloaded)
│
├── DFireDataset/                 # Original D-Fire
│
├── models/
│   ├── pretrained/               # Downloaded pretrained models
│   │   ├── yolov10_fire_smoke.pt (61 MB)
│   │   ├── yolov5s_dfire.pt (14 MB)
│   │   └── ...
│   └── backup_before_kaggle/     # Safety backups
│
├── runs/                         # Training outputs
│   └── train/
│       ├── fire_yolov8n/         # D-Fire trained
│       └── kaggle_finetune/      # Kaggle fine-tuned
│
└── weights/                      # Other weight files
```

---

## Migration Steps

### Step 1: Create New Folder Structure
```powershell
# Create fire-drone-data folder (same level as project)
New-Item -ItemType Directory -Path "<YOUR_PATH>/fire-drone-data" -Force

# Move large data
Move-Item "data\datasets" "<YOUR_PATH>/fire-drone-data/datasets"
Move-Item "data\DFireDataset" "<YOUR_PATH>/fire-drone-data/DFireDataset"
Move-Item "data\models" "<YOUR_PATH>/fire-drone-data/models"
Move-Item "data\runs" "<YOUR_PATH>/fire-drone-data/runs"
Move-Item "data\FLAME_Dataset" "<YOUR_PATH>/fire-drone-data/FLAME_Dataset"
```

### Step 2: Rename Main Project
```powershell
# Rename to clean name
Rename-Item "<YOUR_PATH>/Project-swarm" "<YOUR_PATH>/fire-drone-swarm"
```

### Step 3: Create Symlink (Optional)
```powershell
# Link data folder into project (for scripts that expect data/)
# Run as Administrator
New-Item -ItemType Junction -Path "<YOUR_PATH>/fire-drone-swarm/data" -Target "<YOUR_PATH>/fire-drone-data"
```

### Step 4: Clean Up Project
```powershell
# Remove files that shouldn't be in Git
Remove-Item ".venv" -Recurse -Force
Remove-Item "*.jpg" -Force
Remove-Item "*.png" -Force
Remove-Item "*.csv" -Force
Remove-Item "*.log" -Force
Remove-Item "*.cache" -Force -Recurse
```

---

## .gitignore Content

```gitignore
# Data folder (local only)
data/
fire-drone-data/

# Large files
*.pt
*.pth
*.onnx
*.tflite
!models/yolov8n.pt

# Python
__pycache__/
*.pyc
.venv/
venv/
.env

# Generated files
*.jpg
*.png
*.csv
*.log
*.cache
detection_log.csv
dashboard.log

# OS
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/
*.swp
```

---

## Updated paths in code

Scripts will need to reference data from the linked folder:
```python
# Before
model_path = "data/models/pretrained/yolov10_fire_smoke.pt"

# After (with symlink, same path works)
model_path = "data/models/pretrained/yolov10_fire_smoke.pt"

# OR (absolute path - replace with your path)
model_path = "<YOUR_PATH>/fire-drone-data/models/pretrained/yolov10_fire_smoke.pt"
```

---

## Size Comparison

| Before | After (GitHub) |
|--------|----------------|
| 141+ GB | ~5 MB |
| Can't upload | ✅ Can upload |
| Hard for LLM | ✅ Easy for LLM |
| Mixed concerns | ✅ Clean separation |

---

## Benefits

1. **GitHub-ready** - Upload entire project easily
2. **LLM-friendly** - Small codebase is easier to understand
3. **Clean separation** - Code vs data
4. **Backup flexibility** - Back up code and data separately
5. **Collaboration** - Others can clone without 141 GB download
6. **CI/CD ready** - Can run tests without massive data

---

## Next Steps After Reorganization

1. Initialize Git in fire-drone-swarm
2. Create GitHub repo
3. Push clean codebase
4. Add collaborators
5. Keep fire-drone-data backed up locally (or on external drive)


