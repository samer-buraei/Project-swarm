"""
FIRE SWARM - MULTI-DRONE SITL LAUNCHER
=======================================
Launches 5 ArduPilot SITL instances on different ports.

Usage:
    python launch_fleet.py

This will start:
    - Drone 1: Port 5760 (Home: 44.8125, 20.4612)
    - Drone 2: Port 5770 (Home: 44.8135, 20.4622)
    - Drone 3: Port 5780 (Home: 44.8115, 20.4602)
    - Drone 4: Port 5790 (Home: 44.8140, 20.4592)
    - Drone 5: Port 5800 (Home: 44.8110, 20.4632)
"""

import subprocess
import sys
import time
import os
import signal

# Configuration
DRONES = [
    {"id": "D1", "port": 5760, "lat": 44.8125, "lon": 20.4612, "instance": 0},
    {"id": "D2", "port": 5770, "lat": 44.8135, "lon": 20.4622, "instance": 1},
    {"id": "D3", "port": 5780, "lat": 44.8115, "lon": 20.4602, "instance": 2},
    {"id": "D4", "port": 5790, "lat": 44.8140, "lon": 20.4592, "instance": 3},
    {"id": "D5", "port": 5800, "lat": 44.8110, "lon": 20.4632, "instance": 4},
]

processes = []

def launch_sitl(drone):
    """Launch a single SITL instance"""
    cmd = [
        sys.executable, "-m", "dronekit_sitl", "copter",
        f"--home={drone['lat']},{drone['lon']},0,0",
        f"-I{drone['instance']}"
    ]
    
    print(f"🚁 Starting {drone['id']} on port {drone['port']}...")
    print(f"   Home: ({drone['lat']}, {drone['lon']})")
    
    # Start process
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    return proc

def main():
    print("=" * 60)
    print("🔥 FIRE SWARM - MULTI-DRONE SITL LAUNCHER")
    print("=" * 60)
    print(f"\nLaunching {len(DRONES)} simulated drones...\n")
    
    # Kill any existing SITL instances
    if os.name == 'nt':
        os.system("taskkill /F /IM apm.exe 2>nul")
    else:
        os.system("pkill -f apm.exe 2>/dev/null")
    
    time.sleep(2)
    
    # Launch all drones
    for drone in DRONES:
        proc = launch_sitl(drone)
        processes.append(proc)
        time.sleep(3)  # Wait between launches
    
    print("\n" + "=" * 60)
    print("✅ ALL DRONES LAUNCHED!")
    print("=" * 60)
    print("\n📡 Connection Ports:")
    for drone in DRONES:
        print(f"   {drone['id']}: tcp:127.0.0.1:{drone['port']}")
    
    print("\n🎮 To control the fleet:")
    print("   streamlit run dashboard_fleet_real.py")
    print("\n⚠️  Press Ctrl+C to stop all drones")
    print("=" * 60)
    
    # Wait for Ctrl+C
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    print(f"⚠️  Drone {DRONES[i]['id']} stopped unexpectedly")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down fleet...")
        
        # Kill all processes
        for proc in processes:
            try:
                proc.terminate()
            except:
                pass
        
        # Kill any remaining apm.exe
        if os.name == 'nt':
            os.system("taskkill /F /IM apm.exe 2>nul")
        
        print("✅ All drones stopped")

if __name__ == "__main__":
    main()

