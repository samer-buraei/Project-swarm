"""
Download all available pretrained fire detection models
"""
import os
import urllib.request
import sys

# Create models directory
os.makedirs("models/pretrained", exist_ok=True)

print("=" * 60)
print("🔥 FIRE DETECTION MODEL DOWNLOADER")
print("=" * 60)

# Models to download (direct links that work without auth)
models = {
    # YOLOv8 base model (we'll use for training)
    "yolov8n.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt",
    "yolov8s.pt": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8s.pt",
}

def download_file(url, filename, dest_folder="models/pretrained"):
    """Download a file with progress"""
    filepath = os.path.join(dest_folder, filename)
    
    if os.path.exists(filepath):
        print(f"✓ {filename} already exists")
        return True
        
    print(f"\n📥 Downloading {filename}...")
    print(f"   From: {url}")
    
    try:
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                sys.stdout.write(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, filepath, progress)
        print(f"\n   ✅ Downloaded to {filepath}")
        return True
    except Exception as e:
        print(f"\n   ❌ Failed: {e}")
        return False

# Download base YOLO models
print("\n📦 Downloading base YOLO models...")
for name, url in models.items():
    download_file(url, name)

# Now let's try to get a fire-specific model from Roboflow
print("\n" + "=" * 60)
print("📦 Attempting Roboflow Fire Model...")
print("=" * 60)

try:
    # Try installing roboflow
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "roboflow", "-q"])
    
    from roboflow import Roboflow
    
    # Get a public fire detection model
    rf = Roboflow(api_key="")  # Empty key for public datasets
    
    # Try to download fire detection dataset with pretrained model
    project = rf.workspace("fireandsmokepart1").project("fireandsmokedataset1")
    version = project.version(1)
    
    print("Downloading dataset with model...")
    dataset = version.download("yolov8", location="models/roboflow_fire")
    print("✅ Downloaded Roboflow fire model!")
    
except Exception as e:
    print(f"⚠️  Roboflow download skipped: {e}")
    print("   (This is normal - Roboflow may require API key)")

print("\n" + "=" * 60)
print("📊 DOWNLOAD SUMMARY")
print("=" * 60)

# Check what models we have
print("\nModels available:")
for folder in ["models/pretrained", "models", "runs/train"]:
    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(".pt"):
                    path = os.path.join(root, f)
                    size = os.path.getsize(path) / (1024 * 1024)
                    print(f"  ✓ {path} ({size:.1f} MB)")

print("\n" + "=" * 60)
print("📋 NEXT STEPS:")
print("=" * 60)
print("""
1. Your D-Fire training is running in background
   Check: runs/train/fire_yolov8n/weights/best.pt

2. To test fire detection with camera:
   py live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt

3. For best pretrained models, manually download from:
   - HuggingFace: https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection
   - D-Fire YOLOv5: https://1drv.ms/u/c/c0bd25b6b048b01d/ERy9-UpeDeRHkEb_eqPeC7EBdblsWLwujJ1BlssUWfz_Lg
""")

