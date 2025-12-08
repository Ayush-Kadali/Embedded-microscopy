# Marine Plankton AI Microscopy System

**5-Day Hackathon Project - Smart India Hackathon**

An embedded intelligent microscopy system for identification and counting of microscopic marine organisms.

---

## Quick Start (5 minutes)

```bash
# Setup
cd plank-1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify
python verify_setup.py

# Run
python main.py
```

Expected output:
```
Pipeline execution complete!
Total organisms detected: 4
Shannon diversity: 0.562
Results exported to: ./results/summary_<uuid>.csv
```

---

## Project Overview

###End-to-End Pipeline

```
Image Acquisition → Preprocessing → Segmentation → Classification →
Counting → Analytics → Export
```

All processing happens on-device (Raspberry Pi target), with results exported as CSV and displayed in web dashboard.

### Key Features

- Modular architecture with 7 independent modules
- Standard input/output contracts for parallel development
- Real-time diversity metrics (Shannon, Simpson indices)
- Harmful algal bloom detection
- CSV/JSON export for downstream analysis
- Optional Streamlit dashboard

---

## Project Structure

```
plank-1/
├── modules/              # 7 pipeline modules
│   ├── acquisition.py   # Image capture
│   ├── preprocessing.py # Denoise & normalize
│   ├── segmentation.py  # Organism detection
│   ├── classification.py# Species identification
│   ├── counting.py      # Counting & sizing
│   ├── analytics.py     # Diversity metrics
│   └── export.py        # Results export
├── pipeline/
│   ├── manager.py       # Pipeline orchestrator
│   └── validators.py    # Config validation
├── config/
│   └── config.yaml      # Configuration
├── dashboard/           # Streamlit dashboard (WIP)
├── docs/                # Documentation
├── tests/               # Unit tests
├── examples/            # Usage examples
└── main.py              # Entry point
```

---

## Module Status

| Module | Status | Completeness | Priority |
|--------|--------|--------------|----------|
| Acquisition | 🟡 Stub | 30% | HIGH |
| Preprocessing | 🟢 Working | 90% | MEDIUM |
| Segmentation | 🟢 Working | 85% | MEDIUM |
| Classification | 🟡 Stub | 20% | CRITICAL |
| Counting | 🟢 Complete | 100% | LOW |
| Analytics | 🟢 Complete | 95% | LOW |
| Export | 🟡 Partial | 70% | MEDIUM |

**Legend**: 🟢 Working | 🟡 Needs Work | 🔴 Not Started

---

## Usage

### Basic Usage

```bash
python main.py
```

### Custom Parameters

```bash
python main.py --magnification 2.5 --exposure 150
```

### Configuration

Edit `config/config.yaml`:

```yaml
classification:
  class_names:
    - "Copepod"
    - "Diatom"
    - "Dinoflagellate"
  confidence_threshold: 0.7

analytics:
  bloom_thresholds:
    Dinoflagellate: 5000
```

---

## Output Files

### Generated in `results/` directory

**summary_<uuid>.csv**: Per-class counts and metrics
```csv
sample_id,timestamp,class_name,count,shannon_diversity,bloom_alert
abc123,2025-12-08T10:00:00,Copepod,3,0.562,False
abc123,2025-12-08T10:00:00,Diatom,1,0.562,False
```

**organisms_<uuid>.csv**: Per-organism details
```csv
organism_id,class_name,confidence,size_um,centroid_x_px,centroid_y_px
0,Copepod,0.873,37.03,978,364
1,Diatom,0.843,85.85,1125,909
```

**results_<uuid>.json**: Complete structured results

---

## For Team Members

### New to Project?

Read: `TEAM_QUICKSTART.md` (15 minutes)

### Module Assignment

See: `docs/MODULE_ASSIGNMENTS_HACKATHON.md`

### Hackathon Timeline

See: `HACKATHON_PLAN.md` (5-day breakdown)

### Module Contracts

