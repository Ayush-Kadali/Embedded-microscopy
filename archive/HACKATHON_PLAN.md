# 5-Day Hackathon Plan - Marine Plankton AI Microscopy

**Goal**: Working demo in 5 days, polish based on judge feedback after

**Strategy**: Maximum parallel work, integrate continuously, MVP first

---

## Day 1: Setup & Parallel Development Kickoff (8 hours)

### Hour 0-1: Environment Setup (Everyone)
```bash
cd plank-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python verify_setup.py
python main.py
```

**Deliverable**: Everyone has pipeline running

### Hour 1-2: Module Assignment & Contract Review

| Person | Module | Priority | Deliverable |
|--------|--------|----------|-------------|
| Person 1 | Classification + Model | CRITICAL | Working classifier stub with better accuracy |
| Person 2 | Acquisition | HIGH | Real camera OR better synthetic images |
| Person 3 | Dashboard | HIGH | Basic Streamlit dashboard |
| Person 4 | Preprocessing + Segmentation | MEDIUM | Optimize existing code |
| Person 5 | Testing + Integration | MEDIUM | Continuous integration, fix bugs |

**Deliverable**: Everyone knows their module contract

### Hour 2-8: Parallel Development Sprint

**Classification Team (Person 1)**:
- [ ] Download pre-trained plankton dataset (Kaggle/WHOI)
- [ ] Use transfer learning (MobileNetV2 pre-trained)
- [ ] Train for 2-3 hours max
- [ ] Export to TFLite
- [ ] Replace stub in classification.py

**Acquisition Team (Person 2)**:
- Option A: Integrate real camera if available
- Option B: Use better synthetic images from dataset
- [ ] Update acquisition.py
- [ ] Test image quality
- [ ] Ensure proper metadata

**Dashboard Team (Person 3)**:
- [ ] Install Streamlit
- [ ] Create basic dashboard layout
- [ ] Read CSV files from results/
- [ ] Show: counts table, diversity metrics, simple bar chart
- [ ] No map needed for Day 1

**Optimization Team (Person 4)**:
- [ ] Profile current preprocessing
- [ ] Optimize segmentation parameters
- [ ] Test with different image types
- [ ] Document optimal settings

**Integration Team (Person 5)**:
- [ ] Set up Git workflow
- [ ] Create integration branch
- [ ] Test each module as it's updated
- [ ] Fix any contract violations
- [ ] Keep main.py working always

**End of Day 1**:
- Classification model training started or using transfer learning
- Dashboard shows basic results
- Pipeline still runs end-to-end

---

## Day 2: Integration & First Demo (8 hours)

### Morning (Hour 0-4): Module Integration

**Classification**:
- [ ] Finish model training
- [ ] Integrate TFLite model into classification.py
- [ ] Test accuracy on validation set
- [ ] If accuracy low, use confidence boosting

**Dashboard**:
- [ ] Add time-series plot (if historical data)
- [ ] Add organism size distribution chart
- [ ] Add export button for results
- [ ] Polish UI

**Acquisition**:
- [ ] Finalize image source
- [ ] Test with real microscope if available
- [ ] Otherwise use dataset images
- [ ] Ensure metadata is correct

**Integration**:
- [ ] Merge all changes
- [ ] Run full pipeline with new modules
- [ ] Fix any integration bugs
- [ ] Test with 5-10 sample images

### Afternoon (Hour 4-8): First Internal Demo

**Prepare Demo**:
- [ ] Run pipeline on 3 diverse images
- [ ] Generate all outputs
- [ ] Prepare 2-minute demo script
- [ ] Document any known issues

**Demo Script**:
1. Show image acquisition (or upload)
2. Show preprocessing result
3. Show segmentation (organisms detected)
4. Show classification results
5. Show dashboard with metrics
6. Show exported CSV

**End of Day 2**:
- Working demo from image to dashboard
- All modules integrated
- Known issues documented

---

## Day 3: Polish & Enhancement (8 hours)

