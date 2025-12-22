# 📡 CONNECTIVITY ARCHITECTURE

**Last Updated:** December 22, 2025  
**Status:** Finalized for Phase 1 Implementation

---

## Overview

The Fire Swarm system uses a **hybrid connectivity approach**:
- **Primary:** 4G/LTE cellular for video streaming and real-time telemetry
- **Backup:** LoRa mesh for offline operation when cellular is unavailable

```
┌─────────────────────────────────────────────────────────────────┐
│  CONNECTIVITY PRIORITY                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 4G/LTE (Primary)     ──► Video + Telemetry + Commands      │
│     │                                                           │
│     ▼ (if unavailable)                                          │
│  2. LoRa (Backup)        ──► Text alerts + GPS + Basic status  │
│     │                                                           │
│     ▼ (if both fail)                                            │
│  3. Auto-RTL             ──► Drone returns to launch point      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. PRIMARY: 4G/LTE Cellular

### Hardware

| Component | Model | Price | Vendor |
|-----------|-------|-------|--------|
| **Modem** | Sixfab 4G/LTE Cellular Modem Kit | $100 | [sixfab.com](https://sixfab.com/product/raspberry-pi-4g-lte-modem-kit/) |
| Alternative | Waveshare SIM7600 4G HAT | $60 | Amazon |
| **SIM Card** | Global IoT SIM (included with Sixfab) | - | Sixfab |
| **Antenna** | 4G LTE Antenna (included) | - | Sixfab |

### Sixfab Kit Contents
- Raspberry Pi HAT with Quectel modem
- Global IoT SIM card (works in 100+ countries)
- 4G LTE antennas (2x for MIMO)
- USB power cable
- Setup guide

### Data Usage Estimates

| Data Type | Size/Second | Per Hour | Per Day (8h) |
|-----------|-------------|----------|--------------|
| Thermal video (480p) | ~50 KB/s | 180 MB | 1.4 GB |
| RGB video (720p) | ~200 KB/s | 720 MB | 5.8 GB |
| Telemetry only | ~1 KB/s | 3.6 MB | 29 MB |
| **Recommended Plan** | | | **10 GB/month/drone** |

### Configuration

```python
# /etc/network/interfaces.d/wwan0
auto wwan0
iface wwan0 inet dhcp
    pre-up /usr/bin/qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode=online
    pre-up /usr/bin/qmicli -d /dev/cdc-wdm0 --wds-start-network="apn='iot.1nce.net'" --client-no-release-cid
```

### Failover Logic

```python
# connectivity_manager.py
import subprocess
import time

class ConnectivityManager:
    def __init__(self):
        self.primary = "4G"
        self.backup = "LoRa"
        self.current = self.primary
    
    def check_4g_status(self):
        """Ping test to check 4G connectivity"""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def get_connection(self):
        """Return best available connection"""
        if self.check_4g_status():
            self.current = "4G"
            return "4G"
        else:
            self.current = "LoRa"
            return "LoRa"
    
    def send_alert(self, lat, lon, temp, confidence):
        """Send fire alert via best available channel"""
        conn = self.get_connection()
        
        if conn == "4G":
            # Full data via 4G
            return self.send_4g_alert(lat, lon, temp, confidence, include_video=True)
        else:
            # Text-only via LoRa
            return self.send_lora_alert(lat, lon, temp)
```

---

## 2. BACKUP: LoRa Mesh

### Hardware

| Component | Model | Price | Vendor |
|-----------|-------|-------|--------|
| **Drone Module** | Heltec ESP32 + LoRa V3 | $25 | AliExpress |
| **Ground Module** | Heltec ESP32 + LoRa V3 | $25 | AliExpress |
| **Antenna** | 868MHz 5dBi SMA | $10 | AliExpress |

### Specifications

| Parameter | Value |
|-----------|-------|
| Frequency | 868 MHz (EU) / 915 MHz (US) |
| Range (open field) | 20 km |
| Range (forest) | 5-10 km |
| Bandwidth | 5 kbps max |
| Message size | 25 bytes max |
| Latency | <200 ms |

### Message Protocol

```python
# LoRa Message Format (21 bytes)
# "FIRE 44.12345 21.54321 245"
#  ^^^^ ^^^^^^^^ ^^^^^^^^ ^^^
#  Type Latitude Longitude Temp(°C)

