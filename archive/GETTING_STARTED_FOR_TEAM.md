# Getting Started - Team Onboarding Guide

**Welcome to the Marine Plankton AI Microscopy Project!**

This guide will get you up and running in **15 minutes**.

---

## 🎯 What We Have

A **complete, working modular pipeline** for marine plankton identification:

```
Acquisition → Preprocessing → Segmentation → Classification →
Counting → Analytics → Export
```

✅ All 7 modules implemented with standard interfaces
✅ End-to-end pipeline working
✅ Example outputs generated
✅ Comprehensive documentation
✅ Ready for parallel team development

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Get the Code
```bash
cd plank-1
```

### Step 2: Set Up Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Setup
```bash
python verify_setup.py
```

You should see:
```
🎉 All checks passed! Your environment is ready.
```

### Step 4: Run the Pipeline
```bash
python main.py
```

Expected output:
```
INFO:pipeline.manager:Pipeline execution complete!
INFO:pipeline.manager:Total organisms detected: 4
INFO:pipeline.manager:Species richness: 2
INFO:pipeline.manager:Shannon diversity: 0.562
```

### Step 5: Check Results
```bash
ls results/
cat results/summary_*.csv
```

**✅ If you got here, you're ready to start developing!**

---

## 📚 Essential Reading (10 minutes)

### Read These First (in order):

1. **QUICKSTART.md** (5 min)
   - How to run the pipeline
   - Common commands
   - Understanding output

2. **docs/DEVELOPER_GUIDE.md** (5 min initially, reference later)
   - Your module's contract (input/output specification)
   - How to test independently
   - Development workflow

3. **PROJECT_STATUS.md** (quick scan)
   - What's working
   - What needs work
   - Current progress

---

## 👥 Find Your Module

Each team member will work on ONE module. Here's what each does:

| Module | What It Does | Current Status | Difficulty |
|--------|--------------|----------------|------------|
| **Acquisition** | Captures images from camera | Stub - needs camera integration | Medium |
| **Preprocessing** | Cleans up images | Working - needs fine-tuning | Easy |
| **Segmentation** | Finds individual organisms | Working - needs optimization | Medium |
| **Classification** | Identifies species | Stub - needs ML model | Hard |
| **Counting** | Counts organisms | Complete | Easy |
| **Analytics** | Calculates diversity | Complete | Easy |
| **Export** | Saves results & dashboard | Partial - needs dashboard | Medium |

**Ask your lead which module you're assigned to.**

---

## 🔧 Working on Your Module

### Understanding Your Contract

Every module has:
1. **Input Contract** - What data it receives
2. **Output Contract** - What data it must return
3. **Configuration** - Settings in `config/config.yaml`

**RULE #1**: Never change your module's input/output contract without team discussion.

### Example: If you're assigned "Preprocessing"

1. **Read your contract** in `docs/DEVELOPER_GUIDE.md` (search for "Module 2")

2. **Your input contract**:
   ```python
   {
       'image': np.ndarray[H, W, 3],
       'preprocessing_config': dict,
   }
   ```

3. **Your output contract**:
   ```python
   {
       'status': 'success' | 'error',
       'error_message': str | None,
       'processed_image': np.ndarray[H, W, 3],
       'preprocessing_stats': dict,
   }
   ```

4. **Your job**: Improve the implementation in `modules/preprocessing.py`
   while keeping the contract **exactly the same**.

---

## 🧪 Testing Your Module

### Option 1: Test Independently (Recommended)

```bash
# Run the examples
python examples/test_individual_module.py
```

This shows how to test modules without running the full pipeline.

### Option 2: Test in Full Pipeline

```bash
python main.py
```

See if your changes work end-to-end.

### Option 3: Write Unit Tests

Create `tests/test_<your_module>.py`:

```python
from modules.your_module import YourModule

def test_basic():
    module = YourModule(config)
    result = module.process(input_data)
    assert result['status'] == 'success'
```

Run with:
```bash
pytest tests/test_your_module.py -v
```

---

## 📂 Key Files You'll Edit

Depending on your module:

