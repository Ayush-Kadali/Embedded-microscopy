# Marine Plankton AI Microscopy Dashboard - User Guide

## Quick Start

### Running the Dashboard

```bash
# Activate virtual environment
source .venv/bin/activate

# Start the dashboard
streamlit run dashboard/app.py
```

The dashboard will automatically open in your default web browser at:
- **Local URL**: http://localhost:8501
- **Network URL**: Access from other devices on your network

---

## Dashboard Features

### 1. Image Acquisition (Two Methods)

#### Method A: Camera Capture 📷
- Click the camera icon to activate your webcam/microscope camera
- Position your sample under the microscope
- Click "Take Photo" to capture the image
- The captured image will be displayed for review

#### Method B: File Upload 📁
- Click "Browse files" or drag and drop an image
- Supported formats: JPG, JPEG, PNG, BMP, TIFF
- Upload microscope images from your computer

---

### 2. Sample Location Setting

In the sidebar:
- Enter the geographic location where the sample was collected
- This metadata is saved with your results
- Example: "Bay of Bengal", "Arabian Sea", etc.

---

### 3. Running Analysis

1. After capturing or uploading an image, review it in the "Input Image" preview
2. Click the **"Run Analysis"** button
3. The system will execute the 7-stage pipeline:
   - **Stage 1**: Image Acquisition
   - **Stage 2**: Preprocessing (denoising, enhancement)
   - **Stage 3**: Segmentation (organism detection)
   - **Stage 4**: Classification (species identification with AI)
   - **Stage 5**: Counting (population statistics)
   - **Stage 6**: Analytics (diversity metrics, bloom detection)
   - **Stage 7**: Export (CSV/JSON generation)

4. Processing typically takes 10-20 seconds
5. Once complete, view results in the **"Results"** tab

---

### 4. Understanding Results

#### Key Metrics Dashboard

Four main metrics are displayed prominently:

1. **Total Organisms** 🦠
   - Total number of plankton detected in the sample

2. **Species Detected** 🧬
   - Number of unique species identified

3. **Shannon Diversity** 📊
   - Diversity index (0-3 scale)
   - Higher values = more diverse ecosystem
   - Formula accounts for both richness and evenness

4. **Simpson Diversity** 📈
   - Probability that two randomly selected organisms are different species
   - Range: 0-1 (higher = more diverse)

---

#### Species Distribution Pie Chart

**What it shows:**
- Percentage of each species in the sample
- Interactive: Hover for exact counts
- Click legend items to show/hide species

**Interpretation:**
- **Balanced distribution**: Healthy, diverse ecosystem
- **One dominant species (>50%)**: Possible bloom condition
- **Multiple similar-sized slices**: Good diversity

---

#### Size Distribution Histogram

**What it shows:**
- Distribution of organism sizes (in pixels)
- Red dashed line = mean size
- X-axis: Size in pixels
- Y-axis: Count of organisms

**Interpretation:**
- **Single peak**: Uniform population (possibly single species)
- **Multiple peaks**: Multiple size classes or species
- **Wide spread**: Diverse age groups or mixed species

---

#### Confidence Scores Chart

**What it shows:**
- AI model's confidence for each organism classification
- Horizontal bar chart (color-coded: red=low, yellow=medium, green=high)

**Interpretation:**
- **>70% confidence**: High reliability (trust the prediction)
- **50-70% confidence**: Moderate (probably correct)
- **<50% confidence**: Low (requires manual verification)

**Note**: Model average confidence is 75-90% for most species

---

#### Annotated Image

**What it shows:**
- Original image with bounding boxes around detected organisms
- Each organism labeled with:
  - Species name
  - Confidence score
  - Unique ID number

**How to use:**
- Zoom in to see individual organisms
- Verify AI classifications visually
- Identify any missed or false detections

---

### 5. Detailed Results (Expandable Sections)

#### Classification Details 🔬

**Table showing:**
- Organism ID
- Species name
- Confidence percentage

**Use cases:**
- Export to spreadsheet for further analysis
- Cross-reference with annotated image
- Identify low-confidence predictions for review

---

#### Counting Statistics 🔢

**Class Counts:**
- List of species with their counts
- Example: "Nitzschia: 15, Chaetoceros: 8"

**Size Statistics:**
- Mean, median, min, max sizes
- Useful for:
  - Age structure analysis
  - Species verification (size ranges)
  - Quality control (outlier detection)

---

#### Diversity Analytics 📊

