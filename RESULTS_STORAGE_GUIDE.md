# Results Storage Guide

**Date**: December 9, 2025

Complete guide to where all results and outputs are stored.

---

## 📁 Directory Structure

```
plank-1/
├── results/                              # Main results directory
│   ├── annotated_images/                 # 🖼️ Annotated images with bounding boxes
│   │   ├── annotated_*.jpg               # Images with bounding boxes overlaid
│   │   └── comparison_*.jpg              # Side-by-side: original vs annotated
│   │
│   ├── simulation/                       # Previous simulation results
│   │   ├── *_01_original.jpg
│   │   ├── *_02_preprocessed.jpg
│   │   ├── *_03_segmentation.jpg
│   │   ├── *_04_classification.jpg
│   │   └── *_05_final_analysis.jpg
│   │
│   ├── summary_*.csv                     # Per-image species counts
│   ├── organisms_*.csv                   # Individual organism details
│   ├── results_*.json                    # Complete structured data
│   └── dashboard.html                    # HTML dashboard
│
└── test_images/                          # Your input images
    ├── Screenshot 2025-12-08 at 22.39.54.png
    ├── Screenshot 2025-12-08 at 22.40.04.png
    ├── Screenshot 2025-12-08 at 22.40.33.png
    ├── WhatsApp Image 2025-12-08 at 13.08.08.jpeg
    └── WhatsApp Image 2025-12-08 at 13.09.23.jpeg
```

---

## 📊 Output File Types

### 1. Annotated Images 🖼️

**Location**: `results/annotated_images/`

**Two types of images per input**:

