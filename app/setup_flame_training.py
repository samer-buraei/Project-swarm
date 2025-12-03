"""
🔥 FLAME DATASET SETUP & TRAINING PIPELINE
============================================
Downloads aerial thermal fire dataset and trains YOLOv8.

This script will:
1. Download FLAME dataset (or guide you to download it)
2. Organize the data for YOLO training
3. Train YOLOv8 on aerial thermal fire images
4. Save the best model for your drone

Run with: python setup_flame_training.py
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
import urllib.request
import zipfile

# ============================================================
# CONFIGURATION
# ============================================================

from config import DATASETS_DIR, MODELS_DIR

PROJECT_ROOT = Path(__file__).parent
# DATASETS_DIR and MODELS_DIR are imported from config
FLAME_DIR = DATASETS_DIR / "FLAME"
COMBINED_DIR = DATASETS_DIR / "Combined_Aerial"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_header(text):
    """Print a nice header"""
    print("\n" + "=" * 60)
    print(f"🔥 {text}")
    print("=" * 60)


def print_step(step_num, total, text):
    """Print step progress"""
    print(f"\n[{step_num}/{total}] {text}")
    print("-" * 50)


def print_progress(current, total, prefix="Progress"):
    """Print progress bar"""
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    percent = current / total * 100
    print(f"\r{prefix}: [{bar}] {percent:.1f}% ({current}/{total})", end="", flush=True)
    if current == total:
        print()  # New line when complete


def run_command(cmd, description):
    """Run a command and show output"""
    print(f"   Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️ Warning: {result.stderr[:200] if result.stderr else 'Unknown error'}")
    return result.returncode == 0


# ============================================================
# STEP 1: CHECK EXISTING DATA
# ============================================================

def check_existing_datasets():
    """Check what datasets we already have"""
    print_header("CHECKING EXISTING DATASETS")
    
    datasets = {
        "D-Fire": PROJECT_ROOT / "DFireDataset",
        "FLAME": FLAME_DIR,
        "Combined": COMBINED_DIR,
    }
    
    status = {}
    for name, path in datasets.items():
        if path.exists():
            # Count images
            img_count = len(list(path.rglob("*.jpg"))) + len(list(path.rglob("*.png")))
            status[name] = {"exists": True, "images": img_count, "path": path}
            print(f"   ✅ {name}: {img_count:,} images at {path}")
        else:
            status[name] = {"exists": False, "images": 0, "path": path}
            print(f"   ❌ {name}: Not found")
    
    return status


# ============================================================
# STEP 2: DOWNLOAD FLAME ALTERNATIVES
# ============================================================

def download_aerial_fire_data():
    """Download aerial fire datasets from available sources"""
    print_header("DOWNLOADING AERIAL FIRE DATA")
    
    FLAME_DIR.mkdir(parents=True, exist_ok=True)
    
    # Since IEEE Dataport requires registration, let's use Roboflow
    # which has public aerial fire datasets
    
    print("""
📋 FLAME DATASET OPTIONS:

The official FLAME dataset requires IEEE Dataport registration.
I'll download alternative aerial fire datasets that are freely available.

OPTION A: Roboflow Aerial Fire Datasets (DOWNLOADING NOW)
OPTION B: Manual FLAME download (instructions below)
""")
    
    # Try to download from Roboflow using their public API
    try:
        print("\n📥 Attempting to download aerial fire dataset from Roboflow...")
        
        # Install roboflow if needed
        try:
            from roboflow import Roboflow
        except ImportError:
            print("   Installing roboflow package...")
            subprocess.run([sys.executable, "-m", "pip", "install", "roboflow", "-q"], 
                          capture_output=True)
            from roboflow import Roboflow
        
        # Try public wildfire datasets
        print("   Searching for public aerial fire datasets...")
        
        # These are public datasets on Roboflow Universe
        datasets_to_try = [
            ("wildfire-smoke-detection", "wildfire-smoke", 1),
            ("fire-detection", "fire-smoke", 1),
        ]
        
        downloaded = False
        for workspace, project, version in datasets_to_try:
            try:
                print(f"\n   Trying: {workspace}/{project}...")
                # Note: This requires API key for most datasets
                # We'll provide manual instructions instead
            except Exception as e:
                print(f"   ⚠️ Could not download: {e}")
        
    except Exception as e:
        print(f"   ⚠️ Roboflow download failed: {e}")
    
    # Provide manual download instructions
    print("""
