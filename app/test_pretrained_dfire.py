"""
🔥 TEST D-FIRE PRETRAINED MODEL
================================
Tests the official D-Fire pretrained YOLOv5 model.

First download the model from:
https://1drv.ms/u/c/c0bd25b6b048b01d/EeZYmpKPBppNr3lo8oaOqecB9GDj1dDvbogCJyegO0PY1Q

Save as: models/pretrained/yolov5s_dfire.pt

Then run: python test_pretrained_dfire.py
"""

import warnings
warnings.filterwarnings('ignore', message='Bad certificate')

import cv2
import numpy as np
from pathlib import Path
import time
from datetime import datetime

# Check for pretrained model
PRETRAINED_PATHS = [
    Path("models/pretrained/yolov5s_dfire.pt"),
    Path("models/pretrained/yolov5l_dfire.pt"),
    Path("models/pretrained/yolov5s.pt"),
    Path("models/pretrained/yolov5l.pt"),
]

OUR_TRAINED = Path("runs/train/fire_yolov8n/weights/best.pt")


def find_model():
    """Find available model"""
    # Check pretrained first
    for path in PRETRAINED_PATHS:
        if path.exists():
            return path, "pretrained"
    
    # Fall back to our trained model
    if OUR_TRAINED.exists():
        return OUR_TRAINED, "trained"
    
    return None, None


def main():
    print("=" * 60)
    print("🔥 D-FIRE PRETRAINED MODEL TEST")
    print("=" * 60)
    
    model_path, model_type = find_model()
    
    if model_path is None:
        print("""
❌ No model found!

Please download the D-Fire pretrained model:

1. Go to: https://1drv.ms/u/c/c0bd25b6b048b01d/EeZYmpKPBppNr3lo8oaOqecB9GDj1dDvbogCJyegO0PY1Q

2. Click "Download"

3. Save to: models/pretrained/yolov5s_dfire.pt

4. Run this script again
""")
        return
    
    print(f"\n✅ Found model: {model_path}")
    print(f"   Type: {model_type}")
    
    # Load model
    print("\n🤖 Loading YOLO model...")
    from ultralytics import YOLO
    model = YOLO(str(model_path))
    print(f"   Classes: {model.names}")
    
    # Open camera
    print("\n📷 Opening camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("✅ Camera ready!")
    
    print("\n" + "=" * 60)
    print("🎯 Point camera at fire images/videos on your phone!")
    print("   Press Q to quit, S to save screenshot")
    print("=" * 60 + "\n")
    
    threshold = 0.25
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        
        # Run detection
        results = model(frame, verbose=False, conf=threshold)
        
        # Draw results
        fire_count = 0
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                # Color based on class
                if 'fire' in cls_name.lower():
                    color = (0, 0, 255)  # Red
                    fire_count += 1
                elif 'smoke' in cls_name.lower():
                    color = (128, 128, 128)  # Gray
                    fire_count += 1
                else:
                    color = (0, 255, 0)  # Green
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{cls_name}: {conf:.0%}"
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw HUD
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), (20, 20, 20), -1)
        cv2.putText(frame, f"D-FIRE MODEL ({model_type.upper()}) | Threshold: {threshold:.0%}", 
                   (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
        
        if fire_count > 0:
            cv2.rectangle(frame, (0, 40), (frame.shape[1], 80), (0, 0, 200), -1)
            cv2.putText(frame, f"🔥 FIRE/SMOKE DETECTED! ({fire_count})", 
                       (10, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow("D-Fire Detection", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = screenshots_dir / f"dfire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(str(filename), frame)
            print(f"📸 Saved: {filename}")
        elif key == ord('+') or key == ord('='):
            threshold = min(0.9, threshold + 0.05)
            print(f"Threshold: {threshold:.0%}")
        elif key == ord('-'):
            threshold = max(0.05, threshold - 0.05)
            print(f"Threshold: {threshold:.0%}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Done!")


if __name__ == "__main__":
    main()

