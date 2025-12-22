"""
Hardware Configuration for Real Raspberry Pi Drones
====================================================

This file configures connections to REAL drone hardware.
Copy to config_hardware_local.py and customize for your setup.

Each Raspberry Pi drone needs:
- Flight controller (Pixhawk, ArduPilot, etc.)
- MAVLink connection exposed via MAVProxy
- Static IP on your network
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

# ============== OPERATION MODE ==============

class OperationMode(Enum):
    SIMULATION = "simulation"      # DroneKit-SITL on localhost
    HARDWARE = "hardware"          # Real Raspberry Pi drones
    HYBRID = "hybrid"              # Mix of simulated and real

# Set your current mode here:
CURRENT_MODE = OperationMode.SIMULATION  # Change to HARDWARE for real drones


# ============== DRONE CONFIGURATION ==============

@dataclass
class DroneConfig:
    """Configuration for a single drone"""
    id: str                        # Unique identifier (D1, D2, etc.)
    name: str                      # Human-readable name
    ip: str                        # IP address (127.0.0.1 for simulation)
    port: int                      # MAVLink port (usually 5760)
    is_simulated: bool = True      # True for SITL, False for real hardware
    
    # Hardware-specific settings
    pi_username: str = "pi"        # SSH username for Raspberry Pi
    pi_password: str = ""          # SSH password (use keys in production!)
    camera_port: int = 8080        # Video stream port
    telemetry_rate: int = 10       # Hz for telemetry updates
    
    @property
    def connection_string(self) -> str:
        """Get MAVLink connection string"""
        return f"tcp:{self.ip}:{self.port}"
    
    @property
    def video_url(self) -> str:
        """Get video stream URL"""
        return f"http://{self.ip}:{self.camera_port}/stream"


# ============== SIMULATION FLEET (DEFAULT) ==============

SIMULATION_FLEET: List[DroneConfig] = [
    DroneConfig(id="D1", name="Alpha",   ip="127.0.0.1", port=5760, is_simulated=True),
    DroneConfig(id="D2", name="Bravo",   ip="127.0.0.1", port=5770, is_simulated=True),
    DroneConfig(id="D3", name="Charlie", ip="127.0.0.1", port=5780, is_simulated=True),
    DroneConfig(id="D4", name="Delta",   ip="127.0.0.1", port=5790, is_simulated=True),
    DroneConfig(id="D5", name="Echo",    ip="127.0.0.1", port=5800, is_simulated=True),
]


# ============== HARDWARE FLEET (CUSTOMIZE THIS) ==============

HARDWARE_FLEET: List[DroneConfig] = [
    # Example configuration for real Raspberry Pi drones
    # Update IP addresses to match your network setup
    
    DroneConfig(
        id="D1", 
        name="FireHawk-1",
        ip="192.168.1.101",       # <<< YOUR PI #1 IP
        port=5760,
        is_simulated=False,
        pi_username="pi",
        camera_port=8080,
        telemetry_rate=10
    ),
    DroneConfig(
        id="D2", 
        name="FireHawk-2",
        ip="192.168.1.102",       # <<< YOUR PI #2 IP
        port=5760,
        is_simulated=False,
        pi_username="pi",
        camera_port=8080,
        telemetry_rate=10
    ),
    DroneConfig(
        id="D3", 
        name="FireHawk-3",
        ip="192.168.1.103",       # <<< YOUR PI #3 IP
        port=5760,
        is_simulated=False,
        pi_username="pi",
        camera_port=8080,
        telemetry_rate=10
    ),
    # Add more drones as needed...
]


# ============== NETWORK SETTINGS ==============

NETWORK_CONFIG = {
    # Ground Control Station (your PC)
    "gcs_ip": "192.168.1.100",        # Your PC's IP on drone network
    "gcs_port": 14550,                 # GCS listening port
    
    # Network timeouts
    "connection_timeout": 10,          # Seconds to wait for drone connection
    "heartbeat_timeout": 5,            # Seconds before marking drone offline
    "reconnect_interval": 3,           # Seconds between reconnection attempts
    
    # WiFi network (for reference)
    "wifi_ssid": "DroneSwarm_Network", # Your drone network SSID
    "wifi_channel": 6,                 # WiFi channel (1, 6, or 11 recommended)
}


# ============== SAFETY SETTINGS ==============

SAFETY_CONFIG = {
    # Geofence (meters from home position)
    "max_distance": 500,               # Maximum distance from home
    "max_altitude": 120,               # Maximum altitude (check local laws!)
    "min_altitude": 10,                # Minimum altitude during flight
    
    # Battery
    "battery_warning": 30,             # Warning at 30%
    "battery_critical": 15,            # RTL at 15%
    "battery_emergency": 10,           # Land immediately at 10%
    
    # Failsafes
    "enable_geofence": True,
    "enable_battery_failsafe": True,
    "enable_gcs_failsafe": True,       # RTL if GCS connection lost
    "gcs_timeout": 30,                 # Seconds before GCS failsafe triggers
}


# ============== HELPER FUNCTIONS ==============

def get_active_fleet() -> List[DroneConfig]:
    """Get the fleet based on current operation mode"""
    if CURRENT_MODE == OperationMode.SIMULATION:
        return SIMULATION_FLEET
    elif CURRENT_MODE == OperationMode.HARDWARE:
        return HARDWARE_FLEET
    else:  # HYBRID - combine both
        return SIMULATION_FLEET + HARDWARE_FLEET


def get_drone_by_id(drone_id: str) -> Optional[DroneConfig]:
    """Get a specific drone configuration by ID"""
    for drone in get_active_fleet():
        if drone.id == drone_id:
            return drone
    return None


def get_connection_strings() -> dict:
    """Get all drone connection strings as a dictionary"""
    return {d.id: d.connection_string for d in get_active_fleet()}


# ============== RASPBERRY PI SETUP COMMANDS ==============

RASPBERRY_PI_SETUP = """
# ================================================
# RASPBERRY PI DRONE SETUP INSTRUCTIONS
# ================================================

