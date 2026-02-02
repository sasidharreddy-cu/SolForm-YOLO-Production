# Solform YOLO - Form Element Detection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Modal](https://img.shields.io/badge/platform-Modal-blueviolet.svg)](https://modal.com)

**Production-ready YOLOv8 pipeline for detecting form elements from document images.** Identifies text lines, text blocks, checkboxes, and signatures with 91% accuracy. Runs entirely on Modal's serverless GPU infrastructure.

![Prediction Example](https://via.placeholder.com/800x200.png?text=Form+Detection+Example)

## ✨ Features

- **🎯 4-Class Detection**: text_line, text_block, checkbox, signature
- **🧠 Smart Filtering**: Removes footer artifacts and oversized boxes automatically
- **⚡ Fast Training**: ~7.4 minutes on B200 GPU for 662 images
- **📦 Batch Processing**: Process multiple forms simultaneously
- **💾 Dual Output**: Annotated images + structured JSON
- **☁️ Cloud-Native**: No local GPU required

## 📊 Performance

Trained on 662 images with 50 epochs:

| Metric | Score |
|--------|-------|
| **mAP50** | **91.0%** |
| Precision | 92.8% |
| Recall | 83.4% |
| Training Time | 7.4 min (B200) |

**Per-Class Results:**
- text_line: 86.7% mAP50
- checkbox: 95.4% mAP50

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Modal Account** - [Sign up free](https://modal.com)
- **Training Data** - PNG images + JSON annotations

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/solform-yolo.git
cd solform-yolo

# 2. Install Modal
pip install -r requirements.txt

# 3. Authenticate with Modal
modal token new
```

### First-Time Setup

```bash
# Create Modal volume and directories
modal run setup_modal.py
```

**Output:**
```
✓ Volume 'solform-data' ready
✓ Created /data/ExportSFsPNGs
✓ Created /data/predict_inputs
✓ Created /data/predict_outputs
✓ Created /data/runs
✓ SETUP COMPLETE!
```

### Training

```bash
# 1. Upload training data
modal volume put solform-data ./training_data /ExportSFsPNGs

# 2. Verify upload
modal volume ls solform-data /ExportSFsPNGs

# 3. Train model
modal run train_standalone.py
```

**Training Output:**
```
============================================================
STARTING TRAINING PIPELINE
============================================================
[1/4] Creating dataset structure... ✓
[2/4] Converting annotations... ✓ Converted 662 images
[3/4] Creating YOLO configuration... ✓
[4/4] Training model...
  Epoch 1/50: mAP50: 0.007
  ...
  Epoch 50/50: mAP50: 0.910
============================================================
✓ TRAINING COMPLETE!
============================================================
Model saved to: /data/runs/forms/weights/best.pt
```

**Training Cost:** ~$8-12 on B200 GPU

### Prediction

```bash
# 1. Upload images to predict on
modal volume put solform-data ./new_forms /predict_inputs

# 2. Run prediction
modal run predict_standalone.py

# 3. Download results
modal volume get solform-data /predict_outputs ./results
```

**Prediction Output:**
```
============================================================
STARTING PREDICTION PIPELINE
============================================================
[1/3] Loading model... ✓
[2/3] Finding input images... ✓ Found 7 images
[3/3] Running predictions...
  ✓ form1.png: 227 detected → 38 kept
  ✓ form2.png: 300 detected → 37 kept
============================================================
✓ PREDICTION COMPLETE!
============================================================
Results saved to: /data/predict_outputs
```

**Prediction Cost:** ~$0.50 per 100 images

---

## 📁 Project Structure

```
solform-yolo/
├── README.md                      # This file
├── QUICKSTART.md                  # Command reference
├── LICENSE                        # MIT License
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git exclusions
│
├── setup_modal.py                 # One-time Modal setup
├── cleanup_modal.py               # Delete all data (reset)
│
├── train_standalone.py            # Training pipeline ⭐
├── predict_standalone.py          # Prediction pipeline ⭐
│
├── example_annotation.json        # Sample annotation format
│
└── training_data/                 # Your training data (not in git)
    ├── form001.png
    ├── form001.json
    └── ...
```

**⭐ = Main files you'll use**

---

## 📝 Training Data Format

Your JSON annotations should match this structure:

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
    },
    {
      "tags": ["checkbox"],
      "boundingBox": {
        "left": 50,
        "top": 200,
        "width": 20,
        "height": 20
      }
    }
  ]
}
```

**Supported tags:**
- `text_line` - Single line of text
- `text_block` - Paragraph or multi-line text
- `checkbox` - Checkbox or radio button
- `signature` - Signature field

See `example_annotation.json` for a complete example.

---

## 💾 Output Format

### JSON Detection Format

Each detected element:

```json
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
```

### Annotated Images

- Red bounding boxes around elements
- Labels showing class + confidence score
- Same filename as input (PNG format)

Example: `form1.png` → `form1.png` (annotated) + `form1.json` (detections)

---

## ⚙️ Configuration

Edit settings in `train_standalone.py` or `predict_standalone.py`:

### Model Selection

```python
TRAINING = {
    "model": "yolov8s.pt",  # Change here
    "epochs": 50,
    "imgsz": 1024,
    "batch": 32
}
```

| Model | Speed | Accuracy | Size | Best For |
|-------|-------|----------|------|----------|
| yolov8n | Fastest | Good | 6MB | Quick testing |
| **yolov8s** | **Fast** | **Better** | **22MB** | **Recommended** |
| yolov8m | Medium | Great | 52MB | High accuracy |
| yolov8l | Slow | Excellent | 88MB | Maximum accuracy |

### GPU Selection

```python
GPU_CONFIG = {
    "gpu": "B200",  # Change here
    "memory": (131_072, 131_072)  # 128GB
}
```

| GPU | VRAM | Speed | Cost/hr | Best For |
|-----|------|-------|---------|----------|
| T4 | 16GB | 1x | $0.60 | Budget training |
| A10G | 24GB | 3x | $1.10 | Balanced |
| A100 | 40GB | 5x | $3.14 | Fast training |
| **B200** | **192GB** | **10x** | **$6.50** | **Production** |

### Detection Filters

```python
FILTER_CONFIG = {
    "min_confidence": 0.35,      # Minimum confidence score
    "bottom_margin": 0.95,       # Remove footer boxes
    "max_height_ratio": 0.15,    # Remove tall artifacts
    "max_width_ratio": 0.95      # Remove wide artifacts
}
```

Adjust these to:
- **Increase precision**: Raise `min_confidence` to 0.5
- **Increase recall**: Lower `min_confidence` to 0.25
- **Remove more noise**: Decrease `max_height_ratio`

---

## 🛠️ Common Tasks

### Check Modal Volume Contents

```bash
# List all files
modal volume ls solform-data

# Check training data
modal volume ls solform-data /ExportSFsPNGs

# Check predictions
modal volume ls solform-data /predict_outputs
```

### Download Files from Modal

```bash
# Download trained model
modal volume get solform-data /runs ./local_runs

# Download predictions
modal volume get solform-data /predict_outputs ./results
```

### Delete Files from Modal

```bash
# Delete specific file
modal volume rm solform-data /predict_inputs/old_file.png

# Delete entire directory
modal volume rm solform-data /predict_outputs/*
```

### Complete Reset

```bash
# Delete everything and start fresh
modal run cleanup_modal.py
# Type 'DELETE' to confirm

# Re-run setup
modal run setup_modal.py
```

### Monitor Training

Visit [modal.com/apps](https://modal.com/apps) to:
- View real-time logs
- Monitor GPU utilization
- Track training progress
- Check costs

---

## 💰 Cost Optimization

| Strategy | Impact | Savings |
|----------|--------|---------|
| Use T4 instead of B200 | Slower training | **90% cheaper** |
| Reduce epochs (50 → 30) | Slightly lower accuracy | 40% less time |
| Use yolov8n model | Faster training | 50% faster |
| Reduce batch size | Lower memory | Slower per epoch |
| Delete old runs | Storage | $0.10/GB/month |

**Typical Costs:**
- **Training** (50 epochs, 662 images, B200): $8-12
- **Prediction** (100 images, B200): $0.50
- **Storage** (10GB data): $1/month

---

## 🐛 Troubleshooting

### Error: "Volume not found"

```bash
modal run setup_modal.py
```

### Error: "Model not found"

Train the model first:
```bash
modal run train_standalone.py
```

### Error: "No images found"

Upload training data:
```bash
modal volume put solform-data ./training_data /ExportSFsPNGs
modal volume ls solform-data /ExportSFsPNGs  # Verify
```

### Out of GPU Memory

Reduce batch size in the script:
```python
TRAINING = {"batch": 16}  # or 8
```

### Low Accuracy

Try these:
1. Increase epochs: `"epochs": 100`
2. Use larger model: `"model": "yolov8m.pt"`
3. Add more training data
4. Lower confidence threshold: `"min_confidence": 0.25`

### Slow Training

Try these:
1. Use smaller model: `"model": "yolov8n.pt"`
2. Reduce image size: `"imgsz": 640`
3. Increase batch size (if GPU allows): `"batch": 64`

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/solform-yolo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/solform-yolo/discussions)
- **Modal Docs**: [modal.com/docs](https://modal.com/docs)
- **YOLO Docs**: [docs.ultralytics.com](https://docs.ultralytics.com)

---

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection framework
- [Modal](https://modal.com) - Serverless compute platform
- All contributors and users of this project

---

## 📈 Roadmap

- [ ] Support for additional form elements (tables, radio buttons)
- [ ] Model versioning and A/B testing
- [ ] Web demo interface
- [ ] Automated testing pipeline
- [ ] PDF input support
- [ ] Multi-page document processing
- [ ] Export to COCO format

---

**Made with ❤️ for form processing automation**

*Questions? Open an issue or start a discussion!*
