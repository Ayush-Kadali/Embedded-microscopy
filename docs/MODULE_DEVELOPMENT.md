# Module Development Guide

**Step-by-step guide for each team member**

---

## Table of Contents

1. [Overview](#overview)
2. [Person 1: Classification Module](#person-1-classification-module)
3. [Person 2: Dashboard Module](#person-2-dashboard-module)
4. [Person 3: Data Collection Module](#person-3-data-collection-module)
5. [Person 4: Integration Lead](#person-4-integration-lead)
6. [Person 5: Presentation](#person-5-presentation)
7. [Testing Your Module](#testing-your-module)
8. [Common Patterns](#common-patterns)

---

## Overview

### Core Principles

**1. Contract-Based Development**
- Your module has a defined input and output (see `docs/CONTRACTS.md`)
- NEVER change the contract without team discussion
- If you follow the contract, integration will work

**2. Test-Driven Development**
- Test your module frequently
- Both unit tests and integration tests must pass
- Don't commit broken code

**3. Independent Development**
- Work only on your assigned files
- Don't modify other modules
- Use your own Git branch

### Development Cycle

```
1. Pull latest code
2. Make changes to YOUR module
3. Test locally
4. Commit and push
5. Integration lead merges
6. Pull merged changes
7. Repeat
```

---

## Person 1: Classification Module

**Goal**: Replace stub classifier with real ML model

**Priority**: CRITICAL - Most important module

**Files to modify**:
- `modules/classification.py` - Your main file
- `config/config.yaml` - Update class names if needed
- `models/` - Add your .tflite model here

### Step 1: Setup Your Branch

```bash
cd plank-1
source .venv/bin/activate
git checkout -b feature/classification
git push -u origin feature/classification
```

### Step 2: Install ML Dependencies

```bash
pip install tensorflow
# OR for Raspberry Pi:
pip install tflite-runtime

# Update requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "classification: added TensorFlow dependency"
git push origin feature/classification
```

### Step 3: Get a Model

**Option A: Download Pretrained Model (Fastest - 1-2 hours)**

```bash
# Create models directory
mkdir -p models

# Download from Kaggle/HuggingFace
# Example: WHOI Plankton classifier
# Or use any marine plankton TFLite model

# Place in models/
mv ~/Downloads/plankton_classifier.tflite models/

# Verify
ls -lh models/
```

**Option B: Train Your Own (4-6 hours)**

```python
# train_model.py
import tensorflow as tf
from tensorflow import keras

# 1. Load dataset (use Person 3's collected images)
# 2. Preprocess images
# 3. Create model architecture (MobileNetV2 recommended)
# 4. Train
# 5. Convert to TFLite

model = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)

# ... training code ...

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save
with open('models/plankton_classifier.tflite', 'wb') as f:
    f.write(tflite_model)
```

### Step 4: Integrate Model into Module

**Open `modules/classification.py` and modify:**

```python
class ClassificationModule(PipelineModule):
    def __init__(self, config):
        super().__init__(config)
        self.class_names = config.get('class_names', [])
        self.confidence_threshold = config.get('confidence_threshold', 0.7)

        # Load TFLite model
        self.interpreter = None
        self.load_model()

    def load_model(self):
        """Load TFLite model."""
        import tflite_runtime.interpreter as tflite
        # Or: import tensorflow.lite as tflite

        model_path = 'models/plankton_classifier.tflite'

        if not os.path.exists(model_path):
            logger.warning("Model not found, using stub")
            return

        try:
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()

            # Get input/output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            logger.info(f"Model loaded: {model_path}")
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            self.interpreter = None

    def _predict(self, organism_image):
        """Predict class for single organism."""
        if self.interpreter is None:
            # Fallback to stub
            return self._stub_predict(organism_image)

        # Preprocess image
        img = cv2.resize(organism_image, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # Run inference
        self.interpreter.set_tensor(
            self.input_details[0]['index'],
            img
        )
        self.interpreter.invoke()

        # Get output
        output = self.interpreter.get_tensor(
            self.output_details[0]['index']
        )

        return output[0]  # Return probabilities

    def _stub_predict(self, organism_image):
        """Fallback stub predictor."""
        # Keep existing stub logic for development
        size_px = organism_image.shape[0] * organism_image.shape[1]

        if size_px < 5000:
            return np.array([0.85, 0.10, 0.03, 0.01, 0.01])
        else:
            return np.array([0.10, 0.75, 0.10, 0.03, 0.02])
```

### Step 5: Update Configuration

**Edit `config/config.yaml`:**

```yaml
classification:
  model_path: 'models/plankton_classifier.tflite'
  class_names:
    - 'Copepod'
    - 'Diatom'
    - 'Dinoflagellate'
    - 'Ciliate'
    - 'Other'
  confidence_threshold: 0.7
  top_k: 3  # Return top 3 predictions
```

### Step 6: Test Your Changes

```bash
# Test classification module only
pytest tests/test_all_modules.py::TestClassificationModule -v

# Should pass all tests

# Test full pipeline
python main.py

# Should see your classifications in results/
cat results/summary_*.csv
```

### Step 7: Commit and Push

```bash
git add modules/classification.py models/ config/config.yaml
git commit -m "classification: integrated TFLite model with 72% accuracy"
git push origin feature/classification

# Notify integration lead in team chat
```

### Step 8: Measure Performance

```python
# Add to your module
import time

def process(self, input_data):
    start = time.time()

    # ... classification logic ...

    elapsed = time.time() - start
    logger.info(f"Classification: {len(predictions)} organisms in {elapsed:.3f}s")

    return result
```

**Target**: <3 seconds for 20 organisms

### Troubleshooting

**Model won't load**:
```bash
# Check file exists
ls -lh models/plankton_classifier.tflite

# Check TFLite version
python -c "import tensorflow as tf; print(tf.__version__)"

# Try absolute path
import os
model_path = os.path.abspath('models/plankton_classifier.tflite')
```

**Low accuracy**:
- Check image preprocessing matches training
- Verify class order matches model output
- Lower confidence threshold temporarily
- Add more training data

**Too slow**:
- Use INT8 quantization
- Reduce input resolution
- Batch process organisms

---

## Person 2: Dashboard Module

**Goal**: Create Streamlit dashboard for visualization

**Priority**: HIGH - User-facing component

**Files to create**:
- `dashboard/app.py` - Main dashboard
- `dashboard/utils.py` - Helper functions (optional)

### Step 1: Setup Your Branch

```bash
cd plank-1
source .venv/bin/activate
git checkout -b feature/dashboard
git push -u origin feature/dashboard
```

### Step 2: Install Dashboard Dependencies

```bash
pip install streamlit plotly pandas folium streamlit-folium

# Update requirements
pip freeze > requirements.txt
git add requirements.txt
git commit -m "dashboard: added Streamlit dependencies"
git push origin feature/dashboard
```

### Step 3: Create Basic Dashboard

**Create `dashboard/app.py`:**

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath('..'))

from pipeline.manager import PipelineManager
from pipeline.validators import ConfigValidator
import yaml

st.set_page_config(
    page_title="Plankton Analysis Dashboard",
    page_icon="🔬",
    layout="wide"
)

# Title
st.title("🔬 Marine Plankton AI Microscopy System")
st.markdown("Automated plankton identification and analysis")

# Sidebar
st.sidebar.header("Configuration")

# File uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload Microscope Image",
    type=['png', 'jpg', 'jpeg', 'tiff']
)

# Parameters
magnification = st.sidebar.slider(
    "Magnification",
    min_value=0.7,
    max_value=4.5,
    value=2.5,
    step=0.1
)

exposure = st.sidebar.slider(
    "Exposure (ms)",
    min_value=50,
    max_value=500,
    value=150,
    step=10
)

# Run analysis button
if st.sidebar.button("🔬 Analyze Image", type="primary"):
    if uploaded_file is None:
        st.error("Please upload an image first")
    else:
        with st.spinner("Running pipeline..."):
            # Save uploaded file
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # Load config
            with open('config/config.yaml', 'r') as f:
                config = yaml.safe_load(f)

            # Initialize pipeline
            manager = PipelineManager(config)

            # Run pipeline
            params = {
                'magnification': magnification,
                'exposure_ms': exposure,
                'capture_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'operator': 'dashboard_user'
                }
            }

            result = manager.execute_pipeline(params)

            # Clean up
            os.remove(temp_path)

            # Display results
            if result['status'] == 'success':
                st.success("✓ Analysis complete!")

                # Store in session state
                st.session_state['result'] = result
            else:
                st.error(f"Analysis failed: {result.get('error_message')}")

# Display results if available
if 'result' in st.session_state:
    result = st.session_state['result']

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = result['counting']['total_organisms']
        st.metric("Total Organisms", total)

    with col2:
        richness = result['analytics']['species_richness']
        st.metric("Species Richness", richness)

    with col3:
        shannon = result['analytics']['shannon_diversity']
        st.metric("Shannon Diversity", f"{shannon:.3f}")

    with col4:
        blooms = result['analytics']['bloom_alerts']
        st.metric("Bloom Alerts", len(blooms))

    # Two columns for visualizations
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Species Distribution")

        # Prepare data for pie chart
        counts = result['counting']['counts_by_class']
        df_counts = pd.DataFrame([
            {'Species': k, 'Count': v}
            for k, v in counts.items()
        ])

        # Plotly pie chart
        fig = px.pie(
            df_counts,
            values='Count',
            names='Species',
            title='Organism Counts by Species'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Size Distribution")

        # Extract sizes
        organisms = result['counting']['organisms']
        sizes = [org['size_um'] for org in organisms]

        # Histogram
        fig = px.histogram(
            x=sizes,
            nbins=20,
            title='Organism Size Distribution',
            labels={'x': 'Size (μm)', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.subheader("Detected Organisms")

    df_organisms = pd.DataFrame(organisms)
    st.dataframe(
        df_organisms[[
            'organism_id',
            'class_name',
            'confidence',
            'size_um'
        ]],
        use_container_width=True
    )

    # Download buttons
    st.subheader("Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        # CSV export
        csv = df_organisms.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "plankton_results.csv",
            "text/csv"
        )

    with col2:
        # JSON export
        import json
        json_str = json.dumps(result, indent=2)
        st.download_button(
            "📥 Download JSON",
            json_str,
            "plankton_results.json",
            "application/json"
        )

else:
    # Welcome screen
    st.info("👈 Upload an image and click 'Analyze Image' to begin")

    # Example instructions
    st.markdown("""
    ### How to Use

    1. **Upload Image**: Click 'Browse files' in the sidebar
    2. **Adjust Parameters**: Set magnification and exposure
    3. **Analyze**: Click the 'Analyze Image' button
    4. **View Results**: See species counts, diversity metrics, and visualizations
    5. **Export**: Download results as CSV or JSON

    ### Supported Images

    - Format: PNG, JPG, JPEG, TIFF
    - Resolution: 2000x2000 pixels or higher recommended
    - Content: Microscope images of plankton samples
    """)
```

### Step 4: Test Dashboard Locally

```bash
# Make sure you're in project root
cd ~/Documents/university/SIH/plank-1

# Activate environment
source .venv/bin/activate

# Run dashboard
streamlit run dashboard/app.py

# Should open in browser at http://localhost:8501
```

### Step 5: Add Advanced Features (Optional)

**Batch processing**:
```python
uploaded_files = st.sidebar.file_uploader(
    "Upload Multiple Images",
    type=['png', 'jpg'],
    accept_multiple_files=True
)

if st.sidebar.button("Analyze Batch"):
    results = []
    progress_bar = st.progress(0)

    for i, file in enumerate(uploaded_files):
        # Process each file
        result = manager.execute_pipeline(params)
        results.append(result)

        # Update progress
        progress_bar.progress((i + 1) / len(uploaded_files))

    # Show batch results
    st.success(f"Processed {len(results)} images")
```

**GPS Map visualization**:
```python
import folium
from streamlit_folium import st_folium

if 'gps_lat' in result['acquisition']:
    lat = result['acquisition']['gps_lat']
    lon = result['acquisition']['gps_lon']

    m = folium.Map(location=[lat, lon], zoom_start=10)
    folium.Marker(
        [lat, lon],
        popup=f"Sample: {result['export']['sample_id']}"
    ).add_to(m)

    st_folium(m, width=700, height=500)
```

### Step 6: Commit and Push

```bash
git add dashboard/
git commit -m "dashboard: created Streamlit UI with visualizations"
git push origin feature/dashboard
```

### Troubleshooting

**Port already in use**:
```bash
streamlit run dashboard/app.py --server.port 8502
```

**Import errors**:
```bash
# Make sure you're in project root
pwd  # Should show .../plank-1

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Styling**:
```python
# Add custom CSS
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
```

---

## Person 3: Data Collection Module

**Goal**: Collect real plankton images for testing

**Priority**: HIGH - Needed for realistic testing

**Files to modify**:
- `modules/acquisition.py` - Update to load real images
- `datasets/` - Store collected images

### Step 1: Setup Your Branch

```bash
cd plank-1
source .venv/bin/activate
git checkout -b feature/data-collection
git push -u origin feature/data-collection
```

### Step 2: Download Dataset

**Option A: Kaggle Dataset (Recommended)**

```bash
# Install Kaggle CLI
pip install kaggle

# Configure Kaggle
# 1. Go to kaggle.com → Account → Create New API Token
# 2. Download kaggle.json
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download WHOI Plankton dataset
kaggle datasets download -d sshikamaru/whoi-plankton-dataset
unzip whoi-plankton-dataset.zip -d datasets/

# Or search for other datasets
kaggle datasets list -s "plankton"
```

**Option B: Manual Collection**

```bash
# Create datasets directory
mkdir -p datasets/raw

# Download from:
# - WHOI Plankton project
# - NOAA databases
# - Research papers
# - Public microscopy databases
```

### Step 3: Organize Dataset

```bash
# Structure
datasets/
├── raw/              # Original downloads
├── processed/        # Cleaned images
└── metadata.csv      # Image metadata
```

**Create `datasets/metadata.csv`:**
```csv
filename,species,source,quality
image_001.jpg,Copepod,WHOI,high
image_002.jpg,Diatom,WHOI,high
image_003.jpg,Dinoflagellate,NOAA,medium
```

### Step 4: Preprocess Images

**Create `datasets/preprocess_images.py`:**

```python
import cv2
import os
import numpy as np

def preprocess_image(img_path, output_path):
    """Preprocess single image."""
    # Read
    img = cv2.imread(img_path)
    if img is None:
        print(f"Can't read: {img_path}")
        return False

    # Convert to RGB if grayscale
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # Resize to standard size
    img = cv2.resize(img, (2028, 2028))

    # Normalize
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)

    # Save
    cv2.imwrite(output_path, img)
    return True

def process_all():
    """Process all images in datasets/raw/."""
    raw_dir = 'datasets/raw'
    processed_dir = 'datasets/processed'

    os.makedirs(processed_dir, exist_ok=True)

    for filename in os.listdir(raw_dir):
        if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            continue

        input_path = os.path.join(raw_dir, filename)
        output_path = os.path.join(processed_dir, filename)

        print(f"Processing {filename}...")
        preprocess_image(input_path, output_path)

    print("Done!")

if __name__ == '__main__':
    process_all()
```

**Run preprocessing:**
```bash
python datasets/preprocess_images.py
```

### Step 5: Update Acquisition Module

**Edit `modules/acquisition.py`:**

```python
class AcquisitionModule(PipelineModule):
    def __init__(self, config):
        super().__init__(config)
        self.camera_type = config.get('camera_type', 'pi_hq')
        self.sensor_pixel_size_um = config.get('sensor_pixel_size_um', 1.55)

        # For testing: load from files
        self.use_test_images = config.get('use_test_images', True)
        self.test_image_dir = config.get('test_image_dir', 'datasets/processed')
        self.test_image_index = 0

    def _capture_image(self):
        """Capture or load image."""
        if self.use_test_images:
            return self._load_test_image()
        else:
            return self._capture_from_camera()

    def _load_test_image(self):
        """Load image from test dataset."""
        import glob

        # Get all images
        pattern = os.path.join(self.test_image_dir, '*.jpg')
        images = sorted(glob.glob(pattern))

        if not images:
            logger.warning("No test images found, using synthetic")
            return self._generate_synthetic_image()

        # Load next image (cycle through)
        img_path = images[self.test_image_index % len(images)]
        self.test_image_index += 1

        logger.info(f"Loading test image: {img_path}")
        image = cv2.imread(img_path)

        if image is None:
            logger.warning(f"Failed to load {img_path}, using synthetic")
            return self._generate_synthetic_image()

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        return image

    def _capture_from_camera(self):
        """Capture from real camera (for production)."""
        try:
            from picamera2 import Picamera2

            camera = Picamera2()
            camera.configure(camera.create_still_configuration())
            camera.start()

            # Capture
            image = camera.capture_array()

            camera.stop()

            return image

        except Exception as e:
            logger.error(f"Camera capture failed: {e}")
            return self._generate_synthetic_image()
```

### Step 6: Update Configuration

**Edit `config/config.yaml`:**

```yaml
acquisition:
  camera_type: 'pi_hq'
  sensor_pixel_size_um: 1.55
  use_test_images: true  # Set false for real camera
  test_image_dir: 'datasets/processed'
```

### Step 7: Test with Real Images

```bash
# Run pipeline
python main.py

# Should use images from datasets/processed/
# Check logs: "Loading test image: datasets/processed/image_001.jpg"

# Test multiple runs
for i in {1..5}; do
    python main.py
done

# Should cycle through different images
```

### Step 8: Document Dataset

**Create `datasets/README.md`:**

```markdown
# Dataset Information

## Source
- WHOI Plankton Dataset
- Downloaded: 2025-12-08
- URL: https://kaggle.com/...

## Statistics
- Total images: 150
- Species: 5 (Copepod, Diatom, Dinoflagellate, Ciliate, Other)
- Resolution: 2028x2028 pixels
- Format: JPEG

## Usage
- Training: 70% (105 images)
- Validation: 15% (22 images)
- Testing: 15% (23 images)

## Preprocessing
1. Converted to RGB
2. Resized to 2028x2028
3. Normalized to 0-255
```

### Step 9: Commit (but not large images!)

```bash
# Add dataset info
git add datasets/README.md
git add datasets/metadata.csv
git add datasets/preprocess_images.py

# Update acquisition module
git add modules/acquisition.py config/config.yaml

# Commit
git commit -m "data: integrated real plankton images from WHOI dataset"

# DON'T commit large image files!
# Add to .gitignore:
echo "datasets/raw/" >> .gitignore
echo "datasets/processed/" >> .gitignore

git add .gitignore
git commit -m "data: added datasets to gitignore"

git push origin feature/data-collection
```

**Note**: Images are too large for Git. Share via:
- Google Drive/Dropbox link
- Team shared folder
- Or integration lead downloads separately

---

## Person 4: Integration Lead

**Goal**: Merge everyone's work, keep system working

**Priority**: CRITICAL - Keeps team unblocked

**Files to create**:
- `docs/INTEGRATION.md` - Your procedures (optional)

### Your Responsibilities

1. **Merge branches** every 4 hours
2. **Run tests** after each merge
3. **Fix integration bugs**
4. **Keep main branch working** always
5. **Help team** with Git issues
6. **Communicate** status to team

### Integration Checkpoints

**Hour 8 (Day 1)**: First integration
**Hour 12 (Day 1)**: Second integration
**Hour 16 (Day 1)**: End of day integration
**Day 2**: Continuous integration

### Merge Procedure

**Every 4 hours:**

```bash
# 1. Check team status
# Who has pushed? Check team chat and GitHub

# 2. Update main
git checkout main
git pull origin main

# 3. Run baseline tests
pytest tests/test_all_modules.py -v
python main.py

# If fails, fix main first before merging anything!

# 4. Merge one person at a time

# Person 1 - Classification
git fetch origin feature/classification
git merge origin/feature/classification --no-ff -m "integration: merged classification module"

# Test immediately
pytest tests/test_all_modules.py::TestClassificationModule -v
pytest tests/test_all_modules.py::TestIntegration -v
python main.py

# If PASS:
git push origin main
# Notify team: "Classification merged to main"

# If FAIL:
git merge --abort
# Notify Person 1: "Tests fail after merge, please fix"
# Continue with other modules

# 5. Repeat for each person

# Person 2 - Dashboard
git merge origin/feature/dashboard --no-ff -m "integration: merged dashboard"
pytest tests/test_all_modules.py -v
python main.py
git push origin main

# Person 3 - Data
git merge origin/feature/data-collection --no-ff -m "integration: merged data collection"
pytest tests/test_all_modules.py -v
python main.py
git push origin main

# Person 5 - Presentation
# Usually no code changes, just docs/slides
# Review and merge

# 6. Final verification
pytest tests/test_all_modules.py -v
python main.py

# 7. Tag milestone
git tag -a day1-hour8 -m "Day 1, Hour 8 integration complete"
git push origin day1-hour8

# 8. Notify team
# Post in chat: "Hour 8 integration complete. All branches merged. Pull latest main."
```

### Handling Merge Conflicts

```bash
# If merge has conflicts
git merge origin/feature/classification

# Git will show:
# CONFLICT (content): Merge conflict in config/config.yaml

# 1. Check conflicted files
git status

# 2. Open file, look for:
<<<<<<< HEAD
existing code in main
=======
new code from branch
>>>>>>> feature/classification

# 3. Decide what to keep
# Usually:
# - Keep both if different features
# - Keep newer if same feature
# - Ask person if unsure

# 4. Fix file, remove markers

# 5. Test
pytest tests/test_all_modules.py -v

# 6. Complete merge
git add config/config.yaml
git commit -m "integration: resolved config conflict"
git push origin main
```

### If Integration Breaks

```bash
# Option 1: Revert last merge
git revert -m 1 HEAD
git push origin main

# Option 2: Reset to last working commit
git reset --hard <last-good-commit>
git push origin main --force  # ONLY you can do this!

# Notify team immediately
```

### Daily Checklist

**Morning:**
- [ ] Pull latest from all branches
- [ ] Check CI/CD status (if setup)
- [ ] Review overnight commits

**Every 4 hours:**
- [ ] Merge pending branches
- [ ] Run full test suite
- [ ] Update integration status
- [ ] Notify team

**Evening:**
- [ ] Ensure main is working
- [ ] Tag day milestone
- [ ] Post summary in chat

### Communication Template

**After each integration:**
```
🔄 Integration Complete - Hour 8

Merged:
✓ Classification (Person 1) - TFLite model integrated
✓ Dashboard (Person 2) - Basic UI working
✓ Data (Person 3) - 50 test images added

Status:
✓ All tests passing (19/19)
✓ Pipeline running successfully
✓ No blockers

Next checkpoint: Hour 12

Action: Everyone pull latest main
```

---

## Person 5: Presentation

**Goal**: Create compelling presentation and demo

**Priority**: MEDIUM - Can wait until system works

**Files to create**:
- `presentation/slides.pdf` or `.pptx`
- `presentation/demo_script.md`
- `presentation/screenshots/`

### Step 1: Setup Your Branch

```bash
cd plank-1
git checkout -b feature/presentation
mkdir -p presentation/screenshots
git push -u origin feature/presentation
```

### Step 2: Gather Materials (Day 1-2)

**Screenshots needed:**
1. Dashboard UI
2. Results visualization
3. Pipeline execution
4. Test results
5. Architecture diagram

**Code samples:**
- Module contracts
- Key algorithms
- Integration points

### Step 3: Create Slide Deck

**Suggested structure (10-15 slides):**

1. **Title**: Project name, team, hackathon
2. **Problem**: Marine monitoring challenges
3. **Solution**: AI-powered automated system
4. **Architecture**: 7-module pipeline diagram
5. **Key Features**: Real-time, on-device, modular
6. **Demo** (live or video)
7. **Technical Details**: ML model, accuracy, performance
8. **Results**: Sample analysis output
9. **Impact**: Environmental monitoring benefits
10. **Future Work**: Extensions and improvements
11. **Team**: Roles and contributions
12. **Q&A**

### Step 4: Write Demo Script

**Create `presentation/demo_script.md`:**

```markdown
# Demo Script (3 minutes)

## Setup (0:00-0:30)
1. Open dashboard: `streamlit run dashboard/app.py`
2. Have test image ready
3. "We've built an automated system for marine plankton analysis"

## Demo (0:30-2:00)
1. "Upload microscope image" [drag and drop]
2. "Adjust parameters" [show magnification slider]
3. "Click Analyze" [wait ~5 seconds]
4. "Results appear in real-time"
   - Point out: Total count
   - Point out: Species diversity
   - Point out: Pie chart
   - Point out: Size distribution

## Technical (2:00-2:30)
1. "Behind the scenes:"
   - 7-module pipeline
   - TensorFlow Lite ML model
   - 72% accuracy
   - <15s processing time
2. "Runs on Raspberry Pi - portable for field work"

## Impact (2:30-3:00)
1. "Applications:"
   - Harmful algal bloom detection
   - Biodiversity monitoring
   - Water quality assessment
2. "Thank you! Questions?"

## Backup Talking Points
- Modular architecture allows easy upgrades
- Contract-based design ensured parallel development
- 95% test coverage
- Real-time processing for immediate insights
```

### Step 5: Record Backup Video

**In case live demo fails:**

```bash
# Use macOS:
CMD + SHIFT + 5  # Screen recording

# Or Linux:
kazam  # or SimpleScreenRecorder

# Record:
1. Full demo (3 min)
2. Close-ups of key features
3. Narrate while recording
```

### Step 6: Practice

**Day 3-4:**
- Practice full presentation 5+ times
- Time yourself
- Get feedback from team
- Refine based on feedback

**Day 5:**
- Final practice
- Test all equipment
- Prepare for Q&A

### Step 7: Prepare for Q&A

**Expected questions:**

**Technical:**
- "What ML model did you use?" → MobileNetV2, TFLite
- "What's the accuracy?" → 72% on test set
- "How fast is it?" → <15s per image on Pi4
- "What about false positives?" → Confidence thresholds, manual review

**Implementation:**
- "How did you handle parallel development?" → Contract-based modules, Git branches
- "What was the biggest challenge?" → Integration testing, model accuracy
- "How long did this take?" → 5 days, but foundation in 2 days

**Impact:**
- "Who would use this?" → Marine researchers, environmental agencies
- "What's the cost?" → ~$200 for hardware vs $10K+ commercial systems
- "Can it run offline?" → Yes, completely on-device

### Step 8: Commit

```bash
git add presentation/
git commit -m "presentation: completed slides and demo script"
git push origin feature/presentation
```

---

## Testing Your Module

### Unit Tests

**Test your module in isolation:**

```bash
# Run your specific test class
pytest tests/test_all_modules.py::TestYourModule -v

# Run with verbose output
pytest tests/test_all_modules.py::TestYourModule -vv

# Run specific test
pytest tests/test_all_modules.py::TestYourModule::test_output_contract -v
```

### Integration Tests

**Test with full pipeline:**

```bash
# Run integration tests
pytest tests/test_all_modules.py::TestIntegration -v

# Run full pipeline
python main.py

# Check results
cat results/summary_*.csv
```

### Adding Your Own Tests

**Create `tests/test_my_module.py`:**

```python
import pytest
import numpy as np
from modules.your_module import YourModule

class TestYourModuleExtended:
    def test_specific_case(self):
        """Test specific scenario."""
        config = {...}
        module = YourModule(config)

        input_data = {...}
        result = module.process(input_data)

        assert result['status'] == 'success'
        assert result['your_field'] == expected_value

    def test_edge_case(self):
        """Test edge case."""
        # Your test code
        pass
```

**Run your tests:**
```bash
pytest tests/test_my_module.py -v
```

---

## Common Patterns

### Loading Configuration

```python
import yaml

class YourModule(PipelineModule):
    def __init__(self, config):
        super().__init__(config)

        # Get module-specific config
        self.param1 = config.get('param1', default_value)
        self.param2 = config.get('param2', default_value)

        # Validate
        if self.param1 < 0:
            raise ValueError("param1 must be positive")
```

### Error Handling

```python
def process(self, input_data):
    try:
        # Validate input
        self.validate_input(input_data)

        # Process
        result = self._do_processing(input_data)

        return {
            'status': 'success',
            'result_field': result
        }

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return self.handle_error(e)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

class YourModule(PipelineModule):
    def process(self, input_data):
        logger.info("Processing started")
        logger.debug(f"Input keys: {input_data.keys()}")

        # Process

        logger.info(f"Processing complete: {result}")
        return result
```

### Progress Tracking

```python
def process(self, input_data):
    items = input_data['items']
    total = len(items)

    for i, item in enumerate(items):
        # Process item
        progress = (i + 1) / total * 100
        logger.info(f"Progress: {progress:.1f}%")
```

---

## Quick Reference

### Daily Workflow

```bash
# Start
cd plank-1
source .venv/bin/activate
git checkout feature/your-module
git pull origin main  # Get latest

# Work
# ... make changes ...

# Test
pytest tests/test_all_modules.py::TestYourModule -v
python main.py

# Commit
git add .
git commit -m "module: what you did"
git push origin feature/your-module

# End
# Notify in team chat if ready for merge
```

### Getting Help

1. Check `docs/TROUBLESHOOTING.md`
2. Check `docs/GIT_WORKFLOW.md`
3. Ask in team chat
4. Ask integration lead

---

**Remember**: Work on YOUR module only, follow the contract, test frequently, and communicate!