# 1. Install MAVProxy on each Raspberry Pi:
sudo apt-get update
sudo apt-get install python3-pip
pip3 install MAVProxy

# 2. Connect flight controller to Pi via USB or serial:
#    - USB: /dev/ttyUSB0 or /dev/ttyACM0
#    - Serial: /dev/ttyAMA0 (disable Pi's serial console first)

# 3. Start MAVProxy to expose MAVLink over network:
mavproxy.py --master=/dev/ttyUSB0 --baudrate=57600 --out=tcpin:0.0.0.0:5760

# 4. For auto-start on boot, create systemd service:
# /etc/systemd/system/mavproxy.service
# [Unit]
# Description=MAVProxy
# After=network.target
#
# [Service]
# ExecStart=/usr/local/bin/mavproxy.py --master=/dev/ttyUSB0 --baudrate=57600 --out=tcpin:0.0.0.0:5760
# Restart=always
#
# [Install]
# WantedBy=multi-user.target

# 5. Enable and start service:
sudo systemctl enable mavproxy
sudo systemctl start mavproxy

# 6. Set static IP on each Pi:
# Edit /etc/dhcpcd.conf:
# interface wlan0
# static ip_address=192.168.1.101/24
# static routers=192.168.1.1
# static domain_name_servers=192.168.1.1

# 7. Test connection from your PC:
# python -c "from dronekit import connect; v=connect('tcp:192.168.1.101:5760'); print(v.version)"
"""


# ============== PRINT CONFIG ON IMPORT ==============

if __name__ == "__main__":
    print("=" * 60)
    print("🚁 FIRE SWARM HARDWARE CONFIGURATION")
    print("=" * 60)
    print(f"\n📡 Current Mode: {CURRENT_MODE.value.upper()}")
    print(f"\n🔧 Active Fleet ({len(get_active_fleet())} drones):")
    for drone in get_active_fleet():
        status = "🖥️ SIM" if drone.is_simulated else "🚁 REAL"
        print(f"   {status} {drone.id} ({drone.name}): {drone.connection_string}")
    
    print(f"\n🌐 Network Config:")
    print(f"   GCS IP: {NETWORK_CONFIG['gcs_ip']}")
    print(f"   Connection Timeout: {NETWORK_CONFIG['connection_timeout']}s")
    
    print(f"\n⚠️ Safety Limits:")
    print(f"   Max Distance: {SAFETY_CONFIG['max_distance']}m")
    print(f"   Max Altitude: {SAFETY_CONFIG['max_altitude']}m")
    print(f"   Battery Critical: {SAFETY_CONFIG['battery_critical']}%")
    print("=" * 60)

