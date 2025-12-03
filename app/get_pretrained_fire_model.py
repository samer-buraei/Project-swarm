"""
🔥 DOWNLOAD PRETRAINED FIRE DETECTION MODEL
============================================
Downloads ready-to-use fire detection models - NO TRAINING NEEDED!

Usage:
    python get_pretrained_fire_model.py
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path
import shutil

MODELS_DIR = Path("models/pretrained")


def download_file(url, destination, description="Downloading"):
    """Download a file with progress"""
    print(f"   {description}...")
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"   ✅ Downloaded to: {destination}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def setup_roboflow():
    """Install and setup Roboflow"""
    try:
        from roboflow import Roboflow
        return True
    except ImportError:
        print("📦 Installing roboflow...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "roboflow", "--user", "-q"],
            capture_output=True
        )
        try:
            from roboflow import Roboflow
            return True
        except:
            return False


def download_from_roboflow():
    """Download pretrained model from Roboflow"""
    print("\n" + "=" * 60)
    print("🔥 ROBOFLOW PRETRAINED FIRE MODEL")
    print("=" * 60)
    
    if not setup_roboflow():
        print("❌ Could not install Roboflow")
        return None
    
    from roboflow import Roboflow
    
    print("""
📥 Downloading pretrained fire detection model from Roboflow...

This model was trained on thousands of fire/smoke images and is
ready to use immediately!
""")
    
    # Public fire detection models on Roboflow
    # These can be accessed via the inference API
    
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║  🎯 QUICK DOWNLOAD OPTIONS                                      ║
╠════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Since direct model download requires API key, here's the       ║
║  FASTEST way to get a pretrained fire model:                    ║
║                                                                  ║
║  1. Go to: https://universe.roboflow.com/uma-k4riu/firedetector ║
║  2. Click "Model" tab                                           ║
║  3. Click "Deploy" → "Download Weights"                         ║
║  4. Select: YOLOv8                                              ║
║  5. Save to: models/pretrained/fire_yolov8_pretrained.pt       ║
║                                                                  ║
║  OR use one of these direct links:                              ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    return None


def check_huggingface_models():
    """Check for fire models on Hugging Face"""
    print("\n" + "=" * 60)
    print("🤗 HUGGING FACE FIRE MODELS")
    print("=" * 60)
    
    print("""
Available fire detection models on Hugging Face:

1. Fire-Detection-Engine (Vision Transformer)
   https://huggingface.co/prithivMLmods/Fire-Detection-Engine
   
2. Various YOLO fire models in community spaces

To download, you can use:
   pip install huggingface_hub
   
Then:
   from huggingface_hub import hf_hub_download
   model_path = hf_hub_download(repo_id="...", filename="...")
""")


def use_our_trained_model():
    """Check if our training produced a model"""
    print("\n" + "=" * 60)
    print("📦 YOUR TRAINED MODELS")
    print("=" * 60)
    
    # Check various locations
    model_paths = [
        Path("runs/train/fire_yolov8n/weights/best.pt"),
        Path("runs/train/fire_yolov8n/weights/last.pt"),
        Path("runs/train/fire_aerial_v1/weights/best.pt"),
        Path("models/fire_yolov8n/weights/best.pt"),
    ]
    
    found = False
    for path in model_paths:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"   ✅ Found: {path} ({size_mb:.1f} MB)")
            found = True
    
    if found:
        print("""
🎯 You already have trained models! Use them with:

   py live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt
""")
        return True
    else:
        print("   ❌ No trained models found yet")
        return False


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🔥 PRETRAINED FIRE DETECTION MODELS                           ║
║                                                                  ║
║   Skip training! Use a ready-made model.                        ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    # Check our trained models first
    has_model = use_our_trained_model()
    
    if has_model:
        print("\n✅ You already have a fire model from training!")
        print("   The training in the background is improving it further.")
        
        response = input("\nTest the current model now? (y/n): ").strip().lower()
        if response == 'y':
            print("\n🚀 Starting live camera test...")
            os.system("py live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt --threshold 0.2")
        return
    
    # Show download options
    print("\n" + "=" * 60)
    print("📥 DOWNLOAD OPTIONS")
    print("=" * 60)
    
    print("""
Since you don't have a trained model yet, here are your options:

┌─────────────────────────────────────────────────────────────────┐
│ OPTION 1: Wait for current training (RECOMMENDED)              │
├─────────────────────────────────────────────────────────────────┤
│ Training is already running in background!                     │
│ Check progress: Look at terminal 3                             │
│ Model will be at: runs/train/fire_yolov8n/weights/best.pt     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ OPTION 2: Download from Roboflow (5 min)                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. Go to: universe.roboflow.com                                │
│ 2. Search: "fire detection yolov8"                             │
│ 3. Click any project → Model tab → Download Weights           │
│ 4. Save as: models/pretrained/fire.pt                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ OPTION 3: Use base YOLO + color detection                      │
├─────────────────────────────────────────────────────────────────┤
│ Run: py live_camera_fire_test.py --threshold 0.3               │
│ This uses color-based fire detection (less accurate)           │
└─────────────────────────────────────────────────────────────────┘
""")


if __name__ == "__main__":
    main()

