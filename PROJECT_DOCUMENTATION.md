# Solform YOLO - Complete Project Documentation

## 📁 File Structure Explanation

```
solform-yolo/
│
├── 📄 Core Scripts (Use These!)
│   ├── train_standalone.py          # Training pipeline - converts JSON → YOLO → trains model
│   ├── predict_standalone.py        # Prediction pipeline - runs inference on new forms
│   ├── setup_modal.py               # One-time setup - creates Modal volume & directories
│   └── cleanup_modal.py             # Cleanup utility - deletes all data (use with caution)
│
├── 📚 Documentation
│   ├── README.md                    # Main documentation - start here!
│   ├── QUICKSTART.md                # Command reference - quick lookup
│   ├── CONTRIBUTING.md              # Contribution guidelines
│   ├── CHANGELOG.md                 # Version history
│   ├── DEPLOYMENT_CHECKLIST.md      # GitHub deployment guide
│   └── LICENSE                      # MIT License
│
├── 📋 Configuration
│   ├── requirements.txt             # Python dependencies (just modal)
│   ├── .gitignore                   # Files to exclude from git
│   └── example_annotation.json      # Sample training data format
│
└── 🔧 GitHub Integration
    └── .github/
        └── workflows/
            └── lint.yml             # Automated code linting
```

## 🎯 What Each File Does

### Core Scripts

#### `train_standalone.py` ⭐
**Purpose:** Train a YOLOv8 model to detect form elements

**What it does:**
1. Reads PNG images + JSON annotations from Modal volume
2. Converts JSON format to YOLO format
3. Creates YOLO dataset structure
4. Trains model on Modal GPUs
5. Saves trained model to volume

**When to use:** 
- First time setup (after uploading training data)
- When you add new training data
- When you want to retrain with different parameters

**Run:** `modal run train_standalone.py`

**Input:** `/data/ExportSFsPNGs/*.png` + `*.json`  
**Output:** `/data/runs/forms/weights/best.pt`

#### `predict_standalone.py` ⭐
**Purpose:** Run inference on new form images

**What it does:**
1. Loads trained model from volume
2. Reads images from predict_inputs/
3. Runs YOLO detection
4. Filters out noise boxes
5. Draws bounding boxes on images
6. Saves annotated images + JSON detections

**When to use:**
- After training a model
- When you have new forms to process
- For batch processing

**Run:** `modal run predict_standalone.py`

**Input:** `/data/predict_inputs/*.png`  
**Output:** `/data/predict_outputs/*.png` + `*.json`

#### `setup_modal.py`
**Purpose:** One-time setup of Modal infrastructure

**What it does:**
1. Creates Modal volume named "solform-data"
2. Creates directory structure:
   - /ExportSFsPNGs (training data)
   - /predict_inputs (images to process)
   - /predict_outputs (results)
   - /runs (trained models)

**When to use:**
- First time using the project
- After running cleanup_modal.py
- If volume gets deleted

**Run:** `modal run setup_modal.py`

#### `cleanup_modal.py`
**Purpose:** Delete all data and reset

**What it does:**
1. Deletes all files in Modal volume
2. Deletes the volume itself
3. Requires typing "DELETE" to confirm

**When to use:**
- Starting completely fresh
- Removing all old data
- Before archiving project

**Run:** `modal run cleanup_modal.py`

**⚠️ WARNING:** This deletes everything! No undo!

### Documentation Files

#### `README.md`
Main documentation. Covers:
- Project overview
- Installation steps
- Quick start guide
- Configuration options
- Troubleshooting
- Performance metrics

**Target audience:** New users, team members

#### `QUICKSTART.md`
Quick command reference. Covers:
- Common commands
- Volume management
- Workflows
- Quick fixes

**Target audience:** Experienced users who just need commands

#### `CONTRIBUTING.md`
Contribution guidelines. Covers:
- How to report issues
- How to submit code
- Code style guidelines
- Testing requirements

**Target audience:** Contributors

#### `DEPLOYMENT_CHECKLIST.md`
GitHub deployment guide. Covers:
- Pre-deployment checks
- GitHub setup steps
- Repository configuration
- Post-deployment tasks

**Target audience:** Project maintainer

#### `CHANGELOG.md`
Version history and changes.

