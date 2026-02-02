# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-01

### Added
- Initial release of Solform YOLO form detection pipeline
- YOLOv8-based detection for 4 form element classes:
  - text_line
  - text_block
  - checkbox
  - signature
- Standalone training pipeline (`train_standalone.py`)
- Standalone prediction pipeline (`predict_standalone.py`)
- Smart filtering system to remove artifacts and noise
- Modal infrastructure integration for serverless GPU computing
- Comprehensive documentation (README, QUICKSTART, CONTRIBUTING)
- Setup and cleanup scripts for Modal volumes
- Example annotation format
- MIT License

### Performance
- Training: ~7.4 minutes on B200 GPU (662 images, 50 epochs)
- Accuracy: 91.0% mAP50
- Precision: 92.8%
- Recall: 83.4%

### Configuration
- Configurable GPU selection (T4, A10G, A100, B200)
- Adjustable model sizes (yolov8n through yolov8x)
- Customizable detection filters
- Flexible training parameters

## [Unreleased]

### Planned
- Support for additional form elements (tables, radio buttons)
- PDF input support
- Multi-page document processing
- Model versioning system
- Web demo interface
- Automated testing pipeline
- Export to COCO format
