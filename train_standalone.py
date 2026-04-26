"""
Solform YOLO - Training Pipeline (Standalone Version)
====================================================

Trains a YOLOv8 model to detect form elements from annotated images.
Converts custom JSON annotations to YOLO format and runs training on Modal GPUs.

Usage:
    modal run train_standalone.py

Requirements:
    - Modal account with authentication (modal token new)
    - Training images and JSON annotations in /data/ExportSFsPNGs/

Output:
    - Trained model: /data/runs/forms/weights/best.pt
    - Training metrics: /data/runs/forms/results.csv
"""

import modal
import os
import json
from PIL import Image
from ultralytics import YOLO

# ============================================================
# CONFIGURATION
# ============================================================

# Modal settings
APP_NAME = "solform-yolo-max"
VOLUME_NAME = "solform-data"

# Paths in Modal volume
DATA_ROOT = "/data"
RAW_DIR = f"{DATA_ROOT}/ExportSFsPNGs"      # Raw training data
DATASET_DIR = f"{DATA_ROOT}/yolo_dataset"   # Processed YOLO format
RUNS_DIR = f"{DATA_ROOT}/runs"              # Training outputs

# Model classes
CLASSES = ["text_line", "text_block", "checkbox", "signature"]

# Training configuration
TRAINING = {
    "model": "yolov8s.pt",      # Base model: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    "epochs": 50,               # Training epochs
    "imgsz": 1024,              # Input image size
    "batch": 32,                # Batch size (reduce if OOM)
    "workers": 16,              # Data loading workers
    "project_name": "forms"     # Output directory name
}

# GPU configuration for training
GPU_CONFIG = {
    "train": {
        "gpu": "A100",                      # GPU type: T4, A10G, A100, B200
        "cpu": (32, 64),                    # CPU range (min, max)
        "memory": (131_072, 131_072),       # Memory in MB (128 GB)
        "timeout": 6 * 60 * 60              # Timeout in seconds (6 hours)
    }
}

