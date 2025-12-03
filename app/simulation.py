import cv2
from ultralytics import YOLO
import socket
import json
import time
import os
import base64
import argparse
import numpy as np

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description='Drone Simulation')
parser.add_argument('--id', type=str, default='A1', help='Drone ID')
parser.add_argument('--port', type=int, default=5005, help='UDP Port')
parser.add_argument('--file', type=str, default='live_frame.jpg', help='Frame save path')
parser.add_argument('--start_index', type=int, default=0, help='Start index for image dataset')
parser.add_argument('--record', action='store_true', help='Enable recording for training data')
parser.add_argument('--thermal', action='store_true', help='Enable thermal vision simulation')
parser.add_argument('--thermal_mode', type=str, default='inferno', 
                   choices=['white_hot', 'black_hot', 'inferno', 'jet', 'hot'],
                   help='Thermal colormap mode')
args = parser.parse_args()

# --- THERMAL SIMULATION ---
THERMAL_ENABLED = args.thermal
THERMAL_MODE = args.thermal_mode

def apply_thermal_filter(frame, mode='inferno'):
    """Convert RGB frame to simulated thermal imagery"""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    if mode == 'white_hot':
        thermal = cv2.bitwise_not(enhanced)
        thermal = cv2.cvtColor(thermal, cv2.COLOR_GRAY2BGR)
    elif mode == 'black_hot':
        thermal = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    elif mode == 'inferno':
        thermal = cv2.applyColorMap(enhanced, cv2.COLORMAP_INFERNO)
    elif mode == 'jet':
        thermal = cv2.applyColorMap(enhanced, cv2.COLORMAP_JET)
    elif mode == 'hot':
        thermal = cv2.applyColorMap(enhanced, cv2.COLORMAP_HOT)
    else:
        thermal = cv2.applyColorMap(enhanced, cv2.COLORMAP_INFERNO)
    
    return thermal

# --- CONFIGURATION ---
from config import DATA_DIR, MODELS_DIR

DRONE_ID = args.id
UDP_IP = "127.0.0.1"
UDP_PORT = args.port
VIDEO_PATH = str(DATA_DIR / "DFireDataset/test/images")
MODEL_PATH = str(MODELS_DIR / "fire_v8s.pt")
FRAME_SAVE_PATH = args.file
SEND_FRAMES_TO_DASHBOARD = True
START_INDEX = args.start_index
ENABLE_RECORDING = args.record

print(f"🦅 DRONE {DRONE_ID} SIMULATION STARTING ON PORT {UDP_PORT}...")
if THERMAL_ENABLED:
    print(f"🌡️ THERMAL MODE: {THERMAL_MODE}")
print("=" * 50)

# --- OPTIONAL: RECORDING FOR TRAINING DATA ---
recorder = None
if ENABLE_RECORDING:
    try:
        from recorder import DroneRecorder
        recorder = DroneRecorder(DRONE_ID)
        print("🎥 Recording ENABLED - saving training data")
    except ImportError:
        print("⚠️ recorder.py not found - recording disabled")
        ENABLE_RECORDING = False

# --- SETUP UDP ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- LOAD MODEL ---
print(f"📥 Loading Model: {MODEL_PATH}")
try:
    model = YOLO(MODEL_PATH)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("   (Make sure you have internet to download it first time)")
    exit()

# --- OPEN VIDEO SOURCE ---
image_files = []
current_img_idx = START_INDEX
using_images = False
cap = None

if os.path.isdir(VIDEO_PATH):
    print(f"📂 Loading images from: {VIDEO_PATH}")
    import glob
    image_files = sorted(glob.glob(os.path.join(VIDEO_PATH, "*.jpg")))
    if image_files:
        using_images = True
        print(f"✅ Found {len(image_files)} images.")
    else:
        print("⚠️  No images found in directory.")

if not using_images:
    if os.path.exists(VIDEO_PATH) and not os.path.isdir(VIDEO_PATH):
        print(f"🎥 Opening Video: {VIDEO_PATH}")
        cap = cv2.VideoCapture(VIDEO_PATH)
    else:
        print(f"⚠️  Source not found at {VIDEO_PATH}")
        print("   Falling back to Webcam (0)...")
        cap = cv2.VideoCapture(0)

    if cap is None or not cap.isOpened():
        print("❌ Could not open video source.")
        exit()

print("=" * 50)
print("✅ SYSTEM ONLINE. SCANNING...")
print("   Press 'f' to simulate FIRE detection")
print("   Press 't' to toggle THERMAL mode")
print("   Press 'm' to cycle thermal colormap")
print("   Press 'q' to quit")
print("=" * 50)

# Thermal mode state (can toggle at runtime)
thermal_modes = ['white_hot', 'black_hot', 'inferno', 'jet', 'hot']
thermal_mode_idx = thermal_modes.index(THERMAL_MODE) if THERMAL_MODE in thermal_modes else 2

# Manual fire override state
manual_fire_active = False
manual_fire_frames = 0

