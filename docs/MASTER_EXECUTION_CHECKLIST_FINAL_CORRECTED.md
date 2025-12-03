# MASTER EXECUTION CHECKLIST - FINAL CORRECTED VERSION

**Week -2 to Week 12: Complete journey with all technical corrections integrated**

---

## PRE-EXECUTION (TONIGHT): Critical Downloads

**DO NOT SKIP THIS. Takes 45 minutes, prevents 5 weeks of debugging.**

```bash
# 1. D-Fire Real Thermal Dataset (1.2 GB)
# CRITICAL: Real fire images, not synthetic blobs
git clone https://github.com/gaiasd/DFireDataset.git

# 2. P2Pro-Viewer Driver Reference (10 MB)
# CRITICAL: Contains radiometric decoding formula
git clone https://github.com/LeoDJ/P2Pro-Viewer.git

# 3. YOLOv8n-int8 Model (22 MB)
# CRITICAL: Quantized, not standard model
wget https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n-int8.tflite

# Verify all three are ready
ls -lh DFireDataset/ P2Pro-Viewer/ yolov8n-int8.tflite
```

**Status: Ready for Monday morning**

---

## PHASE 0: SOFTWARE VALIDATION (Week -2 to Week 0)

**Cost: €0 | Time: 1 week | Risk reduction: 80-95%**

### MONDAY (Week -2): YOLO Reality Testing

- [ ] Setup Python environment (venv, pip install)
- [ ] Benchmark yolov8n-int8 on your desktop (30 frames)
- [ ] Record latency: ~189ms expected
- [ ] Calculate Pi 4 estimate: 189ms × 4 = 756ms (realistic)
- [ ] Verify: 756ms = 1.3 FPS (acceptable for fire detection)
- [ ] Document: `yolo_benchmark_report.md`

**Expected result:**
```
✓ YOLO latency: 189ms desktop, 756ms Pi 4 (REALISTIC)
✓ FPS: 1.3 on Pi 4 (sufficient)
✓ Decision: PROCEED TO TUESDAY
```

**GO/NO-GO:**
- ✅ If latency < 1000ms on Pi 4 estimate → PROCEED
- ❌ If latency > 1500ms → STOP, consider Jetson Nano

---

### TUESDAY (Week -2): REAL FIRE DATA ACCURACY

- [ ] Verify D-Fire dataset downloaded (21,000 images)
- [ ] Test YOLO on 100 real fire images
- [ ] Test YOLO on 100 real non-fire images
- [ ] Record fire confidence: ~0.87 expected
- [ ] Record non-fire confidence: ~0.26 expected
- [ ] Calculate separation: 0.87 - 0.26 = 0.61 (GOOD)
- [ ] Set threshold: (0.87 + 0.26) / 2 = 0.565
- [ ] Calculate accuracy: Should be ~97%
- [ ] Document: `dfire_accuracy_report.md`

**Critical decision:**
- ✅ Do NOT use synthetic Gaussian blob data (useless)
- ✅ Use D-Fire dataset (real world validated)

**Expected result:**
```
✓ Fire detection: 0.87 confidence (97% accuracy)
✓ Non-fire: 0.26 confidence (98% rejection)
✓ Separation: 0.61 (excellent)
✓ Decision: PROCEED TO WEDNESDAY
```

**GO/NO-GO:**
- ✅ If accuracy > 85% on real data → PROCEED
- ❌ If accuracy < 70% → STOP, model not suitable

---

### WEDNESDAY (Week -2): P2PRO DRIVER + DASHBOARD

#### Part A: P2Pro Driver Research (CRITICAL)

- [ ] Clone P2Pro-Viewer repository
- [ ] Read: `p2pro.py` or `ThermalCamera.py` (find driver code)
- [ ] Find radiometric decoding formula
- [ ] Expected formula: `T(°C) = (raw_value * 0.0625) - 273.15`
- [ ] Test formula on 6 test cases (provided)
- [ ] Verify all test cases pass
- [ ] Document: `p2pro_decoding_verified.md`

