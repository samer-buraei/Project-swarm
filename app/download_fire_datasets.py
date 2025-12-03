"""
🔥 FIRE DATASET DOWNLOADER
===========================
Downloads fire detection datasets for training.

Usage:
    python download_fire_datasets.py --status     # Check what you have
    python download_fire_datasets.py --roboflow   # Download from Roboflow (EASIEST)
    python download_fire_datasets.py --organize   # Combine all datasets
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse


DATASETS_DIR = Path("datasets")
COMBINED_DIR = DATASETS_DIR / "Combined"


def setup_directories():
    """Create necessary directories"""
    DATASETS_DIR.mkdir(exist_ok=True)
    COMBINED_DIR.mkdir(exist_ok=True)
    (COMBINED_DIR / "train" / "images").mkdir(parents=True, exist_ok=True)
    (COMBINED_DIR / "train" / "labels").mkdir(parents=True, exist_ok=True)
    (COMBINED_DIR / "val" / "images").mkdir(parents=True, exist_ok=True)
    (COMBINED_DIR / "val" / "labels").mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")


def download_roboflow_fire():
    """Download fire dataset from Roboflow using their Python package"""
    print("\n" + "=" * 60)
    print("📥 ROBOFLOW FIRE DATASET (EASIEST METHOD)")
    print("=" * 60)
    
    # Install roboflow if needed
    try:
        from roboflow import Roboflow
        print("✅ Roboflow package found")
    except ImportError:
        print("📦 Installing roboflow package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "roboflow"], check=True)
        from roboflow import Roboflow
    
    print("""
🔥 DOWNLOADING FIRE DETECTION DATASET FROM ROBOFLOW

This will download a fire/smoke detection dataset in YOLOv8 format.
""")
    
    # Use a public fire detection dataset
    # This one is public and doesn't require API key
    rf = Roboflow(api_key="PLACEHOLDER")  # Public datasets don't need real key
    
    print("\n📥 Downloading fire detection dataset...")
    try:
        # Try to download a public fire dataset
        project = rf.workspace().project("fire-lhfji")
        dataset = project.version(1).download("yolov8", location=str(DATASETS_DIR / "Roboflow_Fire"))
        print("✅ Downloaded fire dataset!")
        return True
    except Exception as e:
        print(f"⚠️ Roboflow API method failed: {e}")
        print("\n" + "=" * 60)
        print("📋 MANUAL DOWNLOAD INSTRUCTIONS (Takes 2 minutes)")
        print("=" * 60)
        print("""
STEP 1: Go to one of these URLs in your browser:

   🔥 Fire Detection Dataset (RECOMMENDED):
   https://universe.roboflow.com/fire-detection-tcvmj/fire-lhfji/dataset/1

   🌲 Wildfire Smoke Dataset:
   https://universe.roboflow.com/brad-dwyer/wildfire-smoke/dataset/7

STEP 2: Click "Download Dataset" button

STEP 3: Select:
   - Format: "YOLOv8"
   - Download Type: "zip"
   
STEP 4: Extract the downloaded zip to:
   datasets/Roboflow_Fire/

STEP 5: Run this command to organize:
   python download_fire_datasets.py --organize
