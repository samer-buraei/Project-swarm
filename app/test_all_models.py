"""
Test all available fire detection models
Shows detection on a test image or webcam
"""
import os
import sys
import glob
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("🔥 FIRE DETECTION MODEL TESTER")
print("=" * 70)

# Find all available .pt models
from config import DATA_DIR, MODELS_DIR

models_found = []
search_paths = [
    DATA_DIR / "runs/train/**/weights/best.pt",
    MODELS_DIR / "**/*.pt",
    DATA_DIR / "*.pt"
]

print("\n📦 Searching for models...")
for pattern in search_paths:
    for path in glob.glob(pattern, recursive=True):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        models_found.append((path, size_mb))
        print(f"  ✓ Found: {path} ({size_mb:.1f} MB)")

if not models_found:
    print("  ❌ No models found!")
    sys.exit(1)

print(f"\n📊 Found {len(models_found)} models total")

# Test each model
try:
    from ultralytics import YOLO
    import cv2
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Run: pip install ultralytics opencv-python")
    sys.exit(1)

print("\n" + "=" * 70)
print("🧪 TESTING MODELS")
print("=" * 70)

# Use our trained model first
best_model = None
best_path = "runs/train/fire_yolov8n/weights/best.pt"

if os.path.exists(best_path):
    print(f"\n🎯 Using trained model: {best_path}")
    best_model = best_path
else:
    # Use first available
    if models_found:
        best_model = models_found[0][0]
        print(f"\n🎯 Using first available model: {best_model}")

if not best_model:
    print("❌ No model available to test!")
    sys.exit(1)

# Load model
print(f"\n⏳ Loading model...")
try:
    model = YOLO(best_model)
    print(f"✅ Model loaded!")
    print(f"   Classes: {model.names}")
except Exception as e:
    print(f"❌ Failed to load: {e}")
    sys.exit(1)

# Test with webcam
print("\n" + "=" * 70)
print("📹 STARTING WEBCAM TEST")
print("=" * 70)
print("""
Controls:
  Q - Quit
  T - Change detection threshold
  S - Save screenshot

Point your camera at:
  - A phone showing fire video
  - A candle or lighter (may need low threshold)
  - Fire images on screen
""")

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open webcam!")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

threshold = 0.25
thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
thresh_idx = 3

print(f"✅ Webcam opened! Threshold: {threshold}")
print("Press Q to quit...")

frame_count = 0
detection_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Run detection
    results = model(frame, conf=threshold, verbose=False)
    
    # Draw results
    annotated = results[0].plot()
    
    # Count detections
    boxes = results[0].boxes
    if len(boxes) > 0:
        detection_count += 1
        
    # Add info text
    info = f"Threshold: {threshold:.2f} | Detections: {len(boxes)} | Press T to change, Q to quit"
    cv2.putText(annotated, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show
    cv2.imshow("Fire Detection Test - Press Q to quit", annotated)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('t'):
        thresh_idx = (thresh_idx + 1) % len(thresholds)
        threshold = thresholds[thresh_idx]
        print(f"🔧 Threshold changed to: {threshold}")
    elif key == ord('s'):
        filename = f"fire_detection_{frame_count}.jpg"
        cv2.imwrite(filename, annotated)
        print(f"📸 Saved: {filename}")

cap.release()
cv2.destroyAllWindows()

print(f"\n📊 Detection Summary:")
print(f"   Frames processed: {frame_count}")
print(f"   Frames with detections: {detection_count}")
print(f"   Detection rate: {100*detection_count/max(1,frame_count):.1f}%")

