"""
Download More Pretrained Fire Detection Models from HuggingFace
These are already trained by others - ready to use!
"""
import os
import subprocess
import sys

print("=" * 70)
print("🔥 PRETRAINED FIRE DETECTION MODEL DOWNLOADER")
print("=" * 70)

# Models to download from HuggingFace
MODELS = {
    "touati-kamel/yolov8s-forest-fire-detection": "yolov8s_forest_fire.pt",
    "touati-kamel/yolov10n-forest-fire-detection": "yolov10n_forest_fire.pt",
    # Note: Some may need 'huggingface_hub' to download
}

os.makedirs("models/pretrained", exist_ok=True)

def install_huggingface_hub():
    """Install huggingface_hub if not present"""
    try:
        import huggingface_hub
        return True
    except ImportError:
        print("Installing huggingface_hub...")
        subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"])
        return True

def download_model(repo_id, filename):
    """Download a model from HuggingFace"""
    from huggingface_hub import hf_hub_download, list_repo_files
    
    output_path = f"models/pretrained/{filename}"
    
    if os.path.exists(output_path):
        print(f"✅ {filename} already exists")
        return True
    
    try:
        print(f"\n📥 Downloading {repo_id}...")
        
        # List files in repo
        files = list_repo_files(repo_id)
        print(f"   Files in repo: {files}")
        
        # Find the .pt file
        pt_files = [f for f in files if f.endswith('.pt')]
        if pt_files:
            pt_file = pt_files[0]
            print(f"   Found: {pt_file}")
            
            # Download
            path = hf_hub_download(repo_id=repo_id, filename=pt_file)
            
            # Copy to our folder
            import shutil
            shutil.copy(path, output_path)
            print(f"✅ Downloaded to {output_path}")
            return True
        else:
            print(f"   ❌ No .pt file found in repo")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    install_huggingface_hub()
    
    print("\n📋 Models to download:")
    for repo, name in MODELS.items():
        print(f"   • {repo} → {name}")
    
    print("\n" + "-" * 70)
    
    success = 0
    for repo, name in MODELS.items():
        if download_model(repo, name):
            success += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Downloaded {success}/{len(MODELS)} models")
    print("=" * 70)
    
    # List what we have
    print("\n📁 Available pretrained models:")
    for f in os.listdir("models/pretrained"):
        if f.endswith('.pt'):
            size = os.path.getsize(f"models/pretrained/{f}") / (1024*1024)
            print(f"   • {f} ({size:.1f} MB)")

if __name__ == "__main__":
    main()

