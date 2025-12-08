# Troubleshooting Guide

**Complete problem-solving reference for all team members**

---

## Table of Contents

1. [Environment Setup Problems](#environment-setup-problems)
2. [Git Problems](#git-problems)
3. [Pipeline Execution Problems](#pipeline-execution-problems)
4. [Module-Specific Problems](#module-specific-problems)
5. [Testing Problems](#testing-problems)
6. [Dependency Problems](#dependency-problems)
7. [Integration Problems](#integration-problems)
8. [Performance Problems](#performance-problems)
9. [Emergency Recovery](#emergency-recovery)

---

## Environment Setup Problems

### Problem: "python: command not found" or "python3: command not found"

**Symptoms**: Can't run Python commands

**Solutions**:

**macOS/Linux**:
```bash
# Check if Python is installed
which python3

# If not found, install
# macOS:
brew install python3

# Ubuntu/Debian:
sudo apt-get install python3 python3-pip
```

**Windows**:
- Download from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation
- Restart terminal

### Problem: "venv module not found"

**Symptoms**: `python3 -m venv .venv` fails

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# Then retry
python3 -m venv .venv
```

### Problem: Virtual environment won't activate

**Symptoms**: `source .venv/bin/activate` doesn't work

**Solutions**:

**macOS/Linux**:
```bash
# Make sure you're in project directory
cd ~/Documents/university/SIH/plank-1

# Try full path
source .venv/bin/activate

# Check if .venv exists
ls -la .venv/
```

**Windows**:
```bash
# Use Windows path
.venv\Scripts\activate

# Or PowerShell
.venv\Scripts\Activate.ps1
```

**Verify activation**:
```bash
# Prompt should show (.venv)
which python
# Should show: .../plank-1/.venv/bin/python
```

### Problem: "pip: command not found"

**Solution**:
```bash
# After activating venv, use
python -m pip install -r requirements.txt

# Or install pip
python -m ensurepip --upgrade
```

### Problem: verify_setup.py fails

**Symptoms**: Some checks don't pass

**Solution - Methodical check**:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Check Python version
python --version
# Should be 3.8 or higher

# 3. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 4. Check imports individually
python -c "import numpy; print('NumPy OK')"
python -c "import cv2; print('OpenCV OK')"
python -c "import yaml; print('PyYAML OK')"

# 5. If any fail, install explicitly
pip install numpy opencv-python pyyaml pytest

# 6. Retry verification
python verify_setup.py
```

---

## Git Problems

### Problem: "fatal: not a git repository"

**Symptoms**: Git commands fail

**Solution**:
```bash
# Check if you're in project directory
pwd
# Should show: .../plank-1

# If not, navigate to it
cd ~/Documents/university/SIH/plank-1

# Verify git repo
ls -la .git
```

### Problem: "Permission denied (publickey)"

**Symptoms**: Can't push to GitHub

**Solution**:

**Option 1: Use HTTPS instead of SSH**
```bash
# Check current remote
git remote -v

# If it shows git@github.com, change to HTTPS
git remote set-url origin https://github.com/your-team/plank-1.git

# Retry push
git push origin feature/your-branch
```

**Option 2: Set up SSH key**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key
# Paste the key

# Test
ssh -T git@github.com
```

### Problem: "Your branch has diverged"

**Symptoms**: Git says your branch and origin have different histories

**Solution**:
```bash
# See what's different
git log --oneline --graph --all

# Option 1: Pull and merge (safe)
git pull origin feature/your-branch

# Option 2: Reset to origin (LOSES local changes!)
git fetch origin
git reset --hard origin/feature/your-branch
```

### Problem: Merge conflicts

**Symptoms**: After `git merge`, you see conflict markers

**Step-by-step solution**:

```bash
# 1. See which files have conflicts
git status
# Look for "both modified:" files

# 2. Open each conflicted file
# You'll see markers like:
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> main

# 3. Edit the file to keep what you want
# Remove the markers (<<<<<<, =======, >>>>>>>)
# Keep your changes, their changes, or combine both

# 4. Test the file
python main.py
pytest tests/test_all_modules.py -v

# 5. Mark as resolved
git add the-fixed-file.py

# 6. Complete merge
git commit -m "module: resolved merge conflict"

# 7. Push
git push origin feature/your-branch
```

**Example - Resolving config conflict**:

**Before (conflicted)**:
```python
<<<<<<< HEAD
class_names = ["Copepod", "Diatom", "Dinoflagellate"]
confidence_threshold = 0.7
=======
class_names = ["Copepod", "Diatom"]
confidence_threshold = 0.8
>>>>>>> main
```

**After (resolved)**:
```python
# Combined both changes
class_names = ["Copepod", "Diatom", "Dinoflagellate"]
confidence_threshold = 0.8  # Use higher threshold
```

### Problem: "fatal: refusing to merge unrelated histories"

**Symptoms**: Can't merge branches

**Solution**:
```bash
# Allow unrelated histories (rare, ask integration lead first)
git merge feature/your-branch --allow-unrelated-histories
```

### Problem: Accidentally committed sensitive data

**Symptoms**: Committed passwords, API keys, etc.

**Solution**:
```bash
# 1. IMMEDIATELY remove from latest commit
git rm --cached config/secrets.yaml
git commit --amend -m "module: removed secrets"

# 2. If already pushed, tell integration lead NOW

# 3. Prevent future issues - add to .gitignore
echo "config/secrets.yaml" >> .gitignore
git add .gitignore
git commit -m "fix: added secrets to gitignore"
```

### Problem: Committed to wrong branch

**Symptoms**: Made changes on main instead of feature branch

**Solution**:
```bash
# 1. Don't panic, don't push!

# 2. Create feature branch from current position
git checkout -b feature/your-module

# 3. Go back to main
git checkout main

# 4. Reset main to origin
git reset --hard origin/main

# 5. Your changes are now on feature branch
git checkout feature/your-module
git push origin feature/your-module
```

---

## Pipeline Execution Problems

### Problem: "Pipeline execution failed at module X"

**Symptoms**: `python main.py` crashes

**Diagnostic steps**:

```bash
# 1. Check which module failed
python main.py
# Look for "Failed at: module_name"

# 2. Check module logs
# Scroll up to see error message

# 3. Test module individually
pytest tests/test_all_modules.py::TestModuleName -v

# 4. Check configuration
cat config/config.yaml
# Verify your module's config section

# 5. Check input data
# If acquisition/data module, check image files exist
ls datasets/

# 6. Check detailed errors
python main.py 2>&1 | tee pipeline_error.log
# Creates error log file
```

### Problem: "No module named 'modules.your_module'"

**Symptoms**: Import error when running pipeline

**Solution**:
```bash
# 1. Check if file exists
ls modules/your_module.py

# 2. Check if __init__.py exists
ls modules/__init__.py

# 3. Make sure you're in project root
pwd
# Should be: .../plank-1

# 4. Reinstall in development mode
pip install -e .

# 5. Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Problem: "Image file not found"

**Symptoms**: Acquisition module can't find images

**Solution**:
```bash
# 1. Check if datasets directory exists
ls datasets/

# 2. Create if missing
mkdir -p datasets

# 3. Verify images are there
ls datasets/*.jpg datasets/*.png

# 4. Check file paths in code
# Open modules/acquisition.py
# Verify paths match actual file locations

# 5. Use absolute paths if needed
import os
dataset_path = os.path.join(os.getcwd(), 'datasets')
```

### Problem: Pipeline runs but produces no output

**Symptoms**: No files in `results/`

**Solution**:
```bash
# 1. Check if results directory exists
ls results/

# 2. Create if missing
mkdir -p results

# 3. Check permissions
ls -la results/
# Should be writable

# 4. Check export module ran
python main.py 2>&1 | grep -i "export"

# 5. Test export module directly
pytest tests/test_all_modules.py::TestExportModule -v
```

---

## Module-Specific Problems

### Classification Module

**Problem**: "Model file not found"

**Solution**:
```bash
# 1. Check if model file exists
ls models/*.tflite

# 2. If missing, check your download
# Verify model file path in classification.py

# 3. Update path in code
MODEL_PATH = os.path.join('models', 'your_model.tflite')

# 4. For development, use stub mode
# Set use_stub = True in config.yaml
```

**Problem**: "Low classification accuracy"

**Diagnostic**:
```python
# Add debug prints in classification.py
def _predict(self, organism_image):
    prediction = model.predict(organism_image)
    print(f"Prediction: {prediction}")  # Debug
    print(f"Max confidence: {np.max(prediction)}")  # Debug
    return prediction
```

**Solutions**:
- Check input image preprocessing matches training
- Verify class names match model output order
- Check confidence threshold (lower if needed)
- Retrain model with better data

**Problem**: "TensorFlow not found"

**Solution**:
```bash
# Install TensorFlow Lite
pip install tensorflow

# Or for Raspberry Pi
pip install tflite-runtime
```

### Dashboard Module

**Problem**: "streamlit: command not found"

**Solution**:
```bash
# 1. Activate venv
source .venv/bin/activate

# 2. Install Streamlit
pip install streamlit plotly

# 3. Verify
streamlit --version

# 4. Run dashboard
streamlit run dashboard/app.py
```

**Problem**: Dashboard shows no data

**Solution**:
```bash
# 1. Check if pipeline ran
ls results/*.csv

# 2. Run pipeline first
python main.py

# 3. Check dashboard loads results
# Add debug in dashboard/app.py
import os
print(os.listdir('results/'))  # Should show CSV files
```

**Problem**: Port already in use

**Solution**:
```bash
# Use different port
streamlit run dashboard/app.py --server.port 8502

# Or kill process on default port
lsof -ti:8501 | xargs kill
```

### Data Collection Module

**Problem**: "Can't download dataset"

**Solution**:
```bash
# 1. Check internet connection
ping google.com

# 2. For Kaggle datasets:
pip install kaggle

# Configure Kaggle API
# Download kaggle.json from kaggle.com/account
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Download dataset
kaggle datasets download -d username/dataset-name

# 3. Unzip
unzip dataset-name.zip -d datasets/
```

**Problem**: Images wrong format

**Solution**:
```python
# Convert images to required format
import cv2
import os

for img_file in os.listdir('datasets/'):
    img = cv2.imread(f'datasets/{img_file}')
    if img is None:
        print(f"Can't read: {img_file}")
        continue

    # Convert to RGB if needed
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    # Resize if needed
    img = cv2.resize(img, (2028, 2028))

    # Save
    cv2.imwrite(f'datasets/processed_{img_file}', img)
```

---

## Testing Problems

### Problem: Tests fail after making changes

**Symptoms**: `pytest` shows failures

**Diagnostic steps**:

```bash
# 1. Run with verbose output
pytest tests/test_all_modules.py -vv

# 2. Run only failing test
pytest tests/test_all_modules.py::TestYourModule::test_name -vv

# 3. Check error message
# Look for assertion details

# 4. Common causes:
# - Changed output structure (broke contract)
# - Missing required fields
# - Wrong data types
# - Value out of range
```

**Solution - Check contract compliance**:

```bash
# 1. Read your module's contract
cat docs/CONTRACTS.md
# Find your module section

# 2. Compare your output
# Add debug print in your module:
def process(self, input_data):
    result = {
        'status': 'success',
        # ... your outputs
    }
    print(f"Output: {result}")  # Debug
    return result

# 3. Run test again
pytest tests/test_all_modules.py::TestYourModule -v

# 4. Fix mismatches
```

### Problem: "AssertionError" with no details

**Solution**:
```bash
# Run with full traceback
pytest tests/test_all_modules.py::TestYourModule -vv --tb=long

# Add print statements in test
# Edit tests/test_all_modules.py temporarily:
def test_output_contract(self):
    result = module.process(input_data)
    print(f"Result: {result}")  # Debug
    assert result['status'] == 'success'
```

### Problem: Tests pass but pipeline fails

**Symptoms**: Individual tests work, `python main.py` fails

**Solution**:
```bash
# Integration issue - modules don't connect properly

# 1. Test module chain
pytest tests/test_all_modules.py::TestIntegration -vv

# 2. Check module outputs match next module's inputs
# Compare in docs/CONTRACTS.md

# 3. Add logging
# In your module:
import logging
logger = logging.getLogger(__name__)

def process(self, input_data):
    logger.info(f"Input: {input_data.keys()}")
    # ... process ...
    logger.info(f"Output: {result.keys()}")
    return result

# 4. Run pipeline
python main.py
# Check if input/output keys match between modules
```

---

## Dependency Problems

### Problem: "ImportError: No module named 'cv2'"

**Solution**:
```bash
# OpenCV installation
pip install opencv-python

# Or upgrade
pip install --upgrade opencv-python

# Verify
python -c "import cv2; print(cv2.__version__)"
```

### Problem: "NumPy version conflict"

**Symptoms**: Errors about numpy array types

**Solution**:
```bash
# Uninstall all numpy
pip uninstall numpy -y

# Reinstall specific version
pip install numpy==1.24.3

# Or match requirements
pip install -r requirements.txt --force-reinstall
```

### Problem: Dependency installation fails on Raspberry Pi

**Symptoms**: pip install fails with compilation errors

**Solution**:
```bash
# Use piwheels (precompiled packages for Pi)
sudo pip3 install --extra-index-url https://www.piwheels.org/simple opencv-python

# Increase swap for compilation
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Problem: Requirements.txt install fails partway

**Solution**:
```bash
# Install one by one to find culprit
cat requirements.txt | while read package; do
    echo "Installing $package"
    pip install "$package" || echo "FAILED: $package"
done

# Skip problematic package
pip install -r requirements.txt --no-deps
pip install problematic-package --no-deps

# Or create clean environment
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Integration Problems

### Problem: Merge breaks tests

**Symptoms**: Tests passed before merge, fail after

**Solution**:
```bash
# 1. Identify what broke
pytest tests/test_all_modules.py -v

# 2. Check git history
git log --oneline -10

# 3. Find problematic commit
git bisect start
git bisect bad HEAD
git bisect good <last-working-commit>
# Git will checkout commits for you to test
pytest tests/test_all_modules.py -v
git bisect good  # or bad
# Repeat until culprit found

# 4. Revert problematic commit
git revert <bad-commit-id>
git push origin main
```

### Problem: Module A works alone, fails with Module B

**Symptoms**: Integration tests fail

**Solution**:
```bash
# Check data flow between modules

# 1. Test module A output
pytest tests/test_all_modules.py::TestModuleA -v

# 2. Capture its output
# Add in test:
result_a = module_a.process(input_a)
print(f"Module A output: {result_a}")

# 3. Check if Module B expects this format
# Read docs/CONTRACTS.md for Module B input

# 4. Common mismatches:
# - Wrong data type (list vs np.array)
# - Missing keys in dictionary
# - Wrong shape for arrays
# - Wrong units (pixels vs micrometers)

# 5. Add adapter if needed
# In pipeline/manager.py:
def execute_pipeline(self):
    result_a = self.modules['a'].process(input_a)

    # Adapt output for module B
    adapted_input = {
        'field_b_expects': result_a['field_a_provides'],
        # ... map fields ...
    }

    result_b = self.modules['b'].process(adapted_input)
```

---

## Performance Problems

### Problem: Pipeline too slow

**Symptoms**: Takes >30 seconds per image

**Diagnostic**:
```python
# Add timing to main.py
import time

start = time.time()
result = module.process(input_data)
elapsed = time.time() - start
print(f"Module took {elapsed:.2f}s")
```

**Solutions by module**:

**Classification slow**:
- Use TFLite instead of full TensorFlow
- Quantize model (INT8 instead of FP32)
- Reduce image resolution before inference
- Batch process organisms

**Segmentation slow**:
- Reduce image resolution
- Use simpler algorithm (threshold instead of watershed)
- Optimize parameters

**Preprocessing slow**:
- Skip unnecessary operations
- Use cv2.fastNlMeansDenoising instead of bilateral filter

### Problem: High memory usage

**Solution**:
```python
# Free memory after each module
import gc

result = module.process(input_data)
del input_data  # Free input
gc.collect()
```

---

## Emergency Recovery

### "Everything is broken, start fresh"

```bash
# 1. Backup your work
cp -r plank-1 plank-1-backup

# 2. Clone fresh copy
cd ~/Documents/university/SIH
git clone https://github.com/your-team/plank-1.git plank-1-fresh
cd plank-1-fresh

# 3. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Verify
python verify_setup.py
pytest tests/test_all_modules.py -v
python main.py

# 5. Copy your work back
cp plank-1-backup/modules/your_module.py plank-1-fresh/modules/

# 6. Test
pytest tests/test_all_modules.py::TestYourModule -v
```

### "Git history is completely messed up"

**Contact integration lead immediately. Don't try to fix yourself.**

They will:
```bash
# Create backup branch
git branch backup-$(date +%Y%m%d)
git push origin backup-$(date +%Y%m%d)

# Reset main to known good state
git checkout main
git reset --hard <last-good-commit>
git push origin main --force  # Only integration lead can do this!

# Team members re-sync
git fetch origin
git reset --hard origin/main
```

---

## Getting Help

### Before Asking

1. ✓ Read error message completely
2. ✓ Search this document
3. ✓ Check `docs/GIT_WORKFLOW.md`
4. ✓ Try solutions above
5. ✓ Search error message online

### How to Ask for Help

**Good format**:
```
Module: Classification
Problem: Model loading fails
Error: FileNotFoundError: models/plankton.tflite
Tried:
  1. Checked file exists - YES it's there
  2. Checked permissions - can read
  3. Used absolute path - same error
Environment:
  - Python 3.9.6
  - TensorFlow 2.14.0
  - macOS 14.0
Code: [paste relevant code snippet]
Full error: [paste complete traceback]
```

**Bad format**:
```
it doesn't work help
```

### Who to Ask

1. **Git problems** → Integration lead (Person 4)
2. **Classification/ML** → ML lead (Person 1)
3. **Dashboard/UI** → Dashboard lead (Person 2)
4. **Data/images** → Data lead (Person 3)
5. **General/pipeline** → Team chat → Project lead

### Escalation

- **Stuck <15 min**: Try yourself
- **Stuck 15-30 min**: Ask team chat
- **Stuck >30 min**: Ask specific person + project lead
- **Critical blocker**: Notify everyone immediately

---

## Diagnostic Commands

### System Check
```bash
# Python
python --version
which python

# Virtual environment
echo $VIRTUAL_ENV

# Git
git --version
git status
git branch

# Project structure
ls -la
tree -L 2 -I '.venv|__pycache__'

# Dependencies
pip list
pip check
```

### Pipeline Check
```bash
# Full verification
python verify_setup.py

# Module imports
python -c "from modules import *"

# Config valid
python -c "import yaml; print(yaml.safe_load(open('config/config.yaml')))"

# Test suite
pytest tests/test_all_modules.py -v

# Pipeline
python main.py
```

### Debug Mode
```bash
# Verbose output
python main.py --verbose

# Python debug mode
python -m pdb main.py

# Logging
export LOG_LEVEL=DEBUG
python main.py
```

---

**Remember**: Most problems have simple solutions. Read error messages carefully, check this guide, and don't hesitate to ask for help!

**Still stuck?** → Post in team chat with error details
