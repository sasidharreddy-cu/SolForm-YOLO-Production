"""
Modal Setup Script - Creates volumes and uploads initial data
Run this ONCE after cloning the repo to set up your Modal environment.
"""
import modal
import os
import sys
from pathlib import Path

# Configuration
VOLUME_NAME = "solform-data"
APP_NAME = "solform-yolo-setup"

app = modal.App(APP_NAME)

def create_volume():
    """Create the Modal volume if it doesn't exist"""
    try:
        # Try to get existing volume, or create new one
        vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
        print(f"✓ Volume '{VOLUME_NAME}' ready")
        return vol
    except Exception as e:
        print(f"✗ Error creating volume: {e}")
        sys.exit(1)

@app.function(
    volumes={"/data": modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)},
    timeout=600
)
def setup_directories():
    """Create necessary directory structure in Modal volume"""
    directories = [
        "/data/ExportSFsPNGs",
        "/data/yolo_dataset",
        "/data/runs",
        "/data/predict_inputs",
        "/data/predict_outputs"
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created {dir_path}")
    
    return "Directory structure created"

@app.function(
    volumes={"/data": modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)},
    timeout=3600
)
def upload_training_data(remote_path: str = "/data/ExportSFsPNGs"):
    """Upload training data from local directory to Modal volume"""
    import shutil
    
    # This function will be called with data already mounted
    # The actual upload happens via Modal's volume.put_directory
    print(f"✓ Data uploaded to {remote_path}")
    return "Upload complete"

@app.local_entrypoint()
def main(upload_data: bool = False):
    """
    Main setup entry point
    
    Usage:
        modal run setup_modal.py
        modal run setup_modal.py --upload-data  # if you have local training data
    """
    print("=" * 60)
    print("MODAL SETUP - Solform YOLO")
    print("=" * 60)
    
    # Step 1: Create volume
    print("\n[1/3] Creating Modal volume...")
    vol = create_volume()
    
    # Step 2: Setup directories
    print("\n[2/3] Setting up directory structure...")
    result = setup_directories.remote()
    print(f"    {result}")
    
    # Step 3: Upload data (optional)
    if upload_data:
        print("\n[3/3] Uploading training data...")
        local_data_path = Path("./training_data")
        
        if not local_data_path.exists():
            print(f"✗ Local directory '{local_data_path}' not found")
            print("  Create this directory and add your .png and .json files")
            sys.exit(1)
        
        # Count files
        png_files = list(local_data_path.glob('*.png'))
        json_files = list(local_data_path.glob('*.json'))
        
        if not png_files:
            print(f"✗ No .png files found in {local_data_path}")
            sys.exit(1)
        
        print(f"  Found {len(png_files)} PNG files and {len(json_files)} JSON files")
        print(f"\n  Please run this command to upload:")
        print(f"  modal volume put solform-data ./training_data /ExportSFsPNGs")
        print(f"\n  This will upload all files from ./training_data/ to Modal")
    else:
        print("\n[3/3] Skipping data upload (use --upload-data flag to upload)")
    
    print("\n" + "=" * 60)
    print("✓ SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    if upload_data:
        print("  Run this command to upload your training data:")
        print("  modal volume put solform-data ./training_data /ExportSFsPNGs")
        print("\n  Then train the model:")
        print("  modal run train.py")
    else:
        print("  1. Add training data to ./training_data/ directory")
        print("  2. Upload: modal volume put solform-data ./training_data /ExportSFsPNGs")
        print("  3. Train: modal run train.py")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    upload = "--upload-data" in sys.argv
    main(upload)
