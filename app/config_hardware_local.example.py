"""
LOCAL Hardware Configuration - COPY THIS FILE!
===============================================

1. Copy this file to: config_hardware_local.py
2. Update IP addresses to match YOUR Raspberry Pi drones
3. config_hardware_local.py is gitignored (won't be uploaded)

"""

from config_hardware import DroneConfig, OperationMode

# Set to HARDWARE when ready for real drones!
CURRENT_MODE = OperationMode.HARDWARE

# Your actual Raspberry Pi drone fleet:
MY_FLEET = [
    DroneConfig(
        id="D1", 
        name="MyDrone-1",
        ip="192.168.1.101",      # <<< CHANGE TO YOUR PI's IP
        port=5760,
        is_simulated=False,
    ),
    DroneConfig(
        id="D2", 
        name="MyDrone-2", 
        ip="192.168.1.102",      # <<< CHANGE TO YOUR PI's IP
        port=5760,
        is_simulated=False,
    ),
    # Add more drones...
]

# Your network settings:
MY_NETWORK = {
    "gcs_ip": "192.168.1.100",   # <<< YOUR PC's IP
    "wifi_ssid": "MyDroneNetwork",
}



