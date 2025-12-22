# 📅 Development Phases - FireSwarm MVP

**Last Updated:** December 22, 2025  
**Total Timeline:** 10 weeks to field-ready MVP

---

## Overview

```
Week 1-2:  Phase 1 - Single Drone Proof
Week 3-4:  Phase 2 - Fire Detection
Week 5-6:  Phase 3 - Multi-Drone
Week 7-8:  Phase 4 - LoRa Resilience
Week 9-10: Phase 5 - Polish & Field Ready
```

---

## Phase 1: Single Drone Proof (Week 1-2)

### Goals
- ✅ Thermal camera streaming to ground station
- ✅ Basic UI showing one thermal feed
- ✅ MAVLink telemetry on map

### Deliverables
```
├── Thermal camera → Pi 5 → WebRTC stream working
├── Basic React frontend showing one thermal feed
├── MAVLink telemetry displayed on map
└── DELIVERABLE: One drone streaming thermal video
```

### Tasks

| Task | Owner | Status |
|------|-------|--------|
| Set up Pi 5 with camera driver | - | ☐ |
| Configure MediaMTX for WebRTC | - | ☐ |
| Create basic React app with video player | - | ☐ |
| Integrate Leaflet map | - | ☐ |
| Connect MAVLink telemetry to map | - | ☐ |
| Test end-to-end latency | - | ☐ |

### Technical Details

#### Thermal Camera Setup (InfiRay P2 Pro) ⭐

**P2 Pro Specs:**
- Resolution: 256×192 @ 25Hz
- Temperature: -20°C to 550°C
- Weight: 9.5g
- Power: 350mW

```bash
# Clone P2Pro-Viewer
git clone https://github.com/LeoDJ/P2Pro-Viewer.git
cd P2Pro-Viewer

# Install dependencies
pip install opencv-python numpy

# For Linux/Pi: Install libusb
sudo apt install libusb-1.0-0-dev

# Connect P2 Pro via USB-C and test
python p2pro_viewer.py
```

#### Temperature Extraction (P2 Pro)
```python
# From P2Pro-Viewer - radiometric temperature conversion
def raw_to_celsius(raw_value):
    """Convert P2 Pro raw value to Celsius"""
    temperature = (raw_value * 0.0625) - 273.15
    return temperature

# Fire detection threshold
FIRE_THRESHOLD = 80  # Celsius
if max_temp > FIRE_THRESHOLD:
    trigger_fire_alert(lat, lon, max_temp)
```

#### MediaMTX Configuration
```yaml
# mediamtx.yml
paths:
  thermal:
    source: rtsp://localhost:8554/thermal
    sourceOnDemand: yes
  
webrtcServerAddr: :8889
```

### Success Criteria
- [ ] Thermal video displays in browser with <500ms latency
- [ ] Drone position shows on map in real-time
- [ ] Temperature overlay visible on thermal feed

---

## Phase 2: Fire Detection (Week 3-4)

### Goals
- ✅ AI fire detection on thermal stream
- ✅ Bounding box overlay
- ✅ Basic alert system

### Deliverables
```
├── YOLOv8-nano fire detection model
├── Bounding box overlay on thermal stream
├── Basic alert system (on-screen + sound)
└── DELIVERABLE: Automatic fire detection with alerts
```

### Tasks

| Task | Owner | Status |
|------|-------|--------|
| Train/acquire fire detection model | - | ☐ |
| Optimize model for Pi 5 (quantization) | - | ☐ |
| Integrate inference into pipeline | - | ☐ |
| Add bounding box overlay | - | ☐ |
| Create alert component in UI | - | ☐ |
| Add audio alert | - | ☐ |

### Technical Details

#### YOLOv8 on Pi 5 Optimization
```python
from ultralytics import YOLO

# Load nano model for speed
model = YOLO('yolov8n-fire.pt')

# Export to NCNN for Pi 5 optimization
model.export(format='ncnn', half=True)

# Inference every 5th frame for performance
frame_count = 0
for frame in video_stream:
    frame_count += 1
    if frame_count % 5 == 0:
        results = model(frame, conf=0.5)
        # Draw bounding boxes...
```