**Diversity Metrics:**

1. **Shannon Diversity Index**
   - Formula: H' = -Σ(pi × ln(pi))
   - Range: 0 to ~3.5
   - Interpretation:
     - <1.0: Low diversity
     - 1.0-3.0: Moderate diversity
     - >3.0: High diversity

2. **Simpson Diversity Index**
   - Formula: D = 1 - Σ(pi²)
   - Range: 0 to 1
   - Interpretation:
     - <0.3: Low diversity
     - 0.3-0.6: Moderate diversity
     - >0.6: High diversity

3. **Species Richness**
   - Simply the number of different species
   - Does not account for abundance

4. **Species Evenness**
   - How evenly distributed the species are
   - Range: 0 to 1
   - 1.0 = all species equally abundant

**Bloom Detection:**

The system automatically detects harmful algal blooms (HABs):

- **No Bloom**: ✅ Balanced ecosystem
- **Bloom Detected**: ⚠️ Warning with:
  - Dominant species name
  - Dominance percentage
  - Trigger: >50% of a single species

**Why it matters:**
- Blooms can indicate water quality issues
- Some species produce toxins
- Can impact marine ecosystems and fisheries

---

### 6. Exporting Results

Three export options available:

#### 1. Summary CSV 📄
**Contains:**
- Overall statistics
- Sample metadata (location, timestamp)
- Diversity metrics
- Bloom status

**Use for:**
- Reports and presentations
- Time-series tracking
- Regulatory compliance

---

#### 2. Organisms CSV 📊
**Contains:**
- Individual organism records
- Columns: ID, Species, Confidence, Size, Position

**Use for:**
- Detailed analysis
- Database import
- Statistical software (R, Python)

---

#### 3. Complete JSON 📋
**Contains:**
- Full pipeline results
- All intermediate stages
- Complete metadata

**Use for:**
- Backup/archival
- System integration
- Advanced analysis

---

## 19 Species Recognized

The AI model can identify these plankton species:

### Diatoms (12 species)
1. **Asterionellopsis glacialis** - Chain-forming diatom
2. **Cerataulina** - Marine planktonic diatom
3. **Chaetoceros** - Common marine diatom
4. **Entomoneis** - Benthic/planktonic diatom
5. **Guinardia** - Large chain-forming diatom
6. **Hemiaulus** - Tropical/subtropical diatom
7. **Lauderia annulata** - Coastal diatom
8. **Nitzschia** - Pennate diatom (common)
9. **Pinnularia** - Freshwater/brackish diatom
10. **Pleurosigma** - Sigmoid-shaped diatom
11. **Thalassionema** - Needle-shaped diatom
12. **Thalassiosira** - Centric diatom

### Dinoflagellates (7 species)
13. **Alexandrium** - Can form harmful blooms
14. **Ceratium** - Armored dinoflagellate
15. **Noctiluca** - Bioluminescent (causes red tides)
16. **Ornithocercus magnificus** - Large dinoflagellate
17. **Prorocentrum** - Can produce toxins
18. **Protoperidinium** - Heterotrophic dinoflagellate
19. **Pyrodinium** - Can cause harmful blooms

---

## Model Performance

### Overall Statistics
- **Accuracy**: 83.48%
- **Precision**: 88.77% (predictions are reliable)
- **Average Confidence**: 75-90%

### Best Performing Species (F1-Score > 90%)
- Noctiluca: 96.8%
- Asterionellopsis glacialis: 96.7%
- Protoperidinium: 92.9%
- Prorocentrum: 91.8%
- Pinnularia: 91.2%
- Entomoneis: 90.9%

### Species Requiring Caution
- **Pyrodinium**: Lower precision (over-predicted)
- **Alexandrium**: Lower recall (under-predicted)

**Recommendation**: For these species, verify predictions >70% confidence manually.

---

## Tips for Best Results

### Image Quality

1. **Focus**
   - Ensure organisms are in sharp focus
   - Use microscope auto-focus if available
   - Slight blur reduces accuracy

2. **Lighting**
   - Even illumination across the field
   - Avoid overexposure (washed out)
   - Avoid underexposure (too dark)
   - Use brightfield microscopy

3. **Magnification**
   - 100-400x magnification works best
   - Organisms should be clearly visible
   - Not too zoomed in (context helpful)

4. **Background**
   - Clean, minimal debris
   - Good contrast between organisms and background
   - Reduce noise through proper sample prep

