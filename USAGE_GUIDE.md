# Plankton Pipeline Usage Guide

Quick reference for running the pipeline in different modes.

---

## Table of Contents
1. [Synthetic Mode (Testing)](#synthetic-mode)
2. [File Mode (Upload Images)](#file-mode)
3. [Video Mode (Process Videos)](#video-mode)
4. [Camera Mode (Pi HQ Camera)](#camera-mode)
5. [Batch Processing](#batch-processing)

---

## Synthetic Mode

**Use Case**: Testing, development, demos without real data

```python
from pipeline.manager import PipelineManager
import yaml
from datetime import datetime

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Initialize
pipeline = PipelineManager(config)

# Run with synthetic data
params = {
    'mode': 'synthetic',
    'magnification': 2.5,
    'exposure_ms': 150,
    'capture_metadata': {
        'timestamp': datetime.now().isoformat(),
        'gps_lat': 12.34,
        'gps_lon': 56.78,
        'operator_id': 'demo'
    }
}

result = pipeline.execute_pipeline(params)
```

**Or use existing script**:
```bash
python simulate_pipeline.py -n 3
```

---

## File Mode

**Use Case**: Upload single images, process existing microscopy images

### Single Image

```python
from pipeline.manager import PipelineManager
import yaml
from datetime import datetime

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

pipeline = PipelineManager(config)

params = {
    'mode': 'file',
    'image_path': 'datasets/processed/samples/1_0.png',
    'magnification': 2.0,
    'exposure_ms': 100,
    'capture_metadata': {
        'timestamp': datetime.now().isoformat(),
        'gps_lat': None,
        'gps_lon': None,
        'operator_id': 'analysis'
    }
}

result = pipeline.execute_pipeline(params)

if result['status'] == 'success':
    print(f"Detected: {result['summary']['total_organisms']} organisms")
    print(f"Diversity: {result['summary']['shannon_diversity']:.3f}")
```

### Quick Test Script

```bash
python test_with_real_images.py
```

This will process all images in `datasets/processed/samples/`

---

## Video Mode

**Use Case**: Process uploaded videos, extract and analyze frames

### Process Single Frame

```python
params = {
    'mode': 'video',
    'video_path': 'path/to/microscopy_video.mp4',
    'frame_number': 0,  # Which frame to extract
    'magnification': 2.0,
    'exposure_ms': 100,
    'capture_metadata': {
        'timestamp': datetime.now().isoformat(),
        'operator_id': 'video_analysis'
    }
}

result = pipeline.execute_pipeline(params)
```

### Process All Frames (Batch)

```python
import cv2
from pathlib import Path

video_path = 'path/to/video.mp4'
cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.release()

results = []
for frame_num in range(0, total_frames, 10):  # Process every 10th frame
    params = {
        'mode': 'video',
        'video_path': video_path,
        'frame_number': frame_num,
        'magnification': 2.0,
        'exposure_ms': 100,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'operator_id': 'batch_video'
        }
    }

    result = pipeline.execute_pipeline(params)
    if result['status'] == 'success':
        results.append(result)
        print(f"Frame {frame_num}: {result['summary']['total_organisms']} organisms")

# Aggregate results
total_organisms = sum(r['summary']['total_organisms'] for r in results)
print(f"\nTotal across all frames: {total_organisms}")
```

---

## Camera Mode

**Use Case**: Real-time capture from Raspberry Pi HQ Camera

### Single Capture

```python
params = {
    'mode': 'camera',
    'magnification': 2.5,
    'exposure_ms': 150,
    'focus_position': None,  # Auto-focus
    'capture_metadata': {
        'timestamp': datetime.now().isoformat(),
        'gps_lat': 12.34,  # From GPS module
        'gps_lon': 56.78,
        'operator_id': 'field_survey'
    }
}

result = pipeline.execute_pipeline(params)
```

### Continuous Monitoring

```python
import time

# Monitor for 1 hour, capture every 5 minutes
duration = 60 * 60  # seconds
interval = 5 * 60   # seconds

start_time = time.time()
captures = []

while (time.time() - start_time) < duration:
    params = {
        'mode': 'camera',
        'magnification': 2.5,
        'exposure_ms': 150,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'gps_lat': get_gps_lat(),  # Your GPS function
            'gps_lon': get_gps_lon(),
            'operator_id': 'monitoring'
        }
    }

    result = pipeline.execute_pipeline(params)
    captures.append(result)

    print(f"Capture {len(captures)}: {result['summary']['total_organisms']} organisms")

    time.sleep(interval)

print(f"\nTotal captures: {len(captures)}")
```

---

## Batch Processing

### Process Directory of Images

```python
from pathlib import Path

image_dir = Path('datasets/raw/dataset_pm/test/Alexandrium')
image_files = list(image_dir.glob('*.png'))

results = []
for img_path in image_files[:10]:  # First 10 images
    params = {
        'mode': 'file',
        'image_path': str(img_path),
        'magnification': 2.0,
        'exposure_ms': 100,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'operator_id': 'batch_processing'
        }
    }

    result = pipeline.execute_pipeline(params)
    if result['status'] == 'success':
        results.append({
            'file': img_path.name,
            'organisms': result['summary']['total_organisms'],
            'diversity': result['summary']['shannon_diversity']
        })

# Summary
import pandas as pd
df = pd.DataFrame(results)
print(df)
print(f"\nAverage organisms per image: {df['organisms'].mean():.1f}")
```

---

## Configuration

### Adjust Processing Parameters

Edit `config/config.yaml`:

```yaml
preprocessing:
  denoise_method: 'bilateral'  # 'gaussian', 'bilateral', 'nlm', 'none'
  normalize: true
  background_correction: true

segmentation:
  method: 'watershed'  # 'threshold', 'watershed', 'instance_seg'
  min_area_px: 100
  max_area_px: 50000

classification:
  model_path: 'models/plankton_classifier.tflite'  # Update with your model
  confidence_threshold: 0.7
  class_names:
    - Copepod
    - Diatom
    - Dinoflagellate
    - Radiolarian
    - Foraminifera
```

### Command-Line Options

```bash
# Synthetic mode
python main.py --magnification 2.5 --exposure 150 --operator "field_team"

# With GPS
python main.py --gps-lat 12.34 --gps-lon 56.78

# Validation only
python main.py --validate-only
```

---

## Output Files

All results saved to `results/` directory:

### 1. Summary CSV
`results/summary_<uuid>.csv`
```csv
sample_id,timestamp,class_name,count,shannon_diversity,bloom_alert
abc123,2025-12-08T10:00:00,Copepod,15,1.234,False
abc123,2025-12-08T10:00:00,Diatom,3,1.234,False
```

### 2. Organisms CSV
`results/organisms_<uuid>.csv`
```csv
sample_id,organism_id,class_name,confidence,size_um,centroid_x_px,centroid_y_px
abc123,0,Copepod,0.87,45.2,100,200
abc123,1,Diatom,0.92,82.5,150,250
```

### 3. Full JSON
`results/results_<uuid>.json`
- Complete structured data
- All measurements and metadata
- Machine-readable format

---

## GPS Integration

### Using GPS Module (when available)

```python
import serial

def get_gps_coordinates():
    """Read from GPS module via serial"""
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        # Parse NMEA data
        # ... GPS parsing logic ...
        return lat, lon
    except:
        return None, None

# Use in pipeline
lat, lon = get_gps_coordinates()
params = {
    'mode': 'camera',
    'magnification': 2.5,
    'exposure_ms': 150,
    'capture_metadata': {
        'timestamp': datetime.now().isoformat(),
        'gps_lat': lat,
        'gps_lon': lon,
        'operator_id': 'survey'
    }
}
```

---

## Error Handling

```python
result = pipeline.execute_pipeline(params)

if result['status'] == 'success':
    print(f"Success! Detected {result['summary']['total_organisms']} organisms")
else:
    print(f"Error at: {result['failed_at']}")
    print(f"Message: {result['error_message']}")
    # Handle error appropriately
```

---

## Performance Tips

### For Raspberry Pi

1. **Use smaller images**: Resize if FOV allows
2. **Reduce denoise strength**: Faster processing
3. **Skip frames in video**: Process every Nth frame
4. **Use TFLite model**: Much faster than full models

```python
# Optimize for Pi
config['preprocessing']['denoise_method'] = 'gaussian'  # Faster
config['segmentation']['max_area_px'] = 20000  # Reduce search space
```

### For Batch Processing

```python
from multiprocessing import Pool

def process_image(img_path):
    # Each process gets its own pipeline
    pipeline = PipelineManager(config)
    params = {...}
    return pipeline.execute_pipeline(params)

# Process in parallel
with Pool(processes=4) as pool:
    results = pool.map(process_image, image_files)
```

---

## Troubleshooting

### Common Issues

**Issue**: "Picamera2 not available"
```bash
# On Raspberry Pi
pip install picamera2
```

**Issue**: Images too dark
```yaml
# Increase preprocessing contrast
preprocessing:
  normalize: true
  adaptive_histogram: true  # Add this
```

**Issue**: Too many/few organisms detected
```yaml
# Adjust thresholds
segmentation:
  min_area_px: 50   # Lower to detect smaller
  max_area_px: 100000  # Higher for colonies
```

**Issue**: Slow processing
- Use YOLOv8n (nano) instead of larger models
- Reduce image resolution
- Skip denoise step for faster processing

---

## Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify setup: `python verify_setup.py`
- [ ] Test with synthetic: `python simulate_pipeline.py`
- [ ] Test with file: `python test_with_real_images.py`
- [ ] Train/load your model
- [ ] Configure for your hardware
- [ ] Run in production mode

---

**For more details, see**:
- `README.md` - Project overview
- `REAL_DATA_TEST_RESULTS.md` - Test results
- `docs/CONTRACTS.md` - Module specifications
