"""
🔥 Fire Drone Swarm - Central Configuration

HOW TO USE:
-----------
1. By default, paths auto-detect based on project structure
2. For custom paths, create 'config.local.py' (copy from config.local.example.py)
3. config.local.py is gitignored - your private paths stay private

EXAMPLE config.local.py:
------------------------
DATA_PATH = "D:/my-fire-data"
MODELS_PATH = "D:/my-fire-data/models"
"""

import os
from pathlib import Path

# =============================================================================
# AUTO-DETECTED PATHS (work out-of-the-box)
# =============================================================================

# Project root (parent of app/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Default data location (assumes symlink or folder named 'data/')
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

# =============================================================================
# LOAD LOCAL OVERRIDES (if config.local.py exists)
# =============================================================================

# Try to import local config overrides
_DATA_PATH_OVERRIDE = None
_MODELS_PATH_OVERRIDE = None

try:
    from config_local import *
    _DATA_PATH_OVERRIDE = locals().get('DATA_PATH')
    _MODELS_PATH_OVERRIDE = locals().get('MODELS_PATH')
except ImportError:
    pass  # No local config, use defaults

# =============================================================================
# FINAL PATHS (use override if set, otherwise auto-detect)
# =============================================================================

# Main data directory
if _DATA_PATH_OVERRIDE:
    DATA_DIR = Path(_DATA_PATH_OVERRIDE)
else:
    DATA_DIR = DEFAULT_DATA_DIR

# Subdirectories
DATASETS_DIR = DATA_DIR / "datasets"
MODELS_DIR = _MODELS_PATH_OVERRIDE and Path(_MODELS_PATH_OVERRIDE) or DATA_DIR / "models"
PRETRAINED_DIR = MODELS_DIR / "pretrained"
WEIGHTS_DIR = DATA_DIR / "weights"
RUNS_DIR = DATA_DIR / "runs"

# =============================================================================
# MODEL PATHS
# =============================================================================

# Base model (included in repo)
BASE_MODEL_PATH = PROJECT_ROOT / "models" / "yolov8n.pt"

# Pretrained fire models (in data folder)
FIRE_MODELS = {
    "best": PRETRAINED_DIR / "yolov10_fire_smoke.pt",      # 85% mAP
    "dfire": PRETRAINED_DIR / "yolov5s_dfire.pt",          # 80% mAP
    "trained": RUNS_DIR / "train" / "fire_yolov8n" / "weights" / "best.pt",  # 72% mAP
    "small": PRETRAINED_DIR / "yolov10n_forest_fire.pt",   # Pi-ready
}

# Default model to use
DEFAULT_FIRE_MODEL = FIRE_MODELS.get("best", BASE_MODEL_PATH)

# =============================================================================
# DATASET PATHS
# =============================================================================

DATASETS = {
    "dfire": DATASETS_DIR / "Combined",
    "kaggle": DATASETS_DIR / "Kaggle_Combined", 
    "flame": DATASETS_DIR / "FLAME",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_model_path(model_name: str) -> Path:
    """Get path to a model by name or filename."""
    if model_name in FIRE_MODELS:
        return FIRE_MODELS[model_name]
    return MODELS_DIR / model_name


def get_dataset_path(dataset_name: str) -> Path:
    """Get path to a dataset by name."""
    if dataset_name in DATASETS:
        return DATASETS[dataset_name]
    return DATASETS_DIR / dataset_name


def check_paths():
    """Print path status for debugging."""
    print("=" * 60)
    print("🔥 FIRE DRONE SWARM - PATH CONFIGURATION")
    print("=" * 60)
    print(f"\n📁 PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"   Exists: {PROJECT_ROOT.exists()}")
    print(f"\n📁 DATA_DIR: {DATA_DIR}")
    print(f"   Exists: {DATA_DIR.exists()}")
    print(f"   Is symlink: {DATA_DIR.is_symlink() if DATA_DIR.exists() else 'N/A'}")
    print(f"\n📁 MODELS_DIR: {MODELS_DIR}")
    print(f"   Exists: {MODELS_DIR.exists()}")
    print(f"\n🤖 Available Models:")
    for name, path in FIRE_MODELS.items():
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {name}: {path.name}")
    print(f"\n📊 Available Datasets:")
    for name, path in DATASETS.items():
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {name}: {path}")
    print("=" * 60)


# =============================================================================
# RUN CHECK IF EXECUTED DIRECTLY
# =============================================================================

if __name__ == "__main__":
    check_paths()
