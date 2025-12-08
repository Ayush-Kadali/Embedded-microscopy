# Pipeline Simulation System

**Visual verification of the complete pipeline**

---

## Overview

The simulation system allows you to run the pipeline with synthetic images and **save annotated visualizations** at each stage. This helps you:

1. **Verify the pipeline works** - See images processed through all 7 modules
2. **Debug issues** - Visualize what each module does
3. **Demonstrate the system** - Show to evaluators/team
4. **Test changes** - See how modifications affect results

---

## Quick Start

### Run a Single Simulation

```bash
# Activate environment
source .venv/bin/activate

# Run simulation
python simulate_pipeline.py

# Check results
open results/simulation/
```

**Output**: Annotated images saved in `results/simulation/`

### Run Multiple Samples

```bash
# Simulate 5 samples
python simulate_pipeline.py --num-samples 5

# Each gets a unique ID and full visualization
```

---

## What Gets Generated

### For Each Sample

**1. Original Image** (`*_01_original.jpg`)
- Synthetic microscope image
- Metadata overlay (timestamp, magnification, FOV)
- Shows the raw input to the pipeline

**2. Preprocessed Image** (`*_02_preprocessed.jpg`)
- After denoising and normalization
- Statistics overlay (mean intensity, SNR)
- Shows preprocessing improvements

**3. Segmentation** (`*_03_segmentation.jpg`)
- Detected organisms with bounding boxes
- Masks overlaid (semi-transparent yellow)
- Centroids marked (red dots)
- Organism IDs labeled

**4. Classification** (`*_04_classification.jpg`)
- Class labels with confidence scores
- Color-coded by species
- Legend showing all detected classes
- Each organism labeled

**5. Final Analysis** (`*_05_final_analysis.jpg`)
- Split view: image + statistics panel
- Organism counts by class
- Diversity metrics (Shannon, Simpson, richness)
- Bloom alerts (if any)

**6. Summary Grid** (`*_grid_summary.jpg`)
- All stages in one image
- Side-by-side comparison
- Great for presentations

**7. Metadata JSON** (`*_metadata.json`)
- Complete pipeline data
- All parameters and results
- Paths to all images

---

## Usage Examples

### Basic Simulation

```bash
python simulate_pipeline.py
```

**Output**:
```
results/simulation/
├── abc123_01_original.jpg
├── abc123_02_preprocessed.jpg
├── abc123_03_segmentation.jpg
├── abc123_04_classification.jpg
├── abc123_05_final_analysis.jpg
├── abc123_grid_summary.jpg
└── abc123_metadata.json
```

### Multiple Samples

```bash
# Generate 10 samples
python simulate_pipeline.py --num-samples 10
```

**Result**: 10 complete sets of images (70 files total)

### Custom Parameters

```bash
# Higher magnification
python simulate_pipeline.py --magnification 4.0

# Different exposure
python simulate_pipeline.py --exposure 200

# Custom output directory
python simulate_pipeline.py --output-dir my_simulation

# Combine all
python simulate_pipeline.py -n 5 -m 3.5 -e 180 -o demo_results
```

### Command Line Options

```bash
python simulate_pipeline.py --help

Options:
  -n, --num-samples N    Number of samples (default: 1)
  -o, --output-dir DIR   Output directory (default: results/simulation)
  -m, --magnification M  Magnification (default: 2.5)
  -e, --exposure MS      Exposure in ms (default: 150)
```

---

## Understanding the Visualizations

### Color Coding

**Species colors** (in classification images):
- **Green**: Copepod
- **Blue**: Diatom
- **Red**: Dinoflagellate
- **Cyan**: Ciliate
- **Gray**: Other

**Annotations**:
- **Yellow overlay**: Detected organism masks
- **Red dots**: Centroids
- **Blue boxes**: Bounding boxes (segmentation)
- **Colored boxes**: Class-specific boxes (classification)

### Reading the Final Analysis

**Left side**: Annotated image with all detections

**Right side**: Statistics panel
- Organism counts by class
- Diversity metrics
  - Shannon: Species diversity (higher = more diverse)
  - Simpson: Probability two random organisms are different species
  - Richness: Number of unique species
  - Evenness: How evenly distributed species are
- Bloom alerts: Harmful algal bloom warnings

---

## How It Works

### Pipeline Flow

```
1. Acquisition
   ↓ Generates synthetic image (2028x2028 RGB)
   ↓ Adds random organism blobs (5-20 organisms)
   ↓
2. Preprocessing
   ↓ Denoises image
   ↓ Normalizes intensity
   ↓
3. Segmentation
   ↓ Detects organisms using watershed algorithm
   ↓ Creates masks and bounding boxes
   ↓
4. Classification
   ↓ Identifies species (currently stub/heuristic)
   ↓ Assigns confidence scores
   ↓
5. Counting
   ↓ Counts organisms per class
   ↓ Measures sizes
   ↓
6. Analytics
   ↓ Calculates diversity indices
   ↓ Checks for blooms
   ↓
7. Export
   ↓ Saves CSV/JSON
   ↓
8. Visualization (added by simulation system)
   → Saves annotated images at each stage
```

### Synthetic Image Generation

**Located in**: `modules/acquisition.py`

```python
def _capture_image(self, exposure_ms: int) -> np.ndarray:
    # Light background (simulates microscope slide)
    img = np.random.randint(200, 230, (2028, 2028, 3), dtype=np.uint8)

    # Random number of organisms
    num_organisms = np.random.randint(5, 20)

    # Add circular blobs (plankton)
    for _ in range(num_organisms):
        center_x = np.random.randint(100, 1928)
        center_y = np.random.randint(100, 1928)
        radius = np.random.randint(20, 80)  # Size variation

        # Create circular mask
        # Draw dark blob (plankton body)
```

