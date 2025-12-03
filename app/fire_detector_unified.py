"""
Unified Fire Detection System
Supports both RGB and Thermal (simulated) modes
Ready for dual-mode detection when hardware arrives

Usage:
    py fire_detector_unified.py --mode thermal
    py fire_detector_unified.py --mode rgb
    py fire_detector_unified.py --mode dual
"""
import cv2
import numpy as np
import argparse
import warnings
import os
import sys
from pathlib import Path

warnings.filterwarnings('ignore')

# Import our thermal simulator
from thermal_simulation import ThermalSimulator

class UnifiedFireDetector:
    """
    Unified fire detection supporting RGB, Thermal, and Dual modes
    """
    
    def __init__(self, model_path=None, mode='rgb', confidence=0.25):
        """
        Initialize detector
        
        Args:
            model_path: Path to YOLO model (.pt file)
            mode: Detection mode ('rgb', 'thermal', 'dual')
            confidence: Detection confidence threshold
        """
        self.mode = mode
        self.confidence = confidence
        self.thermal_sim = ThermalSimulator(mode='inferno')
        
        # Find best available model
        if model_path and os.path.exists(model_path):
            self.model_path = model_path
        else:
            self.model_path = self._find_best_model()
            
        # Load model
        self._load_model()
        
    def _find_best_model(self):
        """Find the best available fire detection model"""
        from config import DATA_DIR, MODELS_DIR
        
        candidates = [
            DATA_DIR / "runs/train/fire_yolov8n/weights/best.pt",  # Our trained
            DATA_DIR / "runs/train/fire_yolov8n/weights/last.pt",
            MODELS_DIR / "pretrained/fire_yolov8.pt",
            MODELS_DIR / "pretrained/yolov8n.pt",  # Fallback to base
            DATA_DIR / "yolov8n.pt"
        ]
        
        for path in candidates:
            if os.path.exists(path):
                print(f"📦 Using model: {path}")
                return str(path)
                
        print("⚠️ No model found, will download yolov8n.pt")
        return "yolov8n.pt"
        
    def _load_model(self):
        """Load the YOLO model"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            print(f"✅ Model loaded: {self.model_path}")
            print(f"   Classes: {self.model.names}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            sys.exit(1)
            
    def preprocess(self, frame):
        """
        Preprocess frame based on mode
        
        Returns:
            processed frame(s) for detection
        """
        if self.mode == 'rgb':
            return {'rgb': frame}
            
        elif self.mode == 'thermal':
            thermal = self.thermal_sim.convert(frame)
            return {'thermal': thermal}
            
        elif self.mode == 'dual':
            thermal = self.thermal_sim.convert(frame)
            return {'rgb': frame, 'thermal': thermal}
            
        return {'rgb': frame}
        
    def detect(self, frame):
        """
        Run fire detection on frame
        
        Returns:
            dict with detection results and annotated frames
        """
        frames = self.preprocess(frame)
        results = {}
        
        for name, img in frames.items():
            # Run YOLO detection
            detections = self.model(img, conf=self.confidence, verbose=False)
            
            # Get annotated frame
            annotated = detections[0].plot()
            
            # Extract boxes
            boxes = detections[0].boxes
            
            results[name] = {
                'frame': annotated,
                'boxes': boxes,
                'count': len(boxes),
                'raw': detections[0]
            }
            
        return results
        
    def fuse_results(self, results):
        """
        Fuse results from dual-mode detection
        
        If both RGB and Thermal detect fire in same region,
        increase confidence.
        """
        if 'rgb' not in results or 'thermal' not in results:
            return results
            
        rgb_count = results['rgb']['count']
        thermal_count = results['thermal']['count']
        
        # Simple fusion: if both detect, high confidence
        if rgb_count > 0 and thermal_count > 0:
            fusion_confidence = "HIGH"
        elif rgb_count > 0 or thermal_count > 0:
            fusion_confidence = "MEDIUM"
        else:
            fusion_confidence = "NONE"
            
        results['fusion'] = {
            'confidence': fusion_confidence,
            'rgb_detections': rgb_count,
            'thermal_detections': thermal_count
        }
        
        return results
        
    def create_display(self, results, original_frame):
        """Create display frame based on mode"""
        
        if self.mode == 'rgb':
            display = results['rgb']['frame']
            info = f"RGB Mode | Detections: {results['rgb']['count']} | Conf: {self.confidence}"
            
        elif self.mode == 'thermal':
            display = results['thermal']['frame']
            info = f"THERMAL Mode ({self.thermal_sim.mode}) | Detections: {results['thermal']['count']}"
            
        elif self.mode == 'dual':
            # Side by side display
            rgb_frame = results['rgb']['frame']
            thermal_frame = results['thermal']['frame']
            
            # Resize to same height
            h = min(rgb_frame.shape[0], thermal_frame.shape[0])
            rgb_resized = cv2.resize(rgb_frame, (int(rgb_frame.shape[1] * h / rgb_frame.shape[0]), h))
            thermal_resized = cv2.resize(thermal_frame, (int(thermal_frame.shape[1] * h / thermal_frame.shape[0]), h))
            
            display = np.hstack([rgb_resized, thermal_resized])
            
            fusion = results.get('fusion', {})
            info = f"DUAL Mode | RGB: {results['rgb']['count']} | Thermal: {results['thermal']['count']} | Fusion: {fusion.get('confidence', 'N/A')}"
        else:
            display = original_frame
            info = "Unknown mode"
            
        # Add info bar
        cv2.putText(display, info, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display, "Q=Quit M=Mode T=Thermal C=Confidence", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                   
        return display


def main():
    parser = argparse.ArgumentParser(description="Unified Fire Detection System")
    parser.add_argument("--mode", choices=['rgb', 'thermal', 'dual'], default='thermal',
                       help="Detection mode")
    parser.add_argument("--model", type=str, default=None,
                       help="Path to YOLO model")
    parser.add_argument("--confidence", type=float, default=0.25,
                       help="Detection confidence threshold")
    parser.add_argument("--camera", type=int, default=0,
                       help="Camera index")
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔥 UNIFIED FIRE DETECTION SYSTEM")
    print("=" * 70)
    print(f"""
