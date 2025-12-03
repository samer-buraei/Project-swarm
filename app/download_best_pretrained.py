"""
🔥 DOWNLOAD BEST PRETRAINED FIRE MODEL (85% mAP!)
==================================================
Downloads the YOLOv10 Fire & Smoke model from HuggingFace.

This model has 85% mAP - better than D-Fire models!
"""

import warnings
warnings.filterwarnings('ignore')

import os
import sys
from pathlib import Path

MODELS_DIR = Path("models/pretrained")
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def download_from_huggingface():
    """Download YOLOv10 Fire model from HuggingFace"""
    print("=" * 60)
    print("🔥 DOWNLOADING YOLOV10 FIRE MODEL (85% mAP)")
    print("=" * 60)
    
    try:
        from huggingface_hub import hf_hub_download, login
        
        print("\n📥 Attempting to download from HuggingFace...")
        print("   Model: TommyNgx/YOLOv10-Fire-and-Smoke-Detection")
        print("   Accuracy: 85% mAP (best available!)")
        
        # Try to download
        try:
            model_path = hf_hub_download(
                repo_id="TommyNgx/YOLOv10-Fire-and-Smoke-Detection",
                filename="best.pt",
                local_dir=str(MODELS_DIR),
            )
            print(f"\n✅ Downloaded to: {model_path}")
            return model_path
            
        except Exception as e:
            if "401" in str(e) or "access" in str(e).lower() or "agree" in str(e).lower():
                print(f"""
⚠️ This model requires accepting terms on HuggingFace.

MANUAL DOWNLOAD (2 minutes):
────────────────────────────────────────────────────────
1. Go to: https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection

2. Click "Agree and access repository"
   (You may need to create a free HuggingFace account)

3. Click "Files and versions" tab

4. Download "best.pt" 

5. Save to: {MODELS_DIR}/yolov10_fire.pt
────────────────────────────────────────────────────────
""")
            else:
                print(f"   Error: {e}")
            return None
            
    except ImportError:
        print("❌ huggingface_hub not installed")
        return None


def show_roboflow_options():
    """Show Roboflow model options"""
    print("\n" + "=" * 60)
    print("🌐 ROBOFLOW FIRE MODELS (No registration needed!)")
    print("=" * 60)
    
    print("""
BEST ROBOFLOW FIRE MODELS:
────────────────────────────────────────────────────────

1. Fire Detection (YOLO format)
   https://universe.roboflow.com/roboflow-universe-projects/fire-detection-lmxz0
   → Download → YOLOv8 → Get weights

2. Wildfire Smoke Detection  
   https://universe.roboflow.com/brad-dwyer/wildfire-smoke
   → High accuracy for outdoor fires
   
3. Fire and Smoke Detection
   https://universe.roboflow.com/fire-detection/fire-and-smoke-apcdi
   → Combined fire + smoke detection

HOW TO DOWNLOAD:
────────────────────────────────────────────────────────
1. Click any link above
2. Click "Model" tab
3. Click "Deploy" → "Download Weights"  
4. Select: YOLOv8
5. Save to: models/pretrained/
────────────────────────────────────────────────────────
""")


def check_existing_models():
    """Check what models we have"""
    print("\n" + "=" * 60)
    print("📦 YOUR CURRENT MODELS")
    print("=" * 60)
    
    models = []
    
    # Check pretrained folder
    if MODELS_DIR.exists():
        for f in MODELS_DIR.glob("*.pt"):
            size = f.stat().st_size / (1024 * 1024)
            models.append((f, size, "pretrained"))
            print(f"   ✅ {f.name} ({size:.1f} MB) - PRETRAINED")
    
    # Check training outputs
    train_dirs = [
        Path("runs/train/fire_yolov8n/weights"),
        Path("runs/train/fire_aerial_v1/weights"),
        Path("models/fire_yolov8n/weights"),
    ]
    
    for d in train_dirs:
        if d.exists():
            for f in d.glob("*.pt"):
                size = f.stat().st_size / (1024 * 1024)
                models.append((f, size, "trained"))
                print(f"   ✅ {f} ({size:.1f} MB) - YOUR TRAINING")
    
    if not models:
        print("   ❌ No models found")
    
    return models


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🔥 BEST PRETRAINED FIRE DETECTION MODELS                      ║
║                                                                  ║
║   Finding the highest accuracy models for you!                  ║
║                                                                  ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    # Check existing
    models = check_existing_models()
    
    # Try HuggingFace
    hf_model = download_from_huggingface()
    
    # Show Roboflow options
    show_roboflow_options()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY - BEST OPTIONS")
    print("=" * 60)
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│ RANK │ MODEL                    │ mAP   │ SOURCE                │
├─────────────────────────────────────────────────────────────────┤
│  1   │ YOLOv10 Fire+Smoke       │ 85%   │ HuggingFace (manual)  │
│  2   │ D-Fire YOLOv5l           │ 80%   │ OneDrive (manual)     │
│  3   │ Roboflow Fire Models     │ 75-85%│ Roboflow (easy!)      │
│  4   │ Your Training (ongoing)  │ ~43%+ │ Already have!         │
└─────────────────────────────────────────────────────────────────┘

FASTEST WAY TO GET A GOOD MODEL:
─────────────────────────────────
1. Go to: https://universe.roboflow.com/browse/fire
2. Pick any model with high mAP
3. Download YOLOv8 weights
4. Save to models/pretrained/
5. Test with: py test_pretrained_dfire.py
""")


if __name__ == "__main__":
    main()

