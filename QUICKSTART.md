# Solform YOLO - Quick Command Reference

Quick reference for common commands. See [README.md](README.md) for detailed instructions.

## 📦 Initial Setup

```bash
# Install
pip install -r requirements.txt

# Authenticate with Modal
modal token new

# Create Modal volume
modal run setup_modal.py
```

---

## 🏋️ Training

```bash
# Upload training data
modal volume put solform-data ./training_data /ExportSFsPNGs

# Verify upload
modal volume ls solform-data /ExportSFsPNGs

# Train model
modal run train_standalone.py

# Download trained model (optional)
modal volume get solform-data /runs ./local_runs
```

---

## 🔮 Prediction

```bash
# Upload images
modal volume put solform-data ./new_forms /predict_inputs

# Run predictions
modal run predict_standalone.py

# Download results
modal volume get solform-data /predict_outputs ./results

# Clean up inputs (optional)
modal volume rm solform-data /predict_inputs/*
```

---

## 📂 Volume Management

### List Files
```bash
# List all
modal volume ls solform-data

# List specific directory
modal volume ls solform-data /ExportSFsPNGs
modal volume ls solform-data /predict_outputs
modal volume ls solform-data /runs
```

### Upload Files
```bash
# Upload directory
modal volume put solform-data ./local_dir /remote_dir

# Upload single file
modal volume put solform-data ./file.png /predict_inputs/file.png
```

### Download Files
```bash
# Download directory
modal volume get solform-data /remote_dir ./local_dir

# Download single file
modal volume get solform-data /runs/forms/weights/best.pt ./model.pt
```

### Delete Files
```bash
# Delete single file
modal volume rm solform-data /predict_inputs/file.png

# Delete directory contents
modal volume rm solform-data /predict_outputs/*

# Delete entire directory
modal volume rm solform-data /predict_outputs
```

---

## 🔄 Complete Reset

```bash
# Delete all data
modal run cleanup_modal.py
# Type 'DELETE' to confirm

# Re-create volume
modal run setup_modal.py
```

---

## 🔍 Monitoring

### View Logs
```bash
# Visit Modal dashboard
# https://modal.com/apps

# Or use CLI
modal app logs solform-yolo-max
```

### List Apps
```bash
modal app list
```

### Stop Running App
```bash
modal app stop solform-yolo-max
```

---

## 🎯 Common Workflows

### First Time Training
```bash
modal run setup_modal.py
modal volume put solform-data ./training_data /ExportSFsPNGs
modal run train_standalone.py
```

### Batch Predictions
```bash
modal volume put solform-data ./batch_001 /predict_inputs
modal run predict_standalone.py
modal volume get solform-data /predict_outputs ./batch_001_results
modal volume rm solform-data /predict_inputs/*
```

### Retrain with New Data
```bash
# Upload new data
modal volume put solform-data ./more_training_data /ExportSFsPNGs

# Verify combined data
modal volume ls solform-data /ExportSFsPNGs

# Retrain
modal run train_standalone.py
```

---

## 🐛 Quick Fixes

### "Volume not found"
```bash
modal run setup_modal.py
```

### "Model not found"
```bash
modal run train_standalone.py
```

### "No images found" in training
```bash
modal volume put solform-data ./training_data /ExportSFsPNGs
```

### "No images found" in prediction
```bash
modal volume put solform-data ./new_forms /predict_inputs
```

### Check Modal authentication
```bash
modal token new
```

### View Modal status
```bash
modal status
```

---

## ⚙️ Configuration Quick Edit

Edit these lines in the Python scripts:

### Change GPU
```python
GPU_CONFIG = {
    "gpu": "T4",  # T4, A10G, A100, or B200
}
```

### Change Model
```python
TRAINING = {
    "model": "yolov8n.pt",  # n, s, m, l, or x
}
```

### Change Epochs
```python
TRAINING = {
    "epochs": 30,  # Reduce for faster training
}
```

### Change Confidence Threshold
```python
FILTER_CONFIG = {
    "min_confidence": 0.25,  # Lower = more detections
}
```

---

## 📊 Check Results

### View Training Metrics
```bash
modal volume get solform-data /runs/forms/results.csv ./results.csv
cat results.csv
```

### Count Predictions
```bash
modal volume ls solform-data /predict_outputs | wc -l
```

### Check Storage Usage
```bash
modal volume ls solform-data
```

---

## 💡 Tips

1. **Always verify uploads**: Use `modal volume ls` after uploading
2. **Monitor costs**: Check [modal.com/apps](https://modal.com/apps) regularly
3. **Clean up old data**: Delete unused predictions to save storage costs
4. **Use T4 GPU for testing**: Switch to B200 only for production training
5. **Backup your model**: Download `best.pt` after training

---

For detailed explanations, see [README.md](README.md)
