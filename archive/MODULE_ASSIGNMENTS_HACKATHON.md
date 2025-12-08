# Module Assignments - 5-Day Hackathon

**Timeline**: 5 days to working demo
**Strategy**: Parallel development, continuous integration, MVP first

---

## Team Structure

### Recommended Team of 5

| Role | Module | Priority | Hours/Day |
|------|--------|----------|-----------|
| Person 1 | Classification (ML) | CRITICAL | 8-10 |
| Person 2 | Acquisition + Dashboard | HIGH | 8 |
| Person 3 | Dashboard + Export | HIGH | 8 |
| Person 4 | Preprocessing + Segmentation | MEDIUM | 6-8 |
| Person 5 | Integration + Testing | CRITICAL | 8 |

### If Team of 3
- Person 1: Classification
- Person 2: Dashboard + Acquisition
- Person 3: Integration + Optimization

---

## Module 1: Classification (CRITICAL PATH)

**Assigned to**: _______________
**Status**: Stub - needs trained model
**Day 1-3 Priority**: HIGHEST

### Deliverables by Day

**Day 1 (8 hours)**:
- [ ] Download plankton dataset (Kaggle WHOI or similar)
- [ ] Set up training pipeline OR find pretrained model
- [ ] Start transfer learning with MobileNetV2
- [ ] Test accuracy on validation set
- [ ] Target: >60% accuracy minimum

**Day 2 (8 hours)**:
- [ ] Convert model to TFLite
- [ ] Integrate into modules/classification.py
- [ ] Test with full pipeline
- [ ] Optimize inference speed
- [ ] Target: <3s for 20 organisms

**Day 3 (4 hours)**:
- [ ] Fine-tune if accuracy low
- [ ] Add confidence thresholding
- [ ] Test edge cases
- [ ] Document accuracy metrics

### Fast Track Options

**Option A: Transfer Learning** (Recommended)
```python
# Use pretrained MobileNetV2
base_model = tf.keras.applications.MobileNetV2(weights='imagenet')
# Add classification head for plankton classes
# Train for 2-3 hours
# Convert to TFLite
```

**Option B: Pretrained Model**
- Search Kaggle/HuggingFace for "plankton classification"
- Download and adapt to our classes
- May need class mapping

**Option C: Simple Heuristics** (Backup)
- If ML fails, use size + color features
- Rules-based classification
- Better than random

### Integration Points
- Hour 8 (Day 1): Stub with realistic confidence scores
- Hour 16 (Day 2): TFLite model integrated
- Hour 24 (Day 2): Full integration tested

### Files to Modify
- `modules/classification.py` - Main implementation
- `models/` - Add your .tflite model here
- `config/config.yaml` - Update model_path and class_names

### Success Criteria
- [ ] Model integrated and working
- [ ] Accuracy >60% on validation set
- [ ] Inference <3s for typical image
- [ ] No crashes on edge cases

---

## Module 2: Acquisition

**Assigned to**: _______________
**Status**: Stub - needs real images
**Day 1-2 Priority**: HIGH

### Deliverables by Day

**Day 1 (4 hours)**:
- [ ] Decide: Real camera OR dataset images
- [ ] If camera: Install picamera2, test capture
- [ ] If dataset: Download images, implement file loading
- [ ] Update modules/acquisition.py
- [ ] Test image quality

**Day 2 (2 hours)**:
- [ ] Ensure metadata is correct
- [ ] Test with 10+ diverse images
- [ ] Handle errors gracefully
- [ ] Optimize image quality

### Fast Track Options

**Option A: File Upload** (Fastest)
```python
def _capture_image(self, exposure_ms):
    # Load from dataset or user upload
    image = cv2.imread('dataset/sample.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image
```

**Option B: Real Camera**
```python
from picamera2 import Picamera2
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()
image = picam2.capture_array()
```

### Integration Points
- Hour 4 (Day 1): File-based acquisition working
- Hour 16 (Day 2): Camera integration (if using)

### Files to Modify
- `modules/acquisition.py`

### Success Criteria
- [ ] Provides RGB images to pipeline
- [ ] Metadata populated correctly
- [ ] Works with 10+ test images

---

## Module 3: Dashboard (HIGH IMPACT)

