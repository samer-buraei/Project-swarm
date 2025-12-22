# 📷 InfiRay P2 Pro Integration Guide

**Last Updated:** December 22, 2025  
**Status:** Primary thermal camera for FireSwarm

---

## Overview

The **InfiRay P2 Pro** is the selected thermal camera for the FireSwarm drone fire detection system. This guide covers integration with Raspberry Pi 5 for fire detection.

---

## Specifications

| Spec | Value |
|------|-------|
| **Resolution** | 256 × 192 pixels |
| **Frame Rate** | 25 Hz |
| **Temperature Range** | -20°C to 550°C |
| **Accuracy** | ±2°C or ±2% of reading |
| **Field of View** | 56.0° × 42.2° |
| **Weight** | **9.5g** (ultra-light for drones) |
| **Power Consumption** | 350mW |
| **Interface** | USB Type-C (UVC compatible) |
| **Radiometric** | ✅ Yes - outputs raw temperature data |

---

## Why P2 Pro for Fire Detection

1. **Temperature Range (550°C max)** - Covers all fire scenarios
2. **Radiometric Output** - Get actual temperature values, not just images
3. **25Hz Frame Rate** - Smooth real-time detection
4. **9.5g Weight** - Negligible impact on drone flight time
5. **350mW Power** - Minimal battery drain
6. **Open Source Drivers** - P2Pro-Viewer available

---

## Driver Options

