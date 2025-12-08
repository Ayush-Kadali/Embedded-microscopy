# Module Contracts Specification

**Purpose**: Exact input/output contracts for all 7 modules

**Rule**: These contracts are immutable during hackathon. Do not change without team discussion.

---

## Module 1: Acquisition

### Input Contract
```python
{
    'magnification': float,              # Range: 0.7-4.5
    'exposure_ms': int,                  # Range: 50-500
    'focus_position': int | None,        # Optional, motor position
    'capture_metadata': {
        'timestamp': str,                # ISO 8601 format
        'gps_lat': float | None,         # Decimal degrees
        'gps_lon': float | None,         # Decimal degrees
        'operator_id': str | None,       # String identifier
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,         # Error description if status="error"
    'image': np.ndarray,                 # Shape: (H, W, 3), dtype: uint8, RGB
    'metadata': {
        'capture_id': str,               # UUID
        'timestamp': str,                # ISO 8601
        'gps_coordinates': list[float] | None,  # [lat, lon] or None
        'magnification': float,          # Echo from input
        'exposure_ms': int,              # Echo from input
        'resolution_um_per_px': float,   # Calculated from magnification
        'fov_mm': list[float],           # [width_mm, height_mm]
        'sensor_temp_c': float | None,   # Optional sensor temperature
        'focus_position': int | None,    # Echo from input
        'operator_id': str | None,       # Echo from input
    }
}
```

### Validation Rules
- `magnification` must be between 0.7 and 4.5
- `image` must be RGB (3 channels), uint8
- `image` shape must be at least (100, 100, 3)
- `capture_id` must be valid UUID
- `timestamp` must be ISO 8601 format

---

## Module 2: Preprocessing

### Input Contract
```python
{
    'image': np.ndarray,                 # Shape: (H, W, 3), dtype: uint8, RGB
    'preprocessing_config': {
        'denoise_method': str,           # "gaussian" | "bilateral" | "nlm" | "none"
        'normalize': bool,               # True/False
        'background_correction': bool,   # True/False
        'flatfield_correction': bool,    # True/False
        'illumination_profile': np.ndarray | None,  # Optional flatfield image
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,
    'processed_image': np.ndarray,       # Shape: same as input, dtype: uint8, RGB
    'preprocessing_stats': {
        'mean_intensity': float,         # Range: 0-255
        'std_intensity': float,          # Range: 0-255
        'snr_db': float | None,          # Signal-to-noise ratio in dB
        'background_level': float | None,  # Estimated background intensity
    }
}
```

### Validation Rules
- `processed_image` must have same shape as input `image`
- `processed_image` must be uint8
- `mean_intensity` must be between 0 and 255
- `denoise_method` must be one of valid options

---

## Module 3: Segmentation

### Input Contract
```python
{
    'image': np.ndarray,                 # Shape: (H, W, 3), dtype: uint8, RGB
    'segmentation_config': {
        'method': str,                   # "threshold" | "watershed" | "instance_seg"
        'min_area_px': int,              # Minimum organism area in pixels
        'max_area_px': int,              # Maximum organism area in pixels
        'handle_overlaps': bool,         # Enable overlap handling
        'model_path': str | None,        # Path to model if using instance_seg
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,
    'masks': list[np.ndarray],           # List of boolean masks, each shape (H, W)
    'bounding_boxes': list[dict],        # List of {'x': int, 'y': int, 'w': int, 'h': int}
    'centroids': list[tuple],            # List of (x, y) tuples
    'areas_px': list[int],               # List of areas in pixels
    'num_detected': int,                 # Total number of organisms detected
}
```

### Validation Rules
- All lists (`masks`, `bounding_boxes`, `centroids`, `areas_px`) must have same length
- Length of lists must equal `num_detected`
- Each mask must be boolean or uint8 (0/1)
- Each mask must have same H, W as input image
- Bounding boxes must have positive width and height
- Areas must be >= `min_area_px` and <= `max_area_px`

