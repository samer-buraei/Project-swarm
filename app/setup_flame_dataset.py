"""
FLAME Dataset Setup Script
Downloads and prepares the FLAME (Fire Luminosity Airborne-based Machine learning Evaluation) dataset
for training thermal fire detection models.

FLAME contains actual aerial thermal drone footage - perfect for our use case!

Sources:
1. IEEE DataPort (requires free registration): https://ieee-dataport.org/open-access/flame-dataset
2. Kaggle (easier access): https://www.kaggle.com/datasets/phylake1337/fire-dataset

This script will:
1. Check for existing downloads
2. Guide you through manual download if needed
3. Organize the dataset for YOLO training
"""
import os
import sys
import shutil
from pathlib import Path

print("=" * 70)
print("🔥 FLAME DATASET SETUP")
print("=" * 70)

# Dataset paths
# Dataset paths
from config import DATASETS_DIR
DATASET_DIR = DATASETS_DIR / "FLAME"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

def check_existing():
    """Check if FLAME dataset already exists"""
    print("\n📁 Checking for existing FLAME data...")
    
    # Check common download locations
    possible_paths = [
        DATASET_DIR,
        Path("datasets/flame"),
        Path("FLAME"),
        Path.home() / "Downloads" / "FLAME",
        Path.home() / "Downloads" / "flame-dataset",
    ]
    
    for path in possible_paths:
        if path.exists():
            files = list(path.glob("**/*"))
            if len(files) > 10:
                print(f"✅ Found data at: {path}")
                return path
                
    print("❌ FLAME dataset not found locally")
    return None


def try_kaggle_download():
    """Try to download from Kaggle if kaggle is installed"""
    print("\n📥 Attempting Kaggle download...")
    
    try:
        import kaggle
        
        print("   Kaggle API found, downloading...")
        kaggle.api.dataset_download_files(
            'phylake1337/fire-dataset',
            path=str(DATASET_DIR),
            unzip=True
        )
        print("✅ Downloaded from Kaggle!")
        return True
        
    except ImportError:
        print("   ⚠️ Kaggle not installed. Install with: pip install kaggle")
        return False
    except Exception as e:
        print(f"   ⚠️ Kaggle download failed: {e}")
        return False


def show_manual_instructions():
    """Show manual download instructions"""
    print("\n" + "=" * 70)
    print("📋 MANUAL DOWNLOAD INSTRUCTIONS")
    print("=" * 70)
    print("""
Since automated download requires authentication, please download manually:

╔══════════════════════════════════════════════════════════════════════╗
║  OPTION 1: IEEE DataPort (Best - Full Dataset)                      ║
╠══════════════════════════════════════════════════════════════════════╣
║  1. Go to: https://ieee-dataport.org/open-access/flame-dataset      ║
║  2. Create a free IEEE account (or sign in)                         ║
║  3. Download the dataset ZIP files                                  ║
║  4. Extract to: datasets/FLAME/                                     ║
╚══════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════╗
║  OPTION 2: Kaggle (Easier - Subset)                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║  1. Go to: https://www.kaggle.com/datasets/phylake1337/fire-dataset ║
║  2. Sign in to Kaggle                                               ║
║  3. Click "Download" button                                         ║
║  4. Extract to: datasets/FLAME/                                     ║
╚══════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════╗
║  OPTION 3: Roboflow (Pre-formatted for YOLO)                        ║
╠══════════════════════════════════════════════════════════════════════╣
║  1. Go to: https://universe.roboflow.com/browse/fire                ║
║  2. Find a thermal fire dataset                                     ║
║  3. Export as "YOLOv8" format                                       ║
║  4. Extract to: datasets/FLAME/                                     ║
╚══════════════════════════════════════════════════════════════════════╝

After downloading, run this script again to organize the data.
""")