| Driver | Language | Platform | Link |
|--------|----------|----------|------|
| **P2Pro-Viewer** ⭐ | Python | Win/Linux/Pi | [github.com/LeoDJ/P2Pro-Viewer](https://github.com/LeoDJ/P2Pro-Viewer) |
| P2Pro-Viewer-Gui | Python | Win/Linux | [github.com/crexodon/P2Pro-Viewer-Gui](https://github.com/crexodon/P2Pro-Viewer-Gui) |
| thermal-cat | Rust | Win/Linux | [github.com/alufers/thermal-cat](https://github.com/alufers/thermal-cat) |
| Minimal Python | Python | Any | [gist.github.com/ks00x](https://gist.github.com/ks00x/9003fc0e1103bb2a4ecc690ab855633e) |

---

## Installation on Raspberry Pi 5

### 1. System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-opencv libusb-1.0-0-dev git

# Install Python packages
pip install opencv-python numpy
```

### 2. Clone P2Pro-Viewer

```bash
git clone https://github.com/LeoDJ/P2Pro-Viewer.git
cd P2Pro-Viewer
```

### 3. USB Permissions (Linux)

```bash
# Create udev rule for P2 Pro
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="5830", MODE="0666"' | sudo tee /etc/udev/rules.d/99-p2pro.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 4. Test Camera

```bash
# Connect P2 Pro via USB-C
# Run viewer
python p2pro_viewer.py
```

---

## Temperature Conversion

The P2 Pro outputs raw sensor values. Convert to Celsius:

```python
def raw_to_celsius(raw_value):
    """
    Convert P2 Pro raw value to Celsius temperature.
    
    Formula derived from P2Pro-Viewer reverse engineering:
    T(°C) = (raw_value * 0.0625) - 273.15
    
    Args:
        raw_value: 16-bit raw sensor value
        
    Returns:
        Temperature in Celsius
    """
    temperature = (raw_value * 0.0625) - 273.15
    return temperature
```

### Example Usage

```python
import numpy as np

# Assuming raw_frame is 256x192 uint16 array from P2 Pro
def get_temperature_frame(raw_frame):
    """Convert entire frame to Celsius temperatures"""
    temp_frame = (raw_frame.astype(np.float32) * 0.0625) - 273.15
    return temp_frame

def get_max_temperature(raw_frame):
    """Get maximum temperature in frame"""
    temp_frame = get_temperature_frame(raw_frame)
    return np.max(temp_frame)

def get_hotspot_location(raw_frame):
    """Get location of maximum temperature"""
    temp_frame = get_temperature_frame(raw_frame)
    max_idx = np.unravel_index(np.argmax(temp_frame), temp_frame.shape)
    return max_idx  # (row, col)
```

---

## Fire Detection Integration

### Basic Fire Detection Loop

```python
import cv2
import numpy as np
from p2pro import P2ProCamera  # From P2Pro-Viewer

# Configuration
FIRE_THRESHOLD = 80  # Celsius
CONFIDENCE_THRESHOLD = 0.7
ALERT_COOLDOWN = 5  # seconds between alerts

class FireDetector:
    def __init__(self):
        self.camera = P2ProCamera()
        self.last_alert_time = 0
        
    def raw_to_celsius(self, raw_value):
        return (raw_value * 0.0625) - 273.15
    
    def detect_fire(self, raw_frame):
        """
        Detect fire in thermal frame.
        
        Returns:
            dict with fire detection results or None
        """
        # Convert to temperature
        temp_frame = self.raw_to_celsius(raw_frame.astype(np.float32))
        
        # Find maximum temperature
        max_temp = np.max(temp_frame)
        
        # Check threshold
        if max_temp > FIRE_THRESHOLD:
            # Get hotspot location
            max_idx = np.unravel_index(np.argmax(temp_frame), temp_frame.shape)
            
            return {
                'detected': True,
                'max_temp': max_temp,
                'location': max_idx,
                'timestamp': time.time()
            }
        
        return {'detected': False, 'max_temp': max_temp}
    
    def run(self):
        """Main detection loop"""
        while True:
            # Read frame from P2 Pro
            raw_frame = self.camera.read_frame()
            
            # Detect fire
            result = self.detect_fire(raw_frame)
            
            if result['detected']:
                # Check cooldown
                if time.time() - self.last_alert_time > ALERT_COOLDOWN:
                    self.trigger_alert(result)
                    self.last_alert_time = time.time()
            
            # Small delay (camera is 25Hz, so ~40ms between frames)
            time.sleep(0.04)
    
    def trigger_alert(self, result):
        """Send fire alert to ground station"""
        print(f"🔥 FIRE DETECTED! Temp: {result['max_temp']:.1f}°C")
        # Send via 4G or LoRa...
```

---

## Integration with YOLO

For combined thermal + AI fire detection:

```python
from ultralytics import YOLO
import cv2
import numpy as np

class FireDetectorYOLO:
    def __init__(self, model_path='yolov8n-fire.pt'):
        self.yolo = YOLO(model_path)
        self.camera = P2ProCamera()
        
    def detect(self, raw_frame):
        # Convert to temperature
        temp_frame = self.raw_to_celsius(raw_frame.astype(np.float32))
        max_temp = np.max(temp_frame)
        
        # Normalize for YOLO (0-255 grayscale)
        visual_frame = self.temp_to_visual(temp_frame)
        
        # Run YOLO inference
        results = self.yolo(visual_frame, conf=0.5)
        
        # Combine temperature + YOLO confidence
        fire_detected = False
        for r in results:
            for box in r.boxes:
                confidence = box.conf.item()
                # Fire if YOLO confident AND temperature high
                if confidence > 0.7 and max_temp > 80:
                    fire_detected = True
                    break
        
        return {
            'detected': fire_detected,
            'max_temp': max_temp,
            'yolo_results': results
        }
    
    def temp_to_visual(self, temp_frame):
        """Convert temperature frame to visual image for YOLO"""
        # Normalize to 0-255
        min_temp = -20
        max_temp = 550
        normalized = (temp_frame - min_temp) / (max_temp - min_temp)
        normalized = np.clip(normalized, 0, 1)
        visual = (normalized * 255).astype(np.uint8)
        
        # Convert to 3-channel for YOLO
        visual_rgb = cv2.cvtColor(visual, cv2.COLOR_GRAY2RGB)
        return visual_rgb
```

---

## Video Streaming (MediaMTX)

Stream thermal video to ground station:

```python
import subprocess
import cv2

class ThermalStreamer:
    def __init__(self, rtsp_url='rtsp://localhost:8554/thermal'):
        self.rtsp_url = rtsp_url
        self.camera = P2ProCamera()
        
        # Start FFmpeg process
        self.ffmpeg = subprocess.Popen([
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'gray16le',
            '-s', '256x192',
            '-r', '25',
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-f', 'rtsp',
            self.rtsp_url
        ], stdin=subprocess.PIPE)
    
    def stream(self):
        while True:
            raw_frame = self.camera.read_frame()
            self.ffmpeg.stdin.write(raw_frame.tobytes())
```

---

## Troubleshooting

### Camera Not Detected

```bash
# Check USB devices
lsusb | grep -i infiray

# Check video devices
ls -la /dev/video*

# Try different USB port
# Try USB 2.0 instead of 3.0 if issues
```

### Permission Denied

```bash
# Add user to video group
sudo usermod -a -G video $USER

# Re-login or reboot
```

### Frame Rate Low

```bash
# Check CPU usage
htop

# Ensure P2 Pro is on USB 3.0 port
# Check for thermal throttling on Pi 5
vcgencmd measure_temp
```

### Temperature Readings Wrong

- Verify conversion formula
- Check for firmware updates
- Ensure radiometric mode is enabled (not visual-only mode)

---

## Resources

| Resource | Link |
|----------|------|
| P2Pro-Viewer | [github.com/LeoDJ/P2Pro-Viewer](https://github.com/LeoDJ/P2Pro-Viewer) |
| P2Pro-Viewer-Gui | [github.com/crexodon/P2Pro-Viewer-Gui](https://github.com/crexodon/P2Pro-Viewer-Gui) |
| thermal-cat | [github.com/alufers/thermal-cat](https://github.com/alufers/thermal-cat) |
| Minimal Python Gist | [gist.github.com/ks00x](https://gist.github.com/ks00x/9003fc0e1103bb2a4ecc690ab855633e) |
| InfiRay Official | [infiray.com](https://www.infiray.com) |

---

## Verified DIY Projects Using P2 Pro

1. **ThermalDrone** - Similar concept with FLIR Lepton, adaptable for P2 Pro
   - [github.com/jacobfeldgoise/ThermalDrone](https://github.com/jacobfeldgoise/ThermalDrone)

2. **FLAME Dataset Research** - Aerial thermal fire detection
   - [arxiv.org/abs/2012.14036](https://arxiv.org/abs/2012.14036)

3. **FlameFinder Framework** - Deep learning for thermal fire detection
   - [arxiv.org/abs/2404.06653](https://arxiv.org/abs/2404.06653)

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2025
