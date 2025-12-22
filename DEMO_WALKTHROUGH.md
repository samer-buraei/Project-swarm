# 🎙️ Investor Demo Walkthrough Script

## 🎯 Goal
Demonstrate that we have a **working 5-drone swarm** that can be controlled from a web dashboard, plan missions, and detect fires using AI.

---

## 🚀 Setup (2 Minutes)
1.  **Double-click `run_demo.bat`**.
2.  Wait for 3 windows to open:
    - **Main Terminal**: Launches the drones (you'll see "Starting D1...", "Starting D2...").
    - **Browser**: Opens **Fleet Control** (http://localhost:8506).
    - **Browser**: Opens **Mission Planner** (http://localhost:8507).
3.  Wait until the Main Terminal says:
    > `✅ ALL DRONES LAUNCHED!`

---

## 🎬 Checkpoint 1: "The Swarm is Live"
**Goal:** Show connectivity and real-time status.

1.  Go to **Fleet Control Dashboard** (http://localhost:8506).
2.  Click **"🔗 Connect All Drones"** (Top Left).
3.  **Narrative:** *"Here you see our 5 simulated drones coming online. We have full telemetry: altitude, battery, location, and status."*
4.  Point out the **Map**: *"They are currently sitting at our base station in Belgrade."*

---

## 🎬 Checkpoint 2: "Simple Control"
**Goal:** Show we can control them easily.

1.  Click **"🛫 TAKEOFF ALL"** (Left Panel).
2.  Watch the Altitude numbers rise to ~50m.
3.  **Narrative:** *"With a single click, the entire swarm arms and takes off to patrol altitude."*
4.  Switch dropdown (Right Panel) to **"D1 - Alpha"**.
5.  Use the **Manual Nudge** arrows (Right Panel) to move D1 slightly.
6.  **Narrative:** *"We can also take individual control. I'm nudging Alpha drone to the North."*

---

## 🎬 Checkpoint 3: "Mission Planning"
**Goal:** Show intelligent autonomous patrol.

1.  Switch tab to **Mission Planner** (http://localhost:8507).
2.  **Narrative:** *"This is where we plan the search area."*
3.  Click markers on the map to draw a polygon (around the drones).
4.  Click **"Generate Grid"**.
5.  Show the zig-zag path appearing.
6.  Click **"💾 Save Mission"** -> Name it `Investor_Demo`.

---

## 🎬 Checkpoint 4: "Mission Execution"
**Goal:** Show the swarm executing the plan.

1.  Go back to **Fleet Control**.
2.  In **Mission Control** (Right Panel), click refresh (or minimal refresh needed).
3.  Select **"Investor_Demo.json"** from the dropdown.
4.  Click **"📂 Load Mission"**.
    - You will see the orange path appear on the map.
5.  Click **"🚀 EXECUTE MISSION"**.
6.  **Narrative:** *"The swarm now autonomously executes the search pattern. If any drone finds a fire, it alerts the base."*

---

## 🎬 Checkpoint 5: "Fire Detection" (Optional / Q&A)
**Goal:** Prove the AI works.

1.  **Narrative:** *"While they fly, our YOLOv8 AI is processing video feeds in real-time."*
2.  (If challenged to show it):
    - Open a new terminal.
    - Run: `cd app` then `py fire_detector_unified.py --mode thermal`.
    - Show the camera window detecting fire.

---

## 🏁 Closing
1.  Click **"🏠 RTL ALL"** (Return to Launch).
2.  Watch them come back and land.
3.  **Narrative:** *"Mission complete. The swarm returns home automatically."*