while True:
    # --- READ FRAME ---
    if using_images:
        frame = cv2.imread(image_files[current_img_idx])
        current_img_idx = (current_img_idx + 1) % len(image_files)
        time.sleep(0.1)  # Simulate ~10 FPS
    else:
        ret, frame = cap.read()
        if not ret:
            print("End of video, looping...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

    if frame is None:
        print("⚠️ Empty frame, skipping...")
        continue

    # --- APPLY THERMAL FILTER (if enabled) ---
    if THERMAL_ENABLED:
        frame = apply_thermal_filter(frame, THERMAL_MODE)

    # --- INFERENCE ---
    start_time = time.time()
    results = model(frame, verbose=False)
    end_time = time.time()
    inference_time = (end_time - start_time) * 1000  # ms
    
    # --- PROCESS RESULTS ---
    fire_detected = False
    confidence = 0.0
    detections_count = 0
    
    # Check detections
    # NOTE: Standard YOLOv8n uses COCO classes (no 'fire' class)
    # For demo, any detection triggers alert. Train on D-Fire for real fire detection.
    for r in results:
        boxes = r.boxes
        detections_count = len(boxes)
        if detections_count > 0:
            fire_detected = True
            confidence = float(boxes.conf[0])

    # --- MANUAL FIRE OVERRIDE ---
    if manual_fire_active:
        fire_detected = True
        confidence = 0.95
        manual_fire_frames -= 1
        if manual_fire_frames <= 0:
            manual_fire_active = False
            print("🔥 Manual fire override ended")

    # --- BUILD TELEMETRY ---
    lat = 44.8125 + (time.time() % 100) * 0.0001
    lon = 20.4612 + (time.time() % 50) * 0.0001
    
    fps = 1.0 / (end_time - start_time) if (end_time - start_time) > 0 else 0
    
    telemetry = {
        "id": DRONE_ID,
        "gps": [lat, lon], 
        "fire": fire_detected,
        "conf": confidence,
        "fps": round(fps, 1),
        "inference_ms": round(inference_time, 1),
        "detections": detections_count,
        "timestamp": time.strftime("%H:%M:%S"),
        "frame_idx": current_img_idx if using_images else -1
    }
    
    # --- SEND TELEMETRY VIA UDP ---
    message = json.dumps(telemetry).encode()
    sock.sendto(message, (UDP_IP, UDP_PORT))
    
    # --- RECORD FOR TRAINING DATA ---
    if ENABLE_RECORDING and recorder:
        recorder.save_frame(frame)
        recorder.log_telemetry(telemetry)
        if fire_detected:
            recorder.log_detection({
                "timestamp": time.time(),
                "gps": [lat, lon],
                "confidence": confidence,
                "detections": detections_count,
                "frame_idx": current_img_idx if using_images else -1
            })
    
    # --- SAVE FRAME FOR DASHBOARD ---
    if SEND_FRAMES_TO_DASHBOARD:
        # Draw annotations on frame
        annotated_frame = results[0].plot()
        
        # Add status overlay
        status_color = (0, 0, 255) if fire_detected else (0, 255, 0)
        status_text = "🔥 FIRE DETECTED" if fire_detected else "✓ SCANNING"
        cv2.putText(annotated_frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(annotated_frame, f"FPS: {fps:.1f} | Inference: {inference_time:.0f}ms", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"Conf: {confidence:.2f} | Detections: {detections_count}", 
                    (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Save frame for dashboard to read
        try:
            cv2.imwrite(FRAME_SAVE_PATH, annotated_frame)
        except Exception as e:
            print(f"⚠️ Could not save frame: {e}")
    
    # --- DISPLAY IN OPENCV WINDOW (Optional - can be disabled) ---
    display_frame = results[0].plot()
    
    # Build info text
    mode_text = f"[THERMAL: {THERMAL_MODE}]" if THERMAL_ENABLED else "[RGB MODE]"
    cv2.putText(display_frame, f"{mode_text} | 'f'=Fire 't'=Thermal 'm'=Mode 'q'=Quit", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    if fire_detected:
        cv2.putText(display_frame, "!!! FIRE DETECTED !!!", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    window_title = f"DRONE {DRONE_ID} VIEW {'[THERMAL]' if THERMAL_ENABLED else ''}"
    cv2.imshow(window_title, display_frame)
    
    # --- HANDLE KEY PRESSES ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('f'):
        manual_fire_active = True
        manual_fire_frames = 50  # Keep fire active for ~5 seconds
        print("🔥 MANUAL FIRE TRIGGER ACTIVATED (5 seconds)")
    elif key == ord('t'):
        THERMAL_ENABLED = not THERMAL_ENABLED
        print(f"🌡️ THERMAL MODE: {'ON' if THERMAL_ENABLED else 'OFF'}")
    elif key == ord('m'):
        thermal_mode_idx = (thermal_mode_idx + 1) % len(thermal_modes)
        THERMAL_MODE = thermal_modes[thermal_mode_idx]
        print(f"🎨 THERMAL COLORMAP: {THERMAL_MODE}")
    elif key == ord('q'):
        print("👋 Shutting down...")
        break

# --- CLEANUP ---
print("🧹 Cleaning up...")

# Finalize recording
if ENABLE_RECORDING and recorder:
    recorder.finalize()
    print(f"📁 Recording saved to: {recorder.path}")

if cap is not None:
    cap.release()
cv2.destroyAllWindows()

# Remove temp frame file
if os.path.exists(FRAME_SAVE_PATH):
    try:
        os.remove(FRAME_SAVE_PATH)
    except:
        pass

print("✅ Simulation ended.")
