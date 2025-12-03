# 🖥️ PC Simulation Testing Plan

**Goal:** Extract maximum value from PC simulation before hardware arrives.  
**Hardware Budget Saved:** €7,340 (until we're 100% confident)

---

## 🎯 WHAT WE CAN TEST ON PC

### 1. ✅ Fire Detection Accuracy (CRITICAL)
Test YOLO on real fire/non-fire images to prove detection works.

```bash
# Test fire detection accuracy on D-Fire dataset
python scripts/test_fire_detection.py --dataset DFireDataset/test/images
```

**Metrics to measure:**
- True Positive Rate (fire detected correctly)
- False Positive Rate (non-fire flagged as fire)
- False Negative Rate (fire missed)
- Confidence threshold optimization
- Inference speed (simulate Pi 4 latency)

### 2. ✅ Patrol Patterns & Grid Sweeps
Simulate optimal patrol paths before flying real drones.

**Patterns to test:**
- Grid sweep (lawn mower pattern)
- Expanding spiral
- Random walk
- Sector-based patrol
- Perimeter patrol

### 3. ✅ Swarm Commands & Control
Test sending commands to virtual drones:
- RTL (Return to Launch)
- PAUSE / RESUME
- GO_TO (specific coordinates)
- CHANGE_ALTITUDE
- FORMATION changes

### 4. ✅ Multi-Drone Coordination
- Handoff when battery low
- Validation flights (send 2nd drone to confirm)
- Coverage optimization
- Collision avoidance zones

### 5. ✅ Communication Simulation
- Simulate LoRa range limits (drop packets beyond X km)
- Simulate interference/packet loss
- Test failsafe behaviors

### 6. ✅ Battery & Flight Time Simulation
- Simulate 18-minute flight time
- Auto-RTL when battery < 20%
- Charging/swap scheduling

### 7. ✅ Map-Based Planning
- Define patrol zones on real maps
- Calculate coverage area per drone
- Optimize drone positions for maximum coverage

---

## 🚀 IMMEDIATE TESTS TO BUILD

### TEST 1: Fire Detection Accuracy Test
**Status:** TO BUILD  
**Purpose:** Prove YOLO can detect fire vs non-fire

### TEST 2: Patrol Pattern Simulator  
**Status:** TO BUILD  
**Purpose:** Visualize and optimize patrol paths

### TEST 3: Swarm Command Interface
**Status:** TO BUILD  
**Purpose:** Send commands to virtual drones

### TEST 4: Coverage Calculator
**Status:** TO BUILD  
**Purpose:** Calculate optimal drone positions

### TEST 5: Full Mission Simulator
**Status:** TO BUILD  
**Purpose:** Simulate complete patrol mission

---

## 📊 METRICS TO CAPTURE

| Metric | Target | How to Test |
|--------|--------|-------------|
| Fire Detection Accuracy | > 90% | D-Fire test set |
| False Positive Rate | < 10% | Non-fire images |
| Inference Time | < 1000ms | Benchmark on PC, multiply by 4x |
| Coverage per Drone | ~1 km² | Map-based calculation |
| Response Time (fire→alert) | < 5 sec | End-to-end test |
| Battery Efficiency | 18 min flight | Simulated drain |

---

## 🔧 SIMULATION TOOLS TO USE

### Option 1: Pure Python Simulation (Current)
- ✅ Already have multi-drone simulation
- ✅ Real YOLO inference
- ✅ Real video frames
- Add: patrol patterns, commands, battery sim

### Option 2: Gazebo + ROS (Advanced)
- Full physics simulation
- Real drone dynamics
- Requires Ubuntu VM
- Overkill for Phase 0

### Option 3: AirSim (Microsoft)
- Photorealistic simulation
- Drone physics
- Works on Windows
- Good for advanced testing

### Option 4: DroneKit-SITL
- Simulates Pixhawk flight controller
- Can test MAVLink commands
- Good for flight logic testing

**Recommendation:** Enhance current Python simulation first, consider DroneKit-SITL for Phase 1A.

---

## 🗺️ PATROL ZONE PLANNING

### Sample Patrol Zone: Serbian Forest (10 km²)

```
┌─────────────────────────────────────────┐
│                                         │
│    Zone A        Zone B        Zone C   │
│    (Drone 1)     (Drone 2)     (Drone 3)│
│    ┌─────┐       ┌─────┐       ┌─────┐  │
│    │  █  │       │  █  │       │  █  │  │
│    │ 2km │       │ 2km │       │ 2km │  │
│    └─────┘       └─────┘       └─────┘  │
│                                         │
│    Zone D        Zone E (Base)          │
│    (Drone 4)     (Drone 5 + Charging)   │
│    ┌─────┐       ┌─────────────────┐    │
│    │  █  │       │  █  🏠 Base     │    │
│    │ 2km │       │  Charger        │    │
│    └─────┘       └─────────────────────┘│
│                                         │
└─────────────────────────────────────────┘

Each drone covers ~2 km² in grid sweep pattern
Total coverage: 10 km² with 5 drones
Rotation: 1 drone always charging
```

---

## 🎮 SWARM COMMANDS TO IMPLEMENT

| Command | Description | Simulation |
|---------|-------------|------------|
| `RTL` | Return to launch | Move drone to base |
| `RTL_ALL` | All drones return | Move all to base |
| `PAUSE` | Hover in place | Stop movement |
| `RESUME` | Continue patrol | Resume path |
| `GO_TO lat,lon` | Fly to coordinates | Move to point |
| `VALIDATE lat,lon` | Send for 2nd opinion | Send nearest drone |
| `CHANGE_ALT alt` | Change altitude | Update altitude |
| `EMERGENCY` | Land immediately | All drones land |

---

## 📈 SIMULATION PHASES

### Phase S1: Fire Detection Validation (TODAY)
- [ ] Create test script for fire/non-fire classification
- [ ] Run on D-Fire test set
- [ ] Calculate accuracy metrics
- [ ] Optimize confidence threshold

### Phase S2: Patrol Pattern Simulator (THIS WEEK)
- [ ] Implement grid sweep pattern
- [ ] Visualize on map
- [ ] Calculate coverage metrics
- [ ] Add multiple patrol patterns

### Phase S3: Swarm Commands (THIS WEEK)
- [ ] Add command interface to dashboard
- [ ] Implement RTL, PAUSE, GO_TO
- [ ] Test command delivery to drones
- [ ] Add visual feedback

### Phase S4: Full Mission Simulation (NEXT WEEK)
- [ ] 30-minute simulated patrol
- [ ] Battery drain simulation
- [ ] Auto-RTL on low battery
- [ ] Drone rotation/handoff
- [ ] Fire detection + response

### Phase S5: Hardware-in-Loop Prep (BEFORE HARDWARE)
- [ ] DroneKit-SITL integration
- [ ] MAVLink command testing
- [ ] Simulated sensor input
- [ ] End-to-end mission test

---

## 🧪 TEST SCENARIOS

### Scenario 1: Single Fire Detection
```
1. Drone A1 patrolling
2. Encounters fire image
3. YOLO detects fire (conf > 0.7)
4. Alert sent to dashboard
5. Operator confirms
6. Log event, continue patrol
```

### Scenario 2: False Positive Handling
```
1. Drone A2 patrolling
2. Detects "fire" (actually campfire/grill)
3. Alert sent to dashboard
4. Operator DISMISSES
5. Log as training data
6. Continue patrol
```

### Scenario 3: Multi-Drone Validation
```
1. Drone A1 detects possible fire (conf 0.65)
2. Operator requests validation
3. Command: VALIDATE to A2
4. A2 flies to location
5. A2 confirms/denies
6. Combined confidence reported
```

### Scenario 4: Battery Rotation
```
1. A1 battery at 25%
2. Auto-RTL triggered
3. A5 (fully charged) launches
4. A5 takes over A1's zone
5. A1 lands, begins charging
```

### Scenario 5: Communication Loss
```
1. A3 loses connection (simulated)
2. Dashboard shows "OFFLINE"
3. A3 auto-RTL after 5 min timeout
4. Dashboard shows A3 returning
5. Reconnection when in range
```

---

## 💡 VALUE EXTRACTION CHECKLIST

Before spending €598 on hardware, we should have:

- [ ] **Fire Detection:** Proven accuracy > 85% on real fire images
- [ ] **False Positives:** Rate < 15% on non-fire images
- [ ] **Patrol Coverage:** Calculated optimal zones for 10 km²
- [ ] **Command System:** All swarm commands working in simulation
- [ ] **Battery Logic:** Rotation and auto-RTL tested
- [ ] **Multi-Drone:** 5 drones coordinating without collision
- [ ] **Response Time:** Fire → Alert < 5 seconds
- [ ] **Operator Workflow:** Dashboard usable for 30-min session

If ALL these pass in simulation → **High confidence hardware will work**

---

## 🛠️ NEXT STEPS

1. **Create fire detection test script** (immediate)
2. **Add patrol patterns to simulation** (today)
3. **Add command buttons to dashboard** (today)
4. **Create coverage calculator** (this week)
5. **Run full mission simulation** (this week)

---

**Document Created:** November 28, 2024  
**Status:** Planning Complete, Ready to Implement

