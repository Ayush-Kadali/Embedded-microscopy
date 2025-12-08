# Developer Guide - Marine Plankton AI Microscopy System

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python main.py

# Validate configuration only
python main.py --validate-only

# Run with custom parameters
python main.py --magnification 2.5 --exposure 150 --gps-lat 12.34 --gps-lon 56.78
```

## Architecture Overview

The system follows a **strict modular architecture** where each stage is an independent, replaceable module with standardized input/output contracts.

```
[Acquisition] → [Preprocessing] → [Segmentation] → [Classification] → [Counting] → [Analytics] → [Export]
```

### Key Principles

1. **High Cohesion**: Each module has one clear responsibility
2. **Low Coupling**: Modules communicate only via typed contracts
3. **Substitutability**: Any module can be replaced if it respects the contract

## Module Assignment Guide

### How to Work on a Module

Each team member can work on their assigned module independently by following these steps:

1. **Understand your module's contract** (input/output schemas)
2. **Implement the `process()` method** with your logic
3. **Keep the contract unchanged** - never modify input/output structure
4. **Test independently** using the module's unit tests

### Module Assignments

#### Module 1: Image Acquisition (`modules/acquisition.py`)
**Owner**: _Assign to hardware/camera specialist_

**Responsibility**: Capture microscope images and metadata

**Current Status**: Stub implementation with synthetic images

**To Implement**:
- Integrate Picamera2/libcamera for Raspberry Pi HQ camera
- Implement auto-focus (if motorized stage available)
- Add real GPS integration (via gpsd or serial GPS)
- Implement sensor temperature reading
- Handle camera errors gracefully

**Input Contract**:
```python
{
    'magnification': float,          # 0.7-4.5
    'exposure_ms': int,
    'focus_position': int | None,
    'capture_metadata': {
        'timestamp': str,            # ISO 8601
        'gps_lat': float | None,
        'gps_lon': float | None,
        'operator_id': str | None,
    }
}
```

**Output Contract**:
```python
{
    'status': 'success' | 'error',
    'error_message': str | None,
    'image': np.ndarray[H, W, 3],    # uint8 RGB
    'metadata': {
        'capture_id': str,           # UUID
        'timestamp': str,
        'gps_coordinates': [lat, lon] | None,
        'magnification': float,
        'exposure_ms': int,
        'resolution_um_per_px': float,
        'fov_mm': [width_mm, height_mm],
        'sensor_temp_c': float | None,
    }
}
```

**Key Tasks**:
- [ ] Integrate Picamera2
- [ ] Calibrate µm/pixel for different magnifications
- [ ] Add GPS module integration
- [ ] Implement auto-exposure
- [ ] Add focus stacking (optional)

---

#### Module 2: Preprocessing (`modules/preprocessing.py`)
**Owner**: _Assign to image processing specialist_

**Responsibility**: Denoise, normalize, and correct illumination

**Current Status**: Basic implementation with OpenCV filters

**To Implement**:
- Fine-tune denoising parameters for microscope images
- Implement adaptive flatfield correction
- Add quality assessment metrics
- Optimize for speed on Raspberry Pi

**Input Contract**:
```python
{
    'image': np.ndarray[H, W, 3],
    'preprocessing_config': {
        'denoise_method': str,       # 'gaussian' | 'bilateral' | 'nlm'
        'normalize': bool,
        'background_correction': bool,
        'flatfield_correction': bool,
        'illumination_profile': np.ndarray | None,
    }
}
```

**Output Contract**:
```python
{
    'status': str,
    'error_message': str | None,
    'processed_image': np.ndarray[H, W, 3],
    'preprocessing_stats': {
        'mean_intensity': float,
        'std_intensity': float,
        'snr_db': float | None,
        'background_level': float | None,
    }
}
```

**Key Tasks**:
- [ ] Optimize denoise methods for plankton images
- [ ] Implement rolling-ball background subtraction
- [ ] Add image quality checks
- [ ] Profile and optimize performance

---

#### Module 3: Segmentation (`modules/segmentation.py`)
**Owner**: _Assign to computer vision specialist_

**Responsibility**: Detect individual organisms

**Current Status**: Watershed and threshold methods implemented

**To Implement**:
- Fine-tune watershed parameters
- Add instance segmentation model support (YOLO, Mask R-CNN)
- Handle severe overlaps better
- Add size-based filtering

**Input Contract**:
```python
{
    'image': np.ndarray[H, W, 3],
    'segmentation_config': {
        'method': str,               # 'threshold' | 'watershed' | 'instance_seg'
        'min_area_px': int,
        'max_area_px': int,
        'handle_overlaps': bool,
        'model_path': str | None,
    }
}
```

**Output Contract**:
```python
{
    'status': str,
    'error_message': str | None,
    'masks': list[np.ndarray],       # Boolean masks
    'bounding_boxes': list[dict(x, y, w, h)],
    'centroids': list[(x, y)],
    'areas_px': list[int],
    'num_detected': int,
}
```

**Key Tasks**:
- [ ] Train/integrate instance segmentation model
- [ ] Optimize watershed parameters
- [ ] Add overlap handling heuristics
- [ ] Benchmark different methods

---

#### Module 4: Classification (`modules/classification.py`)
**Owner**: _Assign to ML/deep learning specialist_

**Responsibility**: Classify organisms by species/type

**Current Status**: Stub with random predictions

**To Implement**:
- Train plankton classification model
- Convert to TFLite for edge deployment
- Implement quantization for speed
- Add confidence calibration

**Input Contract**:
```python
{
    'image': np.ndarray[H, W, 3],
    'masks': list[np.ndarray],
    'bounding_boxes': list[dict],
    'classification_config': {
        'model_path': str,
        'class_names': list[str],
        'confidence_threshold': float,
        'top_k': int,
    }
}
```

**Output Contract**:
```python
{
    'status': str,
    'error_message': str | None,
    'predictions': list[{
        'organism_id': int,
        'class_name': str,
        'confidence': float,
        'top_k_predictions': list[dict],
    }],
    'model_metadata': {
        'model_name': str,
        'version': str,
        'input_size': (int, int),
        'inference_time_ms': float,
    }
}
```

**Key Tasks**:
- [ ] Collect and label training data
- [ ] Train CNN classifier (MobileNet, EfficientNet)
- [ ] Convert to TFLite and quantize
- [ ] Benchmark inference speed
- [ ] Add model versioning

---

#### Module 5: Counting & Sizing (`modules/counting.py`)
**Owner**: _Assign to data analysis specialist_

**Responsibility**: Aggregate counts and compute sizes

**Current Status**: Complete implementation

**To Implement**:
- Add spatial distribution analysis
- Implement size calibration validation
- Add statistical outlier detection

**Key Tasks**:
- [ ] Validate size estimation accuracy
- [ ] Add spatial clustering analysis
- [ ] Implement size outlier filtering

---

#### Module 6: Analytics (`modules/analytics.py`)
**Owner**: _Assign to ecology/statistics specialist_

**Responsibility**: Compute diversity indices and bloom detection

**Current Status**: Complete implementation

**To Implement**:
- Add more diversity metrics (evenness, dominance)
- Implement time-series trend analysis
- Add ecological alert thresholds

**Key Tasks**:
- [ ] Add Pielou's evenness index
- [ ] Implement trend detection algorithms
- [ ] Create bloom prediction model

---

#### Module 7: Export (`modules/export.py`)
**Owner**: _Assign to full-stack/dashboard developer_

**Responsibility**: Export results and generate dashboard

**Current Status**: CSV/JSON export complete, dashboard stub

**To Implement**:
- Build Streamlit dashboard
- Add Folium map visualization
- Implement real-time plotting
- Add data archival to database

**Key Tasks**:
- [ ] Create interactive Streamlit dashboard
- [ ] Add GPS-based map visualization
- [ ] Implement time-series plots
- [ ] Add export to database (SQLite/PostgreSQL)

---

## Testing Your Module

### Unit Testing

Create a test file in `tests/test_<module_name>.py`:

```python
import pytest
from modules.your_module import YourModule

