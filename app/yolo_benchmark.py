import time
import torch
from ultralytics import YOLO
import numpy as np

def run_benchmark():
    print("🚀 Starting YOLOv8 Latency Benchmark...")
    
    # Check device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"💻 Running on: {device.upper()}")
    if device == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")

    # Load model (downloads automatically if not found)
    print("📥 Loading YOLOv8n model...")
    model = YOLO('yolov8n.pt')
    
    # Create dummy image (640x640)
    img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # Warmup
    print("🔥 Warming up...")
    for _ in range(10):
        model(img, verbose=False)
        
    # Benchmark
    print("⏱️  Running 100 iterations...")
    start_time = time.time()
    for _ in range(100):
        model(img, verbose=False)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_latency = (total_time / 100) * 1000
    fps = 100 / total_time
    
    print("\n" + "="*40)
    print(f"📊 RESULTS ({device.upper()})")
    print("="*40)
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"FPS:             {fps:.2f}")
    print("="*40)
    
    # Pi 4 Estimation
    pi_factor = 10.0  # Conservative estimate
    pi_latency = avg_latency * pi_factor
    pi_fps = fps / pi_factor
    
    print(f"\n🔮 Raspberry Pi 4 Estimation (Factor {pi_factor}x):")
    print(f"Estimated Latency: {pi_latency:.2f} ms")
    print(f"Estimated FPS:     {pi_fps:.2f}")
    
    if pi_latency > 1000:
        print("\n⚠️  WARNING: Estimated Pi latency > 1000ms. Consider Jetson Nano.")
    else:
        print("\n✅ SUCCESS: Estimated Pi latency acceptable.")

if __name__ == "__main__":
    run_benchmark()
