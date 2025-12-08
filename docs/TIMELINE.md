# Hackathon Timeline - Complete by Day 2

**Strategy**: Working system by end of Day 2, polish Days 3-5 based on evaluator feedback

**Team Size**: 5 people working in parallel

---

## Day 1: Build Everything (16 hours - 2 shifts)

### Hour 0-1: Setup (Everyone)

**Everyone does this together**:
```bash
cd plank-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python verify_setup.py
python main.py
```

**Module Assignments**:
- Person 1: Classification (CRITICAL - start immediately)
- Person 2: Dashboard (HIGH - start hour 2)
- Person 3: Acquisition + Data (HIGH - start immediately)
- Person 4: Integration + Testing (CRITICAL - ongoing)
- Person 5: Presentation + Documentation (start hour 4)

---

### Hour 1-8: Sprint 1 (Morning)

**Person 1: Classification**
```
Hour 1-2: Download WHOI/Kaggle plankton dataset
Hour 2-4: Find pretrained model OR start transfer learning
Hour 4-6: Convert to TFLite, test inference
Hour 6-8: Integrate into classification.py, first test
```

Deliverable: Stub classification giving >60% accuracy

**Person 2: Dashboard**
```
Hour 2-3: Install Streamlit, create basic layout
Hour 3-5: File upload, trigger pipeline, show loading
Hour 5-7: Display results table, metrics, simple chart
Hour 7-8: Test with current pipeline output
```

Deliverable: Basic dashboard reads CSV and displays results

**Person 3: Acquisition + Data**
```
Hour 1-3: Download 20+ diverse plankton images
Hour 3-5: Update acquisition.py to load from files
Hour 5-7: Test with preprocessing, ensure good quality
Hour 7-8: Create test image set (clean, noisy, few organisms, many)
```

Deliverable: 20+ test images feeding into pipeline

**Person 4: Integration**
```
Hour 1-2: Set up Git branches, workflow
Hour 2-4: Monitor others' progress, help with blockers
Hour 4-6: Start merging completed modules
Hour 6-8: Test integrated system, document issues
```

Deliverable: Integration plan, first merge attempt

**Person 5: Documentation**
```
Hour 4-5: Take screenshots of current system
Hour 5-6: Start presentation slides (problem, solution, architecture)
Hour 6-7: Draft demo script
Hour 7-8: Help with testing
```

Deliverable: Presentation skeleton

**Hour 8 Checkpoint**: Classification stub integrated, dashboard reads results, 20 test images ready

---

### Hour 8-16: Sprint 2 (Afternoon/Evening)

**Person 1: Classification**
```
Hour 8-10: Improve model accuracy or find better pretrained
Hour 10-12: Optimize inference speed
Hour 12-14: Handle edge cases (0 organisms, many organisms)
Hour 14-16: Final integration test with all images
```

Deliverable: Working classifier, >65% accuracy, <3s inference

**Person 2: Dashboard**
```
Hour 8-10: Add organism details table
Hour 10-12: Add size distribution histogram
Hour 12-14: Add diversity metrics display
Hour 14-16: Polish UI, error handling
```

Deliverable: Complete dashboard with all visualizations

**Person 3: Preprocessing + Segmentation**
```
Hour 8-10: Test current preprocessing on all 20 images
Hour 10-12: Optimize parameters in config.yaml
Hour 12-14: Test segmentation, tune min/max area
Hour 14-16: Document optimal settings for different image types
```

Deliverable: Optimized preprocessing and segmentation

**Person 4: Integration**
```
Hour 8-16: Continuous integration
  - Hour 8: Merge classification updates
  - Hour 10: Merge dashboard updates
  - Hour 12: Merge optimization updates
  - Hour 14: Full system test
  - Hour 16: Day 1 complete demo run
```

Deliverable: All modules integrated, system runs end-to-end

**Person 5: Presentation**
```
Hour 8-10: Complete presentation slides
Hour 10-12: Add screenshots from dashboard
Hour 12-14: Prepare demo script with timing
Hour 14-16: First dry run of presentation
```

Deliverable: Complete presentation draft

**End of Day 1**: All modules working, integrated system, complete pipeline, basic presentation

---

## Day 2: Complete System (16 hours - 2 shifts)

### Hour 0-8: Final Integration & Testing

**Person 1: Model Polish**
```
Hour 0-2: Test classification on all 20 images
Hour 2-4: Fix any misclassifications if possible
Hour 4-6: Add confidence score display
Hour 6-8: Create model documentation
```

**Person 2: Dashboard Complete**
```
Hour 0-2: Add batch processing UI
Hour 2-4: Add export buttons (CSV, JSON download)
Hour 4-6: Add error messages, loading states
Hour 6-8: Final UI polish, test on different screens
```