---

## Module 4: Classification

### Input Contract
```python
{
    'image': np.ndarray,                 # Shape: (H, W, 3), dtype: uint8, RGB
    'masks': list[np.ndarray],           # List of boolean masks
    'bounding_boxes': list[dict],        # List of {'x': int, 'y': int, 'w': int, 'h': int}
    'classification_config': {
        'model_path': str,               # Path to TFLite/ONNX model
        'class_names': list[str],        # List of class names
        'confidence_threshold': float,   # Range: 0.0-1.0
        'top_k': int,                    # Number of top predictions to return
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,
    'predictions': list[dict],           # One dict per organism
    # Each prediction dict:
    # {
    #     'organism_id': int,            # Index in input lists
    #     'class_name': str,             # Predicted class name
    #     'confidence': float,           # Range: 0.0-1.0
    #     'top_k_predictions': list[dict],  # Top K predictions
    #     # Each top_k dict: {'class_name': str, 'score': float}
    # }
    'model_metadata': {
        'model_name': str,               # Model identifier
        'version': str,                  # Model version
        'input_size': tuple[int, int],   # (height, width)
        'inference_time_ms': float,      # Total inference time
    }
}
```

### Validation Rules
- Length of `predictions` must equal length of input `masks`
- Each `organism_id` must be valid index (0 to len(masks)-1)
- Each `confidence` must be between 0.0 and 1.0
- Each `class_name` must be in `class_names` from config
- `top_k_predictions` must have length <= `top_k` from config
- Sum of scores in `top_k_predictions` should be close to 1.0 (softmax output)

---

## Module 5: Counting & Sizing

### Input Contract
```python
{
    'predictions': list[dict],           # From classification module
    'areas_px': list[int],               # From segmentation module
    'centroids': list[tuple],            # From segmentation module
    'metadata': dict,                    # From acquisition module (needs resolution_um_per_px)
    'counting_config': {
        'confidence_threshold': float,   # Range: 0.0-1.0
        'size_range_um': list[float],    # [min_um, max_um]
        'count_by_class': bool,          # True/False
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,
    'counts_by_class': dict[str, int],   # {'class_name': count}
    'total_count': int,                  # Sum of all counts
    'size_distribution': dict[str, dict],  # Per-class size stats
    # Each size_distribution entry:
    # {
    #     'class_name': {
    #         'mean_um': float,
    #         'std_um': float,
    #         'min_um': float,
    #         'max_um': float,
    #         'histogram': list[int],    # Binned size distribution
    #     }
    # }
    'organisms': list[dict],             # Filtered list of organisms
    # Each organism dict:
    # {
    #     'organism_id': int,
    #     'class_name': str,
    #     'confidence': float,
    #     'size_um': float,              # Equivalent diameter
    #     'centroid_px': tuple[int, int],
    #     'centroid_um': tuple[float, float],
    # }
}
```

### Validation Rules
- `total_count` must equal sum of `counts_by_class` values
- `total_count` must equal length of `organisms` list
- All organisms in `organisms` must have `confidence` >= `confidence_threshold`
- All organisms must have `size_um` within `size_range_um`
- `counts_by_class` keys must match class names in predictions

---

## Module 6: Analytics

### Input Contract
```python
{
    'counts_by_class': dict[str, int],   # From counting module
    'organisms': list[dict],             # From counting module
    'historical_data': list[dict] | None,  # Optional historical samples
    'analytics_config': {
        'compute_diversity': bool,       # True/False
        'compute_composition': bool,     # True/False
        'bloom_thresholds': dict[str, int],  # {'class_name': threshold}
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,
    'diversity_indices': dict,
    # {
    #     'shannon': float,              # Shannon diversity index
    #     'simpson': float,              # Simpson diversity index
    #     'species_richness': int,       # Number of unique classes
    # }
    'composition': dict[str, float],     # Percentage per class (sum = 100)
    'bloom_alerts': list[dict],          # List of bloom warnings
    # Each bloom alert:
    # {
    #     'class_name': str,
    #     'count': int,
    #     'threshold': int,
    #     'severity': str,               # "low" | "moderate" | "high" | "critical"
    # }
    'trends': dict | None,               # Optional trend analysis
}
```

