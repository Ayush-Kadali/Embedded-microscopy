# Hackathon Reference Card - Keep This Open

## Timeline

**Day 1-2**: Build complete system
**Day 3-5**: Polish based on evaluator feedback

## Module Responsibilities

| Person | Module | Day 1 Deliverable |
|--------|--------|-------------------|
| 1 | Classification | Working model >60% accuracy |
| 2 | Dashboard | Basic Streamlit UI with results display |
| 3 | Data + Acquisition | 20+ test images, file loading |
| 4 | Integration | All modules merged, system works |
| 5 | Presentation | Complete slides, demo script |

## Critical Rules

1. **Never** change module contracts without team discussion
2. **Never** commit directly to main
3. **Always** test before requesting merge
4. **Always** post blockers in #help immediately

## Quick Commands

```bash
# Daily startup
source .venv/bin/activate

# Test pipeline
python main.py

# Test your module
python examples/test_individual_module.py

# Git workflow
git add .
git commit -m "module: what you did"
git push origin feature/your-module
```

## Standup Schedule

Every 4 hours: Hours 4, 8, 12, 16

Format: "Did X, doing Y, blocked on Z" (1 minute each)

## Integration Checkpoints

- **Hour 8 Day 1**: Classification + Data merged
- **Hour 12 Day 1**: Dashboard merged
- **Hour 16 Day 1**: Full system test
- **Hour 8 Day 2**: Final polish
- **Hour 16 Day 2**: Demo to evaluators

## Module Contracts (DO NOT CHANGE)

### All Modules Return
```python
{
    'status': 'success' | 'error',
    'error_message': str | None,
    # ... module-specific fields
}
```

### Classification Input
```python
{
    'image': np.ndarray,
    'masks': list,
    'bounding_boxes': list,
    'classification_config': dict,
}
```

### Classification Output
```python
{
    'status': str,
    'predictions': list,  # One per organism
    'model_metadata': dict,
}
```

### Dashboard Input
Reads CSV from `results/` directory

### Dashboard Output
Streamlit app at `dashboard/app.py`

## Success Criteria Day 2 End

- [ ] Pipeline runs without crashes
- [ ] Classification >60% accuracy
- [ ] Dashboard shows results
- [ ] CSV export works
- [ ] 3-minute demo ready
- [ ] 5-minute presentation ready

## File Locations

```
modules/your_module.py       # Your code
config/config.yaml           # Settings
main.py                      # Full pipeline test
examples/test_individual_module.py  # Module tests
docs/DEVELOPER_GUIDE.md      # Contracts
HACKATHON_TIMELINE.md        # Detailed timeline
```

## When Stuck

1. Try for 15 minutes
2. Check docs (DEVELOPER_GUIDE.md)
3. Post in #help
4. Continue on something else

## Fast Track Hints

### Classification
- Use Kaggle pretrained model
- Or transfer learning with MobileNetV2
- TFLite conversion for speed

### Dashboard
```python
import streamlit as st
uploaded = st.file_uploader("Image")
if st.button("Analyze"):
    result = run_pipeline(uploaded)
    st.metric("Count", result['count'])
    st.bar_chart(result['counts_by_class'])
```

### Data Collection
- Kaggle WHOI plankton dataset
- Need 20+ diverse images
- Label: clean, noisy, few organisms, many organisms

### Integration
```bash
# Merge order
git merge feature/data        # Safe
git merge feature/classification  # Test carefully
git merge feature/dashboard   # Test separately
```

## Error Messages

**"Missing required input"**: Check your input matches contract

**"Module not found"**: Activate virtual environment

**"Git conflict"**: Ask integration lead

**"Contract violation"**: You changed input/output format

## Team Contacts

- Project Lead: _______________
- Integration Lead: Person 4
- ML Lead: Person 1
- #help channel: Post blockers here

## Remember

- **Speed over perfection**: Working beats perfect
- **Communicate**: Standup every 4 hours
- **Test**: Run `python main.py` after changes
- **Focus**: Your module only, trust others
- **Help**: If you finish early, help teammates

## Day 1 End Goal

All modules integrated, system runs end-to-end, demo works

## Day 2 End Goal

Polished demo, presentation ready, evaluator feedback received

---

**Keep this card open while coding. Quick reference for everything.**