| Module | Files You'll Edit | Don't Touch |
|--------|-------------------|-------------|
| Acquisition | `modules/acquisition.py` | Other modules |
| Preprocessing | `modules/preprocessing.py` | Other modules |
| Segmentation | `modules/segmentation.py` | Other modules |
| Classification | `modules/classification.py`, add model to `models/` | Other modules |
| Counting | `modules/counting.py` | Other modules |
| Analytics | `modules/analytics.py` | Other modules |
| Export | `modules/export.py`, `dashboard/` | Other modules |

**Everyone can edit**: `config/config.yaml` (but coordinate with team)

---

## 🔄 Development Workflow

### Daily Workflow

```bash
# 1. Make sure you're in virtual environment
source .venv/bin/activate

# 2. Pull latest changes
git pull origin main

# 3. Create/switch to your feature branch
git checkout -b feature/your-module-name

# 4. Make your changes
# Edit modules/your_module.py

# 5. Test your changes
python examples/test_individual_module.py
# OR
python main.py

# 6. Commit and push
git add modules/your_module.py
git commit -m "your-module: description of changes"
git push origin feature/your-module-name

# 7. Create Pull Request on GitHub
```

### When to Commit

- ✅ After implementing a feature
- ✅ After fixing a bug
- ✅ At end of day (if code works)
- ❌ When code is broken
- ❌ Before testing

---

## 💬 Getting Help

### If something doesn't work:

1. **Check the documentation**:
   - `QUICKSTART.md` - Basic usage
   - `docs/DEVELOPER_GUIDE.md` - Development details
   - `PROJECT_STATUS.md` - What's working

2. **Run verification**:
   ```bash
   python verify_setup.py
   ```

3. **Check you're in virtual environment**:
   ```bash
   which python  # Should point to .venv/bin/python
   ```

4. **Common fixes**:
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt

   # Reactivate venv
   source .venv/bin/activate
   ```

5. **Ask the team**:
   - Slack channel: #help
   - Tag: @your-lead

---

## 📊 Checking Your Progress

After making changes, verify:

```bash
# 1. Does your module import?
python -c "from modules.your_module import YourModule; print('OK')"

# 2. Does it initialize?
python -c "from modules.your_module import YourModule; m=YourModule({}); print('OK')"

# 3. Does the full pipeline work?
python main.py
```

If all three work, you're good! ✅

---

## 🎓 Learning Resources

### Inside This Project
- `examples/test_individual_module.py` - How to test modules
- `tests/test_example.py` - Example unit tests
- `docs/DEVELOPER_GUIDE.md` - Complete reference
- `project_pipeline_idea.md` - Original design doc

### External Resources
- Python: https://docs.python.org/3/
- OpenCV: https://docs.opencv.org/
- NumPy: https://numpy.org/doc/
- TensorFlow Lite: https://www.tensorflow.org/lite

---

## ⚡ Quick Reference

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify
python verify_setup.py

# Run pipeline
python main.py

# Test your module
python examples/test_individual_module.py

# Run unit tests
pytest tests/ -v

# Check results
ls results/
cat results/summary_*.csv
```

---

## 🎯 Your First Task

**Complete this in your first session:**

1. ✅ Set up your environment
2. ✅ Run `verify_setup.py` - make sure it passes
3. ✅ Run `python main.py` - see the pipeline work
4. ✅ Read your module's contract in `DEVELOPER_GUIDE.md`
5. ✅ Read the current implementation of your module
6. ✅ Run `python examples/test_individual_module.py`
7. ✅ Make a small change to your module (e.g., add a print statement)
8. ✅ Test that it still works
9. ✅ Commit your change

**After completing these steps, you're ready to work on real features!**

---

## 📞 Important Contacts

- **Project Lead**: [Name] - Overall coordination
- **Technical Lead**: [Name] - Architecture questions
- **ML Lead**: [Name] - Classification/model questions
- **Hardware Lead**: [Name] - Raspberry Pi/camera questions
- **Your Module Lead**: [Name] - Module-specific questions

---

## 🎉 You're Ready!

You now have everything you need to:
- ✅ Understand the project structure
- ✅ Run the pipeline
- ✅ Test your module
- ✅ Make changes
- ✅ Commit and collaborate

**Welcome to the team! Let's build something amazing! 🚀**

---

**Questions?** Re-read this guide or ask in #help channel.
**Stuck?** Run `python verify_setup.py` and share the output.
**Confused?** Read `docs/DEVELOPER_GUIDE.md` for your module.
