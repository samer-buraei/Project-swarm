from ultralytics import YOLO
import sys

try:
    print("Attempting to load model from Hugging Face...")
    # Try loading directly using the HF repo ID
    # Note: Ultralytics usually requires 'hf-model-id' or just the name if supported
    # Trying the standard format
    model = YOLO("https://huggingface.co/touati-kamel/yolov8s-forest-fire-detection")
    print("SUCCESS: Loaded via URL")
except Exception as e:
    print(f"FAILED URL: {e}")
    try:
        model = YOLO("touati-kamel/yolov8s-forest-fire-detection") 
        print("SUCCESS: Loaded via ID")
    except Exception as e2:
        print(f"FAILED ID: {e2}")