**Person 3: Data + Demo Prep**
```
Hour 0-2: Create diverse demo dataset (5 images: clean, noisy, bloom, normal, edge case)
Hour 2-4: Test each demo image through pipeline
Hour 4-6: Document expected results for each
Hour 6-8: Prepare backup images
```

**Person 4: Integration + Testing**
```
Hour 0-2: Run comprehensive test suite
Hour 2-4: Fix all critical bugs
Hour 4-6: Test error handling
Hour 6-8: Performance profiling, optimize bottlenecks
```

**Person 5: Presentation + Documentation**
```
Hour 0-2: Update README with current features
Hour 2-4: Create user guide
Hour 4-6: Record demo video (backup if live demo fails)
Hour 6-8: Practice presentation (3 times)
```

**Hour 8 Checkpoint**: System complete, tested, documented, presentation ready

---

### Hour 8-16: Polish & First Demo

**Everyone**:
```
Hour 8-10: Team rehearsal of full demo
Hour 10-12: Fix any issues found during rehearsal
Hour 12-14: Final polish based on team feedback
Hour 14-16: Demo to evaluators for first feedback round
```

**End of Day 2**: Complete working system, presented to evaluators, feedback received

---

## Day 3-5: Iterate Based on Evaluator Feedback

### Day 3: High Priority Improvements

**Morning (Hour 0-8)**:
- Review evaluator feedback from Day 2
- Prioritize top 3 improvements
- Assign improvements to team members
- Implement high-priority changes

**Afternoon (Hour 8-16)**:
- Continue implementation
- Test improvements
- Update presentation with new features
- Second demo to evaluators

### Day 4: Medium Priority + Testing

**Morning (Hour 0-8)**:
- Implement remaining feedback items
- Comprehensive testing of all changes
- Fix any bugs introduced
- Performance optimization

**Afternoon (Hour 8-16)**:
- Final polish
- Update documentation
- Complete presentation slides
- Full dress rehearsal

### Day 5: Final Presentation

**Morning (Hour 0-8)**:
- Final bug fixes only
- Presentation practice (3+ times)
- Prepare backup plans
- Set up demo environment

**Afternoon (Hour 8-16)**:
- Final presentation to judges
- Q&A preparation
- Code submission

---

## Parallel Work Strategy

### Critical Path (Must finish Day 1)

**Path 1: Image → Results**
```
Acquisition (Person 3) → Preprocessing (existing) → Segmentation (existing) →
Classification (Person 1) → Counting (existing) → Analytics (existing) → Export (existing)
```

**Path 2: Results → Display**
```
Export (existing) → Dashboard (Person 2)
```

**Path 3: Integration**
```
Integration (Person 4) coordinates both paths
```

### Dependencies

**Hour 4 Dependencies**:
- Classification needs: Sample images (Person 3)
- Dashboard needs: Sample CSV output (Person 4)
- Integration needs: Both modules ready

**Hour 8 Dependencies**:
- Full pipeline needs: All modules integrated
- Dashboard needs: Full pipeline working
- Presentation needs: Screenshots from dashboard

### No Dependencies (Can work in parallel)

- Classification model training (Person 1)
- Dashboard UI development (Person 2)
- Test image collection (Person 3)
- Presentation slides (Person 5)

---

## Communication Protocol

### Standups (Every 4 hours)

**Format** (5 minutes total):
```
Person 1: "Classification: Trained model, 70% accuracy, integrating now. No blockers."
Person 2: "Dashboard: Upload works, results display done. Need CSV format clarification."
Person 3: "Data: Have 15 images, getting 5 more. No blockers."
Person 4: "Integration: Merged classification, testing now. Blocker: need Person 2's latest code."
Person 5: "Presentation: Slides 50% done. No blockers."
```

**Timing**:
- Day 1: Hours 4, 8, 12, 16
- Day 2: Hours 4, 8, 12, 16
- Day 3-5: Hours 8, 16

### Immediate Communication

**Use when**:
- You're blocked
- You need to change a contract
- You found a critical bug
- You need help urgently

**Don't use for**:
- Progress updates (wait for standup)
- Minor questions (check docs first)
- Nice-to-have features

---

## Integration Strategy

### Hour 4 Integration (Day 1)
```bash
# Person 4 does:
git checkout main
git merge feature/data-collection  # Safe, just adds images
python main.py  # Test with new images
```

### Hour 8 Integration (Day 1)
```bash
git checkout main
git merge feature/classification  # Critical path
python main.py  # Test
# If fails, Person 1 and 4 debug together
```

### Hour 12 Integration (Day 1)
```bash
git checkout main
git merge feature/dashboard  # UI layer
# Test dashboard separately
streamlit run dashboard/app.py
```

### Hour 16 Integration (Day 1)
```bash
# Full system test
python main.py  # Pipeline
streamlit run dashboard/app.py  # Dashboard
# Test end-to-end with 5 images
```

### Continuous Integration (Day 2)
- Merge every 2 hours
- Test after each merge
- Rollback if broken