**Assigned to**: _______________
**Status**: Stub - needs Streamlit UI
**Day 2-4 Priority**: HIGH

### Deliverables by Day

**Day 2 (6 hours)**:
- [ ] Install Streamlit
- [ ] Create basic layout: title, file upload, analyze button
- [ ] Read and display CSV results
- [ ] Show metrics: total count, diversity
- [ ] Show simple bar chart of counts by class

**Day 3 (4 hours)**:
- [ ] Add organism details table
- [ ] Add size distribution histogram
- [ ] Improve visual design
- [ ] Add "Export Results" button

**Day 4 (2 hours)**:
- [ ] Polish UI
- [ ] Add error handling
- [ ] Test with judges' perspective
- [ ] Screenshots for presentation

### Minimum Viable Dashboard

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Marine Plankton Analysis")

# File upload
uploaded = st.file_uploader("Upload microscope image")

if st.button("Analyze"):
    # Run pipeline
    # Show results

# Display results
st.metric("Total Organisms", count)
st.metric("Shannon Diversity", diversity)

# Chart
fig = px.bar(df, x='class_name', y='count')
st.plotly_chart(fig)

# Table
st.dataframe(organisms_df)
```

### Integration Points
- Hour 16 (Day 2): Basic dashboard reads CSV
- Hour 24 (Day 2): Dashboard triggers pipeline
- Hour 32 (Day 3): Polished UI

### Files to Create
- `dashboard/app.py` - Main Streamlit app
- `dashboard/utils.py` - Helper functions

### Success Criteria
- [ ] User can upload image
- [ ] Pipeline runs on click
- [ ] Results display automatically
- [ ] Looks professional
- [ ] No crashes

---

## Module 4: Preprocessing + Segmentation

**Assigned to**: _______________
**Status**: Working - needs optimization
**Day 1-3 Priority**: MEDIUM

### Deliverables by Day

**Day 1 (4 hours)**:
- [ ] Test current implementation with diverse images
- [ ] Profile performance bottlenecks
- [ ] Tune segmentation parameters
- [ ] Document optimal settings

**Day 2 (2 hours)**:
- [ ] Implement parameter tuning based on image quality
- [ ] Add fallback if segmentation fails
- [ ] Test edge cases

**Day 3 (2 hours)**:
- [ ] Final optimization
- [ ] Document parameter choices
- [ ] Create parameter guide for config.yaml

### Optimization Checklist

**Preprocessing**:
- [ ] Test bilateral vs gaussian vs NLM denoising
- [ ] Optimize background correction
- [ ] Measure processing time

**Segmentation**:
- [ ] Test watershed vs threshold methods
- [ ] Tune min/max area parameters
- [ ] Handle overlapping organisms
- [ ] Ensure no false positives

### Integration Points
- Hour 8 (Day 1): Optimized parameters in config
- Hour 24 (Day 2): Robust to diverse images

### Files to Modify
- `modules/preprocessing.py`
- `modules/segmentation.py`
- `config/config.yaml`

### Success Criteria
- [ ] Works on 90% of test images
- [ ] Segmentation precision >70%
- [ ] Processing time <5s
- [ ] No crashes on poor quality images

---

## Module 5: Integration + Testing (CRITICAL)

**Assigned to**: _______________
**Status**: Working - needs continuous work
**Day 1-5 Priority**: ONGOING

### Responsibilities

**Continuous Integration**:
- Pull and merge feature branches every 4 hours
- Test full pipeline after each merge
- Fix contract violations immediately
- Keep main branch always working

**Testing**:
- Test with diverse images
- Test error handling
- Test edge cases
- Document bugs and issues

**Bug Fixing**:
- Fix integration bugs
- Help teammates debug
- Ensure smooth demo

### Daily Tasks

**Day 1**:
- [ ] Set up Git workflow
- [ ] Create integration branch
- [ ] Test initial modules
- [ ] Hour 8: First integration

**Day 2**:
- [ ] Hour 0: Merge classification changes
- [ ] Hour 4: Merge dashboard changes
- [ ] Hour 8: Full system test
- [ ] Document issues

**Day 3**:
- [ ] Run comprehensive test suite
- [ ] Test all export formats
- [ ] Stress test with many images
- [ ] Fix all critical bugs

**Day 4**:
- [ ] Final integration test
- [ ] Prepare demo environment
- [ ] Create backup plan
- [ ] Document known issues

**Day 5**:
- [ ] Final smoke test
- [ ] Help with presentation prep
- [ ] Be ready for live demo support

### Git Workflow

```bash
# Every 4 hours
git fetch --all

