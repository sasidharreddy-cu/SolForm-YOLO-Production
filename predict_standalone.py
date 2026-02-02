"""
Solform YOLO - Prediction Pipeline (Standalone Version)
=======================================================

Runs inference on form images to detect text lines, checkboxes, text blocks, 
and signatures. This standalone version has all dependencies inlined to avoid
Modal import issues.

Usage:
    modal run predict_standalone.py

Requirements:
    - Modal account with authentication (modal token new)
    - Trained model at /data/runs/forms/weights/best.pt
    - Input images in /data/predict_inputs/

Output:
    - Annotated images: /data/predict_outputs/*.png
    - JSON detections: /data/predict_outputs/*.json
"""

import modal
import os
import json
from PIL import Image, ImageDraw
from ultralytics import YOLO

# ============================================================
# CONFIGURATION
# ============================================================

# Modal settings
APP_NAME = "solform-yolo-max"
VOLUME_NAME = "solform-data"

# Paths in Modal volume
DATA_ROOT = "/data"
RUNS_DIR = f"{DATA_ROOT}/runs"
PRED_INPUT = f"{DATA_ROOT}/predict_inputs"
PRED_OUTPUT = f"{DATA_ROOT}/predict_outputs"

# Model classes
CLASSES = ["text_line", "text_block", "checkbox", "signature"]

# Training configuration (for model path)
TRAINING = {
    "project_name": "forms"
}

# GPU configuration for prediction
GPU_CONFIG = {
    "predict": {
        "gpu": "B200",              # GPU type: T4, A10G, A100, B200
        "cpu": (16, 32),            # CPU range (min, max)
        "memory": (65_536, 65_536), # Memory in MB (64 GB)
        "timeout": 60 * 60          # Timeout in seconds (1 hour)
    }
}

# Filtering configuration (removes noise boxes)
FILTER_CONFIG = {
    "min_confidence": 0.35,     # Minimum confidence score
    "bottom_margin": 0.95,      # Remove boxes below 95% image height
    "max_height_ratio": 0.15,   # Remove boxes taller than 15% of image
    "max_width_ratio": 0.95,    # Remove boxes wider than 95% of image
    "min_box_size": 5           # Minimum box dimension in pixels
}

# Visualization configuration
PREDICTION = {
    "confidence_threshold": 0.15,  # Detection confidence threshold
    "draw_boxes": True,            # Draw bounding boxes on output
    "draw_labels": True,           # Draw class labels on output
    "box_color": "red",            # Box color
    "box_width": 3                 # Box line width
}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def keep_box(x1, y1, x2, y2, conf, W, H):
    """
    Filter out unwanted bounding boxes based on size and position.
    
    This removes:
    - Low confidence detections
    - Boxes in footer area (bottom 5%)
    - Boxes that are too tall (likely full-page artifacts)
    - Boxes that are too wide (likely page-width artifacts)
    
    Args:
        x1, y1, x2, y2: Bounding box coordinates
        conf: Detection confidence score
        W, H: Image dimensions
        
    Returns:
        bool: True if box should be kept, False otherwise
    """
    w = x2 - x1
    h = y2 - y1

    # Filter 1: Low confidence
    if conf < FILTER_CONFIG["min_confidence"]:
        return False
    
    # Filter 2: Bottom margin (footer area)
    if y1 > H * FILTER_CONFIG["bottom_margin"]:
        return False
    
    # Filter 3: Too tall (likely artifact)
    if h > H * FILTER_CONFIG["max_height_ratio"]:
        return False
    
    # Filter 4: Too wide (likely artifact)
    if w > W * FILTER_CONFIG["max_width_ratio"]:
        return False

    return True

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
# PREDICTION FUNCTION
# ============================================================

