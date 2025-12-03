"""
🔥 LIVE CAMERA FIRE DETECTION TEST - FIXED VERSION
====================================================
Uses YOLO fire model for detection, color detection as backup.

Usage:
    python live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt
    python live_camera_fire_test.py --threshold 0.2   # Lower = more sensitive

Controls:
    Q - Quit
    S - Save screenshot
    T - Toggle detection overlay
    C - Toggle color detection (on/off)
    + - Increase threshold
    - - Decrease threshold
"""

# Suppress SSL warnings (Windows certificate store issue)
import warnings
warnings.filterwarnings('ignore', message='Bad certificate')

import cv2
import numpy as np
from ultralytics import YOLO
import time
import argparse
from pathlib import Path
from datetime import datetime

# Colors (BGR format)
FIRE_COLOR = (0, 0, 255)      # Red for fire
SMOKE_COLOR = (128, 128, 128)  # Gray for smoke
TEXT_COLOR = (255, 255, 255)   # White text


def draw_fancy_box(frame, box, label, confidence, color):
    """Draw a styled bounding box with label"""
    x1, y1, x2, y2 = map(int, box)
    
    # Draw main box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
    
    # Draw label background
    label_text = f"{label}: {confidence:.0%}"
    (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x1, y1 - 25), (x1 + text_w + 10, y1), color, -1)
    
    # Draw label text
    cv2.putText(frame, label_text, (x1 + 5, y1 - 7), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)
    
    return frame


