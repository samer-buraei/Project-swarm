"""
Check the current training status and model performance
"""
import os
import glob

print("=" * 70)
print("🔥 TRAINING STATUS CHECK")
print("=" * 70)

# Find training runs
train_dirs = glob.glob("runs/train/*/")

if not train_dirs:
    print("❌ No training runs found!")
else:
    for train_dir in train_dirs:
        print(f"\n📁 Training Run: {train_dir}")
        
        # Check for weights
        best_pt = os.path.join(train_dir, "weights", "best.pt")
        last_pt = os.path.join(train_dir, "weights", "last.pt")
        
        if os.path.exists(best_pt):
            size = os.path.getsize(best_pt) / (1024 * 1024)
            print(f"   ✅ best.pt exists ({size:.1f} MB)")
        else:
            print("   ❌ best.pt not found")
            
        if os.path.exists(last_pt):
            size = os.path.getsize(last_pt) / (1024 * 1024)
            print(f"   ✅ last.pt exists ({size:.1f} MB)")
            
        # Check for results
        results_csv = os.path.join(train_dir, "results.csv")
        if os.path.exists(results_csv):
            with open(results_csv, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    epochs_done = len(lines) - 1  # minus header
                    print(f"   📊 Epochs completed: {epochs_done}")
                    
                    # Parse last line for metrics
                    last_line = lines[-1].strip().split(',')
                    if len(last_line) > 7:
                        try:
                            # metrics/mAP50(B) is usually column 6
                            mAP50 = float(last_line[6].strip()) if last_line[6].strip() else 0
                            print(f"   📈 Latest mAP50: {mAP50:.3f}")
                        except:
                            pass

# Check available models
print("\n" + "=" * 70)
print("📦 AVAILABLE MODELS")
print("=" * 70)

for pattern in ["runs/train/**/weights/*.pt", "models/**/*.pt", "*.pt"]:
    for path in glob.glob(pattern, recursive=True):
        size = os.path.getsize(path) / (1024 * 1024)
        print(f"  ✓ {path} ({size:.1f} MB)")

# Quick commands
print("\n" + "=" * 70)
print("🚀 QUICK COMMANDS")
print("=" * 70)
print("""
# Test with webcam (current best model):
py test_all_models.py

# Test with specific model:
py live_camera_fire_test.py --model runs/train/fire_yolov8n/weights/best.pt

# Continue monitoring training:
# (Training is running in background terminal)
""")

