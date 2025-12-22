# 🛒 HARDWARE BILL OF MATERIALS (BOM)

**Last Updated:** December 22, 2025  
**Version:** 2.0 - Merged & Verified  
**Target:** 60-Minute Flight Time, 4G/LTE + LoRa Connectivity

---

## 📋 COMPLETE DRONE BUILD (Per Unit)

### Cost Summary
| Category | Cost (USD) |
|----------|------------|
| Flight Controller & Frame | ~$310 |
| Power System (60-min) | ~$280 |
| Compute & Vision (Pi 5 + P2 Pro) | ~$455 |
| Connectivity (4G + LoRa) | ~$150 |
| Accessories | ~$90 |
| **TOTAL PER DRONE** | **~$1,285** |

> 💡 **5 Drones Total:** ~$6,425 + ~$350 one-time costs = **~$6,775**

---

## 1. FLIGHT CONTROLLER (ArduPilot Compatible)

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **Pixhawk 6C** ⭐ Recommended | $140.99 | ✅ IN STOCK | Holybro | [holybro.com/products/pixhawk-6c](https://holybro.com/products/pixhawk-6c) |
| Pixhawk 6X (Alternative) | $126.99 | ✅ IN STOCK | Holybro | [holybro.com](https://holybro.com) |
| Matek H743-SLIM V3 (Budget) | ~$80 | ✅ IN STOCK | GetFPV | [getfpv.com](https://www.getfpv.com/mateksys-h743-slim-v3-flight-controller.html) |

**Notes:**
- Pixhawk 6C recommended for full ArduPilot compatibility
- Matek H743-SLIM is lighter but requires more setup
- Must describe as "MATEKSYS H743-SLIM" - do NOT buy clones

---

## 2. COMPANION COMPUTER

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **Raspberry Pi 5 - 8GB** ⭐ | $104.50 | ✅ IN STOCK | Adafruit | [adafruit.com/product/5813](https://www.adafruit.com/product/5813) |
| Raspberry Pi 5 - 4GB | $77.00 | ✅ IN STOCK | Adafruit | [adafruit.com/product/5812](https://www.adafruit.com/product/5812) |
| NVIDIA Jetson Nano (AI) | ~$150 | Variable | NVIDIA | [developer.nvidia.com](https://developer.nvidia.com/embedded/jetson-nano) |

**Notes:**
- Pi 5 8GB recommended for YOLO inference headroom
- Jetson Nano/Xavier for higher FPS AI (15-20 FPS vs 1-2 FPS on Pi)
- Consider Coral USB Accelerator ($60) for Pi 5 if more AI speed needed

---

## 3. THERMAL CAMERA - InfiRay P2 Pro ⭐

> ✅ **PRIMARY CHOICE: InfiRay P2 Pro** - Best SDK, proven for fire detection, ultra-lightweight

| Product | Price | Weight | Vendor | Link |
|---------|-------|--------|--------|------|
| **InfiRay P2 Pro** ⭐ | ~$350 | **9.5g** | AliExpress | [aliexpress.com/infiray-p2-pro](https://www.aliexpress.com/w/wholesale-infiray-p2-pro.html) |
| InfiRay P2 Pro | ~$380 | 9.5g | Amazon | [amazon.com](https://www.amazon.com/s?k=infiray+p2+pro) |

### P2 Pro Specifications (Verified)

| Spec | Value |
|------|-------|
| **Resolution** | 256 × 192 |
| **Frame Rate** | 25 Hz |
| **Temperature Range** | -20°C to 550°C |
| **Accuracy** | ±2°C or ±2% |
| **Field of View** | 56.0° × 42.2° |
| **Weight** | **9.5g** (ultra-light for drones) |
| **Power** | 350mW (minimal battery impact) |
| **Interface** | USB Type-C (UVC compatible) |
| **Radiometric** | ✅ Yes - raw temperature data |

### Why P2 Pro for Fire Detection

1. **Temperature Range (550°C max)** - Covers all fire scenarios
2. **Radiometric Output** - Get actual temperature values, not just images
3. **25Hz Frame Rate** - Smooth real-time detection
4. **9.5g Weight** - Negligible impact on drone flight time
5. **350mW Power** - ~1 hour runtime = only 350mWh consumption
6. **Open Source Drivers** - P2Pro-Viewer, thermal-cat available

### Software Driver Options

| Driver | Language | Platform | Link |
|--------|----------|----------|------|
| **P2Pro-Viewer** ⭐ | Python | Win/Linux/Pi | [github.com/LeoDJ/P2Pro-Viewer](https://github.com/LeoDJ/P2Pro-Viewer) |
| thermal-cat | Rust | Win/Linux | [github.com/alufers/thermal-cat](https://github.com/alufers/thermal-cat) |
| Minimal Python | Python | Any | [gist (ks00x)](https://gist.github.com/ks00x/9003fc0e1103bb2a4ecc690ab855633e) |

### Software Pipeline

```
InfiRay P2 Pro → USB-C → Pi 5 → P2Pro-Viewer → OpenCV → YOLO → WebRTC
                                     ↓
                              Temperature Data → Fire Alert if >80°C
```

### Installation on Raspberry Pi 5

```bash
# Clone P2Pro-Viewer
git clone https://github.com/LeoDJ/P2Pro-Viewer.git
cd P2Pro-Viewer

# Install dependencies
pip install opencv-python numpy

# For Linux/Pi: Install libusb
sudo apt install libusb-1.0-0-dev

# Test camera
python p2pro_viewer.py
```

### Radiometric Temperature Extraction

```python
# From P2Pro-Viewer - temperature conversion formula
def raw_to_celsius(raw_value):
    """Convert P2 Pro raw value to Celsius temperature"""
    temperature = (raw_value * 0.0625) - 273.15
    return temperature

# Fire detection threshold
FIRE_THRESHOLD = 80  # Celsius
if temperature > FIRE_THRESHOLD:
    trigger_alert()
```

### Alternative Camera (Backup)

If P2 Pro is unavailable:

| Product | Price | Resolution | Notes |
|---------|-------|------------|-------|
| TopDon TC001 | $248 | 256×192 | Good availability, Amazon |
| FLIR Lepton 3.5 | $300 | 160×120 | Smaller, needs breakout |

---

## 4. FRAME (10-inch Long Range)

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **GEPRC Mark4 10"** ⭐ | ~$100 | ✅ IN STOCK | GetFPV | [getfpv.com/geprc-mark4-10](https://www.getfpv.com) |
| iFlight Chimera 10" | ~$90 | ✅ IN STOCK | RaceDayQuads | [racedayquads.com](https://www.racedayquads.com/search?q=chimera+10+inch) |
| Tarot 650 (Legacy Option) | ~$120 | Variable | Amazon | [amazon.com](https://www.amazon.com) |

**Notes:**
- GEPRC Mark4 optimized for long-range with good payload capacity
- 10" frames provide better efficiency for 60-min flight than smaller quads
- Tarot 650 is heavier but more payload capacity

---

## 5. MOTORS (900KV for Long Flight)

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **BrotherHobby 3115 900KV** ⭐ | ~$25 each | ✅ IN STOCK | GetFPV | [getfpv.com/brotherhobby-3115-900kv](https://www.getfpv.com) |
| iFlight XING 3110 900KV | ~$22 each | ✅ IN STOCK | RaceDayQuads | [racedayquads.com](https://www.racedayquads.com) |
| T-Motor F90 1300KV | ~$30 each | ✅ IN STOCK | GetFPV | [getfpv.com](https://www.getfpv.com) |

**Notes:**
- **Buy 5 motors (1 spare)**
- 900KV is optimal for 6S Li-Ion with 10" props
- Lower KV = more efficient = longer flight time
- BrotherHobby Tornado T5 series is reliable

---

## 6. ESC (Electronic Speed Controller)

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **Holybro Tekko32 F4 50A 4in1** ⭐ | ~$70 | ✅ IN STOCK | GetFPV | [getfpv.com/holybro-tekko32](https://www.getfpv.com) |
| Rush Blade 50A Sport | ~$65 | ✅ IN STOCK | RaceDayQuads | [racedayquads.com](https://www.racedayquads.com) |
| T-Motor Velox 55A | ~$80 | ✅ IN STOCK | GetFPV | [getfpv.com](https://www.getfpv.com) |

**Notes:**
- 50A-60A rating required for 3115 motors
- 30x30 mounting pattern standard
- BLHeli_32 firmware recommended

---

## 7. PROPELLERS

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **HQProp 10x5x3 MacroQuad** ⭐ | ~$8/set | ✅ IN STOCK | GetFPV | [getfpv.com/hqprop-10x5x3](https://www.getfpv.com) |
| Gemfan 1050 | ~$6/set | ✅ IN STOCK | RaceDayQuads | [racedayquads.com](https://www.racedayquads.com) |

**Notes:**
- **Buy at least 4 sets (CW + CCW)**
- 10x5 provides good thrust/efficiency balance
- 3-blade props for redundancy (if one blade chips)

---

## 8. BATTERY (⚠️ CRITICAL FOR 60-MIN FLIGHT)

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **Li-Ion 6S 8000mAh (Molicel P42A)** ⭐ | ~$160 | Variable | Titan Power | [titanpower.com](https://www.titanpower.com) |
| Auline Li-Ion 6S 8000mAh | ~$140 | ✅ IN STOCK | AliExpress | [aliexpress.com/auline](https://www.aliexpress.com) |
| Tattu 6S 8000mAh 25C (LiPo) | $161.99 | ✅ IN STOCK | Amazon | [amazon.com](https://www.amazon.com) |

**⚠️ CRITICAL WARNING:**
```
For 60-MINUTE FLIGHT, you MUST use Li-Ion cells, NOT LiPo!

Li-Ion (Molicel P42A):
  ✅ Energy density: 250-270 Wh/kg
  ✅ Flight time: 50-60 minutes
  ✅ Discharge rate: 10-15C (sufficient for efficient flight)
  
LiPo (Tattu 25C):
  ❌ Energy density: 150-180 Wh/kg
  ❌ Flight time: 18-25 minutes
  ✅ Discharge rate: 25-50C (more power, less endurance)

DO NOT buy generic "Li-Ion" packs!
Specifically need: Molicel P42A or Samsung 40T cells
```

**Build Your Own Pack (Advanced):**
- Molicel P42A 21700 cells: [18650batterystore.com](https://www.18650batterystore.com)
- 6S2P configuration = 8400mAh

---

## 9. GPS MODULE

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **Matek M10-5883** ⭐ | ~$30 | ✅ IN STOCK | GetFPV | [getfpv.com/matek-m10](https://www.getfpv.com) |
| Holybro M10 GPS | ~$35 | ✅ IN STOCK | Holybro | [holybro.com](https://holybro.com) |
| BN-220 (Budget) | ~$15 | ✅ IN STOCK | Amazon | [amazon.com](https://www.amazon.com) |

**Notes:**
- M10 chipset is newer/faster than M8
- Integrated compass (5883) saves weight
- RTK GPS optional for precision landing (future)

---

## 10. CONNECTIVITY

### Primary: 4G/LTE (Phase 1)

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **Sixfab 4G/LTE Cellular Modem Kit** ⭐ | ~$100 | ✅ IN STOCK | Sixfab | [sixfab.com](https://sixfab.com/product/raspberry-pi-4g-lte-modem-kit/) |
| Waveshare SIM7600 4G HAT | ~$60 | ✅ IN STOCK | Amazon | [amazon.com](https://www.amazon.com) |

**Notes:**
- Sixfab includes HAT + Global SIM + Antenna
- Waveshare cheaper but requires separate SIM

### Backup: LoRa / Meshtastic

> 📡 **Meshtastic** provides mesh networking for offline operation when 4G fails.

#### For Drones (Lightweight)

| Product | Price | Range | Vendor | Link |
|---------|-------|-------|--------|------|
| **Heltec V3** ⭐ Drone | ~$25 | 5-8 km | AliExpress | [aliexpress.com](https://www.aliexpress.com) |
| LILYGO TTGO LoRa32 | ~$20 | 3-5 km | AliExpress | [aliexpress.com](https://www.aliexpress.com) |

#### For Ground Station (Long Range)

| Product | Price | Range | Vendor | Link |
|---------|-------|-------|--------|------|
| **RAK WisBlock** ⭐ Best Range | ~$60 | 15+ km | RAK | [rakwireless.com](https://rakwireless.com) |
| LILYGO T-Beam Supreme | ~$45 | 10+ km | AliExpress | [aliexpress.com](https://www.aliexpress.com) |

**Recommended Setup:**
- **Ground Station:** RAK WisBlock with directional antenna (15+ km range)
- **Drones (×5):** Heltec V3 (compact, lightweight, 5-8 km range)

**Notes:**
- 868MHz for EU, 915MHz for US
- Install Meshtastic firmware: [meshtastic.org](https://meshtastic.org)
- Mesh networking allows drone-to-drone relay

---

## 11. RC TRANSMITTER/RECEIVER

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **RadioMaster TX16S** ⭐ | ~$150 | ✅ IN STOCK | GetFPV | [getfpv.com/radiomaster-tx16s](https://www.getfpv.com) |
| HappyModel EP1 ELRS RX | ~$15 | ✅ IN STOCK | GetFPV | [getfpv.com](https://www.getfpv.com) |
| BetaFPV ELRS Micro RX | ~$20 | ✅ IN STOCK | GetFPV | [getfpv.com](https://www.getfpv.com) |

**Notes:**
- ELRS (ExpressLRS) recommended for long range
- One TX for entire fleet (5 drones)
- Each drone needs one RX

---

## 12. CHARGER

| Product | Price | Stock | Vendor | Link |
|---------|-------|-------|--------|------|
| **ISDT D2 Dual Charger** ⭐ | ~$70 | ✅ IN STOCK | Amazon | [amazon.com](https://www.amazon.com) |
| ISDT K4 Quad Charger | ~$150 | ✅ IN STOCK | Amazon | [amazon.com](https://www.amazon.com) |
| ToolkitRC M8S | ~$50 | ✅ IN STOCK | RaceDayQuads | [racedayquads.com](https://www.racedayquads.com) |

**Notes:**
- D2 charges 2 batteries simultaneously
- K4 better for 5-drone fleet (4 batteries at once)
- Li-Ion requires different charge profile than LiPo!

---

## 13. ACCESSORIES

| Item | Price | Vendor |
|------|-------|--------|
| Battery Strap 300mm (Kevlar) | ~$10 | Amazon |
| XT90 Connectors (5 pairs) | ~$15 | Amazon |
| Heatshrink Assortment | ~$10 | Amazon |
| Standoffs M3 Assortment | ~$8 | Amazon |
| Vibration Dampeners | ~$5 | Amazon |
| USB-C Cables (3-pack) | ~$15 | Amazon |
| MicroSD 128GB | ~$15 | Amazon |

---

## 📊 COMPLETE SHOPPING LIST (1 Drone)

| # | Item | Price | Vendor |
|---|------|-------|--------|
| 1 | Pixhawk 6C | $141 | Holybro |
| 2 | Raspberry Pi 5 (8GB) | $105 | Adafruit |
| 3 | **InfiRay P2 Pro Thermal** ⭐ | $350 | AliExpress/Amazon |
| 4 | GEPRC Mark4 10" Frame | $100 | GetFPV |
| 5 | BrotherHobby 3115 900KV (x5) | $125 | GetFPV |
| 6 | Holybro Tekko32 50A 4in1 ESC | $70 | GetFPV |
| 7 | HQProp 10x5x3 (4 sets) | $32 | GetFPV |
| 8 | Li-Ion 6S 8000mAh (Molicel) | $160 | Titan Power |
| 9 | Matek M10-5883 GPS | $30 | GetFPV |
| 10 | Sixfab 4G/LTE Kit | $100 | Sixfab |
| 11 | HappyModel ELRS RX | $15 | GetFPV |
| 12 | Accessories | $50 | Amazon |
| **TOTAL** | | **$1,278** | |

### Additional (One-Time Purchases)
| Item | Price | Vendor |
|------|-------|--------|
| RadioMaster TX16S | $150 | GetFPV |
| ISDT K4 Charger | $150 | Amazon |
| Heltec LoRa (x2) | $50 | AliExpress |
| Ground Station Laptop | Existing | - |
| **ONE-TIME TOTAL** | **$350** | |

---

## 🔋 FLIGHT TIME CALCULATIONS

### 60-Minute Configuration (Li-Ion)
```
Battery: 6S 8000mAh Li-Ion (Molicel P42A)
Motors: 900KV with 10" props
AUW (All-Up Weight): ~2.5 kg
Average Current: ~8A cruise
Flight Time: 8000mAh / 8A = 60 minutes ✅
```

### 25-Minute Configuration (LiPo - NOT Recommended)
```
Battery: 6S 5000mAh LiPo
Motors: 900KV with 10" props
AUW: ~2.2 kg
Average Current: ~10A cruise
Flight Time: 5000mAh / 10A = 30 minutes (with margin = 25 min)
```

---

## 🏪 TRUSTED VENDORS

| Store | Country | Specialty | Website |
|-------|---------|-----------|---------|
| **Holybro** | Official | Flight Controllers | [holybro.com](https://holybro.com) |
| **GetFPV** | USA | Full FPV Parts | [getfpv.com](https://www.getfpv.com) |
| **RaceDayQuads** | USA | Racing/Long Range | [racedayquads.com](https://www.racedayquads.com) |
| **Adafruit** | USA | Electronics/Pi | [adafruit.com](https://www.adafruit.com) |
| **Amazon** | Global | General Parts | [amazon.com](https://www.amazon.com) |
| **Pyrodrone** | USA | FPV Parts | [pyrodrone.com](https://www.pyrodrone.com) |
| **AliExpress** | China | Budget Parts | [aliexpress.com](https://www.aliexpress.com) |
| **Sixfab** | - | Cellular/IoT | [sixfab.com](https://sixfab.com) |

---

## ⚠️ CRITICAL NOTES

### DO:
- ✅ Use Li-Ion (Molicel P42A) for 60-minute flight
- ✅ Use 900KV motors with 10" props for efficiency
- ✅ Buy from trusted vendors (see list above)
- ✅ Order 1 spare motor per drone
- ✅ Use 4G/LTE as primary connectivity

### DON'T:
- ❌ Use LiPo expecting 60-minute flight (max 25 min)
- ❌ Buy clone flight controllers
- ❌ Use generic Li-Ion packs (need Molicel/Samsung cells)
- ❌ Skip the GPS compass (causes flyaways)

---

**Document Version:** 2.0  
**Last Updated:** December 22, 2025  
**Next Review:** After Phase 1A hardware testing
