# 🚀 FIRE DETECTION SYSTEM - QUICK START GUIDE

## Current Status: ✅ PRETRAINED MODEL READY + Training in Progress

---

## 🔥 IMMEDIATE TESTING OPTIONS

### Option 1: Test with 85% mAP Pretrained Model (BEST)
```bash
py fire_detector_unified.py --model models/pretrained/yolov10_fire_smoke.pt --mode thermal
```

### Option 2: Test with Thermal Simulation
```bash
py fire_detector_unified.py --mode thermal
```

**Controls:**
- `Q` - Quit
- `M` - Cycle mode (RGB → Thermal → Dual)
- `T` - Change thermal colormap
- `C` - Adjust confidence threshold
- `S` - Save screenshot

### Option 2: Run Drone Simulation with Thermal
```bash
py simulation.py --thermal --thermal_mode inferno
```

**Controls:**
- `F` - Trigger manual fire alert
- `T` - Toggle thermal mode
- `M` - Cycle thermal colormap
- `Q` - Quit

### Option 3: Demo Thermal Colormaps
```bash
py thermal_simulation.py
```

---

## 📊 CHECK TRAINING STATUS

```bash
py check_training_status.py
```

Or watch the training terminal directly (Epoch 4/20, ~69% complete).

---

## 📥 NEXT STEPS

### 1. Wait for Training to Complete (~15-20 min)
Training is running in background. When done, model will be at:
`runs/train/fire_yolov8n/weights/best.pt`

### 2. Download FLAME Dataset (for thermal training)
```bash
py setup_flame_dataset.py
```
Follow the manual download instructions, then run again to organize.

### 3. Train on FLAME (after download)
```bash
py train_flame_thermal.py
```

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `fire_detector_unified.py` | Main detection system (RGB/Thermal/Dual) |
| `thermal_simulation.py` | Thermal vision simulation module |
| `simulation.py` | Drone simulation with thermal support |
| `setup_flame_dataset.py` | FLAME dataset download helper |
| `train_flame_thermal.py` | Train on thermal data (after FLAME download) |
| `check_training_status.py` | Check D-Fire training progress |

---

## 🎯 THERMAL MODE COLORMAPS

| Mode | Description |
|------|-------------|
| `white_hot` | White = hot (most common thermal) |
| `black_hot` | Black = hot (inverted) |
| `inferno` | Orange/yellow thermal (recommended) |
| `jet` | Rainbow thermal |
| `hot` | Black-red-yellow-white |

---

## ⚠️ KNOWN ISSUES

1. **D-Fire Dataset = RGB ground-level images** - NOT thermal/drone footage
2. **Need FLAME dataset** for proper thermal/aerial training
3. **Small flames (lighters)** may not detect with current model

---

## 📞 NEED HELP?

- Check `docs/SESSION_SUMMARY_20251130.md` for full session details
- Check `CHAT_CONTEXT.md` for discussion history
- Check `LIVE_PROGRESS.md` for current status

