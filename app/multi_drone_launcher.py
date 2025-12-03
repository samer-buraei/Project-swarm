import subprocess
import time
import sys
import os

import argparse

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description='Multi-Drone Launcher')
parser.add_argument('--record', action='store_true', help='Enable recording for all drones')
args = parser.parse_args()

# --- FLEET CONFIGURATION ---
DRONES = [
    {"id": "A1", "port": 5001, "start_idx": 0,    "file": "live_frame_A1.jpg"},
    {"id": "A2", "port": 5002, "start_idx": 500,  "file": "live_frame_A2.jpg"},
    {"id": "A3", "port": 5003, "start_idx": 1000, "file": "live_frame_A3.jpg"},
    {"id": "A4", "port": 5004, "start_idx": 1500, "file": "live_frame_A4.jpg"},
    {"id": "A5", "port": 5005, "start_idx": 2000, "file": "live_frame_A5.jpg"},
]

processes = []

def launch_fleet():
    print(f"🚀 LAUNCHING FLEET OF {len(DRONES)} DRONES...")
    print("=" * 50)
    
    for drone in DRONES:
        cmd = [
            sys.executable, "simulation.py",
            "--id", drone["id"],
            "--port", str(drone["port"]),
            "--file", drone["file"],
            "--start_index", str(drone["start_idx"])
        ]
        
        if args.record:
            cmd.append("--record")
        
        print(f"   [+] Launching Drone {drone['id']} on Port {drone['port']}...")
        # Launch as independent process
        p = subprocess.Popen(cmd)
        processes.append(p)
        time.sleep(1) # Stagger launch slightly

    print("=" * 50)
    print("✅ FLEET AIRBORNE.")
    print("   Press Ctrl+C to land all drones.")

def cleanup():
    print("\n🛑 LANDING FLEET...")
    for p in processes:
        p.terminate()
    print("✅ All drones landed.")

if __name__ == "__main__":
    try:
        launch_fleet()
        # Keep main process alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