### Morning (Hour 0-4): Fix Critical Issues

**Priority Order**:
1. Fix any crashes or errors
2. Improve classification accuracy
3. Improve segmentation quality
4. Polish dashboard UI

**Tasks**:
- [ ] Address bugs from Day 2 demo
- [ ] Improve error handling
- [ ] Add progress indicators
- [ ] Better logging

### Afternoon (Hour 4-8): Add Demo-Friendly Features

**Dashboard Enhancements**:
- [ ] Add sample image gallery
- [ ] Add "Run Analysis" button
- [ ] Show processing status
- [ ] Display confidence scores
- [ ] Highlight bloom alerts if any

**Pipeline Enhancements**:
- [ ] Add batch processing (multiple images)
- [ ] Save intermediate results for debugging
- [ ] Add visualization of segmentation masks
- [ ] Better error messages

**Documentation**:
- [ ] Update README with current status
- [ ] Add screenshots to documentation
- [ ] Create demo video (optional)
- [ ] Prepare presentation slides

**End of Day 3**:
- Polished demo
- No critical bugs
- Dashboard looks professional

---

## Day 4: Testing & Validation (8 hours)

### Morning (Hour 0-4): Comprehensive Testing

**Test Scenarios**:
- [ ] Test with various image types
- [ ] Test with different organism counts (0, 1, many)
- [ ] Test with poor quality images
- [ ] Test error handling
- [ ] Test all export formats

**Accuracy Validation**:
- [ ] Compare with ground truth if available
- [ ] Document classification accuracy
- [ ] Document segmentation precision
- [ ] Calculate diversity indices correctness

**Performance Testing**:
- [ ] Measure end-to-end time
- [ ] Profile bottlenecks
- [ ] Optimize slow parts
- [ ] Target: <30s per image

### Afternoon (Hour 4-8): Prepare Presentation

**Create Presentation**:
- [ ] Problem statement slide
- [ ] Architecture diagram
- [ ] Demo walkthrough
- [ ] Results and metrics
- [ ] Future improvements

**Practice Demo**:
- [ ] Run through demo 3 times
- [ ] Handle Q&A scenarios
- [ ] Prepare backup plan if demo fails
- [ ] Record demo video as backup

**Documentation**:
- [ ] Final README update
- [ ] API documentation
- [ ] Installation guide
- [ ] Troubleshooting guide

**End of Day 4**:
- Tested system
- Presentation ready
- Demo rehearsed

---

## Day 5: Final Polish & Submission (8 hours)

### Morning (Hour 0-4): Final Testing & Bug Fixes

**Last Checks**:
- [ ] Test on fresh machine
- [ ] Verify all dependencies in requirements.txt
- [ ] Check all documentation links
- [ ] Ensure demo works without internet

**Final Polishing**:
- [ ] Clean up code comments
- [ ] Remove debug print statements
- [ ] Standardize code formatting
- [ ] Add license and attribution

### Afternoon (Hour 4-6): Submission Preparation

**Package Everything**:
- [ ] Zip project directory
- [ ] Test zip extraction and run
- [ ] Prepare GitHub repository
- [ ] Write submission README

**Submission Checklist**:
- [ ] Source code
- [ ] Documentation
- [ ] Demo video (optional but recommended)
- [ ] Presentation slides
- [ ] Requirements.txt
- [ ] Sample outputs

### Evening (Hour 6-8): Final Demo & Presentation

**Demo Day**:
- [ ] Set up demo station
- [ ] Test on presentation laptop
- [ ] Have backup laptop ready
- [ ] Run demo for judges

**Post-Demo**:
- [ ] Note judge feedback
- [ ] Note questions asked
- [ ] Document suggested improvements

---

## Critical Success Factors

### Must Have (Non-negotiable)
- [ ] Pipeline runs end-to-end without crashes
- [ ] Dashboard displays results
- [ ] CSV export works
- [ ] Classification gives reasonable results (>60% accuracy acceptable for demo)
- [ ] Demo completes in <3 minutes

