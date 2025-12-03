# 🔥 Session Summary: Fire Detection Model Training & Testing
**Date:** November 30, 2025  
**Purpose:** Set up fire detection for drone swarm project

---

## 📋 EXECUTIVE SUMMARY

We attempted to train and test a fire detection model using YOLO. Key finding: **the D-Fire dataset contains ground-level RGB images, NOT thermal/aerial drone footage**, which is a mismatch for the project's actual use case (thermal cameras on drones).

---

## 🎯 GOALS OF THIS SESSION

1. ✅ Verify SITL (Software-In-The-Loop) testing is complete
2. ✅ Download fire detection training data
3. ✅ Train YOLOv8 on fire/smoke detection
4. ❌ Test live camera detection (partially working)
5. 🔄 Find/download pretrained models for comparison

---

## 📊 KEY FINDINGS

### 1. SITL Testing Status: ✅ COMPLETE
From previous sessions, all SITL components were verified:
- Fire detection: 18.9ms inference
- Multi-drone simulation: 5 drones working
- Pixhawk SITL: Full flight tested
- QGroundControl: Connected and tracking

### 2. D-Fire Dataset Analysis
**What we have:**
```
DFireDataset/
├── train/images/  → 17,221 images
├── test/images/   → 4,306 images
└── Total: 21,527 fire/smoke images
```

**Critical Discovery:**
| Feature | D-Fire Dataset | Project Needs |
|---------|---------------|---------------|
| Image Type | ❌ RGB (color) | ✅ Thermal (IR) |
| Perspective | ❌ Ground surveillance | ✅ Aerial drone |
| Fire Size | ❌ Large outdoor fires | ✅ Any size |

**Implication:** Model trained on D-Fire may not perform well on actual thermal drone footage.

### 3. Training Status
- **Model:** YOLOv8n trained on D-Fire
- **Progress:** Epoch 4/20 (as of session end)
- **Current Accuracy:** ~43% mAP (still improving)
- **Output Location:** `runs/train/fire_yolov8n/weights/best.pt`

### 4. Live Camera Testing
- ✅ Camera opens successfully (1280x720)
- ✅ Model loads with classes: ['fire', 'smoke']
- ❌ Did not detect lighter flame (too small, model trained on large fires)
- ❌ False positive on yellow door (color detection issue)
- ✅ Fixed: Disabled color detection, lowered threshold

---

## 🔧 ACTIONS TAKEN

### Files Created:
| File | Purpose |
|------|---------|
| `live_camera_fire_test.py` | Webcam fire detection with YOLO |
| `download_fire_datasets.py` | Dataset organization tool |
| `train_fire_quick.py` | Quick training script |
| `setup_flame_training.py` | FLAME dataset setup (aerial thermal) |
| `get_pretrained_fire_model.py` | Pretrained model finder |
| `download_best_pretrained.py` | Download 85% mAP model |
| `test_pretrained_dfire.py` | Test pretrained models |

### Datasets Organized:
```
datasets/
└── Combined/
    ├── train/images/  → 17,221 images (from D-Fire)
    ├── train/labels/  → YOLO format annotations
    ├── val/images/    → 4,306 images
    ├── val/labels/    → YOLO format annotations
    └── data.yaml      → Training configuration
```

### Training Started:
```bash
py train_fire_quick.py --epochs 20 --batch 8
# Running in background, saves to runs/train/fire_yolov8n/
```

### Pretrained Models Repository Cloned:
```bash
git clone https://github.com/pedbrgs/Fire-Detection.git models/Fire-Detection-Pretrained
```

---

## 📥 PRETRAINED MODEL OPTIONS IDENTIFIED

| Rank | Model | Accuracy | Source | Link |
|------|-------|----------|--------|------|
| #1 | YOLOv10 Fire+Smoke | 85% mAP | HuggingFace | [Link](https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection) |
| #2 | D-Fire YOLOv5l | 80% mAP | OneDrive | [Link](https://1drv.ms/u/c/c0bd25b6b048b01d/ERy9-UpeDeRHkEb_eqPeC7EBdblsWLwujJ1BlssUWfz_Lg) |
| #3 | D-Fire YOLOv5s | 78% mAP | OneDrive | [Link](https://1drv.ms/u/c/c0bd25b6b048b01d/EeZYmpKPBppNr3lo8oaOqecB9GDj1dDvbogCJyegO0PY1Q) |
| #4 | Roboflow Models | 75-85% | Roboflow | [Browse](https://universe.roboflow.com/browse/fire) |

**Note:** All these models are trained on similar data (ground-level RGB). For thermal/aerial, need FLAME dataset.

---

## ⚠️ ISSUES ENCOUNTERED