---

## Success Criteria

### Must Have by End of Day 2

**Pipeline**:
- [ ] Processes images end-to-end
- [ ] Classification accuracy >60%
- [ ] Outputs CSV with results
- [ ] No crashes on 20 test images

**Dashboard**:
- [ ] Upload image
- [ ] Click "Analyze" button
- [ ] Display results (counts, diversity)
- [ ] Show simple charts
- [ ] Download CSV

**Presentation**:
- [ ] Problem statement clear
- [ ] Solution demonstrated
- [ ] Results shown
- [ ] Architecture explained

### Target by End of Day 2

**Performance**:
- [ ] Process image in <30s
- [ ] Classification accuracy >70%
- [ ] Dashboard responsive

**Quality**:
- [ ] Professional UI
- [ ] Clear error messages
- [ ] Good documentation

**Demo**:
- [ ] 5-minute presentation ready
- [ ] Demo video recorded (backup)
- [ ] Q&A responses prepared

---

## Risk Mitigation

### If Classification Fails (Day 1)

**Hour 4 checkpoint**: If <50% accuracy
- Switch to pretrained model immediately
- Download from Kaggle/HuggingFace
- Accept lower accuracy for Day 2 demo
- Plan to improve Days 3-5

### If Dashboard Breaks (Day 1)

**Hour 12 checkpoint**: If not displaying
- Fallback to Jupyter notebook
- Or demo with CSV opened in Excel
- Dashboard becomes Day 3 improvement

### If Integration Fails (Day 1 end)

**Hour 16 checkpoint**: If modules don't integrate
- Demo modules separately
- Show: "This works" for each module
- Show architecture: "This is how they connect"
- Actually integrate on Day 2 morning

### If Behind Schedule (Day 1)

**Cut in this order**:
1. Dashboard polish (keep basic functionality)
2. Batch processing
3. Advanced analytics
4. Real camera (use file upload)

**Never cut**:
1. Classification (use pretrained if needed)
2. Basic pipeline functionality
3. CSV export

---

## Day 2 End Deliverables

### Code
- [ ] All modules in GitHub
- [ ] README updated
- [ ] requirements.txt complete
- [ ] Working demo

### Documentation
- [ ] User guide
- [ ] API documentation (brief)
- [ ] Setup instructions
- [ ] Known issues list

### Presentation
- [ ] Slides complete
- [ ] Demo script
- [ ] Demo video
- [ ] Q&A prep

### Demo
- [ ] 5 diverse test images
- [ ] Expected results documented
- [ ] Backup plan ready
- [ ] Rehearsed 3+ times

---

## Days 3-5 Improvement Areas

Based on likely evaluator feedback:

**Accuracy Improvements**:
- Better classification model
- Fine-tune segmentation
- Handle edge cases

**UI Improvements**:
- Better visualizations
- Real-time processing
- Batch upload

**Features**:
- Historical trend analysis
- Bloom prediction
- Export formats

**Performance**:
- Faster processing
- Parallel processing
- Caching

**Hardware**:
- Real camera integration
- GPS module
- Mobile app (if time)

---

## Team Resilience

### If Someone Gets Sick/Unavailable

**Person 1 (Classification) backup**: Person 4
- Use pretrained model
- Simplify if needed

**Person 2 (Dashboard) backup**: Person 5
- Focus on basic functionality
- Polish later

**Person 3 (Data) backup**: Person 5
- Download datasets quickly
- Use existing samples

**Person 4 (Integration) backup**: Person 1
- Most technical person
- Everyone helps test

**Person 5 (Presentation) backup**: Person 2
- Everyone contributes slides
- Shared doc editing

### If Critical Blocker

**Process**:
1. Person posts in #help immediately
2. Integration lead drops current work
3. Team swarms the problem
4. Fix or cut feature within 1 hour
5. Continue

---

## What Good Looks Like End of Day 2

**Demo Flow** (3 minutes):

1. Show problem: "Manual plankton identification is slow and error-prone"
2. Open dashboard
3. Upload microscope image
4. Click "Analyze"
5. Wait 10-15 seconds (processing indicator)
6. Results appear:
   - "Detected 12 organisms"
   - "Species: Copepod (7), Diatom (5)"
   - "Shannon diversity: 0.63"
   - Bar chart showing distribution
7. Click "Download Results"
8. Show CSV opened in Excel
9. Explain: "All processing on-device, works on Raspberry Pi"
10. Take questions

**Evaluator sees**:
- Working end-to-end system
- Real results
- Professional interface
- Technical competence
- Team coordination

**Evaluator thinks**:
- "This actually works"
- "They can execute"
- "Good architecture"
- "Could be production-ready with polish"

That gets you top scores for functionality. Days 3-5 get you top scores for quality.

---

This is aggressive but achievable with parallel work and focus. Day 1-2 is sprint mode. Days 3-5 is marathon mode for polish.
