import os
import cv2
import json
import csv
import time
from datetime import datetime

class DroneRecorder:
    def __init__(self, drone_id, base_path="recordings"):
        self.drone_id = drone_id
        self.start_time = datetime.now()
        self.patrol_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(base_path, drone_id, self.start_time.strftime("%Y-%m-%d"), self.patrol_id)
        
        # Create directories
        self.frames_path = os.path.join(self.path, "frames")
        os.makedirs(self.frames_path, exist_ok=True)
        
        # Init logs
        self.telemetry_file = os.path.join(self.path, "telemetry.csv")
        self.detections_file = os.path.join(self.path, "detections.json")
        self.metadata_file = os.path.join(self.path, "metadata.json")
        
        self._init_telemetry()
        self.detections = []
        
        print(f"🎥 Recording started for {drone_id} at {self.path}")

    def _init_telemetry(self):
        with open(self.telemetry_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'lat', 'lon', 'altitude', 'heading', 'battery', 'confidence'])

    def save_frame(self, frame, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        filename = f"frame_{int(timestamp*1000)}.jpg"
        cv2.imwrite(os.path.join(self.frames_path, filename), frame)

    def log_telemetry(self, telemetry_dict):
        # telemetry_dict expected keys: timestamp, lat, lon, alt, heading, bat, conf
        with open(self.telemetry_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                telemetry_dict.get('timestamp', time.time()),
                telemetry_dict.get('gps', [0,0])[0],
                telemetry_dict.get('gps', [0,0])[1],
                telemetry_dict.get('alt', 0),
                telemetry_dict.get('heading', 0),
                telemetry_dict.get('bat', 100),
                telemetry_dict.get('conf', 0)
            ])

    def log_detection(self, detection_data):
        self.detections.append(detection_data)
        # Write incrementally to avoid data loss
        with open(self.detections_file, 'w') as f:
            json.dump(self.detections, f, indent=2)

    def finalize(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        metadata = {
            "drone_id": self.drone_id,
            "patrol_id": self.patrol_id,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": duration,
            "total_frames": len(os.listdir(self.frames_path)),
            "total_detections": len(self.detections)
        }
        
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"✅ Recording finalized: {self.path}")