# Merge one feature at a time
git checkout main
git merge feature/classification
python main.py  # Test
python verify_setup.py  # Verify

# If successful
git push origin main

# If failed
git merge --abort
# Fix issues with teammate
# Try again
```

### Files to Monitor
- All module files
- `main.py`
- `config/config.yaml`
- `requirements.txt`

### Success Criteria
- [ ] Main branch always works
- [ ] All modules integrated by Day 2 evening
- [ ] No critical bugs by Day 4
- [ ] Demo rehearsed and working

---

## Communication Protocol

### Standup (Every 4 hours)
- **When**: Hours 0, 4, 8 of each day
- **Duration**: 5 minutes max
- **Format**:
  - Person 1: "Did X, doing Y, blocked on Z"
  - Person 2: "Did A, doing B, no blockers"
  - ...

### Immediate Blockers
- Post in #help channel
- Tag integration lead
- Include: module name, error, what you tried

### Integration Checkpoints
- Hour 8 (Day 1): First merge
- Hour 16 (Day 2 morning): Classification integration
- Hour 24 (Day 2 evening): Full integration
- Hour 32+ (Day 3+): Continuous integration

---

## Division of Work

### Clear Ownership

| Module | Owner | Deputy (Backup) |
|--------|-------|-----------------|
| Classification | Person 1 | Person 5 |
| Acquisition | Person 2 | Person 5 |
| Dashboard | Person 3 | Person 2 |
| Preprocessing | Person 4 | Person 5 |
| Segmentation | Person 4 | Person 5 |
| Export | Person 3 | Person 5 |
| Integration | Person 5 | Everyone |

### Shared Responsibilities

**Everyone**:
- Write clean, commented code
- Test your module independently before merging
- Update config.yaml if needed
- Document major changes
- Help teammates if you finish early

**No One Person Should**:
- Change another person's module without asking
- Modify contracts without team discussion
- Merge to main without testing
- Work in isolation for >4 hours

---

## Risk Mitigation

### If Classification Fails
- Use pretrained model even if imperfect
- Use rule-based heuristics as fallback
- Focus on architecture, not accuracy for demo

### If Camera Not Available
- Use dataset images
- Implement file upload in dashboard
- Show as "future hardware integration"

### If Dashboard Breaks Day 5
- Fallback to CSV + Excel demo
- Show results in Jupyter notebook
- Focus on pipeline, not UI

### If Someone Gets Blocked
- Switch to their backup task
- Pair program with integration lead
- Simplify scope if needed

---

## Daily Progress Checklist

### Day 1 End
- [ ] All environments set up
- [ ] Everyone has committed code
- [ ] Main pipeline still works
- [ ] Classification training started

### Day 2 End
- [ ] Classification integrated
- [ ] Dashboard shows basic results
- [ ] All modules merged to main
- [ ] Demo script drafted

### Day 3 End
- [ ] Polished demo working
- [ ] No critical bugs
- [ ] Presentation slides ready
- [ ] Screenshots taken

### Day 4 End
- [ ] Comprehensive testing done
- [ ] Demo rehearsed 3 times
- [ ] Documentation complete
- [ ] Backup plan ready

### Day 5 End
- [ ] Demo delivered
- [ ] Judges' questions answered
- [ ] Code submitted
- [ ] Celebrate!

---

## Success Metrics

**Minimum for Demo**:
- Pipeline runs without crashes
- Classifies organisms (any accuracy)
- Shows diversity metrics
- Exports CSV
- Dashboard displays results

**Target for Scoring**:
- Classification accuracy >70%
- Professional-looking dashboard
- <30s per image processing
- Handles errors gracefully
- Clear documentation

**Stretch Goals**:
- Real camera integration
- Batch processing
- Historical trend analysis
- Bloom detection working

---

This is a hackathon. Working is better than perfect. Get it done, impress judges, iterate based on feedback.