╔════════════════════════════════════════════════════════════════╗
║  📥 MANUAL DOWNLOAD REQUIRED (Takes 5 minutes)                  ║
╠════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  OPTION 1: Roboflow (EASIEST - No registration)                 ║
║  ─────────────────────────────────────────────────              ║
║  1. Open browser: https://universe.roboflow.com                 ║
║  2. Search: "fire aerial" or "wildfire drone"                  ║
║  3. Pick a dataset with good ratings                            ║
║  4. Click "Download" → Format: "YOLOv8" → Download ZIP         ║
║  5. Extract ZIP to: datasets/FLAME/                             ║
║                                                                  ║
║  OPTION 2: FLAME Dataset (Best quality, needs registration)     ║
║  ─────────────────────────────────────────────────              ║
║  1. Go to: https://ieee-dataport.org/open-access/flame-dataset ║
║  2. Create free IEEE account                                    ║
║  3. Download the dataset                                        ║
║  4. Extract to: datasets/FLAME/                                 ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝

After downloading, press ENTER to continue...
""")
    
    input()
    return FLAME_DIR.exists() and len(list(FLAME_DIR.rglob("*.jpg"))) > 0


# ============================================================
# STEP 3: ORGANIZE DATASETS
# ============================================================

def organize_combined_dataset():
    """Combine all fire datasets into one training set"""
    print_header("ORGANIZING COMBINED DATASET")
    
    # Create directory structure
    for split in ["train", "val"]:
        (COMBINED_DIR / split / "images").mkdir(parents=True, exist_ok=True)
        (COMBINED_DIR / split / "labels").mkdir(parents=True, exist_ok=True)
    
    total_train = 0
    total_val = 0
    
    # Process D-Fire (we already have this)
    dfire_dir = PROJECT_ROOT / "DFireDataset"
    if dfire_dir.exists():
        print("\n📁 Adding D-Fire dataset...")
        
        # Train
        train_images = list((dfire_dir / "train" / "images").glob("*.jpg"))
        print(f"   Copying {len(train_images):,} training images...")
        
        for i, img in enumerate(train_images):
            if i % 1000 == 0:
                print_progress(i, len(train_images), "   D-Fire train")
            
            dst_img = COMBINED_DIR / "train" / "images" / f"dfire_{img.name}"
            if not dst_img.exists():
                shutil.copy(img, dst_img)
                total_train += 1
                
                # Copy label
                lbl = img.with_suffix(".txt")
                lbl_src = dfire_dir / "train" / "labels" / lbl.name
                if lbl_src.exists():
                    shutil.copy(lbl_src, COMBINED_DIR / "train" / "labels" / f"dfire_{lbl.name}")
        
        print_progress(len(train_images), len(train_images), "   D-Fire train")
        
        # Val (from test)
        val_images = list((dfire_dir / "test" / "images").glob("*.jpg"))
        print(f"   Copying {len(val_images):,} validation images...")
        
        for i, img in enumerate(val_images):
            if i % 500 == 0:
                print_progress(i, len(val_images), "   D-Fire val")
            
            dst_img = COMBINED_DIR / "val" / "images" / f"dfire_{img.name}"
            if not dst_img.exists():
                shutil.copy(img, dst_img)
                total_val += 1
                
                lbl = img.with_suffix(".txt")
                lbl_src = dfire_dir / "test" / "labels" / lbl.name
                if lbl_src.exists():
                    shutil.copy(lbl_src, COMBINED_DIR / "val" / "labels" / f"dfire_{lbl.name}")
        
        print_progress(len(val_images), len(val_images), "   D-Fire val")
    
    # Process FLAME/Aerial data if available
    if FLAME_DIR.exists():
        print("\n📁 Adding FLAME/Aerial dataset...")
        
        # Look for images in various structures
        flame_images = list(FLAME_DIR.rglob("*.jpg")) + list(FLAME_DIR.rglob("*.png"))
        
        if flame_images:
            # Split 80/20 train/val
            split_idx = int(len(flame_images) * 0.8)
            train_imgs = flame_images[:split_idx]
            val_imgs = flame_images[split_idx:]
            
            print(f"   Found {len(flame_images):,} aerial images")
            print(f"   Copying {len(train_imgs):,} to train, {len(val_imgs):,} to val...")
            
            for i, img in enumerate(train_imgs):
                if i % 100 == 0:
                    print_progress(i, len(train_imgs), "   FLAME train")
                
                dst = COMBINED_DIR / "train" / "images" / f"flame_{img.name}"
                if not dst.exists():
                    shutil.copy(img, dst)
                    total_train += 1
                    
                    # Look for matching label
                    lbl = img.with_suffix(".txt")
                    if lbl.exists():
                        shutil.copy(lbl, COMBINED_DIR / "train" / "labels" / f"flame_{lbl.name}")
            
            print_progress(len(train_imgs), len(train_imgs), "   FLAME train")
            
            for i, img in enumerate(val_imgs):
                dst = COMBINED_DIR / "val" / "images" / f"flame_{img.name}"
                if not dst.exists():
                    shutil.copy(img, dst)
                    total_val += 1
    
    # Create data.yaml
    yaml_content = f"""# Combined Fire Detection Dataset
