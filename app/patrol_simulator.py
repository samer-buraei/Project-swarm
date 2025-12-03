import time
import json
import math
import argparse
import os
import random

# --- CONFIGURATION ---
DRONES = ["A1", "A2", "A3", "A4", "A5"]
CENTER_LAT = 44.8125
CENTER_LON = 20.4612
RADIUS = 0.01 # Approx 1km

class Drone:
    def __init__(self, drone_id, start_lat, start_lon):
        self.id = drone_id
        self.lat = start_lat
        self.lon = start_lon
        self.state = "PATROL" # PATROL, RTL, PAUSE, LANDED
        self.battery = 100.0
        self.heading = 0
        self.speed = 0.0001
        self.target = None
        
    def update(self):
        if self.state == "PAUSE" or self.state == "LANDED":
            return

        if self.state == "RTL":
            # Move towards center
            dx = CENTER_LAT - self.lat
            dy = CENTER_LON - self.lon
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 0.0001:
                self.state = "LANDED"
                print(f"🛬 {self.id} LANDED at Base")
            else:
                self.lat += (dx/dist) * self.speed
                self.lon += (dy/dist) * self.speed
                
        elif self.state == "PATROL":
            # Simple circular patrol
            self.heading += 0.05
            self.lat = CENTER_LAT + math.sin(self.heading + DRONES.index(self.id)) * RADIUS
            self.lon = CENTER_LON + math.cos(self.heading + DRONES.index(self.id)) * RADIUS
            
        # Battery drain
        self.battery -= 0.01
        if self.battery < 20 and self.state != "RTL" and self.state != "LANDED":
            print(f"🔋 {self.id} LOW BATTERY - Returning to Launch")
            self.state = "RTL"

    def save_state(self):
        data = {
            "id": self.id,
            "gps": [self.lat, self.lon],
            "fire": False, # Sim fire logic later
            "conf": 0.0,
            "fps": 30.0,
            "battery": self.battery,
            "state": self.state,
            "timestamp": time.strftime("%H:%M:%S")
        }
        with open(f"drone_state_{self.id}.json", "w") as f:
            json.dump(data, f)

def main(interactive=False):
    print("🚁 PATROL SIMULATOR STARTED")
    print(f"   Managing {len(DRONES)} drones around {CENTER_LAT}, {CENTER_LON}")
    
    fleet = [Drone(d, CENTER_LAT, CENTER_LON) for d in DRONES]
    
    try:
        while True:
            # Check for commands
            if os.path.exists("fleet_command.json"):
                try:
                    with open("fleet_command.json", "r") as f:
                        cmd_data = json.load(f)
                    
                    # Simple command handling
                    cmd = cmd_data.get("command")
                    if cmd == "RTL_ALL":
                        for d in fleet: d.state = "RTL"
                        print("📥 COMMAND: RTL ALL")
                    elif cmd == "PAUSE_ALL":
                        for d in fleet: d.state = "PAUSE"
                        print("⏸️ COMMAND: PAUSE ALL")
                    elif cmd == "RESUME_ALL":
                        for d in fleet: d.state = "PATROL"
                        print("▶️ COMMAND: RESUME ALL")
                    elif cmd == "EMERGENCY":
                        for d in fleet: d.state = "LANDED"
                        print("🚨 COMMAND: EMERGENCY LAND")
                        
                    # Clear command
                    os.remove("fleet_command.json")
                except:
                    pass

            # Update fleet
            for drone in fleet:
                drone.update()
                drone.save_state()
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("🛑 Simulation stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default="sector")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()
    
    main(args.interactive)