def organize_for_yolo(source_path):
    """Organize downloaded data for YOLO training"""
    print(f"\n🔧 Organizing {source_path} for YOLO training...")
    
    # Create YOLO structure
    yolo_dir = Path("datasets/FLAME_YOLO")
    for split in ['train', 'val']:
        (yolo_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (yolo_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Look for images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    for ext in image_extensions:
        images.extend(source_path.glob(f"**/*{ext}"))
        images.extend(source_path.glob(f"**/*{ext.upper()}"))
    
    print(f"   Found {len(images)} images")
    
    if len(images) == 0:
        print("   ❌ No images found!")
        return False
        
    # Split 80/20 train/val
    import random
    random.shuffle(images)
    split_idx = int(len(images) * 0.8)
    
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    # Copy images
    print(f"   Copying {len(train_images)} train images...")
    for i, img in enumerate(train_images):
        dst = yolo_dir / 'train' / 'images' / f"flame_{i:05d}{img.suffix}"
        shutil.copy2(img, dst)
        
    print(f"   Copying {len(val_images)} val images...")
    for i, img in enumerate(val_images):
        dst = yolo_dir / 'val' / 'images' / f"flame_{i:05d}{img.suffix}"
        shutil.copy2(img, dst)
    
    # Create data.yaml
    yaml_content = f"""# FLAME Dataset for Fire Detection
# Aerial thermal drone footage

path: {yolo_dir.absolute()}
train: train/images
val: val/images

nc: 2
names:
  0: fire
  1: smoke

# Note: Labels may need to be created/converted
# If no labels exist, use auto-labeling or manual annotation
"""
    
    with open(yolo_dir / 'data.yaml', 'w') as f:
        f.write(yaml_content)
        
    print(f"✅ Dataset organized at: {yolo_dir}")
    print(f"   Train: {len(train_images)} images")
    print(f"   Val: {len(val_images)} images")
    print(f"   Config: {yolo_dir / 'data.yaml'}")
    
    return True


def create_training_script():
    """Create a training script for FLAME dataset"""
    script = '''"""
Train fire detection model on FLAME thermal dataset
"""
from ultralytics import YOLO

def train_flame():
    # Load base model (or our D-Fire trained model for transfer learning)
    # Option 1: Start from base
    # model = YOLO('yolov8n.pt')
    
    # Option 2: Start from our D-Fire trained model (recommended)
    model = YOLO('runs/train/fire_yolov8n/weights/best.pt')
    
    # Train on FLAME
    results = model.train(
        data='datasets/FLAME_YOLO/data.yaml',
        epochs=50,
        imgsz=640,
        batch=8,
        name='fire_thermal_v1',
        project='models',
        patience=10,
        
        # Transfer learning settings
        freeze=10,  # Freeze first 10 layers (backbone)
        
        # Augmentation for thermal
        hsv_h=0.0,  # No hue change (thermal is grayscale-ish)
        hsv_s=0.0,  # No saturation change
        hsv_v=0.2,  # Some brightness variation
    )
    
    print("✅ FLAME training complete!")
    print(f"   Best model: models/fire_thermal_v1/weights/best.pt")
    
    return results

if __name__ == "__main__":
    train_flame()
'''
    
    with open("train_flame_thermal.py", 'w') as f:
        f.write(script)
    print("✅ Created: train_flame_thermal.py")


def main():
    # Check for existing data
    existing = check_existing()
    
    if existing:
        print(f"\n✅ Dataset found at: {existing}")
        organize_for_yolo(existing)
        create_training_script()
    else:
        # Try Kaggle
        if try_kaggle_download():
            organize_for_yolo(DATASET_DIR)
            create_training_script()
        else:
            # Show manual instructions
            show_manual_instructions()
            create_training_script()
            
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS")
    print("=" * 70)
    print("""
1. Download FLAME dataset (if not done already)
2. Run this script again to organize: py setup_flame_dataset.py
3. Train on FLAME: py train_flame_thermal.py

Or continue with current D-Fire training and test with thermal simulation.
""")


if __name__ == "__main__":
    main()

