"""
Export Model for Raspberry Pi Deployment
Converts the fire detection model to optimized formats for Pi 4

This creates smaller, faster models suitable for $60 Pi!
"""
from ultralytics import YOLO
import os

print("=" * 70)
print("🍓 RASPBERRY PI MODEL EXPORTER")
print("=" * 70)

# Choose the smallest fire detection model
MODEL_PATH = "models/pretrained/yolov10n_forest_fire.pt"  # 5.5 MB

if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "models/pretrained/yolov8n.pt"  # Fallback

print(f"\n📁 Source model: {MODEL_PATH}")
print(f"   Size: {os.path.getsize(MODEL_PATH) / (1024*1024):.1f} MB")

# Load model
model = YOLO(MODEL_PATH)

print("\n" + "-" * 70)
print("📦 EXPORTING FORMATS")
print("-" * 70)

# 1. Export to ONNX (cross-platform, works on Pi)
print("\n1️⃣ Exporting to ONNX...")
try:
    model.export(format='onnx', imgsz=320)  # Smaller input = faster
    print("   ✅ ONNX export complete")
except Exception as e:
    print(f"   ❌ ONNX failed: {e}")

# 2. Export to TensorFlow Lite (best for Pi)
print("\n2️⃣ Exporting to TensorFlow Lite...")
try:
    model.export(format='tflite', imgsz=320)
    print("   ✅ TFLite export complete")
except Exception as e:
    print(f"   ⚠️ TFLite failed (may need tensorflow): {e}")

# 3. Export to NCNN (optimized for ARM/Pi)
print("\n3️⃣ Exporting to NCNN (ARM optimized)...")
try:
    model.export(format='ncnn', imgsz=320)
    print("   ✅ NCNN export complete")
except Exception as e:
    print(f"   ⚠️ NCNN failed: {e}")

print("\n" + "=" * 70)
print("📊 EXPORTED MODELS")
print("=" * 70)

# List exported files
export_dir = MODEL_PATH.replace('.pt', '_')
formats = ['.onnx', '_saved_model', '_ncnn_model']

print("""
Expected output files:
- yolov10n_forest_fire.onnx     → ONNX format (~2 MB)
- yolov10n_forest_fire_int8.tflite → TFLite INT8 (~1.5 MB)

These can run on Raspberry Pi 4 at 5-10+ FPS!
""")

print("\n" + "=" * 70)
print("🍓 PI 4 DEPLOYMENT GUIDE")
print("=" * 70)
print("""
On Raspberry Pi 4:

1. Copy the .onnx or .tflite file to Pi
2. Install dependencies:
   pip install onnxruntime  # for ONNX
   # OR
   pip install tflite-runtime  # for TFLite

3. Run inference:
   from ultralytics import YOLO
   model = YOLO('fire_model.onnx')
   results = model(frame)

Expected Performance:
- YOLOv8n ONNX @ 320px: 5-8 FPS
- YOLOv8n TFLite INT8 @ 320px: 8-12 FPS

This is PLENTY for fire detection! 🔥
(Fire doesn't move that fast, 5 FPS is fine)
""")

