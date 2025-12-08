# START HERE - Hackathon Kickoff

**Read this first** (10 minutes)

**Goal**: Get you from zero to coding in 15 minutes

---

## What This Project Is

Automated microscopy system for identifying and counting marine plankton organisms.

**Pipeline**: Image → Process → Detect → Classify → Count → Analyze → Export

**Status**: Working foundation, ready for team development

**Timeline**: Complete by Day 2, polish Days 3-5

---

## Immediate Actions (15 minutes)

### 1. Setup Environment (5 minutes)

```bash
cd plank-1
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Verify It Works (2 minutes)

```bash
python verify_setup.py
```

**Expected output**: "All checks passed!"

### 3. Run the Pipeline (3 minutes)

```bash
python main.py
```

**Expected**: Pipeline completes, see results in `results/`

### 4. Check Results (2 minutes)

```bash
ls results/
cat results/summary_*.csv
```

You should see plankton counts, diversity metrics, CSV data.

### 5. Understand Your Role (3 minutes)

Ask your team lead which module you're assigned:

| Module | Priority | What You'll Do |
|--------|----------|----------------|
| Classification | CRITICAL | Train/integrate ML model |
| Dashboard | HIGH | Build Streamlit UI |
| Data Collection | HIGH | Gather 20+ test images |
| Integration | CRITICAL | Merge code, keep system working |
| Presentation | MEDIUM | Slides, demo script |

---

## What You Have Right Now

### Working Code

**7 Modules** (all integrated):
1. Acquisition - Image capture (stub with synthetic images)
2. Preprocessing - Image enhancement (working)
3. Segmentation - Organism detection (working)
4. Classification - Species ID (stub, needs your ML model)
5. Counting - Count and size organisms (working)
6. Analytics - Diversity metrics (working)
7. Export - CSV/JSON output (working)

**Tests**: 18/19 passing (95%)

**Pipeline**: Runs end-to-end successfully

### What Needs Work

**CRITICAL** (Day 1-2):
- Classification model (currently random predictions)
- Dashboard UI (currently stub)
- Test images (currently synthetic)

**Important** (Day 3-4):
- Model accuracy >70%
- UI polish
- Error handling

---

## Your Module Contract

Every module has a **contract** - what it receives and what it must return.

**Find yours**:
```bash
cat docs/CONTRACTS.md
# Search for your module
```

**Critical Rule**: DO NOT change your contract without team discussion.

**Why**: Others depend on your output format. Changing it breaks integration.

**Example** (Classification):
```python
# Input you receive:
{
    'image': np.ndarray,
    'masks': list,
    'bounding_boxes': list,
    ...
}

# Output you MUST return:
{
    'status': 'success',
    'predictions': list,  # One per organism
    'model_metadata': dict
}
```

---

## Day 1-2 Timeline

### Day 1: Build Everything (16 hours)

**Hour 0-1**: Setup (what you just did)

**Hour 1-8**: Your module development
- Classification: Train/find model
- Dashboard: Basic Streamlit app
- Data: Collect 20+ images
- Integration: Set up workflow
- Presentation: Slide skeleton

**Hour 8**: Integration checkpoint - merge your code

**Hour 8-16**: Continue development + integration

**Hour 16**: Day 1 complete - full system working

### Day 2: Polish & Demo (16 hours)

**Hour 0-8**: Fix bugs, optimize, test

**Hour 8-16**: Demo to evaluators, get feedback

**Goal**: Complete working system

### Day 3-5: Iterate

Implement evaluator feedback, polish, final presentation

---

## How to Work on Your Module

### Step 1: Read Your Contract (5 min)

```bash
# Find your module's section
cat docs/CONTRACTS.md

# Example: Module 4 - Classification
# Read "Input Contract" and "Output Contract"
```

### Step 2: Understand Current Code (10 min)

```bash
# Open your module file
# modules/classification.py (or your module)

# Find the process() method
# This is what you'll improve
```

### Step 3: Make Changes (ongoing)

```bash
# Edit your module
# Keep the same input/output structure
# Improve the implementation
```

### Step 4: Test (every 30 min)

```bash
# Test your module
pytest tests/test_all_modules.py::TestYourModule -v

# Test full pipeline
python main.py

# Both should pass
```

### Step 5: Commit & Push (hourly)

```bash
git checkout -b feature/your-module
git add .
git commit -m "module: what you did"
git push origin feature/your-module

# Integration lead will merge
```

---

## Module-Specific Quick Starts

### If You're on Classification (Person 1)

**Priority**: CRITICAL - This is the most important module

**Day 1 Goal**: Working model by Hour 8

**Fast Track**:
1. Download Kaggle WHOI plankton dataset
2. Find pretrained model OR use transfer learning (MobileNetV2)
3. Convert to TFLite
4. Replace `_predict()` function in `modules/classification.py`

**Commands**:
```bash
pip install tensorflow
# Download dataset
# Train or adapt pretrained model
# Convert to TFLite
# Update classification.py
```

**Acceptance**: >60% accuracy, <3s inference

---

### If You're on Dashboard (Person 2)

**Priority**: HIGH - User-facing component

**Day 1 Goal**: Basic UI by Hour 12

**Fast Track**:
1. Install Streamlit
2. Create `dashboard/app.py`
3. File upload → Run pipeline → Display results

**Commands**:
```bash
pip install streamlit plotly
# Create dashboard/app.py
streamlit run dashboard/app.py
```

**Basic Structure**:
```python
import streamlit as st

