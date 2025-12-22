# WEEK 1 DESK TEST - SHOPPING LIST & CRITICAL PATH

**This is not the "build 5 drones" list. This is the "prove the core works" list.**

You order these parts TODAY. You test them on the desk THIS WEEK. You prove:
- ✅ Pi 4 reads InfiRay P2Pro thermal camera
- ✅ TensorFlow Lite YOLO runs locally
- ✅ Heltec ESP32 sends LoRa messages
- ✅ Ground station receives messages

**If all 4 work, you proceed to Week 3 (build drones).**
**If any fail, you have 1 week to troubleshoot before committing €6,000 to drone hardware.**

---

## CRITICAL PATH: WHAT BLOCKS WHAT

```
BLOCKER 1: Can Pi 4 read the thermal camera?
  ├─ If YES → Buy 5 more thermal cameras (for drones)
  └─ If NO → Problem. Troubleshoot. Alternative: FLIR Lepton 3.5

BLOCKER 2: Does YOLO run in < 2 sec on Pi 4?
  ├─ If YES → Proceed to drone assembly
  └─ If NO → Problem. Need Jetson Nano (costs €150 more, weight issue)

BLOCKER 3: Does LoRa work 1km away?
  ├─ If YES → Proceed to forest testing
  └─ If NO → Problem. May need higher antenna or different module

BLOCKER 4: Does Streamlit dashboard receive messages?
  ├─ If YES → Build base station
  └─ If NO → Problem. Serial library issue or USB issue
```

**If ANY blocker fails, stop and fix it before ordering drone parts.**

---

## THE PARTS (Week 1 Only)

### **COMPUTE & SENSORS**

| Item | Model | Qty | Cost | Why This One | Link |
|------|-------|-----|------|--------------|------|
| **Raspberry Pi 4** | RPi 4B 8GB | 1 | €60 | 8GB RAM needed for YOLO | Amazon DE |
| **Thermal Camera** | InfiRay P2Pro | 1 | €250 | UVC-compatible, proven drivers | AliExpress |
| **USB Hub** | 7-port powered | 1 | €20 | Pi only has 4 USB, need extras for thermal + LoRa | Amazon |
| **Power Supply** | Anker 65W USB-C | 1 | €35 | Stable 5V for Pi 4 | Amazon |
| **Micro SD Card** | SanDisk 128GB | 1 | €15 | Ubuntu Server 24.04 LTS | Amazon |
| **USB Cable** | USB 3.0 A→Micro-B | 2 | €10 | Connect thermal camera + spare | Amazon |

**Subtotal Compute:** €390

---

### **COMMUNICATIONS (4G/LTE)**