# Filtering configuration (same as prediction)
FILTER_CONFIG = {
    "min_box_size": 5       # Minimum box dimension in pixels
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def json_to_yolo(img_path, json_path, label_path):
    """
    Convert custom JSON annotation to YOLO format.
    
    JSON Format (input):
        {
          "regions": [
            {
              "tags": ["text_line"],
              "boundingBox": {"left": x, "top": y, "width": w, "height": h}
            }
          ]
        }
    
    YOLO Format (output):
        <class_id> <center_x> <center_y> <width> <height>
        (All values normalized to 0-1)
    
    Args:
        img_path: Path to image file
        json_path: Path to JSON annotation file
        label_path: Output path for YOLO label file (.txt)
    """
    # Get image dimensions
    img = Image.open(img_path)
    W, H = img.size

    # Load JSON annotations
    with open(json_path) as f:
        data = json.load(f)

    lines = []

    # Process each region
    for region in data.get("regions", []):
        bb = region.get("boundingBox")
        tags = region.get("tags", [])
        
        if not bb or not tags:
            continue

        # Get class label
        label = tags[0]
        if label not in CLASSES:
            label = "text_line"  # Default to text_line if unknown

        cls = CLASSES.index(label)

        # Extract coordinates
        x1 = max(0, bb["left"])
        y1 = max(0, bb["top"])
        x2 = min(W, bb["left"] + bb["width"])
        y2 = min(H, bb["top"] + bb["height"])

        bw = x2 - x1
        bh = y2 - y1
        
        # Skip tiny boxes (likely noise)
        if bw < FILTER_CONFIG["min_box_size"] or bh < FILTER_CONFIG["min_box_size"]:
            continue

        # Convert to YOLO format (normalized center coordinates + size)
        cx = ((x1 + x2) / 2) / W  # Center X (normalized)
        cy = ((y1 + y2) / 2) / H  # Center Y (normalized)
        w = bw / W                 # Width (normalized)
        h = bh / H                 # Height (normalized)

        lines.append(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

    # Write YOLO label file
    with open(label_path, "w") as f:
        f.write("\n".join(lines))


def create_data_yaml(output_path, dataset_dir):
    """
    Create YOLO data.yaml configuration file.
    
    This file tells YOLO where to find training images and what
    classes to detect.
    
    Args:
        output_path: Where to save the yaml file
        dataset_dir: Root directory of dataset
    """
    with open(output_path, "w") as f:
        f.write(
            f"path: {dataset_dir}\n"
            f"train: images/train\n"
            f"val: images/train\n\n"  # Using training set for validation (small dataset)
            f"names:\n"
            + "\n".join([f"  {i}: {n}" for i, n in enumerate(CLASSES)])
        )

# ============================================================
# MODAL SETUP
# ============================================================

app = modal.App(APP_NAME)

# Define container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libgl1", "libglib2.0-0")  # Required for OpenCV
    .pip_install(
        "ultralytics",               # YOLOv8
        "pillow",                    # Image processing
        "opencv-python-headless",    # OpenCV without GUI
        "torch"                      # PyTorch (YOLO dependency)
    )
)

# Mount persistent storage volume
vol = modal.Volume.from_name(VOLUME_NAME)

# ============================================================
# TRAINING FUNCTION
# ============================================================

@app.function(
    image=image,
    gpu=GPU_CONFIG["train"]["gpu"],
    cpu=GPU_CONFIG["train"]["cpu"],
    memory=GPU_CONFIG["train"]["memory"],
    timeout=GPU_CONFIG["train"]["timeout"],
    volumes={"/data": vol},
)
def train():
    """
    Main training pipeline.
    
    Steps:
        1. Create YOLO dataset directory structure
        2. Convert JSON annotations to YOLO format
        3. Create data.yaml configuration file
        4. Train YOLOv8 model
        5. Save model to persistent volume
        
    Returns:
        dict: Training status and model path
    """
    print("=" * 60)
    print("STARTING TRAINING PIPELINE")
    print("=" * 60)
    
    # ========================================
    # Step 1: Create Dataset Structure
    # ========================================
    print("\n[1/4] Creating dataset structure...")
    
    # YOLO expects:
    # dataset/
    #   images/
    #     train/
    #   labels/
    #     train/
    for p in ["images/train", "labels/train"]:
        os.makedirs(f"{DATASET_DIR}/{p}", exist_ok=True)
    
    print("✓ Directories created")

    # ========================================
    # Step 2: Convert Annotations
    # ========================================
    print("\n[2/4] Converting annotations to YOLO format...")
    
    if not os.path.exists(RAW_DIR):
        raise FileNotFoundError(
            f"Training data not found at {RAW_DIR}. "
            f"Upload data: modal volume put solform-data ./training_data /ExportSFsPNGs"
        )
    
    converted_count = 0
    skipped_count = 0
    
    # Process each PNG file
    for f in os.listdir(RAW_DIR):
        if not f.endswith(".png"):
            continue

        base = f.replace(".png", "")
        img_path = f"{RAW_DIR}/{f}"
        json_path = f"{RAW_DIR}/{base}.json"
        
        # Skip if no annotation file
        if not os.path.exists(json_path):
            skipped_count += 1
            continue

        # Copy image to dataset
        Image.open(img_path).save(f"{DATASET_DIR}/images/train/{f}")
        
        # Convert annotation to YOLO format
        json_to_yolo(
            img_path,
            json_path,
            f"{DATASET_DIR}/labels/train/{base}.txt"
        )
        converted_count += 1
    
    print(f"✓ Converted {converted_count} images")
    if skipped_count > 0:
        print(f"  ⚠ Skipped {skipped_count} images (no annotations)")
    
    if converted_count == 0:
        raise ValueError("No training data found! Check your upload.")

    # ========================================
    # Step 3: Create YOLO Configuration
    # ========================================
    print("\n[3/4] Creating YOLO configuration...")
    create_data_yaml(f"{DATASET_DIR}/data.yaml", DATASET_DIR)
    print(f"✓ Classes: {', '.join(CLASSES)}")

    # ========================================
    # Step 4: Train Model
    # ========================================
    print("\n[4/4] Training model...")
    print(f"  Model: {TRAINING['model']}")
    print(f"  Epochs: {TRAINING['epochs']}")
    print(f"  Image size: {TRAINING['imgsz']}")
    print(f"  Batch size: {TRAINING['batch']}")
    print(f"  Workers: {TRAINING['workers']}")
    print()
    
    # Initialize YOLO model
    model = YOLO(TRAINING["model"])
    
    # Start training
    results = model.train(
        data=f"{DATASET_DIR}/data.yaml",
        epochs=TRAINING["epochs"],
        imgsz=TRAINING["imgsz"],
        batch=TRAINING["batch"],
        workers=TRAINING["workers"],
        project=RUNS_DIR,
        name=TRAINING["project_name"],
        exist_ok=True,
        verbose=True
    )

    # Commit changes to persistent volume
    vol.commit()
    
    model_path = f"{RUNS_DIR}/{TRAINING['project_name']}/weights/best.pt"
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Images trained: {converted_count}")
    print(f"Model saved to: {model_path}")
    print(f"\nRun predictions:")
    print(f"  modal run predict_standalone.py")
    
    return {
        "status": "success",
        "images_trained": converted_count,
        "model_path": model_path
    }

# ============================================================
# ENTRY POINT
# ============================================================

@app.local_entrypoint()
def main():
    """
    Entry point when running: modal run train_standalone.py
    
    Executes the train() function on Modal's infrastructure and
    returns the results to the local terminal.
    """
    result = train.remote()
    print(f"\nResult: {result}")

if __name__ == "__main__":
    main()