See: `docs/DEVELOPER_GUIDE.md` (your module's interface)

---

## Development Workflow

### Test Your Module

```bash
# Option 1: Independent testing
python examples/test_individual_module.py

# Option 2: Full pipeline
python main.py

# Option 3: Unit tests
pytest tests/test_your_module.py -v
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-module

# Make changes
# Edit modules/your_module.py

# Test
python main.py

# Commit
git add .
git commit -m "module: description"
git push origin feature/your-module
```

Integration lead merges to main after testing.

---

## Architecture

### Modular Design

Each module:
- Inherits from `PipelineModule` base class
- Has defined input/output contract
- Validates configuration and input data
- Returns standardized result format
- Handles errors uniformly

### Example Module Structure

```python
from modules.base import PipelineModule

class YourModule(PipelineModule):
    def validate_config(self):
        # Check configuration is valid
        pass

    def validate_input(self, input_data):
        # Check input matches contract
        pass

    def process(self, input_data):
        # Main processing logic
        return {
            'status': 'success',
            # ... other outputs per contract
        }
```

### Pipeline Manager

Orchestrates modules without touching their internals:

```python
manager = PipelineManager(config)
result = manager.execute_pipeline(acquisition_params)
```

---

## Hardware Requirements

### Development (Current)
- Any laptop/desktop
- Python 3.8+
- 4GB RAM

### Production Target
- Raspberry Pi 4 (4GB)
- Raspberry Pi HQ Camera (directly attached to microscope)
- Optional: GPS module

---

## Performance Targets

| Stage | Current | Target (Pi4) |
|-------|---------|--------------|
| Acquisition | N/A | <1s |
| Preprocessing | ~0.5s | <2s |
| Segmentation | ~0.5s | <5s |
| Classification | ~2ms (stub) | <3s |
| Total | ~2s | <15s |

---

## Dependencies

Core:
- numpy
- opencv-python
- PyYAML

Optional:
- streamlit (dashboard)
- plotly (visualization)
- tensorflow/tflite-runtime (classification)

Install all:
```bash
pip install -r requirements.txt
```

---

## Testing

```bash
# Verify setup
python verify_setup.py

# Run example tests
python examples/test_individual_module.py

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=modules
```

---

## Documentation

| File | Purpose |
|------|---------|
| `README_HACKATHON.md` | This file - project overview |
| `TEAM_QUICKSTART.md` | 15-minute team onboarding |
| `HACKATHON_PLAN.md` | 5-day timeline and strategy |
| `docs/DEVELOPER_GUIDE.md` | Module contracts and development |
| `docs/MODULE_ASSIGNMENTS_HACKATHON.md` | Team assignments |

---

## Hackathon Strategy

### Day 1: Parallel Development
- Everyone starts on their module
- Focus on core functionality
- First integration at end of day

### Day 2: Integration
- Merge all modules
- Get full pipeline working
- Basic dashboard ready

### Day 3: Polish
- Fix bugs
- Improve UI
- Optimize performance

### Day 4: Testing
- Comprehensive testing
- Prepare presentation
- Rehearse demo

### Day 5: Demo
- Final polish
- Present to judges
- Submit code

---

## Critical Path

**Must Have for Demo**:
1. Pipeline runs end-to-end
2. Classifies organisms (any accuracy >60%)
3. Shows diversity metrics
4. Exports CSV
5. Dashboard displays results

**Priority Order**:
1. Classification model (CRITICAL)
2. Dashboard (HIGH)
3. Real camera integration (MEDIUM)
4. Performance optimization (LOW)

---

## Risk Mitigation

### If ML training fails
Use pretrained model from Kaggle/HuggingFace

### If camera unavailable
Use dataset images or file upload

### If dashboard breaks
Fallback to CSV + Excel demo

### If integration fails
Demo individual modules separately

---

## Contributing

### During Hackathon

1. Take ownership of your assigned module
2. Do NOT change input/output contracts without team discussion
3. Commit working code frequently
4. Test before requesting merge
5. Help teammates if you finish early

### Code Standards

- Follow existing code style
- Add docstrings to new functions
- Comment complex logic
- Remove debug print statements before committing
- Keep contracts intact

---

## Troubleshooting

### Setup Issues

```bash
# Verify Python version
python3 --version  # Need 3.8+

# Check virtual environment
which python  # Should show .venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Pipeline Errors

```bash
# Check which module failed
# Error message shows: "Failed at: module_name"

# Test that module independently
python examples/test_individual_module.py
```

### Import Errors

```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## License

[Add license]

## Acknowledgments

- Based on architecture from `project_pipeline_idea.md`
- Raspberry Pi Foundation

---

## Contact

- Project Lead: [Name]
- Technical Lead: [Name]
- Repository: [GitHub URL]
- Chat: [Slack/Discord]

---

**Built for Smart India Hackathon 2025**

**Timeline**: 5 days to working demo
**Goal**: Automated marine plankton identification system
**Status**: Foundation complete, ready for team development
