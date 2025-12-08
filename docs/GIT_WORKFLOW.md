# Git Workflow Guide for Team Members

**For beginners and everyone on the team**

This guide will teach you everything you need to work on your module without conflicts.

---

## Table of Contents

1. [Git Basics - What You Need to Know](#git-basics)
2. [Initial Setup - One Time Only](#initial-setup)
3. [Daily Workflow - Every Day](#daily-workflow)
4. [Working on Your Module](#working-on-your-module)
5. [Merging Your Work](#merging-your-work)
6. [Common Problems and Solutions](#common-problems)
7. [Quick Command Reference](#quick-reference)

---

## Git Basics

### What is Git?

Git is a version control system that:
- Tracks all changes to your code
- Lets multiple people work on the same project
- Prevents people from overwriting each other's work
- Lets you go back to previous versions if something breaks

### Key Concepts

**Repository (Repo)**: The project folder with all code and history

**Branch**: A separate "copy" where you work without affecting others
- `main` branch: The stable, working version
- `feature/your-module` branch: Your personal workspace

**Commit**: A saved snapshot of your changes with a message

**Push**: Upload your changes to GitHub

**Pull**: Download changes from GitHub

**Merge**: Combine your changes with the main branch

---

## Initial Setup

### Step 1: Install Git

**macOS**:
```bash
# Check if already installed
git --version

# If not installed, install via Homebrew
brew install git
```

**Linux**:
```bash
sudo apt-get install git
```

**Windows**:
Download from https://git-scm.com/download/win

### Step 2: Configure Git (One Time)

```bash
# Set your name (will appear in commits)
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"

# Verify settings
git config --list
```

### Step 3: Clone the Repository

**Once the integration lead creates the GitHub repo, they'll share a URL like:**
`https://github.com/your-team/plank-1.git`

**Clone it to your computer:**
```bash
# Navigate to where you want the project
cd ~/Documents/university/SIH/

# Clone the repository
git clone https://github.com/your-team/plank-1.git

# Enter the project directory
cd plank-1
```

### Step 4: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

**IMPORTANT**: Always activate `.venv` before working!

---

## Daily Workflow

### Every Time You Start Working

```bash
# 1. Navigate to project
cd ~/Documents/university/SIH/plank-1

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Make sure you're on your branch
git status

# 4. Get latest changes from GitHub
git pull origin main
```

### Every Time You Finish Working

```bash
# 1. Check what you changed
git status

# 2. Add your changes
git add .

# 3. Commit with a message
git commit -m "classification: improved model accuracy"

# 4. Push to GitHub
git push origin feature/your-module-name
```

---

## Working on Your Module

### Step 1: Create Your Branch (First Time Only)

**Each team member works on a separate branch:**

```bash
# Check you're on main branch
git checkout main

# Create your branch
# Use one of these based on your assignment:
git checkout -b feature/classification      # Person 1
git checkout -b feature/dashboard           # Person 2
git checkout -b feature/data-collection     # Person 3
git checkout -b feature/integration         # Person 4
git checkout -b feature/presentation        # Person 5

# Verify you're on your branch
git branch
# Should show * next to your branch name
```

### Step 2: Find Your Module File

**Person 1 (Classification)**:
- File: `modules/classification.py`
- Tests: `tests/test_all_modules.py::TestClassificationModule`
- Contract: `docs/CONTRACTS.md` (Module 4)

**Person 2 (Dashboard)**:
- Directory: `dashboard/`
- Create: `dashboard/app.py`
- Install: `pip install streamlit plotly`

**Person 3 (Data Collection)**:
- File: `modules/acquisition.py`
- Directory: `datasets/` (create this)
- Update: `_capture_image()` method

**Person 4 (Integration)**:
- Monitor: All branches
- Merge: Everyone's code
- File: `docs/INTEGRATION.md` (read this)

**Person 5 (Presentation)**:
- Directory: `presentation/` (create this)
- Files: Slides, demo script, screenshots

### Step 3: Make Changes

**IMPORTANT RULES**:

1. **ONLY modify your assigned files**
   - Person 1: Only touch `modules/classification.py`
   - Person 2: Only work in `dashboard/`
   - Don't edit other people's modules!

2. **NEVER change module contracts**
   - Don't change the input/output structure
   - See `docs/CONTRACTS.md` for your module's contract
   - Ask integration lead if contract needs to change

3. **Test frequently**
```bash
# Test your specific module
pytest tests/test_all_modules.py::TestYourModule -v

# Test full pipeline
python main.py

# Both should pass before committing
```

### Step 4: Commit Your Changes

**Good commit workflow:**

```bash
# 1. Check what changed
git status
# Shows files you modified

# 2. See exact changes
git diff
# Shows line-by-line changes

# 3. Add files to commit
git add modules/classification.py
# OR add everything:
git add .

# 4. Commit with descriptive message
git commit -m "classification: added TFLite model integration"

# 5. Push to GitHub
git push origin feature/classification
```

**Good commit messages:**
```
classification: integrated MobileNetV2 model
classification: improved accuracy to 72%
dashboard: added file upload UI
dashboard: created results visualization
data: added 25 test images from WHOI dataset
integration: merged classification and dashboard branches
presentation: completed slide deck
```

**Bad commit messages:**
```
updated stuff
fixed bug
changes
asdf
work in progress
```

---

## Merging Your Work

### When to Merge

**Integration Checkpoints:**
- Hour 8 (Day 1): First integration - basic functionality
- Hour 16 (Day 1): Second integration - complete features
- Hour 24 (Day 2): Third integration - polish
- Ongoing: Whenever you complete a feature

### How to Merge (For Integration Lead - Person 4)

**The integration lead will:**

```bash
# 1. Make sure main is up to date
git checkout main
git pull origin main

# 2. Merge one person's branch at a time
git merge feature/classification

# 3. Test immediately
pytest tests/test_all_modules.py -v
python main.py

# 4. If tests pass, push to main
git push origin main

# 5. Notify the team
# Post in group chat: "Classification merged to main, pull latest"

# 6. Repeat for next person
git merge feature/dashboard
# ... test again
```

### How to Get Latest Code (For Everyone Else)

**When integration lead merges someone's work:**

```bash
# 1. Commit your current work first
git add .
git commit -m "classification: work in progress"

# 2. Switch to main branch
git checkout main

# 3. Pull latest changes
git pull origin main

# 4. Go back to your branch
git checkout feature/classification

# 5. Merge main into your branch
git merge main

# 6. If there are conflicts, see "Handling Merge Conflicts" below
```

---

## Common Problems and Solutions

### Problem 1: "Your branch is behind 'origin/main'"

**What it means**: Someone else pushed changes to GitHub

**Solution**:
```bash
git pull origin main
```

### Problem 2: "Your branch is ahead of 'origin/main'"

**What it means**: You have local commits not yet pushed

**Solution**:
```bash
git push origin feature/your-branch
```

### Problem 3: Merge Conflicts

**What it means**: You and someone else changed the same lines

**Example conflict**:
```python
<<<<<<< HEAD
# Your changes
class_names = ["Copepod", "Diatom", "Dinoflagellate"]
=======
# Their changes
class_names = ["Copepod", "Diatom", "Ciliate"]
>>>>>>> main
```

**Solution**:
```bash
# 1. Open the conflicted file in your editor
# Look for <<<<<<< markers

# 2. Decide what to keep
# Option A: Keep your changes (remove their lines and markers)
# Option B: Keep their changes (remove your lines and markers)
# Option C: Keep both (combine them thoughtfully)

# 3. Remove the conflict markers
class_names = ["Copepod", "Diatom", "Dinoflagellate", "Ciliate"]

# 4. Add the resolved file
git add modules/classification.py

# 5. Complete the merge
git commit -m "classification: resolved merge conflict in class_names"
```

### Problem 4: "I committed to main by mistake!"

**Solution**:
```bash
# 1. Create your feature branch now
git checkout -b feature/classification

# 2. Push it
git push origin feature/classification

# 3. Tell integration lead to handle main branch cleanup
```

### Problem 5: "I want to undo my last commit"

**Solution**:
```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and discard changes (CAREFUL!)
git reset --hard HEAD~1
```

### Problem 6: "I broke something and want to go back"

**Solution**:
```bash
# See recent commits
git log --oneline

# Go back to a specific commit (copy the commit ID)
git checkout abc1234

# Or discard all changes since last commit
git reset --hard HEAD
```

### Problem 7: "Git says I have changes but I don't see them"

**Solution**:
```bash
# See what changed
git status

# See exact changes
git diff

# If you want to discard these changes
git checkout -- .
```

### Problem 8: ".venv folder causing problems"

**Solution**: The `.gitignore` file should prevent this, but if you accidentally added it:
```bash
# Remove from git (not from your computer)
git rm -r --cached .venv

# Add to .gitignore if not there
echo ".venv/" >> .gitignore

# Commit
git add .gitignore
git commit -m "fix: removed .venv from git tracking"
```

---

## Quick Reference

### Daily Commands

```bash
# Start work
cd plank-1
source .venv/bin/activate
git status

# Save work
git add .
git commit -m "module: what you did"
git push origin feature/your-branch

# Get latest
git pull origin main

# Test
pytest tests/test_all_modules.py::TestYourModule -v
python main.py
```

### Branch Commands

```bash
# See all branches
git branch

# Switch branches
git checkout branch-name

# Create new branch
git checkout -b feature/new-branch

# Delete branch (after merged)
git branch -d feature/old-branch
```

### Status Commands

```bash
# What changed?
git status

# What exactly changed?
git diff

# Commit history
git log --oneline

# Who changed this line?
git blame filename.py
```

### Undo Commands

```bash
# Discard changes in one file
git checkout -- filename.py

# Discard all changes
git reset --hard HEAD

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## Best Practices

### DO:

✓ Commit frequently (every 30-60 minutes)
✓ Write clear commit messages
✓ Pull from main before starting work
✓ Test before committing
✓ Ask for help if stuck
✓ Communicate in team chat

### DON'T:

✗ Commit broken code
✗ Push directly to main (except integration lead)
✗ Change other people's modules
✗ Change module contracts without discussion
✗ Commit `.venv/` or `results/` directories
✗ Use `git push --force` (NEVER!)

---

## Workflow Summary

### For Module Developers (Persons 1, 2, 3, 5)

**Day 1:**
```bash
# Hour 0: Setup
git clone <repo-url>
cd plank-1
source .venv/bin/activate
pip install -r requirements.txt
git checkout -b feature/your-module

# Hours 1-8: Develop
# ... make changes to your module ...
git add .
git commit -m "module: what you did"
git push origin feature/your-module

# Hour 8: Integration checkpoint
# Wait for integration lead to merge
git checkout main
git pull origin main
git checkout feature/your-module
git merge main

# Hours 8-16: Continue development
# ... repeat commit/push cycle ...
```

### For Integration Lead (Person 4)

**Every 4 hours:**
```bash
# Merge each person's branch
git checkout main
git pull origin main
git merge feature/classification
pytest tests/test_all_modules.py -v  # Must pass
python main.py  # Must work
git push origin main

# Notify team
# "Classification merged, everyone pull latest"

# Repeat for other branches
```

---

## Help and Support

### Getting Help

1. **Check this document** first
2. **Check `docs/TROUBLESHOOTING.md`** for technical problems
3. **Ask in team chat** - describe what you tried
4. **Ask integration lead** (Person 4) for Git problems
5. **Share error messages** - copy full error, not just "it doesn't work"

### Useful Resources

- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **GitHub Docs**: https://docs.github.com/en/get-started
- **Visualizing Git**: https://git-school.github.io/visualizing-git/

---

## Emergency Procedures

### "Everything is broken!"

```bash
# 1. Don't panic
# 2. Check if you have uncommitted work
git status

# 3. If you want to save work
git stash  # Temporarily saves changes

# 4. Get clean copy of main
git checkout main
git pull origin main

# 5. Verify system works
python verify_setup.py
pytest tests/test_all_modules.py -v
python main.py

# 6. If main works, your branch has the problem
# Create new branch from main
git checkout -b feature/your-module-fixed

# 7. Restore your saved work if needed
git stash pop

# 8. Ask for help in team chat
```

### "I pushed broken code to main!"

```bash
# 1. Immediately notify team in chat
# 2. Tell integration lead
# 3. They will revert your commit:
git revert <commit-id>
git push origin main
```

---

## Standups and Communication

### Every 4 Hours (Hours 0, 4, 8, 12, 16)

**Post in team chat:**
```
Person 1 (Classification):
  ✓ Did: Integrated TFLite model
  → Doing: Testing accuracy
  ⚠ Blocked: Need test images from Person 3

Person 2 (Dashboard):
  ✓ Did: Created file upload UI
  → Doing: Adding visualization charts
  ⚠ Blocked: None
```

### When Blocked (>15 minutes)

**Post in #help channel:**
```
Module: Classification
Problem: Model loading fails with error "XYZ"
Tried:
  - Reinstalled TensorFlow
  - Checked model file exists
  - Read docs/TROUBLESHOOTING.md
Error message: [paste full error]
```

---

**Remember**: Git is a safety net, not a scary monster. Commit frequently, communicate clearly, and you'll be fine!

**Questions?** Ask your integration lead (Person 4) or check `docs/TROUBLESHOOTING.md`
