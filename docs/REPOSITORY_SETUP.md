# Repository Setup Guide

**For Integration Lead (Person 4) - Complete GitHub setup instructions**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Create GitHub Repository](#create-github-repository)
3. [Initial Repository Setup](#initial-repository-setup)
4. [Branch Protection Rules](#branch-protection-rules)
5. [Team Access Setup](#team-access-setup)
6. [Share with Team](#share-with-team)
7. [Verification](#verification)

---

## Prerequisites

### What You Need

1. **GitHub Account** - Create at https://github.com if you don't have one
2. **Git installed** - Check: `git --version`
3. **Local project ready** - The plank-1 folder

### Check Your Local Setup

```bash
# Navigate to project
cd ~/Documents/university/SIH/plank-1

# Verify it's not a git repo yet (or has no remote)
git remote -v
# Should show nothing or only local

# Verify all files are present
ls -la
# Should see: modules/, docs/, tests/, config/, etc.
```

---

## Create GitHub Repository

### Step 1: Create New Repository

1. Go to https://github.com
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in details:

**Repository settings:**
```
Repository name: plank-1
Description: Marine Plankton AI Microscopy System - SIH 2025
Visibility: ✓ Private (or Public if allowed)

DO NOT initialize with:
  ☐ README
  ☐ .gitignore
  ☐ license

(We already have these files locally)
```

4. Click **"Create repository"**

### Step 2: Note Repository URL

**You'll see a page with setup instructions. Copy the repository URL:**

**HTTPS** (recommended for beginners):
```
https://github.com/YOUR-USERNAME/plank-1.git
```

**SSH** (if you have keys setup):
```
git@github.com:YOUR-USERNAME/plank-1.git
```

**Save this URL - you'll share it with the team**

---

## Initial Repository Setup

### Step 1: Initialize Local Repository

```bash
# Navigate to project
cd ~/Documents/university/SIH/plank-1

# Check if already initialized
git status

# If "not a git repository", initialize
git init

# Verify
git status
# Should show untracked files
```

### Step 2: Create Placeholder Files

**These ensure empty directories are tracked:**

```bash
# Create .gitkeep files for empty directories
touch models/.gitkeep
touch results/.gitkeep
touch datasets/.gitkeep
touch datasets/raw/.gitkeep
touch datasets/processed/.gitkeep
touch presentation/.gitkeep
touch presentation/screenshots/.gitkeep
touch utils/.gitkeep

# Create datasets README
cat > datasets/README.md << 'EOF'
# Datasets Directory

## Structure

```
datasets/
├── raw/              # Original downloaded images (not in git)
├── processed/        # Preprocessed images (not in git)
├── metadata.csv      # Image information (tracked in git)
└── README.md         # This file
```

## Notes

- Image files are too large for Git and are in .gitignore
- Share images via Google Drive or team shared folder
- Each team member should download separately

## Setup

```bash
# Create directories
mkdir -p datasets/raw datasets/processed

# Download images
# (Instructions will be provided by Person 3)
```
EOF

# Create presentation README
cat > presentation/README.md << 'EOF'
# Presentation Materials

## Contents

- `slides.pdf` or `slides.pptx` - Main presentation
- `demo_script.md` - Demo walkthrough
- `screenshots/` - UI screenshots (not in git, too large)
- `video/` - Recorded demos (not in git, share separately)

## Setup

Person 5 will create these files during development.
EOF
```

### Step 3: Add Files to Git

```bash
# Add all files
git add .

# Check what will be committed
git status

# Verify .gitignore is working (should NOT see):
# - .venv/
# - __pycache__/
# - results/*.csv
# - datasets/raw/
# - Any .jpg or .png files

# If you see these, check .gitignore

# Create initial commit
git commit -m "initial: project foundation with 7-module pipeline

- Complete modular architecture
- 7 modules: acquisition, preprocessing, segmentation, classification, counting, analytics, export
- Comprehensive testing suite (95% pass rate)
- Documentation for team development
- Ready for hackathon Day 1"
```

### Step 4: Connect to GitHub

```bash
# Add remote (use the URL from Step 2 of previous section)
git remote add origin https://github.com/YOUR-USERNAME/plank-1.git

# Verify
git remote -v
# Should show:
# origin  https://github.com/YOUR-USERNAME/plank-1.git (fetch)
# origin  https://github.com/YOUR-USERNAME/plank-1.git (push)

# Push to GitHub
git push -u origin main

# OR if it says "main doesn't exist", you might be on "master"
git branch -M main
git push -u origin main
```

### Step 5: Verify on GitHub

1. Go to https://github.com/YOUR-USERNAME/plank-1
2. You should see:
   - All files and folders
   - README.md displayed on homepage
   - Recent commit message
   - File structure matches local

**If files are missing:**
- Check .gitignore didn't exclude them
- Make sure you did `git add .`
- Try `git push origin main` again

---

## Branch Protection Rules

**Protect main branch from accidental breakage**

### Step 1: Enable Branch Protection

1. Go to repository on GitHub
2. Click **Settings** tab
3. Click **Branches** (left sidebar)
4. Click **Add rule** (or **Add branch protection rule**)

### Step 2: Configure Protection

**Branch name pattern:**
```
main
```

**Settings to enable:**

**Basic protections:**
```
☐ Require a pull request before merging
   (Skip this for hackathon - slows down development)

☐ Require status checks to pass before merging
   (Enable if you set up CI/CD)

☐ Require conversation resolution before merging
   (Optional)

☐ Require signed commits
   (Skip for hackathon)

☐ Require linear history
   (Recommended - cleaner history)

☑ Do not allow bypassing the above settings
   (But add yourself as exception)

☐ Restrict who can push to matching branches
   (Skip - you want flexibility during hackathon)

☐ Allow force pushes
   (Keep disabled - dangerous!)

☑ Allow deletions
   (Keep disabled - prevents accidents)
```

**Recommended minimal setup for hackathon:**
- ☐ All options disabled (for speed)
- OR only enable "Require linear history"

**Click "Create" or "Save changes"**

### Alternative: No Branch Protection

**For maximum speed during hackathon:**
- Skip branch protection entirely
- Trust team to be careful
- Integration lead has full control

---

## Team Access Setup

### Step 1: Add Collaborators

**If using personal GitHub account:**

1. Go to repository Settings
2. Click **Collaborators** (left sidebar)
3. Click **Add people**
4. Enter each team member's GitHub username or email
5. Select role: **Write** (can push) or **Admin** (full control)
6. Click **Add**

**Each team member will receive email invitation**

### Step 2: Team Member Acceptance

**Each team member must:**
1. Check email
2. Click invitation link
3. Accept invitation
4. Now they can clone repository

### Alternative: Organization Repository

**If creating under organization:**

1. Create organization first: https://github.com/organizations/new
2. Create repository under organization
3. Add team members to organization
4. Set permissions per team

---

## Share with Team

### Step 1: Prepare Team Message

**Send this to all team members:**

```
🚀 GitHub Repository Ready!

Repository: https://github.com/YOUR-USERNAME/plank-1.git

Setup Instructions:

1. Accept GitHub invitation (check email)

2. Clone repository:
   cd ~/Documents/university/SIH/
   git clone https://github.com/YOUR-USERNAME/plank-1.git
   cd plank-1

3. Setup environment:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

4. Verify:
   python verify_setup.py
   pytest tests/test_all_modules.py -v

5. Create your branch:
   git checkout -b feature/YOUR-MODULE
   (classification, dashboard, data-collection, or presentation)

6. Push your branch:
   git push -u origin feature/YOUR-MODULE

Documentation:
- Start here: START_HERE.md
- Git guide: docs/GIT_WORKFLOW.md
- Your module: docs/MODULE_DEVELOPMENT.md
- Problems: docs/TROUBLESHOOTING.md

Questions? Ask in team chat.

Let's build something amazing! 🔬
```

### Step 2: Share Supplementary Materials

**Large files that can't be in Git:**

**Option A: Google Drive**
```
1. Create shared folder
2. Upload:
   - Dataset images (if Person 3 has them)
   - Model files (if Person 1 has them)
   - Presentation screenshots
3. Share folder link with team
```

**Option B: Dropbox, OneDrive, etc.**
- Same process as Google Drive

**Share in team chat:**
```
📦 Large Files

Google Drive: [LINK]

Contents:
- datasets/ - Plankton images (Person 3)
- models/ - ML models (Person 1)
- presentation/ - Screenshots (Person 5)

Download what you need for your module.
```

---

## Verification

### Step 1: Clone Fresh Copy (As If You're a Team Member)

```bash
# Navigate to different directory
cd ~/Desktop

# Clone
git clone https://github.com/YOUR-USERNAME/plank-1.git plank-1-test

# Enter
cd plank-1-test

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify
python verify_setup.py
pytest tests/test_all_modules.py -v
python main.py

# Check results
ls results/
cat results/summary_*.csv
```

**Expected:**
- ✓ Clone successful
- ✓ Dependencies install
- ✓ Verification passes
- ✓ Tests pass (18/19)
- ✓ Pipeline runs
- ✓ Results generated

**If all pass: Repository setup successful!**

### Step 2: Test Branch Creation

```bash
# Create test branch
git checkout -b feature/test

# Make small change
echo "# Test" >> TEST.md

# Commit
git add TEST.md
git commit -m "test: verification commit"

# Push
git push -u origin feature/test

# Verify on GitHub
# Should see new branch in dropdown
```

### Step 3: Test Team Member Can Clone

**Ask one team member to:**
1. Accept invitation
2. Clone repository
3. Run setup
4. Report if any issues

---

## Repository Structure on GitHub

**After setup, your repository should look like:**

```
YOUR-USERNAME/plank-1/
├── .github/              # (Optional: CI/CD workflows)
├── archive/              # Old documentation
├── config/
│   └── config.yaml
├── dashboard/            # (Will be populated by Person 2)
├── datasets/
│   ├── .gitkeep
│   ├── raw/.gitkeep
│   ├── processed/.gitkeep
│   └── README.md
├── docs/
│   ├── CONTRACTS.md
│   ├── DEVELOPER_GUIDE.md
│   ├── GIT_WORKFLOW.md
│   ├── MODULE_DEVELOPMENT.md
│   ├── REPOSITORY_SETUP.md
│   ├── TESTING.md
│   ├── TIMELINE.md
│   └── TROUBLESHOOTING.md
├── examples/
├── models/
│   └── .gitkeep
├── modules/
│   ├── __init__.py
│   ├── acquisition.py
│   ├── analytics.py
│   ├── base.py
│   ├── classification.py
│   ├── counting.py
│   ├── export.py
│   ├── preprocessing.py
│   └── segmentation.py
├── pipeline/
│   ├── __init__.py
│   ├── manager.py
│   └── validators.py
├── presentation/
│   ├── .gitkeep
│   └── README.md
├── results/
│   └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_all_modules.py
├── utils/
│   └── .gitkeep
├── .gitignore
├── main.py
├── README.md
├── QUICKSTART.md
├── REFERENCE_CARD.md
├── requirements.txt
├── START_HERE.md
├── TESTING_COMPLETE.md
└── verify_setup.py
```

---

## Branch Strategy

### Main Branch

**Purpose**: Always working, deployable code

**Rules**:
- Integration lead merges into main
- Must pass all tests before merge
- Never commit directly (except integration lead)

### Feature Branches

**Pattern**: `feature/module-name`

**Branches to create:**
```
feature/classification      (Person 1)
feature/dashboard           (Person 2)
feature/data-collection     (Person 3)
feature/presentation        (Person 5)
```

**Integration lead doesn't need a branch** (works on main)

### Workflow

```
main ────────────────────────────> (always stable)
  │
  ├── feature/classification ─────> Person 1's work
  │
  ├── feature/dashboard ──────────> Person 2's work
  │
  ├── feature/data-collection ────> Person 3's work
  │
  └── feature/presentation ───────> Person 5's work

Every 4 hours: Merge features back to main
```

---

## Common Issues

### Problem: "fatal: remote origin already exists"

```bash
# Remove existing remote
git remote remove origin

# Add correct one
git remote add origin https://github.com/YOUR-USERNAME/plank-1.git
```

### Problem: "failed to push some refs"

```bash
# Someone else pushed first
git pull origin main --rebase
git push origin main
```

### Problem: "Permission denied (publickey)"

```bash
# Use HTTPS instead
git remote set-url origin https://github.com/YOUR-USERNAME/plank-1.git
```

### Problem: Team member can't clone

**Check:**
1. Did they accept invitation?
2. Is repository private? (must be collaborator)
3. Are they using correct URL?
4. Try HTTPS instead of SSH

### Problem: .venv was committed to Git

```bash
# Remove from git (not from disk)
git rm -r --cached .venv

# Make sure it's in .gitignore
echo ".venv/" >> .gitignore

# Commit
git add .gitignore
git commit -m "fix: removed .venv from git tracking"
git push origin main

# Tell team to pull
```

---

## Optional: CI/CD Setup

**For automatic testing on every push**

### GitHub Actions (Recommended)

**Create `.github/workflows/test.yml`:**

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest tests/test_all_modules.py -v
```

**Commit and push:**
```bash
git add .github/
git commit -m "ci: added GitHub Actions for automated testing"
git push origin main
```

**Now every push will automatically run tests!**

---

## Checklist

**Before sharing with team:**

- [ ] Repository created on GitHub
- [ ] Initial code pushed to main
- [ ] All files present (check structure above)
- [ ] .gitignore working (no .venv, results, etc.)
- [ ] README displays correctly on GitHub
- [ ] Branch protection configured (or skipped intentionally)
- [ ] Team members added as collaborators
- [ ] Repository URL copied
- [ ] Fresh clone tested
- [ ] verify_setup.py passes
- [ ] Tests pass (18/19)
- [ ] Pipeline runs successfully
- [ ] Team message prepared
- [ ] Large files shared via Drive (if applicable)

**Ready to share! Send team message.**

---

## Team Communication

### Initial Message Template

```
🎉 Repository Setup Complete!

✓ GitHub repository created
✓ All code pushed
✓ Tests passing (95%)
✓ Pipeline working
✓ Documentation complete
✓ Ready for parallel development

Next Steps:

1. Check your email for GitHub invitation
2. Follow setup instructions (sent separately)
3. Create your feature branch
4. Start developing your module

Integration Checkpoints:
- Hour 4: Status check
- Hour 8: First integration
- Hour 12: Second integration
- Hour 16: End of Day 1

Let's build this! Questions in team chat.
```

---

## Final Notes

### For Integration Lead

**Your role is critical:**
- Keep main branch working always
- Merge carefully, test after each merge
- Help team with Git issues
- Communicate frequently

**You are the gatekeeper - take it seriously!**

### For Team

**Respect the integration lead:**
- Don't push to main directly
- Keep your branch clean
- Test before pushing
- Communicate progress

**Together you'll build something amazing!**

---

**Questions?** Check `docs/GIT_WORKFLOW.md` or ask in team chat.

**Ready?** Execute the steps above and share with your team!
