# START HERE - 5-Day Hackathon Guide

**Updated for**: Smart India Hackathon - 5 days to working demo

**Current Status**: Complete foundation ready for parallel team development

---

## What You Have

A complete, working pipeline with:

✅ All 7 modules with standard interfaces
✅ End-to-end execution (runs right now)
✅ Example outputs (CSV, JSON)
✅ Hackathon-optimized documentation
✅ Ready for 5-person parallel development

---

## First 30 Minutes - Project Lead

### Minute 1-5: Verify Setup

```bash
cd plank-1
source .venv/bin/activate
python verify_setup.py
```

Expected: All 6 checks pass

### Minute 5-10: Run Pipeline

```bash
python main.py
```

Expected: See results in `results/` folder

### Minute 10-15: Review Documentation

Critical files for hackathon:

1. **HACKATHON_PLAN.md** - Day-by-day breakdown
2. **TEAM_QUICKSTART.md** - 15-min team onboarding
3. **docs/MODULE_ASSIGNMENTS_HACKATHON.md** - Assign modules to team

### Minute 15-25: Assign Modules

Use `docs/MODULE_ASSIGNMENTS_HACKATHON.md`

Recommended for team of 5:
- Person 1: Classification (ML) - CRITICAL PATH
- Person 2: Acquisition + Dashboard
- Person 3: Dashboard + Export
- Person 4: Preprocessing + Segmentation optimization
- Person 5: Integration + Testing

### Minute 25-30: Team Kickoff

Share with team:
1. Read `TEAM_QUICKSTART.md` (15 min)
2. Set up environment (5 min)
3. Start coding (Hour 1)

---

## Documentation Structure (Hackathon-Optimized)

### For Everyone

**TEAM_QUICKSTART.md** (15 min read)
- Environment setup
- Module assignment
- Testing workflow
- Git workflow

### For Planning

**HACKATHON_PLAN.md** (30 min read, reference throughout)
- Day-by-day breakdown
- Hour-by-hour tasks
- Integration checkpoints
- Risk mitigation

### For Development

**docs/DEVELOPER_GUIDE.md** (reference as needed)
- Module contracts (input/output)
- Development guidelines
- Testing examples

**docs/MODULE_ASSIGNMENTS_HACKATHON.md** (reference for your module)
- Specific deliverables per day
- Fast track options
- Success criteria

### For Reference

**README_HACKATHON.md**
- Project overview
- Architecture
- Usage

---

## Timeline Overview

### Day 1 (Setup + Parallel Dev)
**Goal**: Everyone coding on their module

**Hour 0-1**: Environment setup
**Hour 1-8**: Parallel development
**Hour 8**: First integration checkpoint

**End State**: Main pipeline still works, everyone has committed code

### Day 2 (Integration)
**Goal**: All modules working together

**Morning**: Integrate classification and dashboard
**Afternoon**: Full system test, first demo

**End State**: Working demo from image to results

### Day 3 (Polish)
**Goal**: Professional demo

**Morning**: Fix critical bugs
**Afternoon**: Polish UI and outputs

**End State**: Demo-ready system, no crashes

### Day 4 (Testing)
**Goal**: Comprehensive testing

**Morning**: Test all scenarios
**Afternoon**: Prepare presentation, rehearse

**End State**: Tested system, presentation ready

### Day 5 (Demo)
**Goal**: Deliver and impress

**Morning**: Final polish
**Afternoon**: Present to judges

**End State**: Code submitted, demo delivered

---

## Critical Success Factors

### Must Have (Required for demo)
- [ ] Pipeline runs without crashes
- [ ] Classifies organisms (>60% accuracy OK)
- [ ] Shows diversity metrics
- [ ] Exports CSV
- [ ] Dashboard displays results

### Should Have (Better scoring)
- [ ] Classification >70% accuracy
- [ ] Professional UI
- [ ] <30s processing time
- [ ] Good documentation

### Nice to Have (Bonus points)
- [ ] Real camera integration
- [ ] Batch processing
- [ ] Bloom detection working

---

## Module Priorities

**CRITICAL PATH** (blocks demo):
1. Classification - Needs trained model
   - Assign best ML person
   - Start Day 1, finish Day 2
   - Fallback: Pretrained model

**HIGH** (improves demo significantly):
2. Dashboard - User interface
   - Start Day 2, finish Day 3
   - Streamlit-based, simple

3. Acquisition - Image input
   - File upload acceptable
   - Real camera is bonus

**MEDIUM** (polish):
4. Optimization - Make it faster/better
5. Testing - Ensure reliability

---

## Communication Structure

### Standup (Every 4 hours)
- When: Hours 0, 4, 8 each day
- Duration: 5 minutes total
- Format: "Did X, doing Y, blocked on Z"