5. **Sample Preparation**
   - Dilute if too dense (avoid overlap)
   - Remove large debris
   - Use proper mounting medium

---

### Confidence Thresholds

**For critical applications:**
- Only use predictions >70% confidence
- Manually verify <70% predictions
- Flag <50% for expert review

**For general surveys:**
- >50% confidence is acceptable
- Still review annotated image for obvious errors

**For research:**
- Consider all detections
- Use confidence scores as weights
- Validate random subset manually

---

## Troubleshooting

### No Organisms Detected

**Possible causes:**
1. Sample too dilute
2. Image quality too poor
3. Organisms too small or large
4. Wrong magnification

**Solutions:**
- Increase sample concentration
- Improve focus and lighting
- Adjust microscope magnification to 100-400x
- Check if organisms are actually plankton (model trained on specific species)

---

### Low Confidence Scores (<50%)

**Possible causes:**
1. Image quality issues
2. Rare species not in training data
3. Unusual viewing angle
4. Damaged/degraded organisms

**Solutions:**
- Recapture with better focus/lighting
- Manually identify using taxonomy guides
- Consult a plankton expert
- Report new species for future model training

---

### Wrong Classifications

**Possible causes:**
1. Morphologically similar species
2. Image artifacts (bubbles, debris)
3. Overlapping organisms
4. Species outside training set

**Solutions:**
- Check annotated image for obvious errors
- Verify with expert if critical
- Use multiple images from same sample
- Report errors for model improvement

---

### Camera Not Working

**Possible causes:**
1. Browser permissions not granted
2. Camera already in use
3. Incompatible browser

**Solutions:**
- Click "Allow" when browser asks for camera permission
- Close other apps using camera (Zoom, Skype, etc.)
- Use Chrome, Edge, or Firefox (Safari may have issues)
- Try file upload instead

---

## Advanced Features

### Batch Processing (Coming Soon)

- Upload multiple images at once
- Automatic sequential processing
- Combined results summary
- Time-series analysis

### Raspberry Pi Deployment

The system includes a TFLite model (5.2 MB) optimized for Raspberry Pi:

```bash
# On Raspberry Pi
python3 rpi_capture_and_classify.py
```

**Features:**
- Low power consumption
- Real-time processing
- Standalone operation
- Field deployment ready

---

## Data Privacy & Storage

### What's Stored
- Captured/uploaded images are processed locally
- Results saved to `results/` directory
- No data sent to external servers

### Data Retention
- Results persist until manually deleted
- Recommended: Archive important results externally
- Clean up old results periodically to save space

### Sharing Results
- Export CSV/JSON for sharing
- Annotated images can be shared as PNG files
- No personal data included (except manually entered location)

---

## System Requirements

### Minimum
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 500 MB free space
- **Python**: 3.8 or higher
- **Browser**: Chrome, Firefox, Edge (latest)

### Recommended
- **CPU**: Quad-core 2.5 GHz or better
- **RAM**: 8 GB or more
- **Storage**: 2 GB free space
- **GPU**: Optional (speeds up processing)

### Camera
- **Webcam**: Any USB webcam (720p or better)
- **Microscope Camera**: USB microscope camera compatible with computer
- **Raspberry Pi Camera**: v2 or HQ camera module

---

## Keyboard Shortcuts

While in the dashboard:

- **Ctrl+R** / **Cmd+R**: Refresh page (restart analysis)
- **Ctrl+S** / **Cmd+S**: Save current page (browser default)
- **Tab**: Navigate between inputs
- **Space**: Activate buttons

---

## Getting Help

### Documentation
- Full system documentation: `README.md`
- Evaluation report: `EVALUATION_REPORT.md`
- Setup guide: `SETUP_COMPLETE.md`

### Support
- Check `TROUBLESHOOTING.md` for common issues
- Review model documentation for species information
- Contact system administrator for technical support

---

## Citation

If using this system for research, please cite:

```
Marine Plankton AI Microscopy System
EfficientNetB0 Transfer Learning Model
Accuracy: 83.48% (19 species)
Developed: December 2025
```

---

## Changelog

### Version 1.0 (Current)
- Initial release
- EfficientNetB0 model (83.48% accuracy)
- 19 species recognition
- Camera and file upload support
- Real-time analysis
- Interactive visualizations
- CSV/JSON export
- Bloom detection
- Diversity analytics

---

**Dashboard is now live and ready to use!** 🎉

Access at: **http://localhost:8501**