""")
        return False


def organize_datasets():
    """Organize all downloaded datasets into Combined folder"""
    print("\n" + "=" * 60)
    print("📁 ORGANIZING DATASETS")
    print("=" * 60)
    
    setup_directories()
    
    total_train = 0
    total_val = 0
    
    # Process D-Fire (already in project root)
    dfire_dir = Path("DFireDataset")
    if dfire_dir.exists():
        print("\n📁 Processing D-Fire...")
        
        # Copy train images
        train_src = dfire_dir / "train" / "images"
        if train_src.exists():
            count = 0
            for img in train_src.glob("*.jpg"):
                dst = COMBINED_DIR / "train" / "images" / f"dfire_{img.name}"
                if not dst.exists():
                    shutil.copy(img, dst)
                    count += 1
                    
            # Copy labels
            label_src = dfire_dir / "train" / "labels"
            if label_src.exists():
                for lbl in label_src.glob("*.txt"):
                    dst = COMBINED_DIR / "train" / "labels" / f"dfire_{lbl.name}"
                    if not dst.exists():
                        shutil.copy(lbl, dst)
            
            total_train += count
            print(f"   ✅ Train: {count} images")
        
        # Copy test as validation
        test_src = dfire_dir / "test" / "images"
        if test_src.exists():
            count = 0
            for img in test_src.glob("*.jpg"):
                dst = COMBINED_DIR / "val" / "images" / f"dfire_{img.name}"
                if not dst.exists():
                    shutil.copy(img, dst)
                    count += 1
                    
            label_src = dfire_dir / "test" / "labels"
            if label_src.exists():
                for lbl in label_src.glob("*.txt"):
                    dst = COMBINED_DIR / "val" / "labels" / f"dfire_{lbl.name}"
                    if not dst.exists():
                        shutil.copy(lbl, dst)
            
            total_val += count
            print(f"   ✅ Val: {count} images")
    
    # Process any Roboflow datasets
    for roboflow_dir in DATASETS_DIR.glob("*"):
        if not roboflow_dir.is_dir() or roboflow_dir.name == "Combined":
            continue
            
        print(f"\n📁 Processing {roboflow_dir.name}...")
        
        # YOLOv8 format has train/valid/test folders
        for split in ["train", "valid", "test"]:
            src_images = roboflow_dir / split / "images"
            src_labels = roboflow_dir / split / "labels"
            
            if src_images.exists():
                target = "train" if split in ["train", "test"] else "val"
                count = 0
                prefix = roboflow_dir.name.lower().replace(" ", "_")
                
                for img in src_images.glob("*.*"):
                    if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        dst = COMBINED_DIR / target / "images" / f"{prefix}_{img.name}"
                        if not dst.exists():
                            shutil.copy(img, dst)
                            count += 1
                            if target == "train":
                                total_train += 1
                            else:
                                total_val += 1
                
                if src_labels.exists():
                    for lbl in src_labels.glob("*.txt"):
                        dst = COMBINED_DIR / target / "labels" / f"{prefix}_{lbl.name}"
                        if not dst.exists():
                            shutil.copy(lbl, dst)
                
                if count > 0:
                    print(f"   ✅ {split} → {target}: {count} images")
    
    # Create data.yaml for training
    create_data_yaml()
    
    print("\n" + "=" * 60)
    print(f"✅ COMBINED DATASET READY!")
    print(f"   Train: {total_train} images")
    print(f"   Val: {total_val} images")
    print(f"   Location: {COMBINED_DIR.absolute()}")
    print("=" * 60)
    
    return total_train, total_val


def create_data_yaml():
    """Create YOLO data.yaml configuration"""
    yaml_content = f"""# Fire Detection Dataset Configuration
# Auto-generated by download_fire_datasets.py

path: {COMBINED_DIR.absolute()}
train: train/images
val: val/images

# Classes - D-Fire uses: 0=fire, 1=smoke
nc: 2
names: ['fire', 'smoke']
"""
    
    yaml_path = COMBINED_DIR / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Created {yaml_path}")


def print_status():
    """Print current dataset status"""
    print("\n" + "=" * 60)
    print("📊 DATASET STATUS")
    print("=" * 60)
    
    # Check D-Fire
    dfire_dir = Path("DFireDataset")
    if dfire_dir.exists():
        train_count = len(list((dfire_dir / "train" / "images").glob("*.jpg"))) if (dfire_dir / "train" / "images").exists() else 0
        test_count = len(list((dfire_dir / "test" / "images").glob("*.jpg"))) if (dfire_dir / "test" / "images").exists() else 0
        print(f"✅ D-Fire: {train_count:,} train, {test_count:,} test")
    else:
        print("❌ D-Fire: Not found")
    
    # Check Combined
    if COMBINED_DIR.exists():
        train_count = len(list((COMBINED_DIR / "train" / "images").glob("*.*")))
        val_count = len(list((COMBINED_DIR / "val" / "images").glob("*.*")))
        if train_count > 0 or val_count > 0:
            print(f"✅ Combined: {train_count:,} train, {val_count:,} val")
        else:
            print("⚠️ Combined: Empty (run --organize)")
    else:
        print("❌ Combined: Not created (run --organize)")
    
    # Check for additional datasets in datasets/
    if DATASETS_DIR.exists():
        for d in DATASETS_DIR.glob("*"):
            if d.is_dir() and d.name != "Combined":
                img_count = len(list(d.rglob("*.jpg"))) + len(list(d.rglob("*.png")))
                print(f"📁 {d.name}: {img_count:,} images")


def main():
    parser = argparse.ArgumentParser(description="Download fire detection datasets")
    parser.add_argument("--roboflow", action="store_true", help="Download from Roboflow")
    parser.add_argument("--organize", action="store_true", help="Organize datasets into Combined folder")
    parser.add_argument("--status", action="store_true", help="Show dataset status")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔥 FIRE DATASET DOWNLOADER")
    print("=" * 60)
    
    if args.status:
        print_status()
        return
    
    if not any([args.roboflow, args.organize]):
        print_status()
        print("\n💡 Commands:")
        print("   --status    Show what datasets you have")
        print("   --roboflow  Download fire dataset from Roboflow")
        print("   --organize  Combine all datasets for training")
        return
    
    setup_directories()
    
    if args.roboflow:
        download_roboflow_fire()
    
    if args.organize:
        organize_datasets()


if __name__ == "__main__":
    main()