#### Alert System
```python
# alerts.py
import asyncio
from datetime import datetime

class FireAlert:
    def __init__(self, drone_id, lat, lon, temp, confidence, frame):
        self.drone_id = drone_id
        self.lat = lat
        self.lon = lon
        self.temp = temp
        self.confidence = confidence
        self.frame = frame
        self.timestamp = datetime.now()
        self.status = "pending"  # pending, confirmed, dismissed
    
    def confirm(self):
        self.status = "confirmed"
        # Trigger escalation workflow
    
    def dismiss(self):
        self.status = "dismissed"
        # Log as false positive for training
```

### Success Criteria
- [ ] Fire detection runs at 10+ FPS on Pi 5
- [ ] Bounding boxes appear on fire/hotspots
- [ ] Alert appears within 2 seconds of detection
- [ ] False positive rate < 20% on test videos

---

## Phase 3: Multi-Drone (Week 5-6)

### Goals
- ✅ Scale to 5 drones
- ✅ Video matrix UI
- ✅ Swarm status dashboard

### Deliverables
```
├── Scale architecture to 5 drones
├── Video matrix UI (5 simultaneous feeds)
├── Swarm status dashboard
└── DELIVERABLE: 5 simultaneous thermal feeds
```

### Tasks

| Task | Owner | Status |
|------|-------|--------|
| Set up 5 drone instances (SITL) | - | ☐ |
| Configure MediaMTX for 5 streams | - | ☐ |
| Create video matrix component | - | ☐ |
| Add swarm status panel | - | ☐ |
| Implement fleet commands | - | ☐ |
| Test with 5 simultaneous streams | - | ☐ |

### Technical Details

#### Multi-Stream MediaMTX
```yaml
# mediamtx.yml
paths:
  drone1:
    source: rtsp://drone1.local:8554/thermal
  drone2:
    source: rtsp://drone2.local:8554/thermal
  drone3:
    source: rtsp://drone3.local:8554/thermal
  drone4:
    source: rtsp://drone4.local:8554/thermal
  drone5:
    source: rtsp://drone5.local:8554/thermal
```

#### Video Matrix React Component
```jsx
// VideoMatrix.jsx
const VideoMatrix = ({ drones }) => {
  return (
    <div className="video-matrix">
      {drones.map(drone => (
        <VideoTile
          key={drone.id}
          droneId={drone.id}
          streamUrl={`/webrtc/${drone.id}`}
          battery={drone.battery}
          hasAlert={drone.hasFireAlert}
          onClick={() => selectDrone(drone.id)}
        />
      ))}
    </div>
  );
};
```

### Success Criteria
- [ ] All 5 video feeds display simultaneously
- [ ] Each drone shows status (battery, signal, mode)
- [ ] Fleet commands work (RTH All, Pause All)
- [ ] UI responsive with 5 active streams

---

## Phase 4: LoRa Resilience (Week 7-8)

### Goals
- ✅ Meshtastic integration
- ✅ Automatic failover (4G → LoRa)
- ✅ Offline telemetry

### Deliverables
```
├── Meshtastic integration
├── Failover logic (4G→LoRa)
├── Offline telemetry caching
└── DELIVERABLE: Works when cellular fails
```

### Tasks

| Task | Owner | Status |
|------|-------|--------|
| Configure Meshtastic devices | - | ☐ |
| Create meshtastic_bridge.py | - | ☐ |
| Implement failover detection | - | ☐ |
| Add telemetry caching | - | ☐ |
| Create mesh status UI | - | ☐ |
| Test with 4G disabled | - | ☐ |

### Technical Details

#### Meshtastic Bridge
```python
# meshtastic_bridge.py
import meshtastic
import meshtastic.serial_interface

class MeshtasticBridge:
    def __init__(self, port='/dev/ttyUSB0'):
        self.interface = meshtastic.serial_interface.SerialInterface(port)
        self.interface.on_receive = self.on_receive
    
    def on_receive(self, packet, interface):
        if packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            # Parse telemetry from text message
            data = packet['decoded']['text']
            self.process_telemetry(data)
    
    def send_command(self, drone_id, command):
        msg = f"CMD:{drone_id}:{command}"
        self.interface.sendText(msg)
```

