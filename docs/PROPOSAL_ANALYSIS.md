# 🔍 FireSwarm Proposal Analysis

**Last Updated:** December 22, 2025  
**Status:** Reference Document for Architecture Decisions

---

## Quick Verdict

| Aspect | Proposal 1 | Proposal 2 | Our Spec |
|--------|------------|------------|----------|
| Thermal Camera | TopDon TC001 | TopDon TC001 | **InfiRay P2 Pro** ⭐ |
| Drone Count | ✅ 5 drones | ✅ 5 drones | 5 drones |
| LoRa/Meshtastic | ✅ Yes | ✅ Yes | ✅ Required |
| Companion Computer | ✅ Raspberry Pi 5 | ✅ Raspberry Pi 5 | ✅ Pi 5 |
| Video Transport | ✅ WebRTC | ✅ WebRTC/MediaMTX | WebRTC via MediaMTX |
| UI Philosophy | Tactical Matrix | Gamified Dashboard | Hybrid (see below) |
| Failover Logic | ✅ 4G→LoRa | ✅ 4G→LoRa | ✅ Required |

**Bottom Line:** Both proposals are ~80% aligned. Camera decided: **InfiRay P2 Pro**.

---

## 1. Hardware Analysis

### Thermal Camera: InfiRay P2 Pro ⭐ SELECTED

| Feature | InfiRay P2 Pro |
|---------|----------------|
| **Resolution** | 256×192 |
| **Frame Rate** | 25 Hz |
| **Temp Range** | -20°C to 550°C |
| **Accuracy** | ±2°C or ±2% |
| **Weight** | **9.5g** (ultra-light!) |
| **Power** | 350mW |
| **Interface** | USB-C (UVC) |
| **Radiometric** | ✅ Yes (raw temperature data) |
| **Price** | ~$350 |

#### Why P2 Pro Was Selected

1. **Ultra-lightweight (9.5g)** - Negligible impact on drone flight time
2. **25Hz frame rate** - Smooth real-time fire detection
3. **Radiometric output** - Actual temperature values, not just images
4. **550°C max range** - Covers all fire scenarios
5. **Open source drivers** - P2Pro-Viewer, thermal-cat available
6. **Low power (350mW)** - Minimal battery impact

#### Software Pipeline

```
InfiRay P2 Pro Pipeline:
  Camera → USB-C → Pi 5 → P2Pro-Viewer (Python) → OpenCV → YOLO → WebRTC
                              ↓
                    Temperature extraction → Fire alert if >80°C
```

#### Driver Resources