Mode: {args.mode.upper()}
Confidence: {args.confidence}

Controls:
    Q - Quit
    M - Cycle detection mode (rgb → thermal → dual)
    T - Cycle thermal colormap
    C - Cycle confidence threshold
    S - Save screenshot
""")
    
    # Initialize detector
    detector = UnifiedFireDetector(
        model_path=args.model,
        mode=args.mode,
        confidence=args.confidence
    )
    
    # Open webcam
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    modes = ['rgb', 'thermal', 'dual']
    mode_idx = modes.index(args.mode)
    
    confidences = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
    conf_idx = confidences.index(args.confidence) if args.confidence in confidences else 3
    
    frame_count = 0
    detection_frames = 0
    
    print("✅ System ready. Press Q to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # Run detection
        results = detector.detect(frame)
        
        # Fuse results if dual mode
        if detector.mode == 'dual':
            results = detector.fuse_results(results)
            
        # Check for any detections
        total_detections = sum(r.get('count', 0) for r in results.values() if isinstance(r, dict) and 'count' in r)
        if total_detections > 0:
            detection_frames += 1
            
        # Create display
        display = detector.create_display(results, frame)
        
        # Show
        cv2.imshow("Unified Fire Detection - Press Q to quit", display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
            
        elif key == ord('m'):
            mode_idx = (mode_idx + 1) % len(modes)
            detector.mode = modes[mode_idx]
            print(f"🔄 Mode: {detector.mode.upper()}")
            
        elif key == ord('t'):
            new_thermal = detector.thermal_sim.next_mode()
            print(f"🌡️ Thermal: {new_thermal}")
            
        elif key == ord('c'):
            conf_idx = (conf_idx + 1) % len(confidences)
            detector.confidence = confidences[conf_idx]
            print(f"🎚️ Confidence: {detector.confidence}")
            
        elif key == ord('s'):
            filename = f"fire_detection_{frame_count}.jpg"
            cv2.imwrite(filename, display)
            print(f"📸 Saved: {filename}")
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Summary
    print(f"\n📊 Session Summary:")
    print(f"   Frames processed: {frame_count}")
    print(f"   Frames with detections: {detection_frames}")
    print(f"   Detection rate: {100*detection_frames/max(1,frame_count):.1f}%")


if __name__ == "__main__":
    main()