**Target audience:** All users (shows what's new)

### Configuration Files

#### `requirements.txt`
Python dependencies. Contains:
- `modal>=0.63.0` - The only required package!
- Comments about other packages (Modal handles them)

**Why so simple?** 
Modal automatically installs ultralytics, pillow, opencv, and torch in its containers. You only need `modal` locally.

#### `.gitignore`
Tells Git which files to ignore. Excludes:
- Training data (too large for git)
- Model weights (too large for git)
- Python cache files
- IDE settings
- Temporary files

**Important:** Prevents accidentally committing large files or secrets!

#### `example_annotation.json`
Sample showing JSON annotation format. Demonstrates:
- Correct structure for training data
- All 4 class types
- Bounding box format

**Use this as a template** when creating your own annotations.

## 🔄 Typical Workflows

### 1. First Time User

```bash
# 1. Clone repository
git clone https://github.com/yourusername/solform-yolo.git
cd solform-yolo

# 2. Install Modal
pip install -r requirements.txt

# 3. Authenticate
modal token new

# 4. Setup infrastructure
modal run setup_modal.py

# 5. Upload training data
modal volume put solform-data ./my_training_data /ExportSFsPNGs

# 6. Train model
modal run train_standalone.py

# 7. Ready to predict!
modal volume put solform-data ./new_forms /predict_inputs
modal run predict_standalone.py
```

### 2. Regular User (Model Already Trained)

```bash
# 1. Upload new forms
modal volume put solform-data ./batch_123 /predict_inputs

# 2. Run prediction
modal run predict_standalone.py

# 3. Download results
modal volume get solform-data /predict_outputs ./batch_123_results

# 4. Clean up
modal volume rm solform-data /predict_inputs/*
```

### 3. Retraining with More Data

```bash
# 1. Upload new training data (adds to existing)
modal volume put solform-data ./more_data /ExportSFsPNGs

# 2. Retrain
modal run train_standalone.py

# 3. Old model is replaced with new one
```

### 4. Complete Reset

```bash
# 1. Delete everything
modal run cleanup_modal.py
# Type: DELETE

# 2. Start fresh
modal run setup_modal.py

# 3. Upload data again
modal volume put solform-data ./training_data /ExportSFsPNGs

# 4. Train again
modal run train_standalone.py
```

## 🔧 How It Works Internally

### Training Pipeline

```
Raw Data (PNG + JSON)
    ↓
Read JSON annotations
    ↓
Convert to YOLO format (class, cx, cy, w, h)
    ↓
Save to /yolo_dataset/
    ↓
Create data.yaml config
    ↓
Initialize YOLOv8 model
    ↓
Train for N epochs
    ↓
Save best model to /runs/forms/weights/best.pt
```

### Prediction Pipeline

```
Input PNG images
    ↓
Load trained model
    ↓
Run YOLO inference
    ↓
Get bounding boxes + confidence scores
    ↓
Filter boxes (remove noise):
  - Low confidence → remove
  - Footer area → remove
  - Too tall/wide → remove
    ↓
Draw boxes on images
    ↓
Save annotated PNG + JSON detections
```

### Filtering Logic

The `keep_box()` function removes noise:

1. **Confidence filter**: Removes boxes < 35% confidence
2. **Bottom margin**: Removes boxes in bottom 5% (footer area)
3. **Height filter**: Removes boxes > 15% image height (artifacts)
4. **Width filter**: Removes boxes > 95% image width (artifacts)

**Why?** Scanning artifacts, page borders, and headers often get detected but aren't useful form elements.

## 💡 Configuration Options

### In `train_standalone.py`:

```python
# Model size (speed vs accuracy tradeoff)
TRAINING = {
    "model": "yolov8s.pt",  # Change to: n, s, m, l, x
    "epochs": 50,           # More = better (but slower)
    "imgsz": 1024,          # Image size for training
    "batch": 32,            # Larger = faster (but needs more VRAM)
}

# GPU selection (cost vs speed tradeoff)
GPU_CONFIG = {
    "gpu": "B200",  # Change to: T4, A10G, A100, B200
}
```

### In `predict_standalone.py`:

```python
# Detection sensitivity
PREDICTION = {
    "confidence_threshold": 0.15,  # Lower = more detections
}

# Filtering rules
FILTER_CONFIG = {
    "min_confidence": 0.35,      # Keep only high-confidence boxes
    "bottom_margin": 0.95,       # Remove footer boxes
    "max_height_ratio": 0.15,    # Remove tall artifacts
    "max_width_ratio": 0.95,     # Remove wide artifacts
}
```

## 🎓 Understanding Modal

### What is Modal?
Modal is a serverless platform for running Python code on GPUs in the cloud.

### Why Modal?
- No need to set up GPU machines
- Pay only when code runs
- Automatic scaling
- Simple Python API

### Key Concepts

**Volume:** Persistent cloud storage
- Like a shared hard drive
- Survives between runs
- Accessible from all functions

**App:** Collection of functions
- Defined with `app = modal.App("name")`
- Groups related functions

**Function:** Code that runs in the cloud
- Decorated with `@app.function()`
- Specifies GPU, memory, timeout

**Image:** Container environment
- Defines Python packages
- Sets up system dependencies

### Modal Volume Paths

All data lives in `/data/` in Modal:

```
/data/
├── ExportSFsPNGs/       # Training data (you upload)
├── yolo_dataset/        # Processed data (auto-created)
├── runs/                # Trained models (auto-created)
├── predict_inputs/      # Images to predict (you upload)
└── predict_outputs/     # Results (auto-created)
```

## 💰 Cost Breakdown

### Training
- **Time:** ~7.4 minutes (662 images, 50 epochs, B200)
- **Cost:** ~$0.80 (B200 at $6.50/hour)
- **One-time:** Only when training/retraining

### Prediction
- **Time:** ~0.5 seconds per image (B200)
- **Cost:** ~$0.001 per image
- **Per-use:** Every prediction batch

### Storage
- **Cost:** $0.10/GB/month
- **Typical:** 1-10 GB total
- **Continuous:** While data exists

### Cost Optimization Tips
1. Use T4 GPU for testing ($0.60/hr vs $6.50/hr)
2. Delete old predictions regularly
3. Use smaller model for speed (yolov8n vs yolov8s)
4. Reduce epochs for initial testing (30 vs 50)

## 🐛 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'config'"
**Solution:** Use `*_standalone.py` files (they have config inlined)

### "Volume not found"
**Solution:** Run `modal run setup_modal.py`

### "Model not found"
**Solution:** Train model first: `modal run train_standalone.py`

### "No images found" during training
**Solution:** Upload data: `modal volume put solform-data ./data /ExportSFsPNGs`

### Out of GPU memory
**Solution:** Reduce batch size in script: `"batch": 16` or `"batch": 8`

### Low accuracy
**Solutions:**
- Increase epochs: `"epochs": 100`
- Use larger model: `"model": "yolov8m.pt"`
- Add more training data
- Check annotation quality

### Slow training
**Solutions:**
- Use smaller model: `"model": "yolov8n.pt"`
- Reduce image size: `"imgsz": 640`
- Use faster GPU: Switch to B200

## 🎯 Best Practices

### Data Management
1. **Keep originals:** Don't delete source training data
2. **Backup models:** Download `best.pt` after training
3. **Clean regularly:** Delete old predictions to save costs
4. **Verify uploads:** Use `modal volume ls` after uploading

### Development
1. **Test locally first:** Validate data before uploading
2. **Start small:** Test with subset before full training
3. **Monitor costs:** Check Modal dashboard regularly
4. **Use T4 for dev:** Switch to B200 only for production

### Version Control
1. **Don't commit data:** Keep `.gitignore` up to date
2. **Tag releases:** Use semantic versioning (v1.0.0)
3. **Document changes:** Update CHANGELOG.md
4. **Test before push:** Verify all commands work

## 📈 Performance Tuning

### For Better Accuracy
- Increase epochs (50 → 100)
- Use larger model (s → m → l)
- Add more training data
- Clean/fix annotations
- Increase confidence threshold

### For Faster Training
- Use smaller model (s → n)
- Reduce image size (1024 → 640)
- Reduce epochs (50 → 30)
- Use faster GPU (T4 → B200)
- Increase batch size (if GPU allows)

### For Faster Prediction
- Use smaller model
- Reduce confidence threshold
- Use faster GPU
- Batch process multiple images

## 🚀 Next Steps

After getting familiar with the basics:

1. **Experiment:** Try different models and parameters
2. **Optimize:** Find best accuracy/speed tradeoff
3. **Scale:** Process larger batches
4. **Integrate:** Connect to your application
5. **Contribute:** Share improvements back to project

---

**Questions?** Open an issue on GitHub or check the documentation!
