"""
Download YOLOv10 Fire & Smoke Detection model from HuggingFace
Model: TommyNgx/YOLOv10-Fire-and-Smoke-Detection
Reported mAP: 85%
"""
import os
import urllib.request
import sys

print("=" * 70)
print("🔥 DOWNLOADING YOLOV10 FIRE & SMOKE DETECTION MODEL")
print("=" * 70)
print("Source: HuggingFace - TommyNgx/YOLOv10-Fire-and-Smoke-Detection")
print("Reported Accuracy: 85% mAP")
print()

# Create models directory
os.makedirs("models/pretrained", exist_ok=True)

# Model URL (direct download)
MODEL_URL = "https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection/resolve/main/best.pt"
OUTPUT_PATH = "models/pretrained/yolov10_fire_smoke.pt"

def download_with_progress(url, output_path):
    """Download file with progress bar"""
    print(f"📥 Downloading from: {url}")
    print(f"📁 Saving to: {output_path}")
    print()
    
    if os.path.exists(output_path):
        size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ File already exists! ({size:.1f} MB)")
        return True
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            bar_len = 40
            filled = int(bar_len * percent / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            sys.stdout.write(f"\r   [{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
            sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, output_path, progress_hook)
        print()  # New line after progress
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"\n✅ Download complete! ({size:.1f} MB)")
            return True
        else:
            print("\n❌ Download failed - file not found")
            return False
            
    except Exception as e:
        print(f"\n❌ Download error: {e}")
        return False

# Download
success = download_with_progress(MODEL_URL, OUTPUT_PATH)

if success:
    print()
    print("=" * 70)
    print("✅ MODEL READY TO USE!")
    print("=" * 70)
    print(f"""
To use this model:

1. With Unified Fire Detector:
   py fire_detector_unified.py --model models/pretrained/yolov10_fire_smoke.pt

2. With simulation:
   (Update MODEL_PATH in simulation.py to 'models/pretrained/yolov10_fire_smoke.pt')

Note: This model uses YOLOv10 architecture, ensure you have:
   pip install ultralytics>=8.2.0
""")
else:
    print()
    print("=" * 70)
    print("⚠️ MANUAL DOWNLOAD REQUIRED")
    print("=" * 70)
    print("""
The automatic download failed. Please download manually:

1. Go to: https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection/tree/main
2. Click on 'best.pt' to download
3. Move the file to: models/pretrained/yolov10_fire_smoke.pt

Or use wget/curl:
   curl -L -o models/pretrained/yolov10_fire_smoke.pt "https://huggingface.co/TommyNgx/YOLOv10-Fire-and-Smoke-Detection/resolve/main/best.pt"
""")