def test_module_basic():
    # Initialize module
    config = {'param1': 'value1'}
    module = YourModule(config)

    # Prepare input
    input_data = {
        # ... your input contract
    }

    # Execute
    result = module.process(input_data)

    # Verify
    assert result['status'] == 'success'
    assert 'expected_output_key' in result
```

Run tests:
```bash
pytest tests/test_your_module.py -v
```

### Integration Testing

Test your module in the full pipeline:

```python
from pipeline import PipelineManager
import yaml

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Initialize pipeline
pipeline = PipelineManager(config)

# Get your module
your_module = pipeline.get_module('your_module_name')

# Test independently
result = your_module.process(input_data)
```

## Contract Compliance

### Rules for Modifying Modules

1. **NEVER change the input/output contract** without team discussion
2. **ALWAYS maintain backward compatibility**
3. **MUST handle errors** using `handle_error()` method
4. **MUST validate input** in `validate_input()`
5. **MUST validate config** in `validate_config()`

### Adding New Features

If you need to add new output fields:

1. Add them as **optional** fields (don't break existing code)
2. Document in module docstring
3. Update this guide
4. Notify team

## Performance Optimization

Target performance on Raspberry Pi 4 (4GB):
- **Acquisition**: <1s per image
- **Preprocessing**: <2s
- **Segmentation**: <5s
- **Classification**: <3s (for 20 organisms)
- **Total pipeline**: <15s per sample

### Optimization Tips

1. Use **quantized models** (INT8) for classification
2. **Vectorize** operations with NumPy
3. **Resize** images before processing if possible
4. Use **OpenCV** instead of PIL/scipy when possible
5. **Profile** your code: `python -m cProfile main.py`

## Deployment

### Raspberry Pi Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-opencv python3-numpy libatlas-base-dev

# Install picamera2
sudo apt install -y python3-picamera2

# Install Python packages
pip3 install -r requirements.txt

# Run pipeline
python3 main.py
```

### Configuration for Different Hardware

Copy and modify hardware profiles in `config/hardware_profiles/`:

- `pi4.yaml` - Raspberry Pi 4
- `jetson.yaml` - NVIDIA Jetson (future)
- `laptop.yaml` - Development on laptop

## Common Issues

### Import Errors
```bash
# Make sure you're in project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Camera Not Found
```bash
# Check camera connection
libcamera-hello --list-cameras

# Check permissions
sudo usermod -a -G video $USER
```

### Slow Inference
- Use quantized TFLite models
- Reduce image resolution in preprocessing
- Use smaller model architecture (MobileNetV2)

## Communication

When making changes:
1. Update module docstring
2. Update this guide if contract changes
3. Notify team in chat/standup
4. Create pull request with clear description

## Contact

- **Project Lead**: [Name]
- **Architecture**: [Name]
- **ML Team**: [Name]
- **Hardware Team**: [Name]