@app.function(
    image=image,
    gpu=GPU_CONFIG["predict"]["gpu"],
    cpu=GPU_CONFIG["predict"]["cpu"],
    memory=GPU_CONFIG["predict"]["memory"],
    timeout=GPU_CONFIG["predict"]["timeout"],
    volumes={"/data": vol},
)
def predict():
    """
    Main prediction pipeline.
    
    Steps:
        1. Load trained YOLO model from volume
        2. Find all PNG images in predict_inputs/
        3. Run inference on each image
        4. Filter detections using keep_box()
        5. Draw bounding boxes on images
        6. Save annotated images and JSON results
        
    Returns:
        dict: Status and number of images processed
    """
    print("=" * 60)
    print("STARTING PREDICTION PIPELINE")
    print("=" * 60)
    
    # ========================================
    # Step 1: Load Model
    # ========================================
    print("\n[1/3] Loading model...")
    os.makedirs(PRED_OUTPUT, exist_ok=True)
    
    model_path = f"{RUNS_DIR}/{TRAINING['project_name']}/weights/best.pt"
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            f"Run training first: modal run train_standalone.py"
        )
    
    model = YOLO(model_path)
    print(f"✓ Model loaded from {model_path}")

    # ========================================
    # Step 2: Find Input Images
    # ========================================
    print("\n[2/3] Finding input images...")
    
    if not os.path.exists(PRED_INPUT):
        raise FileNotFoundError(
            f"Input directory {PRED_INPUT} not found. "
            f"Upload images: modal volume put solform-data ./images /predict_inputs"
        )
    
    input_files = [f for f in os.listdir(PRED_INPUT) if f.endswith(".png")]
    
    if not input_files:
        print("✗ No PNG files found in predict_inputs/")
        return {"status": "error", "message": "No input images found"}
    
    print(f"✓ Found {len(input_files)} images to process")

    # ========================================
    # Step 3: Process Each Image
    # ========================================
    print("\n[3/3] Running predictions...")
    processed = 0
    
    for f in input_files:
        path = f"{PRED_INPUT}/{f}"
        
        # Run YOLO inference
        results = model(path, conf=PREDICTION["confidence_threshold"])[0]

        # Load image for visualization
        img = Image.open(path).convert("RGB")
        W, H = img.size
        draw = ImageDraw.Draw(img)

        boxes_json = []
        kept_boxes = 0

        # Process each detected box
        for box in results.boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            cls = CLASSES[int(box.cls)]
            conf = float(box.conf)

            # Apply filtering rules
            if not keep_box(x1, y1, x2, y2, conf, W, H):
                continue

            kept_boxes += 1

            # Draw bounding box
            if PREDICTION["draw_boxes"]:
                draw.rectangle(
                    [x1, y1, x2, y2],
                    outline=PREDICTION["box_color"],
                    width=PREDICTION["box_width"]
                )
            
            # Draw label
            if PREDICTION["draw_labels"]:
                draw.text(
                    (x1, y1 - 10),
                    f"{cls} {conf:.2f}",
                    fill=PREDICTION["box_color"]
                )

            # Add to JSON output
            boxes_json.append({
                "type": cls,
                "confidence": round(conf, 3),
                "bbox": {
                    "x": round(x1, 1),
                    "y": round(y1, 1),
                    "w": round(x2 - x1, 1),
                    "h": round(y2 - y1, 1),
                }
            })

        # Save annotated image
        img.save(f"{PRED_OUTPUT}/{f}")
        
        # Save JSON detections
        json_path = f"{PRED_OUTPUT}/{f.replace('.png', '.json')}"
        with open(json_path, "w") as jf:
            json.dump(boxes_json, jf, indent=2)
        
        print(f"  ✓ {f}: {len(results.boxes)} detected → {kept_boxes} kept")
        processed += 1

    # Commit changes to persistent volume
    vol.commit()
    
    print("\n" + "=" * 60)
    print("✓ PREDICTION COMPLETE!")
    print("=" * 60)
    print(f"Processed {processed} images")
    print(f"Results saved to: {PRED_OUTPUT}")
    print(f"\nDownload results:")
    print(f"  modal volume get {VOLUME_NAME} /predict_outputs ./results")
    
    return {
        "status": "success",
        "images_processed": processed
    }

# ============================================================
# ENTRY POINT
# ============================================================

@app.local_entrypoint()
def main():
    """
    Entry point when running: modal run predict_standalone.py
    
    Executes the predict() function on Modal's infrastructure and
    returns the results to the local terminal.
    """
    result = predict.remote()
    print(f"\nResult: {result}")

if __name__ == "__main__":
    main()
