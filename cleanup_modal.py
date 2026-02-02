"""
Cleanup Script - Deletes all data from Modal Volume
WARNING: This will delete ALL data in your solform-data volume!
Use this to start fresh.
"""
import modal
import sys

VOLUME_NAME = "solform-data"
APP_NAME = "solform-cleanup"

app = modal.App(APP_NAME)

@app.function(
    volumes={"/data": modal.Volume.from_name(VOLUME_NAME)},
    timeout=600
)
def delete_all_contents():
    """Delete all files and directories in the volume"""
    import shutil
    import os
    
    directories_to_delete = [
        "/data/ExportSFsPNGs",
        "/data/predict_inputs",
        "/data/predict_inputs.png",
        "/data/predict_outputs",
        "/data/predictions",
        "/data/runs",
        "/data/yolo_dataset"
    ]
    
    deleted = []
    errors = []
    
    for dir_path in directories_to_delete:
        try:
            if os.path.exists(dir_path):
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
                    deleted.append(f"✓ Deleted directory: {dir_path}")
                else:
                    os.remove(dir_path)
                    deleted.append(f"✓ Deleted file: {dir_path}")
            else:
                deleted.append(f"  Skipped (not found): {dir_path}")
        except Exception as e:
            errors.append(f"✗ Error deleting {dir_path}: {e}")
    
    return deleted, errors

@app.local_entrypoint()
def main():
    """Main cleanup entry point with confirmation"""
    print("=" * 70)
    print("⚠️  MODAL VOLUME CLEANUP - WARNING ⚠️")
    print("=" * 70)
    print(f"\nThis will DELETE ALL data in volume: '{VOLUME_NAME}'")
    print("\nThis includes:")
    print("  - All training data (ExportSFsPNGs)")
    print("  - All trained models (runs)")
    print("  - All predictions (predict_outputs)")
    print("  - All datasets (yolo_dataset)")
    print("\n" + "=" * 70)
    
    # Confirmation
    response = input("\nType 'DELETE' to confirm (or anything else to cancel): ")
    
    if response.strip() != "DELETE":
        print("\n✓ Cancelled. No data was deleted.")
        sys.exit(0)
    
    print("\n🗑️  Deleting all data...")
    deleted, errors = delete_all_contents.remote()
    
    print("\n" + "=" * 70)
    print("DELETION RESULTS")
    print("=" * 70)
    
    for msg in deleted:
        print(msg)
    
    if errors:
        print("\nErrors:")
        for err in errors:
            print(err)
    
    print("\n" + "=" * 70)
    print("✓ CLEANUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run: modal run setup_modal.py")
    print("  2. Upload training data: modal run setup_modal.py --upload-data")
    print("  3. Train: modal run train.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