### Validation Rules
- `shannon` must be >= 0
- `simpson` must be between 0 and 1
- `species_richness` must be >= 0
- Sum of `composition` values must equal 100.0 (within floating point tolerance)
- Each bloom alert `count` must be >= `threshold`

---

## Module 7: Export

### Input Contract
```python
{
    'metadata': dict,                    # From acquisition module
    'counts_by_class': dict[str, int],   # From counting module
    'organisms': list[dict],             # From counting module
    'diversity_indices': dict,           # From analytics module
    'bloom_alerts': list[dict],          # From analytics module
    'export_config': {
        'output_dir': str,               # Directory path
        'generate_dashboard': bool,      # True/False
        'export_images': bool,           # True/False
    }
}
```

### Output Contract
```python
{
    'status': str,                       # "success" | "error"
    'error_message': str | None,
    'csv_path': str,                     # Path to summary CSV
    'dashboard_url': str | None,         # URL or path to dashboard
    'exported_files': list[str],         # List of all exported file paths
}
```

### Validation Rules
- `csv_path` file must exist and be readable
- All paths in `exported_files` must exist
- CSV must have required columns: sample_id, timestamp, class_name, count, shannon_diversity

---

## CSV Output Format

### Summary CSV (sample_id per class)
```csv
sample_id,timestamp,gps_lat,gps_lon,magnification,class_name,count,shannon_diversity,bloom_alert
uuid,ISO8601,float|null,float|null,float,string,int,float,bool
```

### Organisms CSV (one row per organism)
```csv
sample_id,organism_id,class_name,confidence,size_um,centroid_x_px,centroid_y_px,centroid_x_um,centroid_y_um
uuid,int,string,float,float,int,int,float,float
```

---

## JSON Output Format

Complete results in structured JSON:
```json
{
  "metadata": {...},
  "counts_by_class": {...},
  "diversity_indices": {...},
  "bloom_alerts": [...],
  "organisms": [...]
}
```

---

## Testing Strategy

### Simulation Testing (Current)
- Synthetic images
- Random organism blobs
- Stub classification
- Validates contracts work

### Prototype Testing (Real System)
- Real microscope images
- Trained classification model
- Calibrated resolution
- GPS coordinates
- Real plankton species

### Contract Compliance Testing
Every module must pass:
1. Input validation (rejects invalid input)
2. Output validation (produces valid output)
3. Type checking (all fields have correct types)
4. Range checking (values in valid ranges)
5. Length checking (lists have consistent lengths)

---

## Common Validation Functions

### For All Modules
```python
def validate_status(result):
    assert 'status' in result
    assert result['status'] in ['success', 'error']
    if result['status'] == 'error':
        assert 'error_message' in result
        assert result['error_message'] is not None
```

### For Image Data
```python
def validate_image(image):
    assert isinstance(image, np.ndarray)
    assert len(image.shape) == 3
    assert image.shape[2] == 3  # RGB
    assert image.dtype == np.uint8
    assert image.shape[0] >= 100 and image.shape[1] >= 100
```

### For Lists
```python
def validate_list_lengths(masks, bboxes, centroids, areas):
    assert len(masks) == len(bboxes) == len(centroids) == len(areas)
```

---

## Contract Change Protocol

If you need to change a contract:

1. **Stop coding** on your module
2. **Post in #help** with proposed change
3. **Wait for team discussion**
4. **Get approval** from all affected modules
5. **Update this document** first
6. **Update tests** to match new contract
7. **Update your module** implementation
8. **Notify integration lead** to re-test

**Never change contracts silently. It breaks integration.**