### Should Have (Important for scoring)
- [ ] Diversity metrics calculated correctly
- [ ] Segmentation works on most images
- [ ] Dashboard looks professional
- [ ] Documentation is clear
- [ ] Code is organized

### Nice to Have (Bonus points)
- [ ] Real camera integration
- [ ] Batch processing
- [ ] Historical trend analysis
- [ ] GPS integration
- [ ] Bloom detection working

---

## Parallel Work Enablers

### Contract Guarantee
**Rule**: DO NOT change module input/output contracts during hackathon
- If you need to change a contract, discuss with entire team first
- Prefer adding optional fields rather than modifying existing ones

### Integration Points
- **Hour 8 (Day 1)**: First integration check
- **Hour 16 (Day 2 morning)**: Second integration
- **Hour 24 (Day 2 evening)**: Full integration
- **Hour 32+**: Continuous integration

### Communication Protocol
- **Standup**: Every 4 hours (morning, afternoon)
- **Format**: What you did, what you're doing, blockers
- **Duration**: 5 minutes max
- **Slack/Discord**: Immediate blockers only

### Git Workflow
```bash
# Everyone works on feature branches
git checkout -b feature/your-module

# Commit often
git add .
git commit -m "module: what you did"
git push origin feature/your-module

# Merge to main only when tested
# Integration lead handles merges
```

---

## Risk Mitigation

### If Classification Model Training Fails
**Backup Plan**: Use pretrained model from Kaggle/HuggingFace
- Download plankton classification model
- Adapt to our classes
- Use as-is even if not perfect

### If Real Camera Not Available
**Backup Plan**: Use dataset images
- Download WHOI plankton dataset
- Use as input to pipeline
- Simulate acquisition with file upload

### If Dashboard Breaks
**Backup Plan**: Focus on CSV output
- Make sure CSV export always works
- Use Excel/Google Sheets to show results in presentation
- Dashboard is bonus, not critical

### If Integration Fails
**Backup Plan**: Demo individual modules
- Show each module working independently
- Explain integration plan
- Focus on architecture and potential

---

## Daily Deliverables

| Day | Deliverable | Success Criteria |
|-----|-------------|------------------|
| 1 | Parallel dev started | Everyone working on their module |
| 2 | First integration | Pipeline runs with new modules |
| 3 | Polished demo | No crashes, looks professional |
| 4 | Tested system | Works on test images, presentation ready |
| 5 | Submission | Code submitted, demo completed |

---

## Demo Script (2-3 minutes)

**Minute 1: Problem & Solution**
- Show problem: Need to identify plankton quickly
- Show solution: Our automated pipeline

**Minute 2: Live Demo**
- Upload/capture microscope image
- Click "Analyze" button
- Show results appearing in dashboard:
  - Organisms detected: 12
  - Species identified: Copepod (7), Diatom (5)
  - Shannon diversity: 0.63
- Show exported CSV

**Minute 3: Architecture & Future**
- Show modular architecture diagram
- Explain each module briefly
- Mention: Real-time processing, batch analysis, bloom detection
- Take questions

---

## Success Metrics

**Minimum Viable Demo**:
- [ ] Process one image end-to-end: 100% required
- [ ] Classify organisms: 100% required
- [ ] Show diversity metric: 100% required
- [ ] Export CSV: 100% required
- [ ] Dashboard display: 100% required

**Scoring Boosters**:
- Classification accuracy >70%: Bonus points
- Real camera integration: Bonus points
- Professional UI: Bonus points
- Batch processing: Bonus points
- Code quality: Bonus points

**Target**: Working demo that impresses judges, not production-ready system

---

## Post-Hackathon (Based on Judge Feedback)

After judges give feedback:
- Note all suggestions
- Prioritize top 3 improvements
- Implement quick wins
- Document longer-term roadmap

This is a sprint, not a marathon. Get it working, make it impressive, polish based on feedback.
