# SITL Setup Guide (Software In The Loop)

## Overview
SITL allows you to run ArduPilot on your PC, simulating the flight controller hardware. This lets us test `drone_control.py` without risking a real drone.

## Prerequisites
1.  **Mission Planner** (Windows)
    *   Download: https://ardupilot.org/planner/docs/mission-planner-installation.html
2.  **Python 3.10+**
3.  **MAVProxy** (Optional, for advanced routing)

## Setting up Simulation in Mission Planner
1.  Open Mission Planner.
2.  Go to the **Simulation** tab.
3.  Select **Multirotor**.
4.  Click **Plane/Quad** icon to download firmware.
5.  Click **Run**.
6.  The simulator will start and open a TCP port (usually 5760).

## Connecting Python Script
1.  Ensure `dronekit` is installed:
    ```bash
    pip install dronekit
    ```
2.  Run the test script:
    ```bash
    python test_sitl_mavlink.py
    ```
3.  If successful, you should see the drone arm and takeoff in the console (and on the Mission Planner map).

## Next Steps
*   Integrate `drone_control.py` with the real `simulation.py` logic.
*   Test failsafes (battery low, RC lost).
