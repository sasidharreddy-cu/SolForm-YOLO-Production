# Contributing to Solform YOLO

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide details**:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, Modal version)
   - Error messages and logs

### Suggesting Features

1. **Open an issue** with the `enhancement` label
2. **Explain the use case** and benefits
3. **Provide examples** if possible

### Submitting Code

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow the code style guidelines below
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes**:
   - Run training and prediction to ensure nothing breaks
   - Test on Modal's infrastructure
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots/examples if applicable

## 📝 Code Style Guidelines

### Python

- **Follow PEP 8** style guide
- **Use type hints** where appropriate
- **Maximum line length**: 88 characters (Black formatter style)
- **Naming conventions**:
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Variables: `snake_case`

### Comments

```python
# Good: Explains WHY, not WHAT
# Skip tiny boxes because they're usually noise from scanning artifacts
if bw < FILTER_CONFIG["min_box_size"]:
    continue

# Bad: Just describes what the code does
# Check if width is less than minimum
if bw < FILTER_CONFIG["min_box_size"]:
    continue
```

### Docstrings

Use Google-style docstrings:

```python
def process_image(img_path, confidence=0.5):
    """
    Process a single image and detect form elements.
    
    Args:
        img_path: Path to the image file
        confidence: Minimum confidence threshold (0-1)
        
    Returns:
        List of detected bounding boxes with class labels
        
    Raises:
        FileNotFoundError: If image file doesn't exist
    """
    pass
```

## 🧪 Testing

Before submitting:

1. **Test training**:
   ```bash
   modal run train_standalone.py
   ```

2. **Test prediction**:
   ```bash
   modal run predict_standalone.py
   ```

3. **Verify outputs**:
   - Check that model trains successfully
   - Verify predictions are generated
   - Ensure JSON output is valid

## 📚 Documentation

When adding features:

1. **Update README.md** if user-facing
2. **Update QUICKSTART.md** with new commands
3. **Add inline comments** for complex logic
4. **Include examples** in docstrings

## 🏗️ Project Structure

```
solform-yolo/
├── *.py                # Main scripts (keep these simple)
├── README.md          # Main documentation
├── QUICKSTART.md      # Command reference
├── CONTRIBUTING.md    # This file
└── ...
```

Keep scripts self-contained and well-documented.

## 🎯 Priority Areas

We're especially interested in contributions for:

1. **Performance Optimization**:
   - Faster training/prediction
   - Better GPU utilization
   - Memory efficiency

2. **New Features**:
   - Additional form element types (tables, radio buttons)
   - PDF support
   - Multi-page processing
   - Model versioning

3. **Documentation**:
   - Tutorial videos
   - More examples
   - FAQ expansion

4. **Testing**:
   - Automated tests
   - CI/CD pipeline
   - Performance benchmarks

## ❌ What Not to Contribute

- Large binary files (models, images) - use Git LFS if needed
- Breaking changes without discussion
- Code that doesn't follow style guidelines
- Features without documentation
- Untested code

## 💬 Getting Help

- **Questions**: Open a [Discussion](https://github.com/yourusername/solform-yolo/discussions)
- **Bugs**: Open an [Issue](https://github.com/yourusername/solform-yolo/issues)
- **Ideas**: Open an [Issue](https://github.com/yourusername/solform-yolo/issues) with `enhancement` label

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers
- Keep discussions on-topic

## 🎉 Recognition

Contributors will be:
- Listed in release notes
- Mentioned in README acknowledgments
- Given credit in commit history

Thank you for contributing! 🙏
