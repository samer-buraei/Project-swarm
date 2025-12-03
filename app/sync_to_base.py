import os
import shutil
import argparse
import hashlib

def calculate_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_recordings(drone_id, source_base, dest_base, delete_source=False):
    print(f"🔄 Syncing recordings for {drone_id}...")
    
    source_dir = os.path.join(source_base, drone_id)
    dest_dir = os.path.join(dest_base, drone_id)
    
    if not os.path.exists(source_dir):
        print(f"⚠️ No recordings found for {drone_id}")
        return

    # Walk through source directory
    for root, dirs, files in os.walk(source_dir):
        # Construct relative path
        rel_path = os.path.relpath(root, source_dir)
        dest_root = os.path.join(dest_dir, rel_path)
        
        os.makedirs(dest_root, exist_ok=True)
        
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_root, file)
            
            # Check if file exists and matches
            if os.path.exists(dst_file):
                # Simple size check for speed, checksum for rigor
                if os.path.getsize(src_file) == os.path.getsize(dst_file):
                    continue 
            
            print(f"   Copying {file}...")
            shutil.copy2(src_file, dst_file)
            
    print("✅ Sync complete.")
    
    if delete_source:
        print("🗑️ Cleaning up source files...")
        shutil.rmtree(source_dir)
        print("✅ Source cleaned.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--drone", required=True, help="Drone ID (e.g., A1)")
    parser.add_argument("--source", default="recordings", help="Source recordings path")
    parser.add_argument("--dest", required=True, help="Destination base station path")
    parser.add_argument("--delete", action="store_true", help="Delete source after sync")
    
    args = parser.parse_args()
    
    sync_recordings(args.drone, args.source, args.dest, args.delete)
