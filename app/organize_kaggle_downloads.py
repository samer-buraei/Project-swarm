"""
Organize Kaggle Fire Detection Downloads
Run this AFTER downloads complete to prepare data for training

Expected downloads in your Downloads folder:
- archive.zip
- archive (1).zip  
- archive (2).zip
"""
import os
import zipfile
import shutil
from pathlib import Path

print("=" * 70)
print("🔥 KAGGLE FIRE DATASET ORGANIZER")
print("=" * 70)

# Paths - UPDATE THESE TO MATCH YOUR SYSTEM
DOWNLOADS = Path.home() / "Downloads"  # Auto-detects user's Downloads folder
PROJECT = Path(__file__).parent.parent  # Project root (one level up from app/)
DATASETS = PROJECT / "data" / "datasets"  # Assumes data symlink exists
KAGGLE_DIR = DATASETS / "Kaggle_Combined"

# Create output directory
KAGGLE_DIR.mkdir(parents=True, exist_ok=True)

# Expected archives
archives = [
    DOWNLOADS / "archive.zip",
    DOWNLOADS / "archive (1).zip",
    DOWNLOADS / "archive (2).zip",
]

def check_downloads():
    """Check which archives are ready"""
    print("\n📥 Checking downloads...")
    ready = []
    pending = []
    
    for archive in archives:
        if archive.exists():
            size_gb = archive.stat().st_size / (1024**3)
            print(f"  ✅ {archive.name} ({size_gb:.1f} GB)")
            ready.append(archive)
        else:
            print(f"  ❌ {archive.name} - NOT FOUND")
            pending.append(archive)
    
    return ready, pending


def extract_archive(archive_path, extract_to):
    """Extract a zip archive"""
    print(f"\n📦 Extracting {archive_path.name}...")
    
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            # Get total files
            total = len(zip_ref.namelist())
            print(f"   Found {total} files")
            
            # Extract
            zip_ref.extractall(extract_to)
            print(f"   ✅ Extracted to {extract_to}")
            return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def count_images(directory):
    """Count image files in directory"""
    extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    count = 0
    for ext in extensions:
        count += len(list(Path(directory).rglob(f'*{ext}')))
        count += len(list(Path(directory).rglob(f'*{ext.upper()}')))
    return count


def organize_for_yolo():
    """Organize extracted data into YOLO format"""
    print("\n🔧 Organizing for YOLO training...")
    
    # Create YOLO structure
    yolo_train_img = KAGGLE_DIR / "train" / "images"
    yolo_train_lbl = KAGGLE_DIR / "train" / "labels"
    yolo_val_img = KAGGLE_DIR / "val" / "images"
    yolo_val_lbl = KAGGLE_DIR / "val" / "labels"
    
    for d in [yolo_train_img, yolo_train_lbl, yolo_val_img, yolo_val_lbl]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Find all images
    all_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        all_images.extend(KAGGLE_DIR.rglob(ext))
    
    # Filter out already organized ones
    all_images = [img for img in all_images if 'train/images' not in str(img) and 'val/images' not in str(img)]
    
    print(f"   Found {len(all_images)} images to organize")
    
    if len(all_images) == 0:
        print("   No new images to organize")
        return
    
    # Split 80/20
    import random
    random.shuffle(all_images)
    split_idx = int(len(all_images) * 0.8)
    
    train_imgs = all_images[:split_idx]
    val_imgs = all_images[split_idx:]
    
    # Copy images
    print(f"   Copying {len(train_imgs)} train images...")
    for i, img in enumerate(train_imgs):
        dst = yolo_train_img / f"kaggle_{i:06d}{img.suffix}"
        shutil.copy2(img, dst)
        
        # Check for label file
        lbl = img.with_suffix('.txt')
        if lbl.exists():
            shutil.copy2(lbl, yolo_train_lbl / f"kaggle_{i:06d}.txt")
    
    print(f"   Copying {len(val_imgs)} val images...")
    for i, img in enumerate(val_imgs):
        dst = yolo_val_img / f"kaggle_{i:06d}{img.suffix}"
        shutil.copy2(img, dst)
        
        lbl = img.with_suffix('.txt')
        if lbl.exists():
            shutil.copy2(lbl, yolo_val_lbl / f"kaggle_{i:06d}.txt")
    
    # Create data.yaml
    yaml_content = f"""# Kaggle Fire Dataset (Combined)
path: {KAGGLE_DIR}
train: train/images
val: val/images

nc: 2
names:
  0: fire
  1: smoke
"""
    
    with open(KAGGLE_DIR / "data.yaml", 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Dataset organized!")
    print(f"   Train: {len(train_imgs)} images")
    print(f"   Val: {len(val_imgs)} images")
    print(f"   Config: {KAGGLE_DIR / 'data.yaml'}")


def main():
    # Check downloads
    ready, pending = check_downloads()
    
    if pending:
        print(f"\n⏳ {len(pending)} downloads still in progress")
        print("   Run this script again when all downloads complete")
    
    if not ready:
        print("\n❌ No archives ready to process")
        return
    
    # Extract ready archives
    for archive in ready:
        extract_dir = KAGGLE_DIR / archive.stem
        if not extract_dir.exists():
            extract_archive(archive, extract_dir)
        else:
            print(f"\n⏭️ {archive.name} already extracted")
    
    # Count images
    total_images = count_images(KAGGLE_DIR)
    print(f"\n📊 Total images found: {total_images}")
    
    # Organize
    if total_images > 0:
        organize_for_yolo()
    
    print("\n" + "=" * 70)
    print("📋 NEXT STEPS")
    print("=" * 70)
    print("""
1. If more downloads pending, run this script again when complete
2. After all organized, train with:
   
   py train_on_kaggle.py

Or fine-tune the pretrained model:
   
   from ultralytics import YOLO
   model = YOLO('models/pretrained/yolov10_fire_smoke.pt')
   model.train(data='datasets/Kaggle_Combined/data.yaml', epochs=20)
""")


if __name__ == "__main__":
    main()

