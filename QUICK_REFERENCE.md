# Quick Reference Card

## Run Pipeline (Different Modes)

### 1. Synthetic (Testing)
```bash
python simulate_pipeline.py -n 3
```

### 2. Real Images (File Mode)
```bash
python test_with_real_images.py
```

### 3. Single Image
```python
from pipeline.manager import PipelineManager
import yaml, datetime

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

pipeline = PipelineManager(config)

result = pipeline.execute_pipeline({
    'mode': 'file',
    'image_path': 'path/to/image.png',
    'magnification': 2.0,
    'exposure_ms': 100,
    'capture_metadata': {
        'timestamp': datetime.datetime.now().isoformat(),
        'operator_id': 'test'
    }
})
```

## Dataset Locations

- **Full dataset**: `datasets/raw/dataset_pm/`
- **Test samples**: `datasets/processed/samples/`
- **Results**: `results/`

## Key Files

| File | Purpose |
|------|---------|
| `test_with_real_images.py` | Quick test with real images |
| `simulate_pipeline.py` | Test with synthetic data |
| `main.py` | Main entry point |
| `USAGE_GUIDE.md` | Complete usage examples |
| `REAL_DATA_TEST_RESULTS.md` | Test results & findings |
| `IMPLEMENTATION_SUMMARY.md` | What was accomplished |

## Results Format

### Output Files (in `results/`)
- `summary_*.csv` - Per-class counts
- `organisms_*.csv` - Individual organism data  
- `results_*.json` - Complete structured data

### Organism Data Columns
```
organism_id, class_name, confidence, size_um, 
centroid_x_px, centroid_y_px, centroid_x_um, centroid_y_um
```

## Classification Model Status ✅

**STATUS**: WORKING! Real CNN-based classification is now functional.

- Model: Lightweight CNN (3 conv blocks)
- Classes: 19 plankton species
- Files: `models/plankton_classifier.keras` (1.2MB)
- Training: Quick training completed (10 epochs, 100 samples/class)
- Performance: ~333ms per organism
- Confidence: 38-41% (needs more training for higher accuracy)

**To improve accuracy**: Retrain with full dataset (see `CLASSIFIER_INTEGRATION_SUMMARY.md`)

## Next Steps (Priority)

1. **HIGH**: Retrain model with full dataset for better accuracy (currently 38-41% confidence)
2. **MEDIUM**: Test Pi HQ Camera hardware
3. **MEDIUM**: Build dashboard UI
4. **LOW**: Deploy TFLite model on Pi and measure real performance

## Quick Checks

```bash
# Verify setup
python verify_setup.py

# Run tests
pytest tests/

# Check config
python main.py --validate-only
```

## Performance

- Current: ~1.3s per image
- With model: ~2-3s
- On Pi4: ~5-10s (estimated)

## Support

- Issues? Check `REAL_DATA_TEST_RESULTS.md`
- Usage? See `USAGE_GUIDE.md`
- Architecture? Read `docs/CONTRACTS.md`