### Integration Checkpoints
- Day 1 Hour 8: First merge
- Day 2 Hour 8: Full integration
- Day 3+: Continuous

### Channels
- `#general`: General discussion
- `#help`: Immediate blockers
- `#integration`: Merge requests

---

## Git Workflow

### Individual Work
```bash
# Create your branch
git checkout -b feature/your-module

# Work and commit frequently
git add .
git commit -m "module: what you did"
git push origin feature/your-module
```

### Integration (Integration Lead Only)
```bash
# Merge one module at a time
git checkout main
git merge feature/classification
python main.py  # Test
# If works, continue
git push origin main
```

### Rules
- Never commit directly to main
- Always test before requesting merge
- Don't change other modules without asking
- Don't modify contracts without team discussion

---

## Quick Commands

### Setup (Once)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Daily
```bash
source .venv/bin/activate
python verify_setup.py  # Check everything works
python main.py          # Run pipeline
```

### Testing
```bash
python examples/test_individual_module.py  # Test your module
pytest tests/ -v                           # Run unit tests
```

### Git
```bash
git status                    # Check what changed
git add .                     # Stage changes
git commit -m "msg"          # Commit
git push origin feature/name # Push
```

---

## Backup Plans

### If Classification Fails
- Use pretrained model (Kaggle)
- Use rule-based classifier
- Focus on architecture for demo

### If Camera Unavailable
- Use dataset images
- Implement file upload
- Show as "future hardware"

### If Dashboard Breaks
- Demo with CSV in Excel
- Use Jupyter notebook
- Focus on pipeline, not UI

### If Time Runs Out
- Cut scope to MVP
- Demo what works
- Document remaining work

---

## Success Checklist

### By End of Day 1
- [ ] All team members have environment set up
- [ ] Everyone has committed code to their branch
- [ ] Main pipeline still runs
- [ ] Classification training started

### By End of Day 2
- [ ] Classification integrated
- [ ] Dashboard shows basic results
- [ ] Full pipeline tested
- [ ] Demo script drafted

### By End of Day 3
- [ ] No critical bugs
- [ ] UI looks professional
- [ ] Presentation slides ready

### By End of Day 4
- [ ] Comprehensive testing done
- [ ] Demo rehearsed 3+ times
- [ ] Known issues documented
- [ ] Backup plan ready

### By End of Day 5
- [ ] Code submitted
- [ ] Demo delivered
- [ ] Judges impressed
- [ ] Team celebrates

---

## What to Read When

### Right Now (Project Lead)
1. This file (you're reading it)
2. HACKATHON_PLAN.md (skim Day 1 section)
3. docs/MODULE_ASSIGNMENTS_HACKATHON.md (prepare assignments)

### Team Kickoff (Everyone)
1. TEAM_QUICKSTART.md
2. Your module section in MODULE_ASSIGNMENTS_HACKATHON.md
3. Your module contract in DEVELOPER_GUIDE.md

### During Development (As Needed)
- DEVELOPER_GUIDE.md (when you need contract details)
- HACKATHON_PLAN.md (check daily tasks)
- examples/test_individual_module.py (when testing)

### Before Demo (Day 4-5)
- HACKATHON_PLAN.md (demo script section)
- README_HACKATHON.md (for presentation context)

---

## Key Reminders

**Speed Over Perfection**
- Working demo beats perfect code
- Ship MVP, iterate based on feedback
- Don't over-engineer

**Communicate Constantly**
- Standup every 4 hours
- Post blockers immediately
- Ask for help early

**Test Before Merging**
- Always run `python main.py` after changes
- Don't break main branch
- Integration lead tests before accepting merge

**Respect Contracts**
- Don't change module interfaces
- Add optional fields if needed
- Discuss contract changes with team

**Have Fun**
- This is a hackathon, not a job
- Help each other
- Celebrate small wins
- Learn and enjoy

---

## Next Steps

### Right Now
1. Read this file completely
2. Run `python main.py` to see it work
3. Read HACKATHON_PLAN.md Day 1 section
4. Assign modules to team

### Team Meeting (Hour 0)
1. Share TEAM_QUICKSTART.md with team
2. Everyone sets up environment (15 min)
3. Assign modules
4. Start coding

### First Standup (Hour 4)
- Quick check: Everyone making progress?
- Any blockers?
- On track for Hour 8 integration?

---

## Contact During Hackathon

**Project Lead**: [Your name]
**Integration Lead**: [Person 5 name]
**ML Lead**: [Person 1 name]

**Emergency**: If something breaks main branch, ping integration lead immediately

---

**You have 5 days. The foundation is ready. Go build something amazing.**

**Current time investment**: 1 hour to set up foundation
**Your time investment**: 5 days to working demo
**Judge time investment**: 10 minutes to be impressed

Make those 10 minutes count. Good luck!
