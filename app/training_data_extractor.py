import os
import json
import shutil
import argparse

def extract_training_data(recordings_path, output_path):
    print("⛏️ Extracting training data from recordings...")
    
    confirmed_path = os.path.join(output_path, "confirmed_fires")
    false_pos_path = os.path.join(output_path, "false_positives")
    
    os.makedirs(confirmed_path, exist_ok=True)
    os.makedirs(false_pos_path, exist_ok=True)
    
    # Walk through all recordings
    for root, dirs, files in os.walk(recordings_path):
        if "metadata.json" in files:
            # This is a patrol folder
            meta_path = os.path.join(root, "metadata.json")
            detections_path = os.path.join(root, "detections.json")
            frames_dir = os.path.join(root, "frames")
            
            if os.path.exists(detections_path):
                with open(detections_path, 'r') as f:
                    detections = json.load(f)
                    
                for det in detections:
                    # Check for operator decision
                    decision = det.get("operator_decision", "UNKNOWN")
                    timestamp = det.get("timestamp")
                    
                    # Find corresponding frame (approximate match)
                    # In a real system, we'd map timestamps precisely
                    # Here we assume frame filename contains timestamp
                    
                    if decision == "CONFIRM":
                        print(f"   Found CONFIRMED FIRE at {timestamp}")
                        # Copy frame to confirmed_fires
                        # shutil.copy(...)
                    elif decision == "DISMISS":
                        print(f"   Found FALSE POSITIVE at {timestamp}")
                        # Copy frame to false_positives
                        # shutil.copy(...)

    print("✅ Extraction complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--recordings", default="recordings", help="Path to recordings")
    parser.add_argument("--output", default="datasets/OurData", help="Output path")
    args = parser.parse_args()
    
    extract_training_data(args.recordings, args.output)
