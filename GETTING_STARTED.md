# Getting Started with Solform YOLO

Complete beginner's guide to using this project.

## 📚 What You'll Learn

By the end of this guide, you'll be able to:
- Train a custom YOLO model on your form images
- Run predictions on new forms
- Download and use the results

**Time required:** 30-45 minutes (excluding training time)

---

## 🎓 Before You Begin

### What You Need

1. **Python 3.12 or higher**
   ```bash
   python --version  # Should show 3.12+
   ```

2. **Modal Account** (free tier available)
   - Sign up at [modal.com](https://modal.com)
   - No credit card required for free tier

3. **Training Data**
   - PNG images of forms
   - JSON annotations for each image
   - Format: See `example_annotation.json`

### Recommended Setup

- **Operating System:** Windows, Mac, or Linux (all supported)
- **Internet Connection:** Required for Modal
- **Disk Space:** ~1GB free (for training data)

---

## 🚀 Step-by-Step Tutorial

### Part 1: Installation (5 minutes)

#### 1. Get the Code

**Option A: Download ZIP**
```bash
# On GitHub, click "Code" → "Download ZIP"
# Extract to your desired location
cd path/to/extracted/folder
```

**Option B: Git Clone** (if you have Git)
```bash
git clone https://github.com/yourusername/solform-yolo.git
cd solform-yolo
```

#### 2. Install Modal

```bash
# Install the only required package
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed modal-0.63.0
```

#### 3. Authenticate with Modal

```bash
modal token new
```

**What happens:**
1. Your browser opens
2. Log in to Modal (or create account)
3. Click "Authorize"
4. Terminal shows: "Token created successfully"

✅ **Checkpoint:** You should see "Authentication successful"

---

### Part 2: Setup Infrastructure (5 minutes)

#### 1. Create Modal Volume

```bash
modal run setup_modal.py
```

**Expected output:**
```
============================================================
STARTING MODAL SETUP
============================================================
[1/2] Creating/checking volume...
✓ Volume 'solform-data' is ready
[2/2] Creating directories...
✓ Created /data/ExportSFsPNGs
✓ Created /data/predict_inputs
✓ Created /data/predict_outputs
✓ Created /data/runs
============================================================
✓ SETUP COMPLETE!
============================================================
```

**What this did:**
- Created cloud storage called "solform-data"
- Set up folder structure for training and predictions

✅ **Checkpoint:** All directories created successfully

---

### Part 3: Prepare Training Data (10 minutes)

#### 1. Organize Your Data

Create a folder with your training images:

```bash
training_data/
├── form001.png
├── form001.json
├── form002.png
├── form002.json
└── ...
```

**Requirements:**
- Each PNG must have a matching JSON file
- JSON format must match `example_annotation.json`
- Images should be clear and readable

#### 2. Verify Data Format

Check one JSON file:
```bash
cat training_data/form001.json
```

Should look like:
```json
{
  "regions": [
    {
      "tags": ["text_line"],
      "boundingBox": {
        "left": 120,
        "top": 100,
        "width": 450,
        "height": 25
      }
    }
  ]
}
```

#### 3. Upload to Modal

```bash
# Upload all training data
modal volume put solform-data ./training_data /ExportSFsPNGs
```

**Expected output:**
```
Uploading 100 files... ━━━━━━━━━━━━━━ 100% 0:00:10
✓ Upload complete
```

#### 4. Verify Upload

```bash
modal volume ls solform-data /ExportSFsPNGs
```

Should show all your files:
```
form001.png
form001.json
form002.png
form002.json
...
```

✅ **Checkpoint:** All files visible in Modal volume

---

### Part 4: Train Model (Variable time, ~10 min setup)

#### 1. Start Training

```bash
modal run train_standalone.py
```

**Initial output:**
```
============================================================
STARTING TRAINING PIPELINE
============================================================
[1/4] Creating dataset structure... ✓
[2/4] Converting annotations... ✓ Converted 100 images
[3/4] Creating YOLO configuration... ✓
[4/4] Training model...
  Model: yolov8s.pt
  Epochs: 50
  Image size: 1024
  Batch size: 32
```

**Then training begins:**
```
Epoch 1/50: 100% ━━━━━━━━━━━━━━ 30/30 0:01:25
  mAP50: 0.007
Epoch 2/50: 100% ━━━━━━━━━━━━━━ 30/30 0:01:20
  mAP50: 0.052
...
```

**Training time depends on:**
- Number of images (100 images ≈ 5 minutes, 1000 images ≈ 30 minutes)
- Number of epochs (50 epochs recommended)
- GPU type (B200 is fastest)

#### 2. Monitor Progress

**Option A: Watch Terminal**
- Shows epoch-by-epoch progress
- Updates every ~1-2 minutes

**Option B: Modal Dashboard**
1. Go to [modal.com/apps](https://modal.com/apps)
2. Click on "solform-yolo-max"
3. View real-time logs and GPU usage

#### 3. Training Complete

**Final output:**
```
Epoch 50/50: 100% ━━━━━━━━━━━━━━ 30/30 0:01:15
============================================================
✓ TRAINING COMPLETE!
============================================================
Images trained: 100
Model saved to: /data/runs/forms/weights/best.pt

Run predictions:
  modal run predict_standalone.py
```

**What you got:**
- Trained YOLO model (`best.pt`)
- Training metrics (in `/runs/forms/`)
- Model ready for predictions

✅ **Checkpoint:** Training completed, model saved

---

### Part 5: Run Predictions (5 minutes)

#### 1. Prepare Images to Process

Create a folder with new form images:
```bash
new_forms/
├── invoice001.png
├── invoice002.png
└── ...
```

**Note:** These should be **different** from training images

#### 2. Upload Images

```bash
modal volume put solform-data ./new_forms /predict_inputs
```

#### 3. Run Prediction

```bash
modal run predict_standalone.py
```

**Output:**
```
============================================================
STARTING PREDICTION PIPELINE
============================================================
[1/3] Loading model... ✓
[2/3] Finding input images... ✓ Found 10 images
[3/3] Running predictions...
  ✓ invoice001.png: 150 detected → 38 kept
  ✓ invoice002.png: 200 detected → 45 kept
  ...
============================================================
✓ PREDICTION COMPLETE!
============================================================
Results saved to: /data/predict_outputs
```

**What happened:**
- Loaded your trained model
- Detected form elements in each image
- Filtered out noise and artifacts
- Saved annotated images + JSON data

✅ **Checkpoint:** Predictions completed

---

### Part 6: Download Results (5 minutes)

#### 1. Download All Results

```bash
modal volume get solform-data /predict_outputs ./results
```

#### 2. Check Results

```bash
ls results/
```

You'll see:
```
invoice001.png          # Annotated image with boxes
invoice001.json         # Detection data
invoice002.png
invoice002.json
...
```

#### 3. View Annotated Images

Open any PNG file:
- Red boxes around detected elements
- Labels showing element type + confidence

#### 4. Parse JSON Data

Example JSON:
```json
[
  {
    "type": "text_line",
    "confidence": 0.923,
    "bbox": {
      "x": 102.3,
      "y": 45.8,
      "w": 198.5,
      "h": 28.2
    }
  }
]
```

Use this data in your application!

✅ **Checkpoint:** Results downloaded and viewable

---

## 🎉 Congratulations!

You've successfully:
- ✅ Set up Modal infrastructure
- ✅ Uploaded and converted training data
- ✅ Trained a custom YOLO model
- ✅ Run predictions on new forms
- ✅ Downloaded structured results

---

## 🔄 Next Steps

### Continue Using the Model

```bash
# For each new batch:
1. Upload images
   modal volume put solform-data ./batch_new /predict_inputs

2. Run prediction
   modal run predict_standalone.py

3. Download results
   modal volume get solform-data /predict_outputs ./batch_new_results

4. Clean up
   modal volume rm solform-data /predict_inputs/*
```

### Improve the Model

```bash
# Add more training data
modal volume put solform-data ./more_data /ExportSFsPNGs

# Retrain
modal run train_standalone.py
```

### Customize Configuration

Edit `train_standalone.py` or `predict_standalone.py`:
- Change GPU type (line ~53)
- Adjust model size (line ~29)
- Modify detection filters (line ~44)

---

## 🆘 Common Issues

### "Authentication failed"
```bash
modal token new  # Redo authentication
```

### "Volume not found"
```bash
modal run setup_modal.py  # Recreate volume
```

### "No training data found"
```bash
modal volume ls solform-data /ExportSFsPNGs  # Verify upload
```

### Training takes too long
- Use smaller model: Change `"model": "yolov8n.pt"`
- Reduce epochs: Change `"epochs": 30`
- Use fewer images for testing

### Low prediction accuracy
- Train longer: Change `"epochs": 100`
- Add more training data
- Check annotation quality

---

## 📚 Additional Resources

- **Full Documentation:** [README.md](README.md)
- **Command Reference:** [QUICKSTART.md](QUICKSTART.md)
- **Modal Docs:** [modal.com/docs](https://modal.com/docs)
- **YOLO Docs:** [docs.ultralytics.com](https://docs.ultralytics.com)

---

## 💬 Get Help

- **Questions:** Open a [GitHub Issue](https://github.com/yourusername/solform-yolo/issues)
- **Bugs:** Report via [GitHub Issues](https://github.com/yourusername/solform-yolo/issues)
- **Discussions:** Use [GitHub Discussions](https://github.com/yourusername/solform-yolo/discussions)

---

**Happy detecting! 🎯**
