"""
Test ArduPilot SITL Connection

This connects to a simulated Pixhawk and flies a mission!
Run this AFTER starting SITL:
    python -m dronekit_sitl copter --home=44.8125,20.4612,0,0

Usage:
    python test_sitl.py
"""

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

def main():
    print("=" * 60)
    print("🚁 ARDUPILOT SITL TEST - SIMULATED PIXHAWK")
    print("=" * 60)
    
    # Connect to SITL
    print("\n📡 Connecting to SITL on tcp:127.0.0.1:5760...")
    try:
        vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True, timeout=60)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure SITL is running:")
        print("   python -m dronekit_sitl copter --home=44.8125,20.4612,0,0")
        return
    
    print("✅ Connected to simulated Pixhawk!")
    
    # Print vehicle info
    print("\n📊 VEHICLE STATUS:")
    print(f"   Firmware: {vehicle.version}")
    print(f"   GPS: {vehicle.gps_0}")
    print(f"   Battery: {vehicle.battery}")
    print(f"   Mode: {vehicle.mode.name}")
    print(f"   Armed: {vehicle.armed}")
    print(f"   Location: {vehicle.location.global_frame}")
    
    # Wait for GPS
    print("\n🛰️ Waiting for GPS fix...")
    while vehicle.gps_0.fix_type < 3:
        print(f"   GPS Fix: {vehicle.gps_0.fix_type}, Satellites: {vehicle.gps_0.satellites_visible}")
        time.sleep(1)
    print(f"✅ GPS Fix acquired! Satellites: {vehicle.gps_0.satellites_visible}")
    
    # Arm the drone
    print("\n🔓 Arming drone...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    
    timeout = 30
    while not vehicle.armed and timeout > 0:
        print(f"   Waiting for arming... (mode: {vehicle.mode.name})")
        time.sleep(1)
        timeout -= 1
    
    if not vehicle.armed:
        print("❌ Failed to arm!")
        vehicle.close()
        return
        
    print("✅ ARMED!")
    
    # Takeoff
    target_altitude = 50
    print(f"\n🛫 Taking off to {target_altitude}m...")
    vehicle.simple_takeoff(target_altitude)
    
    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"   Altitude: {alt:.1f}m / {target_altitude}m")
        if alt >= target_altitude * 0.95:
            print("✅ Target altitude reached!")
            break
        time.sleep(1)
    
    # Fly to waypoints (around Belgrade base)
    waypoints = [
        (44.8135, 20.4622),  # Point 1 - NE
        (44.8135, 20.4602),  # Point 2 - NW
        (44.8115, 20.4602),  # Point 3 - SW
        (44.8115, 20.4622),  # Point 4 - SE
    ]
    
    print(f"\n📍 Flying patrol pattern ({len(waypoints)} waypoints)...")
    
    for i, (lat, lon) in enumerate(waypoints):
        print(f"\n   → Waypoint {i+1}: ({lat}, {lon})")
        target = LocationGlobalRelative(lat, lon, target_altitude)
        vehicle.simple_goto(target, groundspeed=10)
        
        # Wait to reach waypoint
        while True:
            loc = vehicle.location.global_relative_frame
            dist = ((loc.lat - lat)**2 + (loc.lon - lon)**2) ** 0.5 * 111000  # approx meters
            print(f"      Distance: {dist:.0f}m | Speed: {vehicle.groundspeed:.1f} m/s")
            if dist < 10:  # Within 10 meters
                print(f"   ✅ Reached waypoint {i+1}")
                break
            time.sleep(1)
    
    # Return to launch
    print("\n🏠 Returning to launch...")
    vehicle.mode = VehicleMode("RTL")
    
    while vehicle.armed:
        alt = vehicle.location.global_relative_frame.alt
        print(f"   Altitude: {alt:.1f}m | Mode: {vehicle.mode.name}")
        if alt < 1:
            break
        time.sleep(1)
    
    print("✅ Landed!")
    
    # Close connection
    vehicle.close()
    print("\n✅ Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