st.title("Plankton Analysis")
uploaded = st.file_uploader("Upload microscope image")
if st.button("Analyze"):
    # Run pipeline
    # Display results
    st.metric("Total Organisms", count)
    st.bar_chart(counts_by_class)
```

---

### If You're on Data Collection (Person 3)

**Priority**: HIGH - Needed for testing

**Day 1 Goal**: 20+ images by Hour 8

**Fast Track**:
1. Download WHOI plankton dataset
2. Select 20-30 diverse images
3. Update `acquisition.py` to load from files

**Commands**:
```bash
# Download dataset
# Select diverse images
# Update acquisition._capture_image() to load files
```

---

### If You're on Integration (Person 4)

**Priority**: CRITICAL - Keeps team unblocked

**Ongoing**: Every 4 hours

**Responsibilities**:
- Pull everyone's branches
- Merge one at a time
- Test after each merge
- Fix integration bugs
- Keep main branch always working

**Commands**:
```bash
# Every 4 hours
git fetch --all
git merge feature/classification  # Test
git merge feature/dashboard  # Test
python main.py  # Verify
pytest tests/test_all_modules.py -v  # Verify
```

---

### If You're on Presentation (Person 5)

**Priority**: MEDIUM - Can wait until Day 2

**Day 1 Goal**: Slide skeleton by Hour 8

**Day 2 Goal**: Complete presentation + demo video

**Tasks**:
- Create slide deck (problem, solution, architecture, demo, results)
- Take screenshots of dashboard
- Write demo script (3 minutes)
- Record backup video
- Practice Q&A

---

## Communication

### Standups (Every 4 hours)

**When**: Hours 0, 4, 8, 12, 16

**Format** (5 min total):
```
Person 1: "Did X, doing Y, blocked on Z"
Person 2: "Did A, doing B, no blockers"
...
```

### Post Blockers Immediately

If stuck >15 minutes:
1. Post in #help channel
2. Include: module name, error message, what you tried
3. Continue on something else while waiting

### Integration Checkpoints

- Hour 8 Day 1: First merge
- Hour 16 Day 1: Full integration
- Day 2: Continuous integration

---

## Essential Documentation

### Read Now
- **This file** (you're reading it)
- **QUICKSTART.md** - Command reference
- **docs/CONTRACTS.md** - Your module's interface

### Read During Development
- **docs/DEVELOPER_GUIDE.md** - Development guidelines
- **docs/TIMELINE.md** - Detailed hour-by-hour plan
- **docs/TESTING.md** - Testing strategy

### Reference
- **README.md** - Full project documentation
- **REFERENCE_CARD.md** - One-page cheat sheet

---

## Quick Commands Reference

```bash
# Daily
source .venv/bin/activate
python verify_setup.py

# Run pipeline
python main.py

# Test your module
pytest tests/test_all_modules.py::TestYourModule -v

# Test everything
pytest tests/test_all_modules.py -v

# View results
cat results/summary_*.csv

# Git workflow
git checkout -b feature/your-module
git add . && git commit -m "module: message"
git push origin feature/your-module
```

---

## Success Criteria

### End of Day 1
- [ ] Your module has committed code
- [ ] Your module passes tests
- [ ] System runs end-to-end
- [ ] No critical blockers

### End of Day 2
- [ ] Classification model integrated (any accuracy)
- [ ] Dashboard displays results
- [ ] Pipeline <30s per image
- [ ] Demo to evaluators complete
- [ ] Feedback received

### End of Day 5
- [ ] Feedback implemented
- [ ] Final presentation ready
- [ ] Code submitted
- [ ] Judges impressed

---

## What to Do Now

1. **Verify setup works** (if you haven't): `python verify_setup.py`

2. **Read your module's contract**: `cat docs/CONTRACTS.md`

3. **Look at your module's code**: `cat modules/your_module.py`

4. **Read detailed timeline**: `cat docs/TIMELINE.md`

5. **Start coding**: Improve your module's `process()` function

---

## Remember

**Speed over perfection**: Working demo beats perfect code

**Test frequently**: Run `python main.py` after every change

**Communicate**: Standup every 4 hours, post blockers immediately

**Respect contracts**: Don't change input/output without discussion

**Help others**: If you finish early, help teammates

---

**You have everything you need. The foundation is ready. Start building.**

**Questions?** Read README.md or ask in #help

**Ready?** Read `docs/TIMELINE.md` for your hour-by-hour tasks