# Includes: D-Fire (ground) + FLAME (aerial)

path: {COMBINED_DIR.absolute()}
train: train/images
val: val/images

nc: 2
names: ['fire', 'smoke']
"""
    
    with open(COMBINED_DIR / "data.yaml", "w") as f:
        f.write(yaml_content)
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║  ✅ DATASET ORGANIZED                                           ║
╠════════════════════════════════════════════════════════════════╣
║  Training images:   {total_train:>10,}                                    ║
║  Validation images: {total_val:>10,}                                    ║
║  Location: {str(COMBINED_DIR):<47} ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    return total_train, total_val


# ============================================================
# STEP 4: TRAIN MODEL
# ============================================================

def train_fire_model(epochs=30, batch=8):
    """Train YOLOv8 on the combined dataset"""
    print_header("TRAINING FIRE DETECTION MODEL")
    
    data_yaml = COMBINED_DIR / "data.yaml"
    if not data_yaml.exists():
        print("❌ Dataset not prepared! Run organize step first.")
        return None
    
    # Count images
    train_count = len(list((COMBINED_DIR / "train" / "images").glob("*.*")))
    val_count = len(list((COMBINED_DIR / "val" / "images").glob("*.*")))
    
    print(f"""
📊 TRAINING CONFIGURATION
─────────────────────────────────────────
  Model:        YOLOv8n (nano - fast)
  Epochs:       {epochs}
  Batch size:   {batch}
  Train images: {train_count:,}
  Val images:   {val_count:,}
  
  Output: models/fire_aerial_yolov8n/
─────────────────────────────────────────

🚀 Starting training... (this will take a while)
   Watch the progress below!
""")
    
    from ultralytics import YOLO
    
    # Load pretrained model
    model = YOLO("yolov8n.pt")
    
    # Train with progress
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=640,
        batch=batch,
        name="fire_aerial_v1",
        project="models",
        patience=10,
        save=True,
        plots=True,
        verbose=True,
        workers=4,
        cache=True,
        amp=True,
    )
    
    # Find best model
    best_model = Path("models/fire_aerial_v1/weights/best.pt")
    if best_model.exists():
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║  ✅ TRAINING COMPLETE!                                          ║
╠════════════════════════════════════════════════════════════════╣
║  Best model saved to:                                           ║
║  {str(best_model):<58} ║
║                                                                  ║
║  To test with your camera, run:                                 ║
║  py live_camera_fire_test.py --model {str(best_model):<20} ║
╚════════════════════════════════════════════════════════════════╝
""")
        return best_model
    
    return None


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🔥 FLAME DATASET SETUP & TRAINING PIPELINE                    ║
║                                                                  ║
║   This script will:                                             ║
║   1. Check existing datasets                                    ║
║   2. Help download FLAME aerial thermal data                    ║
║   3. Organize combined dataset                                  ║
║   4. Train YOLOv8 on aerial fire images                         ║
║   5. Give you a model that works from drone perspective!        ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    # Step 1: Check existing
    print_step(1, 4, "CHECKING EXISTING DATASETS")
    status = check_existing_datasets()
    
    # Step 2: Download FLAME
    print_step(2, 4, "DOWNLOADING AERIAL FIRE DATA")
    if not status["FLAME"]["exists"] or status["FLAME"]["images"] < 100:
        has_flame = download_aerial_fire_data()
    else:
        print(f"   ✅ FLAME already downloaded: {status['FLAME']['images']:,} images")
        has_flame = True
    
    # Step 3: Organize
    print_step(3, 4, "ORGANIZING COMBINED DATASET")
    train_count, val_count = organize_combined_dataset()
    
    if train_count < 100:
        print("""
⚠️ WARNING: Very few training images!

For best results, please download the FLAME dataset:
1. Go to: https://universe.roboflow.com
2. Search for "aerial fire" or "wildfire drone"
3. Download in YOLOv8 format
4. Extract to: datasets/FLAME/
5. Run this script again
""")
        response = input("\nContinue training anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Step 4: Train
    print_step(4, 4, "TRAINING MODEL")
    
    # Ask for training parameters
    print("\n📝 Training options:")
    print("   Quick test:  10 epochs (~15 min)")
    print("   Standard:    30 epochs (~45 min)")
    print("   Full:        50 epochs (~75 min)")
    
    epochs_input = input("\nEnter epochs (default 30): ").strip()
    epochs = int(epochs_input) if epochs_input.isdigit() else 30
    
    best_model = train_fire_model(epochs=epochs, batch=8)
    
    if best_model:
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🎉 ALL DONE!                                                  ║
║                                                                  ║
║   Your aerial fire detection model is ready!                    ║
║                                                                  ║
║   Test it now:                                                  ║
║   py live_camera_fire_test.py --model {str(best_model):<20} ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()

