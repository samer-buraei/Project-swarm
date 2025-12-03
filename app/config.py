import os
from pathlib import Path

# Base directory is the parent of the directory containing this file (app/)
# So BASE_DIR is the root of the repo
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"

# Subdirectories
DATASETS_DIR = DATA_DIR / "datasets"
MODELS_DIR = DATA_DIR / "models"
WEIGHTS_DIR = DATA_DIR / "weights"

# Specific files
YOLO_MODEL_PATH = DATA_DIR / "yolov8n.pt"
FIRE_MODEL_PATH = DATA_DIR / "yolo11n.pt" # Or whatever the main fire model is

def get_model_path(model_name):
    """Returns the path to a model file in the models directory."""
    return MODELS_DIR / model_name

def get_dataset_path(dataset_name):
    """Returns the path to a dataset directory."""
    return DATASETS_DIR / dataset_name
