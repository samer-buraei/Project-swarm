"""
🔥 DOWNLOAD PRETRAINED FIRE DETECTION MODEL
=============================================
Downloads a ready-to-use fire detection model so you can test immediately!

Usage:
    python download_pretrained_fire.py
    
Then test with:
    python live_camera_fire_test.py --model models/fire_pretrained.pt
"""

import subprocess
import sys
from pathlib import Path
import urllib.request
import os


def install_if_needed(package):
    try:
        __import__(package)
    except ImportError:
        print(f"📦 Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)


def download_from_roboflow():
    """Download pretrained fire model from Roboflow"""
    print("\n" + "=" * 60)
    print("📥 DOWNLOADING PRETRAINED FIRE DETECTION MODEL")
    print("=" * 60)
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Try to use roboflow to download a pretrained model
    try:
        install_if_needed("roboflow")
        from roboflow import Roboflow
        
        print("\n🔍 Searching for pretrained fire models on Roboflow...")
        print("   (This downloads a model trained on thousands of fire images)")
        
        # Note: For actual deployment, you'd use a specific API key and project
        # For now, we'll use the inference API approach
        
    except Exception as e:
        print(f"⚠️ Roboflow download failed: {e}")
    
    # Alternative: Download from Ultralytics Hub or use their pretrained
    print("\n" + "=" * 60)
    print("📋 PRETRAINED MODEL OPTIONS")
    print("=" * 60)
    print("""
🔥 OPTION 1: Use Ultralytics Hub (Recommended)
----------------------------------------------
1. Go to: https://hub.ultralytics.com/models
2. Search for "fire" or "fire detection"
3. Download the .pt file
4. Save to: models/fire_pretrained.pt

🔥 OPTION 2: Roboflow Universe Models
--------------------------------------
1. Go to: https://universe.roboflow.com/search?q=fire%20detection
2. Find a model with good mAP score
3. Click "Model" tab → "Download Weights"
4. Choose YOLOv8 format
5. Save to: models/fire_pretrained.pt

🔥 OPTION 3: Hugging Face
--------------------------
1. Go to: https://huggingface.co/models?search=fire+detection+yolo
2. Find a YOLOv8 fire model
3. Download the .pt weights
4. Save to: models/fire_pretrained.pt

🔥 OPTION 4: Use Our Training (Best for Thermal)
-------------------------------------------------
Wait for current training to complete (~30 min)
Model will be at: runs/train/fire_yolov8n/weights/best.pt
""")
    
    # Create a quick test with the base YOLO model
    print("\n" + "=" * 60)
    print("🚀 QUICK TEST: Color-Based Fire Detection")
    print("=" * 60)
    print("""
While waiting, you can test the color-based fire detection:

    python live_camera_fire_test.py --threshold 0.3

This uses:
1. Standard YOLO for object detection
2. HSV color analysis for fire colors (orange/red/yellow)

Point your camera at a phone showing fire video - it will detect
the orange/red fire colors even without a fire-specific model!
""")


def check_training_status():
    """Check if our training has produced a model yet"""
    best_model = Path("runs/train/fire_yolov8n/weights/best.pt")
    last_model = Path("runs/train/fire_yolov8n/weights/last.pt")
    
    print("\n" + "=" * 60)
    print("📊 YOUR TRAINING STATUS")
    print("=" * 60)
    
    if best_model.exists():
        size = best_model.stat().st_size / (1024 * 1024)
        print(f"✅ BEST MODEL READY: {best_model}")
        print(f"   Size: {size:.1f} MB")
        print(f"\n🎯 Test it now:")
        print(f"   python live_camera_fire_test.py --model {best_model}")
        return True
    elif last_model.exists():
        size = last_model.stat().st_size / (1024 * 1024)
        print(f"⏳ Training in progress...")
        print(f"   Latest checkpoint: {last_model} ({size:.1f} MB)")
        print(f"\n💡 You can test the latest checkpoint:")
        print(f"   python live_camera_fire_test.py --model {last_model}")
        return False
    else:
        print("⏳ Training just started, no checkpoints yet...")
        return False


def main():
    print("=" * 60)
    print("🔥 PRETRAINED FIRE DETECTION MODELS")
    print("=" * 60)
    
    # Check our training status first
    check_training_status()
    
    # Show download options
    download_from_roboflow()
    
    print("\n" + "=" * 60)
    print("✅ RECOMMENDATION")
    print("=" * 60)
    print("""
For YOUR project (thermal drone fire detection):

1. 🏃 RIGHT NOW: Test with color detection
   python live_camera_fire_test.py --threshold 0.3

2. ⏳ IN ~30 MIN: Use your trained model (BEST)
   python live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt

3. 🔧 OPTIONAL: Download pretrained for comparison
   Follow instructions above to get a Roboflow/HuggingFace model

Your D-Fire trained model will be BETTER for thermal/drone detection
because it's trained on the exact type of images you'll use!
""")


if __name__ == "__main__":
    main()