**Why this works**:
- Tests pipeline logic
- Consistent format (RGB, size)
- Variable organism counts
- Different sizes
- Ready for real images later

---

## Comparing with Real Images

### Current: Simulation Mode

```python
# modules/acquisition.py
def _capture_image(self):
    return self._generate_synthetic_image()
```

**Generates**: Random blobs on each run

### Future: Real Images

```python
# modules/acquisition.py (Person 3 will update)
def _capture_image(self):
    if self.use_test_images:
        return self._load_test_image()  # Load from datasets/
    else:
        return self._capture_from_camera()  # Real camera
```

**Uses**: Actual plankton images from datasets

---

## Troubleshooting

### Problem: "No module named 'utils.visualization'"

**Solution**:
```bash
# Make sure you're in project root
cd ~/Documents/university/SIH/plank-1

# Activate venv
source .venv/bin/activate

# Run from project root
python simulate_pipeline.py
```

### Problem: "Permission denied"

**Solution**:
```bash
# Make script executable
chmod +x simulate_pipeline.py

# Run
./simulate_pipeline.py
```

### Problem: Images not opening

**macOS**:
```bash
open results/simulation/
```

**Linux**:
```bash
xdg-open results/simulation/
```

**Windows**:
```bash
explorer results\simulation
```

### Problem: Out of memory with many samples

**Solution**:
```bash
# Run in batches
python simulate_pipeline.py -n 10  # First batch
python simulate_pipeline.py -n 10  # Second batch

# Or reduce image quality in visualization.py
```

---

## Using in Development

### Test Your Module Changes

```bash
# Make changes to your module
# e.g., edit modules/classification.py

# Run simulation to see effects
python simulate_pipeline.py

# Check visualization
open results/simulation/*_04_classification.jpg
```

### Verify Integration

```bash
# After merging changes
python simulate_pipeline.py -n 5

# Check all stages still work
# Look for errors in output
```

### Demo to Team

```bash
# Generate impressive visualization
python simulate_pipeline.py -n 1 -m 4.0 -e 200

# Show the grid summary
open results/simulation/*_grid_summary.jpg
```

---

## Advanced Usage

### Custom Visualization

**Edit** `utils/visualization.py` to customize:
- Colors
- Font sizes
- Layout
- Additional annotations

### Pipeline-Only Mode

If you just want CSV output without images:

```bash
# Use original main.py
python main.py

# Faster, no image generation
# Results in results/*.csv
```

### Batch Processing

```python
# Create your own script
from simulate_pipeline import simulate_single_sample
from pipeline.manager import PipelineManager
from utils.visualization import PipelineVisualizer
import yaml

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

manager = PipelineManager(config)
visualizer = PipelineVisualizer('my_output')

# Custom loop
for mag in [1.0, 2.0, 3.0, 4.0]:
    simulate_single_sample(manager, visualizer, magnification=mag)
```

---

## File Structure

```
plank-1/
├── simulate_pipeline.py           # Main simulation script
├── utils/
│   └── visualization.py           # Visualization utilities
├── results/
│   ├── simulation/                # Simulation images
│   │   ├── *_01_original.jpg
│   │   ├── *_02_preprocessed.jpg
│   │   ├── *_03_segmentation.jpg
│   │   ├── *_04_classification.jpg
│   │   ├── *_05_final_analysis.jpg
│   │   ├── *_grid_summary.jpg
│   │   └── *_metadata.json
│   ├── *.csv                      # Regular pipeline output
│   └── *.json                     # Regular pipeline output
└── docs/
    └── SIMULATION.md              # This file
```

---

## Performance

**Single sample**:
- Time: ~5 seconds
- Output: 7 files (~15MB)
- RAM: ~200MB

**10 samples**:
- Time: ~50 seconds
- Output: 70 files (~150MB)
- RAM: ~500MB

**Optimization tips**:
- Reduce image dimensions in visualization.py
- Skip grid generation for large batches
- Use JPEG quality compression

---

## Integration with Dashboard

The visualization system can be integrated with Person 2's dashboard:

```python
# In dashboard/app.py
from utils.visualization import PipelineVisualizer

visualizer = PipelineVisualizer('dashboard_output')

# After running pipeline
visualizer.save_classification_image(
    image, sample_id, bboxes, predictions
)

# Display in Streamlit
st.image('dashboard_output/*_04_classification.jpg')
```

---

## FAQ

**Q: Do I need to run simulation every time?**
A: No, use `python main.py` for fast testing. Use simulation when you want to see images.

**Q: Can I use real images?**
A: Yes! Person 3 will update `acquisition.py` to load from `datasets/`. Then simulation will use those images.

**Q: Are images committed to Git?**
A: No, they're in `.gitignore`. Share via Google Drive if needed.

**Q: Can I customize colors/layout?**
A: Yes, edit `utils/visualization.py` - see the `colors` dictionary and drawing functions.

**Q: Why are organism sizes different each time?**
A: Synthetic generation is random. Real images will be consistent.

---

## Next Steps

1. **Try it**: `python simulate_pipeline.py`
2. **Check images**: Open `results/simulation/`
3. **Show team**: Share grid summary
4. **Customize**: Edit visualization.py if needed
5. **Use in development**: Run after changes to verify

---

## Summary

**What it does**: Runs pipeline and saves annotated images at each stage

**Why it's useful**:
- Visual verification of pipeline
- Debugging tool
- Demonstration material
- Testing system

**How to use**:
```bash
python simulate_pipeline.py
open results/simulation/
```

**Output**: 7 images per sample showing complete pipeline processing

---

**Questions?** Check `docs/TROUBLESHOOTING.md` or ask in team chat.