| Item | Model | Qty | Cost | Why This One | Link |
|------|-------|-----|------|--------------|------|
| **4G Dongle** | Huawei E3372h-320 | 1 | €40 | Linux native support (CDC_ETHER) | Amazon |
| **IoT SIM** | Things Mobile / 1NCE | 1 | €10 | Multi-network roaming, 1GB data | Amazon |
| **VPN Service** | Tailscale | 1 | €0 | Free tier covers 100 devices | [tailscale.com](https://tailscale.com) |
| **[BACKUP]** | *Heltec LoRa* | *0* | *€0* | *Moved to Phase 2 (Backup Link)* | - |

**Subtotal Comms:** €50 ( + ~€5/mo data)

---

### **TESTING & SETUP**

| Item | Model | Qty | Cost | Why This One | Link |
|------|-------|-----|------|--------------|------|
| **Network Cable** | CAT6 2m | 1 | €5 | If no WiFi in test area | Amazon |
| **Laptop (your own)** | Modern, Ubuntu-capable | 1 | €0 | You have this |  |
| **Breadboard** | 830-point | 1 | €5 | Wire Heltec SPI pins safely | Amazon |
| **Jumper Wires** | M/F assortment | 1 | €8 | Connect Heltec to Pi SPI | Amazon |
| **Multimeter** | Basic digital | 1 | €12 | Debug power/signal issues | Amazon |
| **USB Power Bank** | 26000mAh 65W | 1 | €40 | Power Pi 4 for 4+ hours during testing | Amazon |

**Subtotal Testing:** €70

---

### **OPTIONAL (Nice to Have)**

| Item | Model | Cost | Why | Defer? |
|------|-------|------|-----|--------|
| GPS module (u-blox M8) | BN-220 | €15 | Not needed Week 1, add Week 3 | YES |
| IMU sensor (9-DOF) | MPU9250 | €10 | Not needed for thermal test | YES |
| RGB USB Webcam | Logitech C920 | €50 | Not needed Week 1, add Week 5 | YES |
| OLED Display | 128×64 SSD1306 | €8 | For drone status, not critical | YES |

**Skip these. Buy only if blocker tests fail and you need debugging tools.**

---

## WEEK 1 SHOPPING CART

```
TOTAL FOR DESK TEST:          €598
├─ Compute & Sensors:         €390
├─ Communications (LoRa):     €138
└─ Testing & Setup:           €70

BUDGET REMAINING (for drone parts after proving tech):
  Total project budget:       €7,340
  Spent on desk test:         -€598
  Available for drones:       €6,742

  (5 drones × €1,200 = €6,000, so you're good)
```

---

## EXACT ORDER: DAY-BY-DAY (Week 1)

### **Day 1 (Monday): Order Everything**
```
Shopping List:
☐ Raspberry Pi 4 8GB                          (Amazon DE)
☐ InfiRay P2Pro thermal camera                (AliExpress, allow 2 weeks)
☐ Heltec ESP32 LoRa modules (× 2)             (AliExpress)
☐ USB Hub (powered, 7-port)                   (Amazon)
☐ Anker 65W USB-C power supply                (Amazon)
☐ SanDisk 128GB Micro SD card                 (Amazon)
☐ USB 3.0 A→Micro-B cables (× 2)              (Amazon)
☐ SMA 868MHz antennas (× 2)                   (AliExpress)
☐ FTDI FT232 USB serial cable                 (AliExpress)
☐ Weatherproof IP67 box                       (Amazon)
☐ Breadboard 830-point                        (Amazon)
☐ Jumper wire M/F assortment                  (Amazon)
☐ Basic multimeter                            (Amazon)
☐ Anker 26000mAh 65W power bank               (Amazon)

Estimated Arrival:
  Amazon items: 2-3 days (expedited)
  AliExpress items: 2-3 weeks (standard shipping)
  
CRITICAL: Order P2Pro FIRST. It takes longest. If it's out of stock,
buy alternative: FLIR Lepton 3.5 (€300, known drivers).
```

### **Days 2-3 (Tue-Wed): Setup Pi 4**
```
☐ Download Ubuntu Server 24.04 LTS (arm64)
☐ Burn to Micro SD card (Raspberry Pi Imager)
☐ Boot Pi 4 with power supply
☐ SSH into Pi: ssh ubuntu@<ip>
☐ Update: sudo apt update && apt upgrade
☐ Install Python 3.10 + pip
☐ Clone repo: git clone https://github.com/you/fire-drone
☐ Create virtual environment: python3 -m venv venv
☐ Activate: source venv/bin/activate
```

### **Days 4-5 (Thu-Fri): Test Thermal Camera**
```
IF P2Pro arrived:
  ☐ Connect P2Pro to Pi USB hub
  ☐ Run: lsusb | grep InfiRay
  ☐ Should see device listed
  ☐ Test driver: python3 -c "import cv2; cap = cv2.VideoCapture('/dev/video0'); ret, frame = cap.read(); print(frame.shape)"
  ☐ If works: capture 10 frames to verify
  ☐ If fails: Troubleshoot (see BLOCKER #1 recovery plan below)

BLOCKER #1 RECOVERY (if P2Pro not working):
  ├─ Check lsusb shows device
  ├─ Check /dev/video* exists
  ├─ If no device: USB driver issue
  │  └─ Solution: Download P2Pro-Viewer from GitHub, test with that
  ├─ If no /dev/video*: Need to load USB video driver
  │  └─ Solution: sudo modprobe uvcvideo
  └─ If still fails: Alternative camera FLIR Lepton 3.5
     └─ Order it, adds 1 week delay to project
```

### **Days 5-7 (Fri-Sun): Test LoRa & YOLO**
```
IF Heltec modules arrived:
  ☐ Wire Heltec #1 to Pi SPI (CS=GPIO8, MOSI=GPIO10, MISO=GPIO9, CLK=GPIO11)
  ☐ Wire Heltec #2 to USB-serial adapter (on desk, separate from Pi)
  ☐ Test LoRa message from Pi → Ground station
  ☐ Expected: "FIRE 44.123 21.543 245" appears on ground station terminal
  
  ☐ Download YOLOv8n-int8.tflite (12MB, optimized for Pi 4)
  ☐ Run inference: time python3 yolo_test.py (should be < 2 sec)
  ☐ Test on thermal frame: YOLO outputs confidence score
  
BLOCKER #2 RECOVERY (if YOLO slow):
  └─ Check CPU usage (htop): Should be ~80% during inference
  └─ If slow: May need quantized model (smaller, faster)
  └─ Download: YOLOv8n-int8.tflite instead of standard
  └─ Retest: Should be 100-200ms now
  
BLOCKER #3 RECOVERY (if LoRa fails):
  ├─ Check Heltec lights up (LED blinks)
  ├─ Check SPI bus: i2cdetect -y 1 (may show device)
  ├─ Verify antenna connected (SMA, threaded)
  ├─ Test at short range: 1m, then increase
  ├─ If no signal at 1m: SPI wiring issue
  │  └─ Recheck breadboard connections, use multimeter
  └─ If signal works at 1m but not 10m: Antenna issue
     └─ Buy higher-gain antenna (5dBi instead of 2dBi)
```

---

## SUCCESS CRITERIA (End of Week 1)

### **You WIN if:**
```
✅ Pi 4 reads P2Pro thermal camera
   └─ Evidence: $ cv2.VideoCapture works, frame shape is (120, 160)

✅ YOLO inference runs locally in < 2 sec
   └─ Evidence: time yolo_inference.py shows ~100-200ms

✅ LoRa sends "FIRE 44.123 21.543" from Pi to ground
   └─ Evidence: Terminal shows received message

✅ Streamlit dashboard displays alert + beeps
   └─ Evidence: Click button, beep happens, log saves to SQLite
```

### **You FAIL if:**
```
❌ P2Pro doesn't connect to Pi
   └─ Action: Buy FLIR Lepton 3.5, delay project 1 week

❌ YOLO inference > 5 sec
   └─ Action: Need faster compute (Jetson Nano), costs extra €150

❌ LoRa fails at any range
   └─ Action: Need different module or antenna, adds 1-2 week delay

❌ Dashboard doesn't start
   └─ Action: Python environment issue, easily fixable
```

**If you have 4/4 WIN, you proceed to Week 3 (buy drone parts).**
**If you have 1+ FAIL, you troubleshoot and delay drone purchase by 1-2 weeks.**

---

## WEEK 1 SUCCESS = WEEK 3 GO/NO-GO

After Week 1, you decide:

### **GO (Proceed to Week 3: Build Drones)**
- All blockers passed
- Tech proven on desk
- Buy 5 complete drone kits (€6,000)
- Proceed with assembly

### **NO-GO (Fix issues, delay 1-2 weeks)**
- P2Pro failed → buy alternative camera
- YOLO too slow → upgrade compute
- LoRa failed → troubleshoot radio
- Dashboard broken → debug Python

**Cost of NO-GO: Time, not money (you only spent €598, not €6,598).**

---

## BUDGET CHECK

```
Week 1 Desk Test:           €598
├─ If successful, add drones: €6,000
└─ If failed, reorder cameras: €300

Total worst-case:           €6,898

SPARE BUDGET:               €442

Use spare for:
├─ Extra LoRa modules (backup)
├─ Additional thermal cameras (test multiple)
├─ Shipping expediting (if parts delayed)
└─ Tool rentals (soldering station if needed)
```

---

## THE EXECUTION CHECKLIST

Print this. Check off as you go.

```
WEEK 1: DESK TEST
═══════════════════════════════════════════════════

DAY 1 (Monday):
☐ Place Amazon orders (Pi, power, USB hub, wires, multimeter, power bank)
☐ Place AliExpress orders (Thermal camera, Heltec modules, antennas, serial)
☐ Verify P2Pro in stock before ordering (call supplier if unsure)
☐ Bookmark P2Pro-Viewer GitHub repo (for backup testing)

DAY 2 (Tuesday):
☐ Download Ubuntu Server 24.04 LTS ARM64
☐ Download Raspberry Pi Imager
☐ Write Ubuntu to SD card
☐ Boot Pi 4 (will take 5 min first time)

DAY 3 (Wednesday):
☐ SSH into Pi (get IP from router DHCP)
☐ sudo apt update && apt upgrade
☐ Install Python: sudo apt install python3.10 python3-pip
☐ Create project directory and virtual environment
☐ Clone your fire-drone GitHub repo

DAY 4 (Thursday):
☐ Thermal camera arrives? Test connection
☐ USB hub arrives? Test power distribution
☐ If not arrived: Do other setup work
☐ Test thermal camera reads frame (if arrived)

DAY 5 (Friday):
☐ Heltec modules arrive (maybe)
☐ Wire Heltec #1 to Pi SPI (use breadboard)
☐ Wire Heltec #2 to USB-serial
☐ Test LoRa at 1m distance
☐ Download YOLOv8n-int8.tflite model

DAY 6 (Saturday):
☐ Run YOLO on thermal frame: time python3 yolo_inference.py
☐ Check latency: should be 100-200ms
☐ If slow: troubleshoot (see BLOCKER #2 above)
☐ Test LoRa at 10m distance
☐ Check antenna connection (SMA threads tight)

DAY 7 (Sunday):
☐ Build Streamlit dashboard (copy from PHASE_1_ARCHITECTURE.md)
☐ Connect Streamlit to SQLite
☐ Test alert: simulate "FIRE" LoRa message
☐ Verify beep plays, log saves
☐ Document any issues for Week 2

END OF WEEK 1:
☐ All 4 blockers passed → PROCEED TO WEEK 3 ✅
☐ 1+ blockers failed → TROUBLESHOOT → +1-2 weeks delay
☐ Show results to fire chief (photo/video of alert on screen)
```

---

## WEEK 1 → WEEK 3 GAP (What Happens in Week 2?)

**If Week 1 PASSES:** Week 2 is buffer time
```
☐ Rest/planning
☐ Design 3D mounts for thermal camera on drone
☐ Research Tarot 650 frame (watch assembly videos)
☐ Prepare workspace for building 5 drones
☐ Pre-order long-lead items (batteries, motors, ESCs)
```

**If Week 1 FAILS:** Week 2 is troubleshooting
```
☐ Debug camera issue or LoRa issue
☐ Order backup parts
☐ Test again
☐ Don't proceed to Week 3 until all blockers pass
```

---

## FINAL SANITY CHECK

Before you hit "buy now" on this list:

1. **Do you have a workbench?**
   ✅ Yes → Good. Set up USB hub + Pi + breadboard there.
   ❌ No → Find one (library, community center, makerspace).

2. **Do you have basic soldering equipment?**
   ✅ Yes → Good. You might need to solder SMA antenna if not pre-soldered.
   ❌ No → Not critical for Week 1. Defer to Week 3.

3. **Do you have Ubuntu/Linux experience?**
   ✅ Yes → Good. You'll be fine on command line.
   ❌ No → Take 2 hours to learn basics (YouTube "Ubuntu Linux basics").

4. **Are you prepared to debug hardware issues?**
   ✅ Yes → Good. Multimeter + Google = you can solve most problems.
   ❌ No → This project requires debugging skills. Learn them now.

5. **Is your internet stable enough for AliExpress shipping?**
   ✅ Yes → Good. Things will arrive.
   ❌ No (in remote area) → Order from EU Amazon instead (costs 2× more but arrives fast).

---

## GO/NO-GO DECISION

**If you answered YES to 4/5 above:**
```
YOU ARE READY.
Close this document.
Place the orders.
Week 1 starts Monday.
```

**If you answered NO to 2+:**
```
WAIT 1 WEEK.
Solve blockers first (find workspace, learn Linux, etc.).
Then order.
You will thank yourself.
```

---

## NEXT DOCUMENT

After Week 1 passes, read: `WEEK_3_DRONE_BUILD_CHECKLIST.md` (we'll create this).

For now: **Order the parts today.**
