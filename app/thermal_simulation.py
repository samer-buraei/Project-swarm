"""
Thermal Vision Simulation Module
Converts RGB input to simulated thermal imagery for testing

This allows testing the detection pipeline with "thermal-like" input
before the actual InfiRay P2Pro hardware arrives.
"""
import cv2
import numpy as np

class ThermalSimulator:
    """Simulates thermal camera output from RGB input"""
    
    # Thermal colormap options
    COLORMAPS = {
        'white_hot': None,  # Grayscale inverted (white = hot)
        'black_hot': 'gray',  # Grayscale normal (black = hot)
        'inferno': cv2.COLORMAP_INFERNO,  # Orange/yellow thermal
        'jet': cv2.COLORMAP_JET,  # Rainbow thermal
        'hot': cv2.COLORMAP_HOT,  # Black-red-yellow-white
        'iron': cv2.COLORMAP_PINK,  # Iron/metal thermal look
    }
    
    def __init__(self, mode='white_hot'):
        """
        Initialize thermal simulator
        
        Args:
            mode: Colormap mode ('white_hot', 'inferno', 'jet', 'hot', 'iron')
        """
        self.mode = mode
        self.modes = list(self.COLORMAPS.keys())
        
    def convert(self, frame):
        """
        Convert RGB frame to simulated thermal
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            Simulated thermal image
        """
        # Convert to grayscale (luminance approximates heat in some cases)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast to make "hot" areas stand out
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        if self.mode == 'white_hot':
            # Invert: bright areas become white (hot)
            thermal = cv2.bitwise_not(enhanced)
            # Convert back to 3 channels for display
            thermal = cv2.cvtColor(thermal, cv2.COLOR_GRAY2BGR)
            
        elif self.mode == 'black_hot':
            # Normal grayscale: dark = hot
            thermal = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
        else:
            # Apply colormap
            colormap = self.COLORMAPS.get(self.mode, cv2.COLORMAP_INFERNO)
            thermal = cv2.applyColorMap(enhanced, colormap)
            
        return thermal
    
    def next_mode(self):
        """Cycle to next thermal display mode"""
        idx = self.modes.index(self.mode)
        self.mode = self.modes[(idx + 1) % len(self.modes)]
        return self.mode
    
    def detect_heat_regions(self, frame, threshold=200):
        """
        Detect potential heat sources based on brightness
        
        This is a simple heuristic - real thermal cameras
        provide actual temperature data.
        
        Args:
            frame: BGR image
            threshold: Brightness threshold (0-255)
            
        Returns:
            Binary mask of hot regions, contours
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find bright (hot) areas
        _, hot_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours of hot regions
        contours, _ = cv2.findContours(
            hot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        return hot_mask, contours
    
    def overlay_heat_detection(self, frame, min_area=100):
        """
        Overlay heat detection boxes on frame
        
        Args:
            frame: BGR image
            min_area: Minimum contour area to consider
            
        Returns:
            Frame with heat regions highlighted
        """
        result = frame.copy()
        _, contours = self.detect_heat_regions(frame)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(result, f"HEAT", (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return result


def demo_thermal_modes():
    """Demo all thermal simulation modes with webcam"""
    import warnings
    warnings.filterwarnings('ignore')
    
    print("=" * 60)
    print("🌡️ THERMAL SIMULATION DEMO")
    print("=" * 60)
    print("""
Controls:
    M - Cycle through thermal modes
    H - Toggle heat detection overlay
    Q - Quit
    
Modes: white_hot, black_hot, inferno, jet, hot, iron
""")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        return
        
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    simulator = ThermalSimulator(mode='inferno')
    show_heat_detection = False
    
    print(f"✅ Webcam opened. Current mode: {simulator.mode}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert to thermal
        thermal = simulator.convert(frame)
        
        # Optionally overlay heat detection
        if show_heat_detection:
            thermal = simulator.overlay_heat_detection(thermal)
        
        # Add info text
        info = f"Mode: {simulator.mode} | Press M to change, H for heat detect, Q to quit"
        cv2.putText(thermal, info, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show side by side: original and thermal
        combined = np.hstack([frame, thermal])
        cv2.imshow("RGB (left) vs Thermal Simulation (right)", combined)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            new_mode = simulator.next_mode()
            print(f"🔄 Switched to: {new_mode}")
        elif key == ord('h'):
            show_heat_detection = not show_heat_detection
            print(f"🔥 Heat detection: {'ON' if show_heat_detection else 'OFF'}")
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    demo_thermal_modes()

