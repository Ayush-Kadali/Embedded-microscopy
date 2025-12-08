# Team Quick Start - 15 Minutes to Start Coding

**Context**: 5-day hackathon, need working demo by Day 5

**Goal**: Get environment running and start parallel development immediately

---

## Setup (5 minutes)

### Step 1: Environment
```bash
cd plank-1
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Step 2: Verify
```bash
python verify_setup.py
```

Expected: All 6 checks should pass

### Step 3: Test Pipeline
```bash
python main.py
```

Expected output:
```
Pipeline execution complete!
Total organisms detected: 4
Species richness: 2
Shannon diversity: 0.562
```

### Step 4: Check Results
```bash
ls results/
cat results/summary_*.csv
```

If you see CSV files with plankton data, you're ready.

---

## Your Module Assignment

Ask team lead which module you're assigned:

| Module | Files to Edit | Current Status |
|--------|---------------|----------------|
| Classification | modules/classification.py | Stub - needs model |
| Acquisition | modules/acquisition.py | Stub - needs camera/images |
| Dashboard | dashboard/, create new files | Stub - needs Streamlit |
| Preprocessing | modules/preprocessing.py | Working - needs optimization |
| Segmentation | modules/segmentation.py | Working - needs tuning |
| Integration | main.py, tests/ | Working - needs continuous testing |

---

## Understanding Your Contract (5 minutes)

Every module has:
1. **Input Contract** - What data it receives
2. **Output Contract** - What data it must return

**CRITICAL RULE**: Do NOT change your contract during hackathon without team discussion

### Example: Classification Module

**Input**:
```python
{
    'image': np.ndarray,
    'masks': list,
    'bounding_boxes': list,
    'classification_config': dict,
}
```

**Output**:
```python
{
    'status': 'success' | 'error',
    'predictions': list,  # One per organism
    'model_metadata': dict,
}
```

**Your job**: Improve implementation in `modules/classification.py` while keeping these contracts exactly the same

Find your module's contract in `docs/DEVELOPER_GUIDE.md`

---

## Testing Your Module (5 minutes)

### Option 1: Test Independently
```bash
python examples/test_individual_module.py
```

This shows how to test your module without running full pipeline

### Option 2: Test in Pipeline
```bash
python main.py
```

See if your changes work end-to-end

### Option 3: Quick Test
```python
from modules.your_module import YourModule

config = {'param': 'value'}
module = YourModule(config)

result = module.process(input_data)
print(result['status'])  # Should be 'success'
```

---

## Development Workflow

### Hour-by-Hour
```
Hour 0: Setup environment, understand contract
Hour 1-4: Implement core functionality
Hour 4: Integration checkpoint - merge your changes
Hour 5-8: Polish and optimize
Hour 8: Day end - commit all working code
```

### Git Workflow
```bash
# Create your branch
git checkout -b feature/your-module

# Make changes and test
# Edit modules/your_module.py
python main.py  # Test

# Commit frequently
git add .
git commit -m "your-module: what you did"
git push origin feature/your-module

# Integration lead will merge
```

---

## Module-Specific Quick Starts

### If You're on Classification

**Priority**: Get ANY working model, accuracy comes later

**Fast Track**:
1. Download pretrained model from Kaggle/HuggingFace
2. Or use transfer learning with MobileNetV2
3. Export to TFLite
4. Replace stub in `modules/classification.py`

**Commands**:
```bash
# Install TensorFlow
pip install tensorflow

# Download dataset (example)
# Use: WHOI Plankton, Kaggle plankton datasets

# Train or use pretrained model
# Convert to TFLite
# Update classification.py
```

**Target**: >60% accuracy is fine for demo

---

### If You're on Acquisition

**Priority**: Get images into pipeline, camera is bonus

**Fast Track Option A** (If no camera):
1. Download plankton image dataset
2. Update acquisition.py to load from files
3. Keep all metadata fields

**Fast Track Option B** (If have camera):
1. Install picamera2
2. Update acquisition.py with camera code
3. Test capture

**Commands**:
```bash
# Option A: File-based
# Just modify _capture_image() to load from file

# Option B: Camera
pip install picamera2
# Update acquisition.py
```

---

### If You're on Dashboard

**Priority**: Show results visually, keep it simple

**Fast Track**:
1. Install Streamlit
2. Read CSV from results/
3. Show: table, bar chart, metrics
4. No fancy maps needed for Day 1

**Commands**:
```bash
pip install streamlit plotly

# Create dashboard/app.py
streamlit run dashboard/app.py
```

**Basic Dashboard Structure**:
```python
import streamlit as st
import pandas as pd

st.title("Plankton Analysis")

# Read latest results
df = pd.read_csv("results/summary_latest.csv")

# Show table
st.dataframe(df)

# Show metrics
st.metric("Total Organisms", total)
st.metric("Shannon Diversity", shannon)

# Show chart
st.bar_chart(counts_by_class)
```

---

### If You're on Preprocessing/Segmentation

**Priority**: Optimize existing code, don't rewrite

**Fast Track**:
1. Profile current code
2. Tune parameters in config.yaml
3. Test with different images
4. Document best settings

**Commands**:
```bash
# Profile
python -m cProfile main.py

# Test different configs
# Edit config/config.yaml
# Run python main.py
# Compare results
```

---

### If You're on Integration/Testing

**Priority**: Keep pipeline always working

**Fast Track**:
1. Pull everyone's changes every 2 hours
2. Run full pipeline
3. Fix any contract violations
4. Document issues

**Commands**:
```bash
# Pull all branches
git fetch --all

# Merge feature branches one by one
git checkout main
git merge feature/classification
python main.py  # Test
# If works, continue
git merge feature/acquisition
python main.py  # Test again
```

---

## Common Issues

### Import Error
```bash
# Check virtual environment is active
which python  # Should show .venv/bin/python

# Reinstall if needed
pip install -r requirements.txt
```

### Pipeline Fails
```bash
# Check which module failed
python main.py  # Look for "Failed at: module_name"

# Test that module independently
python examples/test_individual_module.py
```

### Contract Violation
If integration fails with "Missing required field" or similar:
- You changed a contract
- Check your module's output matches expected contract
- Read error message for which field is missing

---

## Communication

### Every 4 Hours: Standup
- What you did
- What you're doing next
- Any blockers

Keep it under 5 minutes total

### Immediate Blocker
- Post in Slack/Discord #help
- Tag integration lead
- Include: error message, what you tried

---

## Success Criteria

By end of your first 4 hours:
- [ ] Module imports without errors
- [ ] Module processes sample input
- [ ] Module returns expected output format
- [ ] Committed to your branch

By end of your first day:
- [ ] Core functionality implemented
- [ ] Tested with pipeline
- [ ] Merged to main (via integration lead)

---

## Key Files

**Your Module**: `modules/your_module.py`
**Config**: `config/config.yaml`
**Tests**: `examples/test_individual_module.py`
**Full Pipeline**: `main.py`

**Documentation**:
- Module contracts: `docs/DEVELOPER_GUIDE.md`
- Hackathon plan: `HACKATHON_PLAN.md`
- This file: `TEAM_QUICKSTART.md`

---

## Quick Reference

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Verify
python verify_setup.py

# Run
python main.py

# Test module
python examples/test_individual_module.py

# Commit
git add . && git commit -m "module: change" && git push
```

---

**You have 5 days. Focus on working over perfect. Get it done, polish later.**

Read `HACKATHON_PLAN.md` for daily breakdown.
