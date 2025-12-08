# Marine Plankton AI Microscopy System

**Smart India Hackathon 2025** - 5-day project

Automated microscopy system for marine plankton identification and counting.

---

## Quick Start (5 minutes)

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify
python verify_setup.py

# Run
python main.py
```

**Expected output**: Pipeline completes, results in `results/` directory

---

## Project Overview

### What It Does

End-to-end pipeline for plankton analysis:

```
Image → Preprocessing → Segmentation → Classification →
Counting → Analytics → Export (CSV/JSON)
```

**Key Features**:
- Automated organism detection and counting
- Species classification
- Diversity metrics (Shannon, Simpson indices)
- Harmful algal bloom detection
- On-device processing (Raspberry Pi target)
- CSV/JSON export for analysis

### Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Pipeline Architecture | 🟢 Complete | All 7 modules integrated |
| Preprocessing | 🟢 Working | OpenCV-based image enhancement |
| Segmentation | 🟢 Working | Watershed algorithm |
| Classification | 🟡 Stub | Needs trained model |
| Counting & Analytics | 🟢 Complete | All metrics calculated |
| Export | 🟢 Working | CSV/JSON generation |
| Dashboard | 🟡 Stub | Needs Streamlit implementation |
| Testing | 🟢 95% Pass | 18/19 tests passing |

**Legend**: 🟢 Production Ready | 🟡 Needs Work | 🔴 Not Started

---

## For Hackathon Teams

### Timeline: Complete by Day 2

**Day 1 (16 hours)**:
- Hour 0-1: Setup
- Hour 1-8: Parallel module development
- Hour 8-16: Integration and testing
- **Goal**: Working end-to-end system

**Day 2 (16 hours)**:
- Hour 0-8: Polish and optimize
- Hour 8-16: Demo to evaluators, get feedback
- **Goal**: Complete system, initial feedback

**Day 3-5**:
- Implement evaluator feedback
- Final polish and presentation

### Team Roles (5 people recommended)

| Person | Module | Priority | Day 1 Deliverable |
|--------|--------|----------|-------------------|
| 1 | Classification (ML) | CRITICAL | Trained model integrated |
| 2 | Dashboard (UI) | HIGH | Basic Streamlit app |
| 3 | Data Collection | HIGH | 20+ test images |
| 4 | Integration & Testing | CRITICAL | All modules merged |
| 5 | Presentation | MEDIUM | Slides and demo script |

---

## Documentation

### Essential Reading

**For Everyone**:
- **START_HERE.md** - First read (5 min)
- **QUICKSTART.md** - Commands reference (2 min)

**For Developers**:
- **docs/CONTRACTS.md** - Module input/output specifications
- **docs/DEVELOPER_GUIDE.md** - Development guidelines
- **docs/TIMELINE.md** - Hour-by-hour hackathon plan

**For Testing**:
- **docs/TESTING.md** - Testing strategy
- **TESTING_COMPLETE.md** - Test results

**Reference**:
- **REFERENCE_CARD.md** - One-page cheat sheet

### Documentation Structure

```
docs/
├── CONTRACTS.md          # Module interface specifications
├── DEVELOPER_GUIDE.md    # Development guidelines
├── TIMELINE.md           # 5-day hackathon timeline
└── TESTING.md            # Testing strategy

Root level:
├── README.md             # This file
├── START_HERE.md         # Quick start guide
├── QUICKSTART.md         # Command reference
├── REFERENCE_CARD.md     # One-page reference
└── TESTING_COMPLETE.md   # Test results
```

---

## Project Structure

```
plank-1/
├── modules/              # 7 pipeline modules
│   ├── acquisition.py   # Image capture
│   ├── preprocessing.py # Image enhancement
│   ├── segmentation.py  # Organism detection
│   ├── classification.py# Species identification
│   ├── counting.py      # Counting & sizing
│   ├── analytics.py     # Diversity metrics
│   └── export.py        # Results export
│
├── pipeline/             # Orchestration
│   ├── manager.py       # Pipeline coordinator
│   └── validators.py    # Config validation
│
├── config/
│   └── config.yaml      # System configuration
│
├── tests/
│   └── test_all_modules.py  # Comprehensive tests (19 tests)
│
├── examples/
│   └── test_individual_module.py  # Module testing examples
│
├── results/             # Output directory
├── models/              # ML models (add .tflite files here)
├── dashboard/           # Streamlit dashboard (WIP)
├── docs/                # Documentation
└── archive/             # Old documentation
```

---

## Usage

### Basic Usage

```bash
python main.py
```

### With Parameters

```bash
python main.py \
    --magnification 2.5 \
    --exposure 150 \
    --gps-lat 12.34 \
    --gps-lon 56.78 \
    --operator "your_name"
```

### Configuration

Edit `config/config.yaml`:

```yaml
classification:
  class_names: ["Copepod", "Diatom", "Dinoflagellate", "Ciliate", "Other"]
  confidence_threshold: 0.7

analytics:
  bloom_thresholds:
    Dinoflagellate: 5000
    Diatom: 10000
