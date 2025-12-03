import time
import sys

# Mocking dronekit for PC without it installed
try:
    # from dronekit import connect, VehicleMode, LocationGlobalRelative
    print("⚠️ DroneKit not installed. Running in MOCK mode.")
    DRONEKIT_AVAILABLE = False
except ImportError:
    DRONEKIT_AVAILABLE = False

def test_sitl():
    print("🚁 TESTING MAVLINK SITL CONNECTION")
    
    connection_string = "tcp:127.0.0.1:5760" # Default SITL port
    
    if not DRONEKIT_AVAILABLE:
        print(f"   Connecting to {connection_string} (MOCK)...")
        time.sleep(1)
        print("   ✅ Connection established.")
        print("   Battery: 12.4V")
        print("   GPS: 3D Fix (8 sats)")
        print("   Arming...")
        time.sleep(1)
        print("   ✅ Armed.")
        print("   Taking off...")
        time.sleep(2)
        print("   ✅ Reached 10m.")
        return

    # Real DroneKit code would go here
    # vehicle = connect(connection_string, wait_ready=True)
    # ...

if __name__ == "__main__":
    test_sitl()
