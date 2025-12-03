"""
VIDEO FIRE DETECTION TESTER
===========================
Test fire detection on any video file!

Supports:
- Local video files (MP4, AVI, MOV, MKV)
- Webcam (use --webcam)
- Image folders

Usage:
    python test_video.py path/to/video.mp4
    python test_video.py path/to/video.mp4 --save-output
    python test_video.py --webcam
    python test_video.py path/to/images/folder

Tip: Download drone fire footage from YouTube using:
    pip install yt-dlp
    yt-dlp -f mp4 "https://youtube.com/watch?v=VIDEO_ID" -o fire_video.mp4
"""

import cv2
import time
import sys
import os
import argparse
import glob
from datetime import datetime

def test_video(source, save_output=False, confidence_threshold=0.3):
    print("=" * 60)
    print("🔥 VIDEO FIRE DETECTION TESTER")
    print("=" * 60)
    
    # Load YOLO
    print("\n📥 Loading YOLO model...")
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')
    print("✅ Model loaded")
    
    # Determine source type
    if source == "webcam" or source == "0":
        print("\n📷 Opening webcam...")
        cap = cv2.VideoCapture(0)
        source_name = "webcam"
    elif os.path.isdir(source):
        print(f"\n📂 Loading images from folder: {source}")
        images = sorted(glob.glob(os.path.join(source, "*.jpg")) + 
                       glob.glob(os.path.join(source, "*.png")))
        if not images:
            print("❌ No images found!")
            return
        print(f"   Found {len(images)} images")
        cap = None
        source_name = os.path.basename(source)
    else:
        print(f"\n🎬 Opening video: {source}")
        if not os.path.exists(source):
            print(f"❌ File not found: {source}")
            return
        cap = cv2.VideoCapture(source)
        source_name = os.path.basename(source)
    
    # Video properties
    if cap:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps:.1f}")
        print(f"   Total frames: {total_frames}")
    
    # Output video writer
    out = None
    if save_output and cap:
        output_path = f"detection_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"   📹 Saving output to: {output_path}")
    
    # Stats
    frame_count = 0
    fire_frames = 0
    total_detections = 0
    total_inference_time = 0
    fire_timestamps = []
    
    print("\n" + "-" * 60)
    print("🔍 Starting detection... (Press 'q' to quit)")
    print("-" * 60)
    
    # For image folder mode
    if cap is None:
        image_idx = 0
    
    start_time = time.time()
    
    try:
        while True:
            # Get frame
            if cap:
                ret, frame = cap.read()
                if not ret:
                    break
            else:
                if image_idx >= len(images):
                    break
                frame = cv2.imread(images[image_idx])
                image_idx += 1
                if frame is None:
                    continue
            
            frame_count += 1
            
            # Run inference
            t0 = time.time()
            results = model(frame, verbose=False, conf=confidence_threshold)
            inference_time = (time.time() - t0) * 1000
            total_inference_time += inference_time
            
            # Check for detections
            fire_detected = False
            num_detections = 0
            max_conf = 0
            
            for r in results:
                if len(r.boxes) > 0:
                    fire_detected = True
                    num_detections = len(r.boxes)
                    max_conf = float(r.boxes.conf.max())
                    total_detections += num_detections
            
            if fire_detected:
                fire_frames += 1
                timestamp = frame_count / fps if cap and fps > 0 else frame_count
                fire_timestamps.append(timestamp)
            
            # Annotate frame
            annotated = results[0].plot()
            
            # Add overlay
            overlay_color = (0, 0, 255) if fire_detected else (0, 255, 0)
            status_text = f"FIRE DETECTED ({max_conf:.0%})" if fire_detected else "SCANNING..."
            
            # Status bar at top
            cv2.rectangle(annotated, (0, 0), (width, 40), overlay_color, -1)
            cv2.putText(annotated, status_text, (10, 28), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Stats at bottom
            cv2.rectangle(annotated, (0, height-50), (width, height), (0, 0, 0), -1)
            stats_text = f"Frame: {frame_count} | Inference: {inference_time:.0f}ms | Fires: {fire_frames}"
            cv2.putText(annotated, stats_text, (10, height-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Progress bar for videos
            if cap and total_frames > 0:
                progress = frame_count / total_frames
                bar_width = int(width * progress)
                cv2.rectangle(annotated, (0, height-5), (bar_width, height), (0, 255, 255), -1)
            
            # Display
            cv2.imshow("Fire Detection Test", annotated)
            
            # Save to output
            if out:
                out.write(annotated)
            
            # Print fire alerts
            if fire_detected:
                if cap:
                    timestamp_str = f"{int(timestamp//60)}:{int(timestamp%60):02d}"
                else:
                    timestamp_str = f"Frame {frame_count}"
                print(f"   🔥 FIRE at {timestamp_str} - Confidence: {max_conf:.0%} ({num_detections} detections)")
            
            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n⏹️ Stopped by user")
                break
            elif key == ord(' '):  # Pause
                print("   ⏸️ Paused - press any key to continue")
                cv2.waitKey(0)
            elif key == ord('s'):  # Screenshot
                screenshot_path = f"screenshot_{frame_count}.jpg"
                cv2.imwrite(screenshot_path, annotated)
                print(f"   📸 Screenshot saved: {screenshot_path}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user")
    
    finally:
        if cap:
            cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
    
    # Final stats
    elapsed = time.time() - start_time
    avg_inference = total_inference_time / frame_count if frame_count > 0 else 0
    processing_fps = frame_count / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 DETECTION RESULTS")
    print("=" * 60)
    print(f"\n📹 Video Stats:")
    print(f"   Source:           {source_name}")
    print(f"   Frames processed: {frame_count}")
    print(f"   Duration:         {elapsed:.1f}s")
    
    print(f"\n🔥 Fire Detection:")
    print(f"   Fire frames:      {fire_frames} ({100*fire_frames/frame_count:.1f}%)" if frame_count > 0 else "   Fire frames: 0")
    print(f"   Total detections: {total_detections}")
    
    if fire_timestamps:
        print(f"\n⏱️ Fire Timestamps:")
        for ts in fire_timestamps[:10]:  # Show first 10
            if cap:
                print(f"      {int(ts//60)}:{int(ts%60):02d}")
            else:
                print(f"      Frame {int(ts)}")
        if len(fire_timestamps) > 10:
            print(f"      ... and {len(fire_timestamps) - 10} more")
    
    print(f"\n⚡ Performance:")
    print(f"   Avg inference:    {avg_inference:.1f}ms")
    print(f"   Processing FPS:   {processing_fps:.1f}")
    print(f"   Est. Pi 4 FPS:    {1000/(avg_inference*6):.1f}")
    
    if save_output:
        print(f"\n📹 Output saved to: {output_path}")
    
    print("=" * 60)
    
    # Verdict
    if fire_frames > 0:
        print("\n🔥 FIRE WAS DETECTED IN THIS VIDEO!")
        print(f"   Detection rate: {100*fire_frames/frame_count:.1f}% of frames")
    else:
        print("\n✅ No fire detected in this video")
    
    return {
        "frames": frame_count,
        "fire_frames": fire_frames,
        "detections": total_detections,
        "avg_inference": avg_inference
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test fire detection on video")
    parser.add_argument("source", nargs="?", default=None, help="Video file, image folder, or 'webcam'")
    parser.add_argument("--webcam", action="store_true", help="Use webcam")
    parser.add_argument("--save-output", action="store_true", help="Save annotated video")
    parser.add_argument("--confidence", type=float, default=0.3, help="Detection confidence threshold")
    args = parser.parse_args()
    
    if args.webcam:
        source = "webcam"
    elif args.source:
        source = args.source
    else:
        # Default: use D-Fire test images
        source = "DFireDataset/test/images"
        if not os.path.exists(source):
            print("Usage: python test_video.py <video_file>")
            print("       python test_video.py --webcam")
            print("       python test_video.py path/to/images/folder")
            print("\nTip: Download video from YouTube:")
            print("     pip install yt-dlp")
            print('     yt-dlp -f mp4 "https://youtube.com/watch?v=VIDEO_ID" -o fire_video.mp4')
            sys.exit(1)
    
    test_video(source, args.save_output, args.confidence)