def encode_alert(lat: float, lon: float, temp: int) -> bytes:
    """Encode fire alert for LoRa transmission"""
    msg = f"FIRE {lat:.5f} {lon:.5f} {temp}"
    return msg.encode('utf-8')[:25]  # Max 25 bytes

def decode_alert(data: bytes) -> dict:
    """Decode received LoRa alert"""
    msg = data.decode('utf-8').strip()
    parts = msg.split()
    return {
        "type": parts[0],
        "lat": float(parts[1]),
        "lon": float(parts[2]),
        "temp": int(parts[3])
    }
```

### Arduino Code (Heltec ESP32)

```cpp
// drone_lora.ino
#include <LoRa.h>

#define LORA_BAND 868E6  // EU frequency
#define LORA_SYNC 0x34   // Private sync word

void setup() {
    Serial.begin(115200);
    LoRa.begin(LORA_BAND);
    LoRa.setSyncWord(LORA_SYNC);
    LoRa.setSpreadingFactor(10);  // Long range
    LoRa.setSignalBandwidth(125E3);
}

void sendFireAlert(float lat, float lon, int temp) {
    char msg[26];
    snprintf(msg, 26, "FIRE %.5f %.5f %d", lat, lon, temp);
    
    LoRa.beginPacket();
    LoRa.print(msg);
    LoRa.endPacket();
}

void loop() {
    // Listen for commands from ground station
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
        String cmd = "";
        while (LoRa.available()) {
            cmd += (char)LoRa.read();
        }
        processCommand(cmd);
    }
}
```

---

## 3. FAILSAFE: Auto-RTL

If both 4G and LoRa fail for more than 60 seconds:

```python
# failsafe.py
import time
from pymavlink import mavutil

class Failsafe:
    def __init__(self, vehicle, timeout=60):
        self.vehicle = vehicle
        self.timeout = timeout
        self.last_contact = time.time()
    
    def heartbeat_received(self):
        """Called when any communication received"""
        self.last_contact = time.time()
    
    def check(self):
        """Check if failsafe should trigger"""
        elapsed = time.time() - self.last_contact
        
        if elapsed > self.timeout:
            print(f"⚠️ No contact for {elapsed}s - Triggering RTL")
            self.trigger_rtl()
    
    def trigger_rtl(self):
        """Command drone to return to launch"""
        self.vehicle.mav.set_mode_send(
            self.vehicle.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            6  # RTL mode
        )
```

---

## 4. GROUND STATION SETUP

### Hardware

| Component | Purpose | Notes |
|-----------|---------|-------|
| Laptop | Dashboard + control | Any modern laptop |
| Heltec ESP32 | LoRa receiver | USB connected |
| 4G Router (optional) | Backup internet | If laptop has no SIM |
| External antenna | Extended LoRa range | Roof-mounted for van |

### Software Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  GROUND STATION                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   4G/LTE     │     │  Streamlit   │     │   SQLite     │   │
│  │  Receiver    │────▶│  Dashboard   │────▶│  Database    │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│         │                    │                    │            │
│         │                    ▼                    │            │
│  ┌──────────────┐     ┌──────────────┐           │            │
│  │    LoRa      │     │   Operator   │           │            │
│  │  Receiver    │────▶│   Alerts     │◀──────────┘            │
│  └──────────────┘     └──────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Dashboard Integration

```python
# dashboard_connectivity.py
import streamlit as st
from connectivity_manager import ConnectivityManager

def render_connectivity_status(drones):
    st.header("📡 Connectivity Status")
    
    cols = st.columns(5)
    for i, drone in enumerate(drones):
        with cols[i]:
            conn = drone.connectivity.current
            if conn == "4G":
                st.success(f"D{i+1}: 4G 📶")
            elif conn == "LoRa":
                st.warning(f"D{i+1}: LoRa 📻")
            else:
                st.error(f"D{i+1}: OFFLINE ❌")
