# Annotated Images Location Guide

## 📁 Where to Find Annotated Images

### **Main Location:**
```
/Users/ayushkadali/Documents/university/SIH/plank-1/results/annotated_images/
```

---

## 🖼️ Available Annotated Images

### **From Your Test Images (5 images)**

1. **annotated_Screenshot 2025-12-08 at 22.39.54.jpg** (161 KB)
   - Species: Ceratium (41.8% confidence)
   - With bounding boxes and labels

2. **annotated_Screenshot 2025-12-08 at 22.40.04.jpg** (134 KB)
   - Species: Entomoneis (18.5% confidence)
   - With bounding boxes and labels

3. **annotated_Screenshot 2025-12-08 at 22.40.33.jpg** (456 KB)
   - Species: Entomoneis (37.5% confidence)
   - With bounding boxes and labels

4. **annotated_WhatsApp Image 2025-12-08 at 13.08.08.jpg** (179 KB)
   - Species: Ornithocercus magnificus (88.1% confidence)
   - With bounding boxes and labels

5. **annotated_WhatsApp Image 2025-12-08 at 13.09.23.jpg** (331 KB)
   - Species: Thalassiosira (33.6% confidence)
   - With bounding boxes and labels

---

## 📊 Additional Visualization Images

### **Model Evaluation Plots** (in `results/`)
- **confusion_matrix.png** (247 KB) - Model confusion matrix
- **per_class_metrics.png** (121 KB) - Per-species performance
- **class_distribution.png** (94 KB) - Dataset distribution

### **Comparison Images** (in `results/annotated_images/`)
Side-by-side original vs annotated for all 5 test images:
- comparison_Screenshot 2025-12-08 at 22.39.54.jpg
- comparison_Screenshot 2025-12-08 at 22.40.04.jpg
- comparison_Screenshot 2025-12-08 at 22.40.33.jpg
- comparison_WhatsApp Image 2025-12-08 at 13.08.08.jpg
- comparison_WhatsApp Image 2025-12-08 at 13.09.23.jpg

---

## 🔍 How to View Them

### **Option 1: Finder (macOS)**
```bash
open results/annotated_images/
```

### **Option 2: Command Line**
```bash
# View list
ls -lh results/annotated_images/

# Open specific image
open "results/annotated_images/annotated_WhatsApp Image 2025-12-08 at 13.08.08.jpg"
```

### **Option 3: View All at Once**
```bash
open results/annotated_images/*.jpg
```

---

## 📝 What Annotated Images Show

Each annotated image contains:
1. **Original image** as background
2. **Bounding boxes** around detected organisms (colored rectangles)
3. **Labels** with:
   - Species name
   - Confidence score (%)
   - Organism ID number

**Example:**
```
┌─────────────────┐
│ Entomoneis      │
│ 91.3%  [ID: 1]  │
└─────────────────┘
```

---

## 🎯 Generate New Annotated Images

### **For New Test Images:**

**Option 1: Full Pipeline (Recommended)**
```bash
# Place images in test_images/ folder
# Then run:
source .venv/bin/activate
python test_user_images.py
```

**Option 2: Using Batch Processing**
```bash
source .venv/bin/activate
python batch_process.py test_images/ -o results/my_batch/
```

**Output Location:**
- Annotated images appear in `results/` directory
- Named with UUID prefixes or original filenames

---

## 📊 Full Pipeline Analysis Results

When you run `test_user_images.py`, you get:

### **Per-Image Files** (9 images processed):
Each image generates multiple visualization stages:
- `{uuid}_01_original.jpg` - Original input
- `{uuid}_02_preprocessed.jpg` - After denoising
- `{uuid}_03_segmentation.jpg` - Detected organisms highlighted
- `{uuid}_04_classification.jpg` - With species labels
- `{uuid}_05_final_analysis.jpg` - Complete annotated image
- `{uuid}_grid_summary.jpg` - All stages in one grid

### **Summary Files:**
- `summary_{uuid}.csv` - Overall statistics
- `organisms_{uuid}.csv` - Per-organism details
- `results_{uuid}.json` - Complete JSON results

---

## 🎨 Latest Analysis Results

From your most recent run (9 images):

**Total Organisms Detected**: 66
**Species Found**:
- Entomoneis: 27 organisms
- Nitzschia: 16 organisms
- Hemiaulus: 13 organisms
- Cerataulina: 8 organisms
- Lauderia annulata: 2 organisms

---

## 💡 Quick Access Commands

```bash
# Go to project directory
cd /Users/ayushkadali/Documents/university/SIH/plank-1

# Open annotated images folder
open results/annotated_images/

# View specific image
open "results/annotated_images/annotated_WhatsApp Image 2025-12-08 at 13.08.08.jpg"

# List all annotated images
ls -lh results/annotated_images/annotated_*

# View latest results
ls -lht results/*.jpg | head -20
```

---

## 📂 Directory Structure

```
results/
├── annotated_images/           # ← Main annotated images here
│   ├── annotated_*.jpg         # Annotated test images (5)
│   └── comparison_*.jpg        # Side-by-side comparisons (5)
├── confusion_matrix.png        # Model evaluation
├── per_class_metrics.png       # Model performance chart
├── class_distribution.png      # Dataset distribution
├── summary_*.csv               # Analysis summaries
├── organisms_*.csv             # Detailed organism data
└── results_*.json              # Complete JSON results
```

---

## ✅ Summary

**Annotated Images Location:**
```
results/annotated_images/
```

**Total Annotated Images**: 5 test images + 5 comparison images = **10 images**

**To view them all:**
```bash
open results/annotated_images/
```

**To generate more:**
```bash
python test_user_images.py
```

---

**All your annotated images are ready and waiting!** 🖼️