def draw_hud(frame, fps, threshold, fire_count, use_color_detection):
    """Draw heads-up display with stats"""
    h, w = frame.shape[:2]
    
    # Top bar
    cv2.rectangle(frame, (0, 0), (w, 45), (20, 20, 20), -1)
    
    # Title
    cv2.putText(frame, "FIRE DETECTION - YOLO MODEL", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    
    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Bottom bar
    cv2.rectangle(frame, (0, h - 40), (w, h), (20, 20, 20), -1)
    
    # Controls
    color_status = "ON" if use_color_detection else "OFF"
    controls = f"[Q]uit [S]ave [C]olor:{color_status} [+/-]Thresh:{threshold:.0%}"
    cv2.putText(frame, controls, (10, h - 12), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
    
    # Fire alert
    if fire_count > 0:
        if int(time.time() * 3) % 2 == 0:
            cv2.rectangle(frame, (0, 45), (w, 85), (0, 0, 200), -1)
            cv2.putText(frame, f"FIRE DETECTED! ({fire_count})", 
                        (w // 2 - 120, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    return frame


def detect_fire_by_brightness(frame, min_area=100):
    """
    Detect fire by looking for BRIGHT + HOT colored regions.
    More strict than before - requires high brightness AND fire colors.
    This filters out yellow doors but catches actual flames.
    """
    # Convert to different color spaces
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # STEP 1: Find VERY BRIGHT regions (flames are bright!)
    # Lighter flames are typically > 200 brightness
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # STEP 2: Find fire colors (orange/red/yellow)
    # Red-orange range
    lower_fire1 = np.array([0, 100, 200])   # High value (brightness) required
    upper_fire1 = np.array([25, 255, 255])
    # Yellow-orange range  
    lower_fire2 = np.array([25, 80, 200])   # High value required
    upper_fire2 = np.array([40, 255, 255])
    
    color_mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
    color_mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
    color_mask = cv2.bitwise_or(color_mask1, color_mask2)
    
    # STEP 3: Combine - must be BOTH bright AND fire colored
    fire_mask = cv2.bitwise_and(bright_mask, color_mask)
    
    # Clean up noise
    kernel = np.ones((5, 5), np.uint8)
    fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
    fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    fire_regions = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Calculate confidence based on brightness and area
            roi = frame[y:y+h, x:x+w]
            brightness = np.mean(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
            
            # Higher brightness = higher confidence
            conf = min(1.0, brightness / 255 * 1.2)
            
            if conf > 0.6:  # Only report high-confidence fire colors
                fire_regions.append({
                    'box': (x, y, x+w, y+h),
                    'confidence': conf,
                    'type': 'brightness'
                })
    
    return fire_regions


def main():
    parser = argparse.ArgumentParser(description="Live camera fire detection")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--threshold", type=float, default=0.15, help="Detection threshold (lower = more sensitive)")
    parser.add_argument("--model", type=str, default="runs/train/fire_yolov8n/weights/best.pt", help="YOLO model path")
    parser.add_argument("--width", type=int, default=1280, help="Camera width")
    parser.add_argument("--height", type=int, default=720, help="Camera height")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔥 FIRE DETECTION - YOLO MODEL")
    print("=" * 60)
    
    # Check if fire model exists
    fire_model_path = Path(args.model)
    if not fire_model_path.exists():
        print(f"⚠️ Fire model not found: {args.model}")
        print("   Using default yolov8n.pt instead")
        args.model = "yolov8n.pt"
    
    print(f"\n📷 Opening camera {args.camera}...")
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"❌ Could not open camera {args.camera}")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"✅ Camera opened: {actual_w}x{actual_h}")
    
    # Load YOLO model
    print(f"\n🤖 Loading model: {args.model}...")
    model = YOLO(args.model)
    class_names = model.names
    print(f"✅ Model loaded! Classes: {list(class_names.values())}")
    
    # Check if this is a fire model
    is_fire_model = any('fire' in str(v).lower() or 'smoke' in str(v).lower() 
                        for v in class_names.values())
    
    if is_fire_model:
        print("🔥 Fire detection model detected!")
    else:
        print("⚠️ General object model - will use color detection for fire")
    
    print("\n" + "=" * 60)
    print("📺 CONTROLS:")
    print("   Q     - Quit")
    print("   S     - Save screenshot")  
    print("   C     - Toggle color detection")
    print("   +/-   - Adjust threshold")
    print("=" * 60)
    print("\n🎯 Point camera at ACTUAL FIRE (lighter, candle, etc.)")
    print("   The model looks for real flames, not just orange colors!\n")
    
    # State
    threshold = args.threshold
    show_overlay = True
    use_color_detection = False  # OFF by default now - YOLO is primary
    fps = 0
    frame_times = []
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # Mirror for natural interaction
        frame = cv2.flip(frame, 1)
        
        detections = []
        
        # PRIMARY: Run YOLO fire detection
        results = model(frame, verbose=False, conf=threshold)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = class_names[cls_id]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Check if fire-related class
                is_fire = any(kw in cls_name.lower() for kw in ['fire', 'flame', 'smoke', 'blaze'])
                
                detections.append({
                    'box': (x1, y1, x2, y2),
                    'confidence': conf,
                    'class': cls_name,
                    'is_fire': is_fire,
                    'type': 'yolo'
                })
        
        # SECONDARY: Color/brightness detection (only if enabled)
        if use_color_detection:
            brightness_fires = detect_fire_by_brightness(frame)
            for bf in brightness_fires:
                bf['class'] = 'Fire (bright)'
                bf['is_fire'] = True
                detections.append(bf)
        
        # Draw detections
        fire_count = 0
        if show_overlay:
            for det in detections:
                if det.get('is_fire', False):
                    color = FIRE_COLOR
                    fire_count += 1
                    label = det.get('class', 'Fire')
                    frame = draw_fancy_box(frame, det['box'], label, det['confidence'], color)
                elif det['type'] == 'yolo':
                    # Show other YOLO detections in green (optional)
                    pass
        
        # Calculate FPS
        frame_time = time.time() - start_time
        frame_times.append(frame_time)
        if len(frame_times) > 30:
            frame_times.pop(0)
        fps = 1.0 / (sum(frame_times) / len(frame_times))
        
        # Draw HUD
        frame = draw_hud(frame, fps, threshold, fire_count, use_color_detection)
        
        # Show frame
        cv2.imshow("Fire Detection", frame)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == 27:
            print("\n👋 Exiting...")
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = screenshots_dir / f"fire_{timestamp}.jpg"
            cv2.imwrite(str(filename), frame)
            print(f"📸 Saved: {filename}")
        elif key == ord('c'):
            use_color_detection = not use_color_detection
            status = "ON" if use_color_detection else "OFF"
            print(f"🎨 Color detection: {status}")
        elif key == ord('+') or key == ord('='):
            threshold = min(0.95, threshold + 0.05)
            print(f"📈 Threshold: {threshold:.0%}")
        elif key == ord('-') or key == ord('_'):
            threshold = max(0.05, threshold - 0.05)
            print(f"📉 Threshold: {threshold:.0%}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Done!")


if __name__ == "__main__":
    main()