```

---

## 5. DATA FLOW DIAGRAM

```
                    ┌─────────────────────────────────────────────┐
                    │              DRONE                          │
                    │  ┌─────────┐    ┌─────────┐    ┌─────────┐ │
                    │  │ P2 Pro  │───▶│P2Pro-   │───▶│  YOLO   │ │
                    │  │ Thermal │    │Viewer   │    │ on Pi 5 │ │
                    │  │ 256×192 │    │(Python) │    │         │ │
                    │  └─────────┘    └────┬────┘    └────┬────┘ │
                    │                      │              │      │
                    │              Temp>80°C?      Confidence?   │
                    │                      │              │      │
                    │                      ▼              ▼      │
                    │                   ┌────────────────────┐   │
                    │                   │   Fire Alert?      │   │
                    │                   │   Temp>80 AND      │   │
                    │                   │   Conf>0.7         │   │
                    │                   └─────────┬──────────┘   │
                    │                             │              │
                    │                             ▼              │
                    │                      ┌────────────┐        │
                    │                      │ Conn Mgr   │        │
                    │                      └─────┬──────┘        │
                    └────────────────────────────┼───────────────┘
                                                         │
                    ┌────────────────────────────────────┼───────┐
                    │                                    │       │
              4G Available?                        4G Unavailable
                    │                                    │       │
                    ▼                                    ▼       │
           ┌──────────────┐                     ┌──────────────┐ │
           │   4G/LTE     │                     │    LoRa      │ │
           │   Modem      │                     │   Module     │ │
           └──────┬───────┘                     └──────┬───────┘ │
                  │                                    │         │
                  │ Video + Telemetry                  │ Text    │
                  │ + Full Data                        │ Alert   │
                  │                                    │         │
                  ▼                                    ▼         │
           ┌─────────────────────────────────────────────────────┤
           │                 GROUND STATION                      │
           │  ┌───────────┐          ┌───────────┐               │
           │  │   4G RX   │          │  LoRa RX  │               │
           │  └─────┬─────┘          └─────┬─────┘               │
           │        │                      │                     │
           │        └──────────┬───────────┘                     │
           │                   │                                 │
           │                   ▼                                 │
           │            ┌────────────┐                           │
           │            │ Dashboard  │                           │
           │            │ + Alerts   │                           │
           │            └─────┬──────┘                           │
           │                  │                                  │
           │                  ▼                                  │
           │            ┌────────────┐                           │
           │            │  Operator  │                           │
           │            │  Decision  │                           │
           │            └────────────┘                           │
           └─────────────────────────────────────────────────────┘
```

---

## 6. COST SUMMARY

### Per Drone

| Component | Cost |
|-----------|------|
| Sixfab 4G/LTE Kit | $100 |
| Heltec LoRa Module | $25 |
| Antennas | $15 |
| **Total** | **$140** |

### Ground Station

| Component | Cost |
|-----------|------|
| Heltec LoRa Module | $25 |
| External Antenna | $20 |
| **Total** | **$45** |

### Monthly Operating Costs

| Service | Cost/Month |
|---------|------------|
| IoT Data Plan (10GB/drone) | ~$10-20/drone |
| 5 Drones × $15 average | ~$75/month |

---

## 7. IMPLEMENTATION PHASES

### Phase 1: 4G/LTE Primary
1. ✅ Order Sixfab kits
2. Configure Pi 5 with cellular modem
3. Test video streaming latency
4. Implement failover to LoRa

### Phase 2: LoRa Backup
1. ✅ Configure Heltec modules
2. Test 1km range (desk)
3. Test 5km range (field)
4. Integrate with dashboard

### Phase 3: Mesh Networking (Future)
1. Multi-hop LoRa for extended range
2. Meshtastic integration
3. Drone-to-drone relay

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2025
