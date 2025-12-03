import time
import math
import json

class DroneController:
    """
    Unified Drone Control API.
    Works for:
    1. Internal Simulation (patrol_simulator.py)
    2. MAVLink/Pixhawk (via pymavlink/dronekit) - Placeholder
    """
    
    def __init__(self, drone_id, connection_string=None):
        self.id = drone_id
        self.conn_str = connection_string
        self.state = "DISARMED"
        self.pos = [0, 0]
        self.alt = 0
        
        if connection_string:
            print(f"🔌 Connecting to drone {drone_id} at {connection_string}...")
            # self.vehicle = connect(connection_string, wait_ready=True)
            self.mode = "REAL"
        else:
            print(f"💻 Initializing VIRTUAL drone {drone_id}...")
            self.mode = "SIM"

    def arm_and_takeoff(self, target_altitude):
        print(f"[{self.id}] Arming motors...")
        time.sleep(1)
        print(f"[{self.id}] Taking off to {target_altitude}m...")
        self.state = "FLYING"
        self.alt = target_altitude
        time.sleep(2)
        print(f"[{self.id}] Reached target altitude.")

    def goto(self, lat, lon):
        print(f"[{self.id}] Moving to {lat}, {lon}...")
        self.pos = [lat, lon]
        time.sleep(1) # Sim travel time

    def rtl(self):
        print(f"[{self.id}] Returning to Launch (RTL)...")
        self.state = "RTL"
        time.sleep(2)
        self.state = "LANDED"
        print(f"[{self.id}] Landed.")

    def set_mode(self, mode):
        print(f"[{self.id}] Switching mode to {mode}")
        self.state = mode

# Example Usage
if __name__ == "__main__":
    drone = DroneController("A1")
    drone.arm_and_takeoff(10)
    drone.goto(44.8125, 20.4612)
    drone.rtl()