#### A. `annotated_*.jpg`
- Original image with bounding boxes
- Green boxes around each detected organism
- Labels showing: `Species name: confidence`
- Organism IDs numbered (e.g., #0, #1, #2)

**Example**: `annotated_WhatsApp Image 2025-12-08 at 13.09.23.jpg`
- Shows 35 organisms
- Each with green bounding box
- Species name and confidence displayed

#### B. `comparison_*.jpg`
- Side-by-side comparison
- Left: Original image
- Right: Annotated image with detections
- Title showing count: "Detected: X organisms"

**Example**: `comparison_WhatsApp Image 2025-12-08 at 13.09.23.jpg`
- Visual before/after comparison
- Easy to see detection quality

**File sizes**: 134K - 456K per image

---

### 2. Data Files (CSV) 📋

**Location**: `results/`

#### A. Summary CSV (`summary_*.csv`)

Shows species counts per image:

```csv
sample_id,class_name,count
61eea0ae-...,Asterionellopsis glacialis,35
```

**Use case**: Quick overview of what was found

#### B. Organisms CSV (`organisms_*.csv`)

Detailed data for each detected organism:

```csv
sample_id,organism_id,class_name,confidence,size_um,centroid_x_px,centroid_y_px,centroid_x_um,centroid_y_um
61eea0ae-...,0,Asterionellopsis glacialis,0.404,76.26,301,27,233.28,20.93
61eea0ae-...,1,Asterionellopsis glacialis,0.407,69.72,423,33,327.82,25.57
...
```

**Columns explained**:
- `sample_id`: Unique ID for this image
- `organism_id`: Sequential number (0, 1, 2, ...)
- `class_name`: Species name
- `confidence`: Model confidence (0-1)
- `size_um`: Size in micrometers
- `centroid_x_px`, `centroid_y_px`: Position in pixels
- `centroid_x_um`, `centroid_y_um`: Position in micrometers

**Use case**:
- Analysis in Excel/Python
- Size distribution studies
- Spatial analysis
- Confidence filtering

---

### 3. Structured Data (JSON) 📦

**Location**: `results/`

**File**: `results_*.json`

Complete structured data in JSON format:

```json
{
  "metadata": {
    "capture_id": "61eea0ae-c5dc-4bd3-9387-3fe041397fa0",
    "timestamp": "2025-12-09T00:15:30.123456",
    "magnification": 2.0,
    "resolution_um_per_px": 0.775,
    "fov_mm": [1.24, 0.88],
    "source_file": "WhatsApp Image 2025-12-08 at 13.09.23.jpeg"
  },
  "counts_by_class": {
    "Asterionellopsis glacialis": 35
  },
  "diversity_indices": {
    "shannon": -0.000,
    "simpson": 0.0,
    "species_richness": 1
  },
  "bloom_alerts": [],
  "organisms": [
    {
      "organism_id": 0,
      "class_name": "Asterionellopsis glacialis",
      "confidence": 0.404,
      "size_um": 76.26,
      "centroid_px": [301, 27],
      "centroid_um": [233.28, 20.93]
    },
    ...
  ]
}
```

**Use case**:
- Programmatic access
- Web applications
- Database import
- API integration

---

### 4. Dashboard (HTML) 🌐

**Location**: `results/dashboard.html`

Simple HTML dashboard showing:
- Summary statistics
- Species counts
- Links to data files

**How to view**:
```bash
open results/dashboard.html
# Or double-click the file
```

---

## 🎯 Quick Access

### View Your Test Results:

**1. Visual Results (Images with boxes)**
```bash
open results/annotated_images/
```

**2. Data Results (CSV)**
```bash
open results/
# Look for latest organisms_*.csv files
```

**3. Side-by-side Comparisons**
```bash
open results/annotated_images/comparison_*.jpg
```

---

## 📝 File Naming Convention

All output files use unique IDs to avoid conflicts:

- `summary_<UUID>.csv`
- `organisms_<UUID>.csv`
- `results_<UUID>.json`

Where `<UUID>` is a unique identifier generated for each run.

**To find your results**: Sort by date (most recent = latest)

```bash
# List most recent results
ls -lt results/*.csv | head -10
ls -lt results/*.json | head -10
```

---

## 💾 Storage Size

### Current Results:

**Annotated Images**: ~2.3 MB for 5 test images
- 10 files (5 annotated + 5 comparison)
- Average: 230 KB per image

**CSV Files**: ~1-4 KB per image
- Small and efficient
- Easy to share and analyze

**JSON Files**: ~1-10 KB per image
- Depends on number of organisms
- Complete structured data

**Total for 5 test images**: ~2.5 MB

---

## 🔄 Regenerating Annotated Images

If you process new images and want annotated versions:

```bash
source .venv/bin/activate
python create_annotated_images.py
```

This will:
1. Process all images in `test_images/`
2. Generate annotated images
3. Save to `results/annotated_images/`

---

## 📊 Your Current Results Summary

### Test Images Processed: 5

| Image | Organisms | Annotated Image | Comparison | Data Files |
|-------|-----------|-----------------|------------|------------|
| Screenshot 22.39.54 | 14 | ✅ | ✅ | ✅ |
| Screenshot 22.40.04 | 1 | ✅ | ✅ | ✅ |
| Screenshot 22.40.33 | 1 | ✅ | ✅ | ✅ |
| WhatsApp 13.08.08 | 8 | ✅ | ✅ | ✅ |
| WhatsApp 13.09.23 | 35 | ✅ | ✅ | ✅ |

**Total organisms detected**: 59

---

## 🛠️ Working with Results

### Import CSV in Python:
```python
import pandas as pd

# Load organism data
df = pd.read_csv('results/organisms_<UUID>.csv')

# Analyze
print(f"Total organisms: {len(df)}")
print(f"Species: {df['class_name'].unique()}")
print(f"Average size: {df['size_um'].mean():.2f} μm")
print(f"Size range: {df['size_um'].min():.2f} - {df['size_um'].max():.2f} μm")
```

### Import JSON in Python:
```python
import json

with open('results/results_<UUID>.json', 'r') as f:
    data = json.load(f)

print(f"Sample ID: {data['metadata']['capture_id']}")
print(f"Timestamp: {data['metadata']['timestamp']}")
print(f"Species counts: {data['counts_by_class']}")
print(f"Total organisms: {len(data['organisms'])}")
```

### Batch Analysis:
```python
import pandas as pd
from pathlib import Path

# Load all organism CSVs
results_dir = Path('results')
all_dfs = []

for csv_file in results_dir.glob('organisms_*.csv'):
    df = pd.read_csv(csv_file)
    all_dfs.append(df)

# Combine all results
combined = pd.concat(all_dfs, ignore_index=True)

print(f"Total samples: {combined['sample_id'].nunique()}")
print(f"Total organisms: {len(combined)}")
print("\nSpecies distribution:")
print(combined['class_name'].value_counts())
```

---

## 📌 Important Notes

### Annotated Images:
- Created on-demand (not automatic)
- Run `create_annotated_images.py` to generate
- Stored separately from data files

### Data Files:
- Created automatically during processing
- One set per processed image
- Never overwritten (unique IDs)

### File Cleanup:
If results directory gets too large:
```bash
# Archive old results
mkdir results_archive
mv results/*.csv results_archive/
mv results/*.json results_archive/

# Keep annotated images
# (they're in results/annotated_images/)
```

---

## 🎯 Summary

**Everything you need is in**: `./results/`

1. **Visual results**: `results/annotated_images/`
2. **Data for analysis**: `results/*.csv`
3. **Structured data**: `results/*.json`
4. **Web view**: `results/dashboard.html`

**To view your results**:
```bash
# Open annotated images folder
open results/annotated_images/

# Or view in file browser
cd results && ls -lth
```

---

## 🚀 Quick Commands

```bash
# Process images and create annotated versions
python test_user_images.py
python create_annotated_images.py

# View results
open results/annotated_images/
open results/dashboard.html

# Analyze in Python
python -c "import pandas as pd; df = pd.read_csv('results/organisms_*.csv'); print(df.describe())"
```

---

**Last Updated**: December 9, 2025
**Total Test Images**: 5
**Total Organisms Detected**: 59
**All Results Available**: ✅