```

---

## Module Architecture

### Modular Design

Each module:
- Has standard input/output contract (see `docs/CONTRACTS.md`)
- Can be replaced independently
- Validates its own input and configuration
- Returns standardized error format

### Example Module Structure

```python
class YourModule(PipelineModule):
    def validate_config(self):
        # Validate configuration
        pass

    def validate_input(self, input_data):
        # Validate input matches contract
        pass

    def process(self, input_data):
        # Main processing logic
        return {
            'status': 'success',
            # ...module-specific outputs
        }
```

### Critical Rule

**DO NOT change module contracts without team discussion.**

Changing input/output structure breaks integration.

---

## Testing

### Run All Tests

```bash
pytest tests/test_all_modules.py -v
```

**Current Results**: 18/19 passing (95%)

### Test Your Module

```bash
pytest tests/test_all_modules.py::TestYourModule -v
```

### Test Pipeline

```bash
python main.py
```

### What's Tested

- **Contract Compliance**: All inputs/outputs match specifications
- **Integration**: Modules work together correctly
- **End-to-End**: Full pipeline executes successfully

See `docs/TESTING.md` for details.

---

## Development Workflow

### Setup (Once)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Daily Workflow

```bash
# Activate environment
source .venv/bin/activate

# Create your branch
git checkout -b feature/your-module

# Make changes
# Edit modules/your_module.py

# Test
python main.py
pytest tests/test_all_modules.py::TestYourModule -v

# Commit
git add .
git commit -m "module: what you changed"
git push origin feature/your-module

# Request merge from integration lead
```

---

## Dependencies

**Core**:
- Python 3.8+
- NumPy
- OpenCV
- PyYAML

**ML** (when ready):
- TensorFlow Lite
- Or ONNX Runtime

**Dashboard** (when ready):
- Streamlit
- Plotly
- Folium

**Install all**:
```bash
pip install -r requirements.txt
```

---

## Hardware Target

### Development
- Any laptop/desktop
- Python 3.8+
- 4GB RAM

### Production
- Raspberry Pi 4 (4GB recommended)
- Raspberry Pi HQ Camera
- Seeed 300X Microscope Lens (0.7-4.5x)
- GPS module (optional)

---

## Performance Targets

| Stage | Current | Target (Pi4) |
|-------|---------|--------------|
| Preprocessing | ~0.5s | <2s |
| Segmentation | ~0.5s | <5s |
| Classification | ~2ms (stub) | <3s (20 organisms) |
| **Total** | ~2s | <15s per image |

---

## Output Files

Generated in `results/` directory:

**summary_<uuid>.csv**:
```csv
sample_id,timestamp,class_name,count,shannon_diversity,bloom_alert
abc123,2025-12-08T10:00:00,Copepod,8,0.349,False
abc123,2025-12-08T10:00:00,Dinoflagellate,1,0.349,False
```

**organisms_<uuid>.csv**:
```csv
organism_id,class_name,confidence,size_um,centroid_x_px,centroid_y_px
0,Copepod,0.87,37.03,978,364
1,Dinoflagellate,0.92,85.85,1125,909
```

**results_<uuid>.json**: Complete structured results

---

## Critical Path for Hackathon

### Must Have (Day 2)

1. **Classification Model** - CRITICAL
   - Download pretrained from Kaggle/HuggingFace
   - Or train with transfer learning
   - Convert to TFLite
   - >60% accuracy acceptable for demo

2. **Dashboard** - HIGH
   - Basic Streamlit UI
   - Upload image → Analyze → Show results
   - Simple charts and metrics

3. **Test Images** - HIGH
   - 20+ diverse plankton images
   - From WHOI dataset or similar

### Should Have (Day 3-4)

- Classification accuracy >70%
- Professional UI design
- Batch processing
- Error handling

### Nice to Have (Day 5)

- Real camera integration
- GPS integration
- Historical trend analysis

---

## Troubleshooting

### Pipeline Fails

```bash
# Check which module failed
python main.py
# Look for "Failed at: module_name"

# Test that module
pytest tests/test_all_modules.py::TestModuleName -v
```

### Import Errors

```bash
# Check virtual environment active
which python  # Should show .venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Fail

```bash
# Run with verbose output
pytest tests/test_all_modules.py -vv

# Check if you broke a contract
cat docs/CONTRACTS.md
```

---

## Support

### Documentation

- General questions: Read `START_HERE.md`
- Module contracts: `docs/CONTRACTS.md`
- Development: `docs/DEVELOPER_GUIDE.md`
- Timeline: `docs/TIMELINE.md`
- Testing: `docs/TESTING.md`

### During Hackathon

- Integration lead: Person 4
- ML lead: Person 1
- Project lead: [Your name]

---

## License

[Add your license]

---

## Acknowledgments

- Architecture based on modular pipeline design
- Seeed 300X Microscope Lens specifications
- Raspberry Pi Foundation

---

**Built for Smart India Hackathon 2025**

**Current Status**: Foundation complete, 95% tests passing, ready for Day 1

**Goal**: Working demo by Day 2, polished presentation by Day 5

---

## Quick Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Verify
python verify_setup.py

# Run pipeline
python main.py

# Run tests
pytest tests/test_all_modules.py -v

# Test your module
pytest tests/test_all_modules.py::TestYourModule -v

# Git workflow
git checkout -b feature/your-module
git add . && git commit -m "module: message"
git push origin feature/your-module
```

---

**Read START_HERE.md to begin.**
