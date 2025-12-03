"""
🔥 QUICK FIRE DETECTION MODEL TRAINING
======================================
Trains YOLOv8n to detect fire and smoke.

Usage:
    python train_fire_quick.py                 # Quick test (5 epochs)
    python train_fire_quick.py --epochs 50     # More training
    python train_fire_quick.py --epochs 100    # Full training
"""

from ultralytics import YOLO
import argparse
from pathlib import Path


def train_fire_model(epochs=5, batch=16, imgsz=640, resume=False):
    print("=" * 60)
    print("🔥 FIRE DETECTION MODEL TRAINING")
    print("=" * 60)
    
    data_yaml = Path("datasets/Combined/data.yaml")
    if not data_yaml.exists():
        print("❌ Dataset not found! Run: python download_fire_datasets.py --organize")
        return None
    
    print(f"\n📊 Training Configuration:")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch}")
    print(f"   Image size: {imgsz}")
    print(f"   Dataset: {data_yaml}")
    
    # Count images
    train_imgs = len(list(Path("datasets/Combined/train/images").glob("*.*")))
    val_imgs = len(list(Path("datasets/Combined/val/images").glob("*.*")))
    print(f"   Train images: {train_imgs:,}")
    print(f"   Val images: {val_imgs:,}")
    
    print("\n🚀 Starting training...")
    print("   (This will take a while - watch the progress below)\n")
    
    # Load pretrained YOLOv8n
    model = YOLO("yolov8n.pt")
    
    # Train on fire dataset
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name="fire_yolov8n",
        project="runs/train",
        patience=20,
        save=True,
        plots=True,
        verbose=True,
        # Optimization for faster training
        workers=4,
        cache=True,  # Cache images in RAM for faster training
        amp=True,    # Mixed precision training
    )
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    
    # Find best model
    best_model = Path("runs/train/fire_yolov8n/weights/best.pt")
    if best_model.exists():
        print(f"\n📦 Best model saved to: {best_model}")
        print(f"\n💡 To use this model for live detection:")
        print(f"   python live_camera_fire_test.py --model {best_model}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Train fire detection model")
    parser.add_argument("--epochs", type=int, default=5, 
                        help="Number of epochs (default: 5 for quick test)")
    parser.add_argument("--batch", type=int, default=16, 
                        help="Batch size (default: 16, reduce if OOM)")
    parser.add_argument("--imgsz", type=int, default=640, 
                        help="Image size (default: 640)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    
    args = parser.parse_args()
    
    train_fire_model(
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        resume=args.resume
    )


if __name__ == "__main__":
    main()