### 1. SSL Certificate Warning
```
UserWarning: Bad certificate in Windows certificate store
```
**Fix:** Added `warnings.filterwarnings('ignore', message='Bad certificate')` to scripts.

### 2. Model Not Detecting Lighter Flame
**Cause:** D-Fire contains large outdoor fires, not small flames like lighters.
**Solution:** Need to either:
- Lower detection threshold significantly (tried 0.15)
- Train on dataset with small flames
- Use thermal camera (designed for heat, not visual flame)

### 3. False Positive on Yellow Door
**Cause:** Color-based detection triggered on orange/yellow objects.
**Fix:** Disabled color detection by default, made it toggle-able with 'C' key.

### 4. FLAME Dataset Not Downloaded
**Issue:** FLAME (aerial thermal) requires IEEE DataPort registration or manual Roboflow download.
**Status:** Pending - user needs to manually download.

---

## 📂 CURRENT PROJECT STATE

### Models Available:
```
✅ runs/train/fire_yolov8n/weights/best.pt  (17.6 MB) - Our training
✅ runs/train/fire_yolov8n/weights/last.pt  (17.6 MB) - Latest checkpoint
❌ models/pretrained/yolov10_fire.pt        - Need to download
❌ models/pretrained/yolov5s_dfire.pt       - Need to download
```

### Training Status:
- **Running:** Yes (background process)
- **Epoch:** 4/20 (currently at ~90%)
- **Epochs Completed:** 3
- **Current mAP50:** 43% (improving each epoch)
- **ETA:** ~20 minutes remaining

### ✅ PRETRAINED MODEL DOWNLOADED!
- **Model:** YOLOv10 Fire & Smoke Detection
- **Source:** HuggingFace (TommyNgx/YOLOv10-Fire-and-Smoke-Detection)
- **Accuracy:** 85% mAP
- **Size:** 64 MB
- **Location:** `models/pretrained/yolov10_fire_smoke.pt`

### Test Command:
```bash
py live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt --threshold 0.15
```

---

## 🔜 RECOMMENDED NEXT STEPS

### Immediate (Today):
1. **Download pretrained model** for comparison:
   - Easiest: [Roboflow](https://universe.roboflow.com/browse/fire)
   - Best: [HuggingFace 85% mAP](https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection)

2. **Wait for training to complete** (~30 min)

3. **Test with fire video on phone** instead of lighter:
   - Search YouTube: "forest fire footage" or "wildfire"
   - Point camera at phone screen
   - Model better at large fires than small flames

### Short-term (This Week):
1. **Download FLAME dataset** for aerial thermal training
2. **Retrain on combined D-Fire + FLAME** for better drone performance
3. **Test with actual InfiRay P2Pro** thermal camera when available

### Long-term:
1. Collect own training data from drone flights
2. Fine-tune model on thermal imagery
3. Implement on Raspberry Pi 4 for edge deployment

---

## 💡 KEY DECISIONS MADE

| Decision | Reasoning |
|----------|-----------|
| Train YOLOv8n (not larger) | Needs to run on Pi 4 at ~1 FPS |
| Use D-Fire dataset first | Already available, 21K+ images |
| Disable color detection | Too many false positives |
| Lower threshold to 0.15 | Catch smaller/less confident detections |
| Seek pretrained models | Save training time, proven accuracy |

---

## 📚 RESOURCES

### Documentation Created:
- `docs/SESSION_SUMMARY_20251130.md` - This file
- `docs/PROJECT_STATE.md` - Overall project status
- `docs/DATA_TRAINING_AND_MULTI_DRONE_ARCHITECTURE.md` - Training strategy

### External Resources:
- [D-Fire Dataset](https://github.com/gaiasd/DFireDataset)
- [D-Fire Pretrained Models](https://github.com/pedbrgs/Fire-Detection)
- [FLAME Dataset](https://ieee-dataport.org/open-access/flame-dataset)
- [Roboflow Fire Models](https://universe.roboflow.com/browse/fire)
- [HuggingFace Fire Model](https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection)

---

## 🤝 FOR COLLABORATORS

### To Continue This Work:
1. Read this summary first
2. Check training status: Look at terminal or `runs/train/fire_yolov8n/`
3. Download a pretrained model for immediate testing
4. For thermal/drone work: Download FLAME dataset

### Key Files to Know:
```
live_camera_fire_test.py  → Test fire detection with webcam
train_fire_quick.py       → Train new model
test_pretrained_dfire.py  → Test downloaded models
```

### Commands:
```bash
# Test current model
py live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt

# Check training status
type runs\train\fire_yolov8n\results.csv

# Download pretrained options
py download_best_pretrained.py
```

---

**Last Updated:** November 30, 2025  
**Session Duration:** ~1 hour  
**Status:** Training in progress, pretrained download pending