#### Failover Logic
```python
# connectivity.py
class ConnectivityManager:
    def __init__(self):
        self.primary = "4G"
        self.backup = "LoRa"
        self.last_4g_success = time.time()
        self.failover_timeout = 10  # seconds
    
    def check_connection(self):
        if self.test_4g():
            self.last_4g_success = time.time()
            return "4G"
        
        if time.time() - self.last_4g_success > self.failover_timeout:
            return "LoRa"
        
        return "4G"  # Still trying 4G
    
    def send(self, data):
        conn = self.check_connection()
        if conn == "4G":
            self.send_4g(data)
        else:
            self.send_lora(data)
```

### Success Criteria
- [ ] Telemetry continues when 4G disconnected
- [ ] Failover happens within 10 seconds
- [ ] LoRa range tested to 1+ km
- [ ] Mesh status visible in UI

---

## Phase 5: Polish (Week 9-10)

### Goals
- ✅ Mission planning (patrol polygon)
- ✅ Alert workflow (verify, escalate)
- ✅ Reporting (fire logs, patrol history)

### Deliverables
```
├── Mission planning (patrol polygon)
├── Alert workflow (verify, escalate)
├── Reporting (fire logs, patrol history)
└── DELIVERABLE: Field-ready MVP
```

### Tasks

| Task | Owner | Status |
|------|-------|--------|
| Create patrol polygon drawing UI | - | ☐ |
| Implement mission execution | - | ☐ |
| Build alert workflow UI | - | ☐ |
| Add fire log database | - | ☐ |
| Create reports page | - | ☐ |
| Field testing | - | ☐ |

### Technical Details

#### Alert Workflow UI
```jsx
// AlertPanel.jsx
const AlertPanel = ({ alert }) => {
  return (
    <div className="alert-panel alert-fire">
      <h3>🔥 FIRE DETECTED</h3>
      <p>Drone: {alert.droneId}</p>
      <p>Location: {alert.lat.toFixed(5)}, {alert.lon.toFixed(5)}</p>
      <p>Temperature: {alert.temp}°C</p>
      <p>Confidence: {alert.confidence}%</p>
      
      <img src={alert.thermalSnapshot} alt="Thermal" />
      
      <div className="alert-actions">
        <button className="confirm" onClick={() => confirmFire(alert)}>
          ✅ Confirm Fire
        </button>
        <button className="dismiss" onClick={() => dismissAlert(alert)}>
          ❌ False Positive
        </button>
        <button className="investigate" onClick={() => sendDrone(alert)}>
          🚁 Send Drone to Verify
        </button>
      </div>
    </div>
  );
};
```

### Success Criteria
- [ ] Can draw patrol area on map
- [ ] Drones execute patrol mission
- [ ] Alert workflow functional
- [ ] Fire logs saved to database
- [ ] System tested in field conditions

---

## Hardware Required by Phase

| Phase | Hardware Needed | Est. Cost |
|-------|-----------------|-----------|
| Phase 1 | 1× Pi 5, 1× InfiRay P2 Pro, 1× Drone (SITL OK) | ~$455 |
| Phase 2 | Same as Phase 1 | - |
| Phase 3 | 5× Pi 5, 5× InfiRay P2 Pro, 5× Drones (SITL OK) | ~$2,275 |
| Phase 4 | Add: 6× Meshtastic (5× Heltec V3 + 1× RAK WisBlock) | ~$185 |
| Phase 5 | Full drone hardware (see HARDWARE_BOM.md) | ~$6,775 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Camera driver issues | Test both TopDon and InfiRay early |
| YOLO too slow on Pi 5 | Use YOLOv8-nano, skip frames, or offload |
| WebRTC latency high | Use go2rtc or direct RTSP fallback |
| LoRa range insufficient | Use RAK WisBlock with directional antenna |
| 5 streams overload browser | Reduce resolution, use HLS fallback |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Video latency | < 500ms |
| Fire detection accuracy | > 80% |
| False positive rate | < 20% |
| LoRa failover time | < 10s |
| Battery flight time | 60 min |
| Simultaneous streams | 5 |

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2025