**Critical decision:**
- ✅ Do NOT use cv2.VideoCapture directly (won't decode temperatures)
- ✅ Use P2Pro-Viewer radiometric decoder (verified formula)

**Expected result:**
```
✓ P2Pro formula verified (6/6 test cases pass)
✓ Radiometric decoding understood
✓ Ready for Phase 1A hardware testing
```

**GO/NO-GO:**
- ✅ If all 6 test cases pass → PROCEED
- ❌ If any fail → Research P2Pro docs further before Phase 1A

#### Part B: Streamlit Dashboard

- [ ] Create `dashboard.py` with mock data
- [ ] Create SQLite mock database
- [ ] Build UI: Metrics, map, detection log
- [ ] Test all buttons click
- [ ] Test map displays correctly
- [ ] Run: `streamlit run dashboard.py`
- [ ] Verify: `localhost:8501` shows complete UI

**Expected result:**
```
✓ Dashboard loads at localhost:8501
✓ Metrics visible (5 boxes)
✓ Map shows drone positions
✓ Detection log shows mock data
✓ All buttons functional
```

---

### THURSDAY (Week -2): LORA MESSAGE PROTOCOL

- [ ] Create `lora_protocol.py`
- [ ] Implement: `encode_alert()` (drone → ground)
- [ ] Implement: `decode_alert()` (ground → drone)
- [ ] Test 3 scenarios: Fire, medium fire, false positive
- [ ] Verify message always < 25 bytes
- [ ] Verify encode/decode fidelity (no data loss)
- [ ] Document: `lora_protocol_spec.md`

**Expected result:**
```
✓ Message encoding: FIRE 44.123 21.543 245 (21 bytes) ✓
✓ Decoding: Recovers lat, lon, temp exactly
✓ Size: Always < 25 bytes (LoRa packet limit)
```

---

### FRIDAY (Week -2): OPERATOR DECISION RULES

- [ ] Create `operator_rules.py`
- [ ] Implement: `get_decision(confidence, temp)`
- [ ] Rules: CONFIRM if conf > 0.85 AND temp > 200
- [ ] Rules: DISMISS if conf < 0.50 OR temp < 80
- [ ] Rules: VALIDATE if uncertain
- [ ] Test 4+ scenarios
- [ ] All tests pass

**Expected result:**
```
✓ CONFIRM: (0.95, 300) → CONFIRM ✓
✓ CONFIRM: (0.88, 220) → CONFIRM ✓
✓ DISMISS: (0.45, 60) → DISMISS ✓
✓ VALIDATE: (0.72, 180) → VALIDATE ✓
```

---

### SATURDAY (Week -2): LEARNING FEEDBACK LOOP

- [ ] Create `learning_trajectory.py`
- [ ] Simulate 4-week improvement
- [ ] Week 1: 15% → 27%
- [ ] Week 2: 40% → 61%
- [ ] Week 3: 65% → 87%
- [ ] Week 4: 85% → 91% (deployment ready)
- [ ] Generate graph: `learning_trajectory.png`

**Expected result:**
```
✓ Trajectory realistic (15% day 1 → 91% day 28)
✓ Week 4 > 85% accuracy (deployment threshold)
✓ Graph shows improvement curve
```

---

### SUNDAY (Week -2 → Week 0): INTEGRATION + REPORT

- [ ] Create `phase0_final_test.py` (end-to-end integration)
- [ ] Test: YOLO → LoRa message → Decode → Decision → Confirm
- [ ] All steps pass
- [ ] Create: `PHASE_0_COMPLETION_REPORT.md`
- [ ] Commit all code to GitHub

**Expected result:**
```
✓ Full integration test passes
✓ All 8 components work together
✓ No surprises expected in Phase 1A
```

---

## PHASE 0 SUCCESS GATE (End of Week 0)

**Before ordering €598 hardware, checklist:**

```
YOLO Validation:
  ✓ Latency measured on desktop (189ms)
  ✓ Pi 4 estimate realistic (756ms)
  ✓ FPS acceptable (1.3 FPS)

Real Fire Testing:
  ✓ Tested on D-Fire (21k images, real-world)
  ✓ Accuracy 97% (not synthetic blobs)
  ✓ Threshold set (0.565)

P2Pro Driver:
  ✓ Formula verified (6/6 test cases pass)
  ✓ Radiometric decoder understood
  ✓ No surprises expected in Phase 1A

Dashboard:
  ✓ UI functional
  ✓ Database works
  ✓ All visualizations tested

Integration:
  ✓ Full end-to-end test passes
  ✓ All components work together
  ✓ No unknowns remain
```

**DECISION:**
- ✅ If all ✓: PROCEED TO PHASE 1A (order hardware)
- ❌ If any ✗: FIX FIRST (save €598)

---

## HARDWARE ORDERING GATE (Week 1 Monday AM)

**If Phase 0 passed, order €598 from WEEK_1_SHOPPING_LIST.md:**

```
Part                           Cost      Order from
─────────────────────────────────────────────────────
Raspberry Pi 4 8GB             €60       Amazon
InfiRay P2Pro thermal camera   €250      AliExpress
Heltec ESP32 LoRa modules (×2) €100      AliExpress
USB Hub 7-port                 €20       Amazon
Power supply + cables          €45       Amazon
Misc (SD card, breadboard)     €123      Amazon
─────────────────────────────────────────────────────
TOTAL                          €598
```

**Tracking:**
- [ ] Order placed (date: _______)
- [ ] Amazon items tracking: _______________
- [ ] AliExpress items tracking: ______________
- [ ] Expected arrival: Week 1 Thu-Fri

---

## PHASE 1A: HARDWARE DESK TEST (Week 1-2)

**Cost: €598 | Time: 2 weeks | Risk reduction: 40%**

### BLOCKER #1: Thermal Camera (Week 1 Thursday-Friday)

When InfiRay P2Pro arrives:

- [ ] Unbox P2Pro
- [ ] Connect to Pi 4 via USB
- [ ] Run: `lsusb | grep InfiRay`
- [ ] Verify device appears
- [ ] Run P2Pro-Viewer test script
- [ ] Verify outputs temperature values (not green/purple corruption)
- [ ] Record actual temperatures: Should be 20-40°C ambient

**Expected:**
```
✓ Device appears in lsusb
✓ USB connection stable
✓ Temperature values reasonable
✓ No driver errors
```

**GO/NO-GO:**
- ✅ If camera works → PASS blocker #1
- ❌ If camera corrupted image → Debug USB driver (1 day)
- ❌ If no device → Try alternative camera (1-2 weeks)

---

### BLOCKER #2: YOLO Speed on Pi 4 (Week 2 Monday-Tuesday)

- [ ] Copy yolov8n-int8.tflite to Pi 4
- [ ] Run: `benchmark_yolo.py` on Pi 4
- [ ] Record actual latency (expect ~700-900ms)
- [ ] Verify < 1500ms (acceptable)
- [ ] Calculate actual FPS (expect 1.1-1.5 FPS)

**Expected:**
```
✓ Latency: 756ms ±200ms (matches estimate)
✓ FPS: 1.3 FPS (acceptable)
✓ No thermal throttling observed
```

**GO/NO-GO:**
- ✅ If latency < 1000ms → PASS blocker #2
- ❌ If latency > 1500ms → Need Jetson Nano (€150, 1-2 weeks)

---

### BLOCKER #3: LoRa Communication (Week 2 Wednesday)

- [ ] Wire Heltec module to Pi 4 SPI (breadboard)
- [ ] Run LoRa test: Send message from Pi
- [ ] Ground station Heltec receives message
- [ ] Test at 1m (should work)
- [ ] Test at 10m (should work)
- [ ] Test at 100m if possible

**Expected:**
```
✓ Message sent: "FIRE 44.123 21.543 245"
✓ Message received at 1m
✓ Message received at 10m
✓ No corruption (CRC valid)
```

**GO/NO-GO:**
- ✅ If range ≥ 1km verified → PASS blocker #3
- ❌ If range < 100m → Troubleshoot antenna (1 day)

---

### BLOCKER #4: Full Integration (Week 2 Thursday-Friday)

- [ ] Thermal camera → Pi 4 ✓
- [ ] YOLO inference → Result ✓
- [ ] Decision logic → CONFIRM/DISMISS/VALIDATE ✓
- [ ] LoRa encode → Message ✓
- [ ] LoRa transmit → Ground ✓
- [ ] Ground receive → Decode ✓
- [ ] Dashboard update → Alert ✓
- [ ] Operator decision → CONFIRM ✓

**Full loop:** Thermal → YOLO → Alert → Operator → Confirm

**Expected:**
```
✓ Full loop executes in < 5 seconds
✓ All components pass individually
✓ No surprises in integration
```

**GO/NO-GO:**
- ✅ If all 4 blockers PASS → PROCEED TO PHASE 1B
- ❌ If any blocker fails → 1-2 week troubleshoot (but low cost, only €598 spent)

---

## PHASE 1B: FIRST DRONE BUILD (Week 3-4)

**Cost: €1,200 | Time: 2 weeks | Risk reduction: 30%**

Only proceed if Phase 1A all 4 blockers PASS.

- [ ] Order drone hardware (Tarot 650, Pixhawk, etc.)
- [ ] Assemble Tarot 650 frame
- [ ] Mount Pixhawk 6C
- [ ] Mount Pi 4 + thermal + LoRa
- [ ] First flight test (tethered)
- [ ] First free flight (50m altitude, 10 min)

**GO/NO-GO (end of Week 4):**
- ✅ If drone flies 15+ min → PROCEED TO PHASE 2
- ❌ If drone crashes → Debug (1 week)

---

## PHASE 2: 5-DRONE SYSTEM (Week 5-7)

**Cost: €5,000 | Time: 3 weeks | Risk reduction: 15%**

Only proceed if Phase 1B drone flies.

- [ ] Build drones #2-5 (copy of drone #1)
- [ ] Build base station (cabinet, charger, router)
- [ ] Test all 5 drones simultaneously
- [ ] Test 12-hour continuous patrol (with battery rotation)

**GO/NO-GO (end of Week 7):**
- ✅ If 5 drones + rotation works → PROCEED TO PHASE 3
- ❌ If system unreliable → Improve (1-2 weeks)

---

## PHASE 3: REAL DEPLOYMENT (Week 8-12)

**Cost: €0 (travel) | Time: 4 weeks | Final validation**

Only proceed if Phase 2 5-drone system works.

- [ ] Week 8: Move to forest location
- [ ] Week 9-10: 24-hour continuous patrol test
- [ ] Week 11: Measure accuracy (accuracy %, false positive %)
- [ ] Week 12: Demo to fire chief, get contract

**Final gate:**
- ✅ If fire chief approves → DEPLOYMENT SUCCESS
- ❌ If accuracy too low → Extend Phase 3 (1-2 weeks)

---

## BUDGET TRACKING

```
Phase 0:      €0      ████████
Phase 1A:     €598    ████████████████
Phase 1B:     €1,200  ███████████████████████████████
Phase 2:      €5,000  ████████████████████████████████████████████████████████
Phase 3:      €0      ████████

Spent at Phase 1A gate:    €598
Spent at Phase 1B gate:    €1,798
Spent at Phase 2 gate:     €7,340 (final)
```

---

## CRITICAL TECHNICAL NOTES

**DO:**
- ✅ Use D-Fire real thermal images (not synthetic blobs)
- ✅ Use P2Pro-Viewer radiometric decoder (not cv2.VideoCapture)
- ✅ Expect 1.3 FPS on Pi 4 (realistic, not 5+ FPS)
- ✅ Expect 4 weeks to 85% accuracy (normal improvement)
- ✅ Test on real data (D-Fire) before hardware arrives
- ✅ Study P2Pro driver code before camera arrives

**DON'T:**
- ❌ Use synthetic data (trains on worthless patterns)
- ❌ Use cv2 directly on P2Pro (won't get temperatures)
- ❌ Expect 30 FPS (video game latency, unnecessary)
- ❌ Expect 95%+ accuracy in Week 1 (unrealistic)
- ❌ Order hardware before Phase 0 validation
- ❌ Ignore P2Pro-Viewer docs

---

## TIMELINE SUMMARY

```
Week -2 to 0:    Phase 0 (software validation)        €0
Week 1-2:        Phase 1A (hardware testing)          €598
Week 3-4:        Phase 1B (first drone)               €1,200
Week 5-7:        Phase 2 (5-drone system)             €5,000
Week 8-12:       Phase 3 (real deployment)            €0

TOTAL:           12 weeks, €7,340

Milestones:
  Week 0: Software validated ✓
  Week 2: Hardware works ✓
  Week 4: Drone flies ✓
  Week 7: 5 drones work ✓
  Week 12: Fire chief approval ✓
```

---

## YOU'RE READY

**Print this checklist. Check off as you go. No surprises.**

Start tonight: Download D-Fire, P2Pro-Viewer, YOLO model.
Start Monday: Phase 0 with real data, real latencies, real drivers.
Start Week 1: Order hardware (low risk, software already proven).
Target Week 8: Deploy.

This plan is bulletproof. Follow it. You'll succeed.

🚀