| Driver | Language | Link |
|--------|----------|------|
| **P2Pro-Viewer** ⭐ | Python | [github.com/LeoDJ/P2Pro-Viewer](https://github.com/LeoDJ/P2Pro-Viewer) |
| thermal-cat | Rust | [github.com/alufers/thermal-cat](https://github.com/alufers/thermal-cat) |
| Minimal gist | Python | [gist.github.com/ks00x](https://gist.github.com/ks00x/9003fc0e1103bb2a4ecc690ab855633e) |

### Meshtastic Hardware Options

For 5-drone swarm with terrain obstruction:

| Option | Range | Form Factor | Price | Recommendation |
|--------|-------|-------------|-------|----------------|
| **RAK WisBlock** | 15+ km | Modular | ~$60 | ⭐ Ground Station |
| LILYGO T-Beam Supreme | 10+ km | Dev board | ~$45 | Alternative GS |
| **Heltec V3** | 5-8 km | Compact | ~$25 | ⭐ On Drones (weight) |

**Setup:**
- Ground Station: RAK WisBlock with directional antenna
- Drones: Heltec V3 (lighter weight)

### Hardware Match Status

| Component | Proposals | Our Spec | Status |
|-----------|-----------|----------|--------|
| Flight Controller | Matek H743 | Pixhawk 6C / Matek H743 | ✅ Compatible |
| Companion Computer | Raspberry Pi 5 | Raspberry Pi 5 | ✅ Match |
| LoRa Module | Meshtastic T-Beam | Heltec V3 / RAK | ✅ Compatible |
| Cellular | 4G/5G modem | Sixfab 4G/LTE | ✅ Match |

---

## 2. Software Architecture

### Proposal 1 (Simpler) vs Proposal 2 (Complex)

```
PROPOSAL 1 (Recommended for MVP):
┌─────────────────────────────────────────────────────────────┐
│                     GROUND STATION                          │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Browser)                                         │
│  ├── Zone A: Map (Leaflet/Mapbox)                          │
│  └── Zone B: Video Matrix (5 WebRTC streams)               │
├─────────────────────────────────────────────────────────────┤
│  Backend (Python)                                           │
│  ├── meshtastic_bridge.py (LoRa telemetry)                 │
│  └── webrtc_server.py (video aggregation)                  │
└─────────────────────────────────────────────────────────────┘
        │ 4G/5G (Video)          │ LoRa (Telemetry)
        ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                     DRONE (×5)                              │
│  Pi 5 → thermal_driver.py → MediaMTX → 4G                  │
│  Pi 5 → MAVLink → Meshtastic → LoRa                        │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Comparison

| Criterion | Proposal 1 | Proposal 2 | Winner |
|-----------|------------|------------|--------|
| Simplicity | Simpler, fewer parts | More complex | **P1** |
| Scalability | 5 drones fixed | Extensible | P2 |
| Field Reliability | Better (less can break) | More failure points | **P1** |
| Feature Richness | Basic | Click-to-fly, joystick | P2 |
| Dev Time (MVP) | 2-3 weeks | 4-6 weeks | **P1** |

**Recommendation:** Start with Proposal 1's simpler architecture for MVP.

### Software Components

| Component | Proposal Spec | Reality Check | Verdict |
|-----------|---------------|---------------|---------|
| WebRTC Server | MediaMTX / go2rtc | Both work well on Pi 5 | ✅ Good |
| VPN | Tailscale / ZeroTier | Tailscale easier | ✅ Either works |
| MAVLink Router | mavlink-router | Standard, works | ✅ Good |
| Drone Control | MAVSDK-Python | Good for high-level | ⚠️ See below |
| Thermal Processing | PyThermalCamera | Depends on camera | ⚠️ Camera-specific |
| AI Detection | YOLO overlay | Heavy on Pi 5 | ⚠️ Needs optimization |

### MAVSDK vs pymavlink

- **MAVSDK-Python:** Great for simple commands, but laggy for real-time teleoperation
- **pymavlink:** Better for "virtual joystick" with `RC_CHANNELS_OVERRIDE` (<100ms latency)

**Recommendation:** Use MAVSDK for high-level commands, pymavlink for real-time control.

### YOLO on Pi 5 Optimization

Running YOLOv8 on every thermal frame will overload Pi 5:

| Model | FPS on Pi 5 |
|-------|-------------|
| YOLOv8n (nano) | ~15 FPS |
| YOLOv8s (small) | ~5 FPS |

**Solutions:**
1. Use YOLOv8-nano or custom fire-specific model
2. Run inference every Nth frame (e.g., every 5th)
3. Offload to ground station (send compressed frames)

---

## 3. UI/UX Design

### Recommended: Hybrid Approach

Combine the best of both proposals:

```
┌──────────────────────────────────────────────────────────────────┐
│ [Site A ▼] ● D1 ● D2 ● D3 ● D4 ● D5   🔥 ALERTS (0)   [⚙️]     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                                                             │ │
│  │                    PRIMARY VIEW                             │ │
│  │         (Map OR Selected Drone Full-Screen)                 │ │
│  │                                                             │ │
│  │    Mode: [MAP] [GRID] [SINGLE]                             │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐             │
│  │ D1    │ │ D2    │ │ D3 🔥 │ │ D4    │ │ D5    │             │
│  │ 87% ● │ │ 72% ● │ │ 91% ● │ │ 65% ● │ │ 88% ● │             │
│  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘             │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [Draw Patrol] [Start Mission] [RTH All] [Emergency Stop]        │
└──────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Persistent Thumbnail Strip:** Always see all 5 drones
- **Flexible Primary View:** Switch between map, grid, single
- **Click thumbnail to expand:** Don't lose situational awareness
- **Fire indicator on thumbnail:** Immediate visual alert

---

## 4. Missing Features (To Be Implemented)

### 🔥 Fire Detection Workflow

Current proposals only cover "Detection". Full pipeline needed:

```
1. DETECTION: AI spots anomaly (auto)
2. VERIFICATION: Operator confirms (1-click: "Confirm Fire" / "False Positive")
3. ESCALATION: Alert sent to external system (fire department API?)
4. RESPONSE: Log, timestamp, GPS, thermal snapshot saved
```

### 🌡️ Thermal Thresholding UI

```
┌─────────────────────────────────────┐
│ THERMAL ALERTS                      │
│ Warning Threshold: [150°C] ▲▼       │
│ Critical Threshold: [300°C] ▲▼      │
│ Min Detection Area: [2m²] ▲▼        │
└─────────────────────────────────────┘
```

### 📡 Mesh Network Visualization

```
┌─────────────────────────────────────┐
│ MESH STATUS                         │
│ D1 ←→ D2 ←→ D3    Signal: Strong    │
│      ↕     ↕                        │
│     D4 ←→ D5      Hops: 2 max       │
│                   Latency: 1.2s     │
└─────────────────────────────────────┘
```

### 🔋 Swarm Battery Coordination

```
"Drone 3 at 25% - Auto-RTH in 5 min"
"Drone 6 (reserve) launching to cover Zone C"
```

Visual representation of battery vs. remaining patrol time.

---

## 5. Corrected Tech Stack

| Layer | Original Proposals | Final Decision |
|-------|-------------------|----------------|
| **Thermal Camera** | TopDon TC001 | **InfiRay P2 Pro** ⭐ |
| **Thermal Driver** | PyThermalCamera | **P2Pro-Viewer** (Python) |
| Video Server | MediaMTX | MediaMTX ✅ |
| AI Inference | YOLO on Pi 5 | **YOLOv8-nano** or offload to GCS |
| MAVLink | MAVSDK | **pymavlink** for low-latency control |
| LoRa | Meshtastic | Meshtastic ✅ (Heltec V3) |
| VPN | Tailscale | Tailscale ✅ |
| Frontend | React | React ✅ |
| Backend | FastAPI | FastAPI ✅ |

---

## 6. What to Take From Each Proposal

### From Proposal 1
- Dual-zone layout (Map + Matrix)
- Video matrix (see all drones)
- Simple status indicators
- 4G→LoRa failover logic
- Phase 1/2 separation

### From Proposal 2
- FastAPI backend structure
- MAVSDK integration patterns
- Click-to-fly interaction
- Tailscale VPN approach
- React component architecture

---

## 7. Immediate Action Items

1. ☐ Decide on thermal camera (TopDon TC001 vs InfiRay P2 Pro)
2. ☐ Order Meshtastic hardware (Heltec V3 for drones, RAK for GS)
3. ☐ Test thermal driver on Pi 5 with chosen camera
4. ☐ Benchmark YOLOv8-nano inference speed on Pi 5
5. ☐ Set up MediaMTX and verify WebRTC latency
6. ☐ Create basic React app with single video + map

---

**Document Version:** 1.0  
**Source:** Comparative analysis of two contractor proposals  
**Status:** Reference for architecture decisions
