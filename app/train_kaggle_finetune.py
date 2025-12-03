"""
Fine-tune on 221K Kaggle Fire Images
Starting from the best pretrained model (85% mAP)

BACKUP SAVED AT: models/backup_before_kaggle/
TO UNDO: Copy files from backup folder back to models/pretrained/
"""
from ultralytics import YOLO
import os
from datetime import datetime

print("=" * 70)
print("🔥 KAGGLE FINE-TUNING (221K IMAGES)")
print("=" * 70)

# Configuration
BASE_MODEL = "models/pretrained/yolov10_fire_smoke.pt"  # Start from 85% mAP
DATASET = "datasets/Kaggle_Combined/data.yaml"
EPOCHS = 15  # Less epochs since we're fine-tuning, not training from scratch
BATCH = 32   # RTX 4090 can handle this
IMGSZ = 640

# Verify files exist
if not os.path.exists(BASE_MODEL):
    print(f"❌ Base model not found: {BASE_MODEL}")
    exit(1)

if not os.path.exists(DATASET):
    print(f"❌ Dataset config not found: {DATASET}")
    exit(1)

print(f"""
📋 TRAINING CONFIGURATION
─────────────────────────────────────────────────────────────────────
Base Model:    {BASE_MODEL} (85% mAP pretrained)
Dataset:       {DATASET}
Images:        221,940 (177,552 train / 44,388 val)
Epochs:        {EPOCHS}
Batch Size:    {BATCH}
Image Size:    {IMGSZ}
─────────────────────────────────────────────────────────────────────

⏱️ ESTIMATED TIME: 5-8 hours on RTX 4090

🔄 BACKUP LOCATION: models/backup_before_kaggle/
   If you don't like results, restore from backup!

Starting in 5 seconds... (Ctrl+C to cancel)
""")

import time
for i in range(5, 0, -1):
    print(f"  {i}...", end=" ", flush=True)
    time.sleep(1)
print("\n")

# Load model
print("📦 Loading base model...")
model = YOLO(BASE_MODEL)

# Train
print("🚀 Starting fine-tuning...")
start_time = datetime.now()

import torch
device = 0 if torch.cuda.is_available() else 'cpu'
print(f"🖥️ Using device: {'GPU (CUDA)' if device == 0 else 'CPU'}")

results = model.train(
    data=DATASET,
    epochs=EPOCHS,
    imgsz=IMGSZ,
    batch=BATCH if device == 0 else 8,  # Smaller batch on CPU
    name='kaggle_finetune',
    project='runs/train',
    patience=5,           # Early stopping if no improvement
    save=True,
    save_period=5,        # Save checkpoint every 5 epochs
    device=device,        # Auto-detect GPU/CPU
    workers=4,
    cache=False,          # Don't cache on CPU to save RAM
    amp=device == 0,      # Mixed precision only on GPU
    verbose=True,
)

end_time = datetime.now()
duration = end_time - start_time

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE!")
print("=" * 70)
print(f"""
📊 RESULTS
─────────────────────────────────────────────────────────────────────
Duration:      {duration}
Final Model:   runs/train/kaggle_finetune/weights/best.pt

📁 TO USE THE NEW MODEL:
   py fire_detector_unified.py --model runs/train/kaggle_finetune/weights/best.pt

🔄 TO UNDO (restore original):
   Copy-Item "models/backup_before_kaggle/*" -Destination "models/pretrained/" -Force
─────────────────────────────────────────────────────────────────────
""")

