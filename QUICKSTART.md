# Quick Start - Essential Commands

**5-minute setup and run**

---

## First Time Setup

```bash
# Clone/navigate to project
cd plank-1

# Create virtual environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify everything works
python verify_setup.py
```

**Expected**: "All checks passed!"

---

## Run Pipeline

```bash
# Basic run
python main.py

# With custom parameters
python main.py --magnification 2.5 --exposure 150

# With GPS
python main.py --gps-lat 12.34 --gps-lon 56.78
```

**Expected**: "Pipeline execution complete!"

**Output**: Files in `results/` directory

---

## Testing

```bash
# Run all tests
pytest tests/test_all_modules.py -v

# Test specific module
pytest tests/test_all_modules.py::TestClassificationModule -v

# Test with coverage
pytest tests/test_all_modules.py --cov=modules
```

**Expected**: 18/19 tests passing

---

## Development

```bash
# Daily startup
source .venv/bin/activate

# Create your branch
git checkout -b feature/your-module

# Make changes
# Edit modules/your_module.py

# Test locally
python main.py
pytest tests/test_all_modules.py::TestYourModule -v

# Commit
git add .
git commit -m "module: what you did"
git push origin feature/your-module
```

---

## File Locations

```
modules/your_module.py       # Your code
config/config.yaml           # Configuration
docs/CONTRACTS.md            # Your module's contract
docs/DEVELOPER_GUIDE.md      # Development guide
tests/test_all_modules.py    # Tests
```

---

## Common Commands

### Check Environment
```bash
which python  # Should show .venv/bin/python
python --version  # Should be 3.8+
```

### View Results
```bash
ls results/
cat results/summary_*.csv
cat results/organisms_*.csv
```

### Clean Results
```bash
rm results/*.csv results/*.json
```

### Reinstall Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Module-Specific Quick Starts

### Classification (Person 1)
```bash
# Install TensorFlow
pip install tensorflow

# Download dataset
# (Kaggle WHOI plankton dataset)

# Train or use pretrained model
# Convert to TFLite

# Update classification.py
```

### Dashboard (Person 2)
```bash
# Install Streamlit
pip install streamlit plotly

# Create dashboard app
# dashboard/app.py

# Run dashboard
streamlit run dashboard/app.py
```

### Data Collection (Person 3)
```bash
# Download images to datasets/
# Update acquisition.py to load from files
```

---

## Troubleshooting

### "Module not found"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Pipeline fails"
```bash
python main.py  # Check error message
# Look for "Failed at: module_name"
pytest tests/test_all_modules.py::TestModuleName -v
```

### "Tests fail"
```bash
# Check if you broke a contract
cat docs/CONTRACTS.md
# Fix your module to match contract
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Activate venv | `source .venv/bin/activate` |
| Run pipeline | `python main.py` |
| Run tests | `pytest tests/test_all_modules.py -v` |
| Test module | `pytest tests/test_all_modules.py::TestYourModule -v` |
| View results | `cat results/summary_*.csv` |
| Git commit | `git add . && git commit -m "msg"` |

---

**Read README.md for full documentation**

**Read START_HERE.md for detailed onboarding**

**Read REFERENCE_CARD.md for one-page cheat sheet**
