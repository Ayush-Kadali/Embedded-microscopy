# Flow Cell Scanning System

## Overview

The Flow Cell Scanning System enables **continuous, real-time plankton monitoring** as water flows through your custom flow cell. This is a significant innovation over static slide imaging.

### Innovation Highlights

✅ **Continuous Flow Monitoring** - Process flowing water samples, not static slides
✅ **Real-time Detection** - Immediate plankton identification and counting
✅ **Volume Tracking** - Calculate organisms per mL based on flow rate
✅ **Custom Flow Cell** - Works with your DIY microscope slide + masking tape design
✅ **Live Feedback** - See results as they happen

## System Architecture

```
Water Sample (Syringe)
    ↓ (controlled flow rate)
Flow Cell (2 microscope slides + masking tape walls)
    ↓ (under microscope)
USB/Pi Camera (continuous capture)
    ↓ (frame extraction at intervals)
Pipeline Processing (preprocessing → segmentation → classification)
    ↓ (real-time analysis)
Results (concentration, species distribution, alerts)
```

## Hardware Requirements

### Required
- **Flow Cell**: 2 microscope slides + masking tape walls (your custom design)
- **Syringe & Pump**: For controlled water flow (1-5 mL/min)
- **Microscope**: Your existing microscope setup
- **Camera**: USB camera or Raspberry Pi Camera attached to microscope
- **Computer**: Laptop or Raspberry Pi

### Optional
- Monitor/display (for live view)
- Second monitor (for presentation)

## Software Components

### 1. Camera Test Tool (`test_flow_cell.py`)

**Purpose**: Verify camera connectivity and view live feed

```bash
# List available cameras
python test_flow_cell.py --list

# Test specific camera
python test_flow_cell.py --camera 0
```

**Use when**: First setup, troubleshooting camera issues

### 2. Flow Cell Scanner (`flow_cell_scanner.py`)

**Purpose**: Main scanning application with live display

```bash
# Basic usage
python flow_cell_scanner.py --camera 0

# Full options
python flow_cell_scanner.py \
    --camera 0 \
    --flow-rate 2.0 \
    --interval 1.5 \
    --duration 120
```

**Features**:
- Live video window with overlay
- Real-time statistics in console
- Press 'q' to stop
- Automatic result export

**Use when**: Demonstrations, presentations, visual monitoring

### 3. Headless Scanner (`flow_cell_headless.py`)

**Purpose**: Background scanning without display (SSH/remote operation)

```bash
# Run in background
python flow_cell_headless.py --camera 0 --duration 300 &

# Stop with Ctrl+C or kill signal
```

**Features**:
- No GUI (works over SSH)
- Periodic status updates (every 10s)
- Graceful shutdown handling
- Perfect for Raspberry Pi

**Use when**: Remote operation, automated monitoring, no display available

## Quick Start Workflow

### 5-Minute Setup

```bash
# Step 1: Activate environment
source .venv/bin/activate

# Step 2: Test camera
python test_flow_cell.py --list
python test_flow_cell.py --camera 0  # Press 'q' when you see video

# Step 3: Run test scan (30 seconds)
python flow_cell_scanner.py --camera 0 --duration 30

# Step 4: Check results
ls -la results/flow_cell_*/
cat results/flow_cell_*/session_summary.txt
```

### For Presentation (2-hour setup)

```bash
# 1. Hardware setup (30 min)
#    - Assemble flow cell
#    - Mount on microscope
#    - Connect camera
#    - Set up syringe pump

# 2. Calibration (30 min)
#    - Focus microscope
#    - Test camera: python test_flow_cell.py --camera 0
#    - Measure actual flow rate
#    - Adjust lighting

# 3. Test runs (30 min)
#    - Short test: python flow_cell_scanner.py --camera 0 --duration 30
#    - Check detection quality
#    - Adjust config/config.yaml if needed
#    - Practice starting/stopping

# 4. Final preparation (30 min)
#    - Prepare water sample
#    - Clean flow cell
#    - Final test run
#    - Prepare backup plan (recorded video)
```

## Configuration

### Flow Rate Calibration

**Measure your actual flow rate**:

1. Fill syringe with known volume (e.g., 10 mL)
2. Start pump, time until empty
3. Calculate: `flow_rate = volume_mL / time_minutes`

Example:
- 10 mL syringe
- Takes 4 minutes to empty
- Flow rate = 10 / 4 = 2.5 mL/min

Use this value: `--flow-rate 2.5`

### Frame Interval Selection

**Balance between coverage and processing**:

| Interval | Frames/min | Use Case |
|----------|------------|----------|
| 0.5s | 120 | Maximum detail, slow flow |
| 1.0s | 60 | Good balance (recommended) |
| 2.0s | 30 | Faster processing, higher flow |
| 5.0s | 12 | Quick survey, very high flow |

**Recommendation**: Start with 1.0s, adjust based on organism density

### Detection Settings

Edit `config/config.yaml`:

```yaml
segmentation:
  min_organism_size_px: 50   # Increase to reduce noise
  max_organism_size_px: 500  # Decrease to filter artifacts

classification:
  confidence_threshold: 0.7   # Higher = stricter classification
```

## Understanding Results

### During Scanning

**Console Output**:
```
─────────────────────────────────────────────────────────────────
SESSION STATS - Elapsed: 45s
─────────────────────────────────────────────────────────────────
  Frames processed: 45
  Total organisms: 234
  Volume scanned: 0.750 mL
  Concentration: 312.0 organisms/mL
  Organisms by class:
    copepod: 108 (46.2%)
    diatom: 78 (33.3%)
    dinoflagellate: 48 (20.5%)
─────────────────────────────────────────────────────────────────
```

**Live Window** (if using `flow_cell_scanner.py`):
- Real-time camera feed
- Overlay showing: time, frames, organisms, volume
- Press 'q' to stop

### After Scanning

**Results Directory**: `results/flow_cell_YYYYMMDD_HHMMSS/`

**Files**:
- `session_summary.txt` - Human-readable summary
- `frame_XXXXXX.jpg` - Individual frame images
- `preview_frame_X.jpg` - Preview images (every 10 frames)
- CSV/JSON exports from pipeline (if configured)

**Key Metrics**:
- **Total organisms**: All detected organisms
- **Volume scanned**: Based on flow rate and time
- **Concentration**: Organisms per mL
- **Species breakdown**: Percentage by class

## Troubleshooting

### Camera Issues

**Problem**: Camera not found
```bash
# Solution: List and test cameras
python test_flow_cell.py --list
python test_flow_cell.py --camera 1  # Try different indices
```

**Problem**: Camera permission denied
```bash
# Solution: Check permissions (macOS)
# System Preferences → Security & Privacy → Camera
# Allow Terminal/Python
```

### Flow Cell Issues

**Problem**: Focus not sharp
- Adjust microscope focus manually
- Watch live feed while adjusting
- May need to restart scan after adjustment

**Problem**: Bubbles in flow cell
- Tap flow cell gently to dislodge
- Ensure proper filling technique
- Pre-wet flow cell before use

**Problem**: Uneven flow
- Check syringe pump operation
- Ensure no blockages
- Verify tube connections

### Detection Issues

**Problem**: Too many false detections (noise)
```yaml
# Edit config/config.yaml
segmentation:
  min_organism_size_px: 100  # Increase from 50
```

**Problem**: Missing small organisms
```yaml
# Edit config/config.yaml
segmentation:
  min_organism_size_px: 30   # Decrease from 50
```

**Problem**: Processing too slow
```bash
# Increase frame interval
python flow_cell_scanner.py --camera 0 --interval 2.0
```

### Software Issues

**Problem**: Import errors
```bash
# Ensure virtual environment activated
source .venv/bin/activate
pip install -r requirements.txt
```

**Problem**: Pipeline errors
```bash
# Verify configuration
python main.py --validate-only
```

## Advanced Usage

### Recording for Later Processing

```bash
# Option 1: Record video with camera directly
# (Use camera software to record)

# Option 2: Process recorded video
python flow_cell_scanner.py --camera recording.mp4
```

### Batch Processing Multiple Samples

```bash
# Create simple script
for i in {1..5}; do
    echo "Processing sample $i"
    python flow_cell_headless.py \
        --camera 0 \
        --duration 60 \
        --flow-rate 2.0
    echo "Sample $i complete, change sample..."
    sleep 30  # Time to change sample
done
```

### Custom Analysis

```python
# Load results for custom analysis
import json
from pathlib import Path

results_dir = Path("results/flow_cell_20251211_123456")
summary = results_dir / "session_summary.txt"

# Read and process results
# Add custom calculations, plots, etc.
```

## Best Practices

### Before Scanning

✅ Test camera first (`test_flow_cell.py`)
✅ Calibrate flow rate with actual measurement
✅ Clean flow cell thoroughly
✅ Check focus with live feed
✅ Run 30-second test scan

### During Scanning

✅ Minimize vibration
✅ Maintain consistent lighting
✅ Monitor live stats for anomalies
✅ Keep backup of settings used

### After Scanning

✅ Save results immediately
✅ Record metadata (sample source, date, conditions)
✅ Clean flow cell promptly
✅ Review results for quality

### For Demonstrations

✅ Pre-test everything 1 hour before
✅ Have backup video ready
✅ Practice start/stop procedure
✅ Prepare explanation of results
✅ Have printed backup slides

## Performance Optimization

### For Maximum Speed

```bash
# Increase interval, reduce processing
python flow_cell_scanner.py \
    --camera 0 \
    --interval 2.0 \
    --flow-rate 3.0
```

### For Maximum Accuracy

```bash
# Decrease interval, thorough processing
python flow_cell_scanner.py \
    --camera 0 \
    --interval 0.5 \
    --flow-rate 1.0
```

### For Raspberry Pi

```bash
# Use headless version
python flow_cell_headless.py \
    --camera 0 \
    --interval 2.0 \
    --duration 300
```

## Integration with Main System

The flow cell scanner **fully integrates** with your existing system:

- Uses same `config/config.yaml`
- Uses same trained models
- Uses same pipeline modules
- Produces compatible output format

**No modifications needed to existing code!**

## Future Enhancements

Potential additions (beyond 4-hour timeframe):

- [ ] Automated focus adjustment
- [ ] Multi-camera support (multiple flow cells)
- [ ] Real-time web dashboard
- [ ] Database storage of results
- [ ] Email/SMS alerts for blooms
- [ ] Integration with environmental sensors

## Support

### Documentation
- Quick Start: `FLOW_CELL_QUICK_START.md`
- This file: Complete reference

### During Demo
- Have this file open for reference
- Keep test script ready: `test_flow_cell.py`
- Know how to stop: Press 'q' or Ctrl+C

### Example Commands for Copy-Paste

```bash
# Quick camera test
python test_flow_cell.py --camera 0

# 2-minute demo scan
python flow_cell_scanner.py --camera 0 --duration 120 --flow-rate 2.0

# 5-minute thorough scan
python flow_cell_scanner.py --camera 0 --duration 300 --flow-rate 1.5 --interval 1.0

# Headless background scan
python flow_cell_headless.py --camera 0 --duration 180 --flow-rate 2.0
```

## Summary

You now have a **complete flow cell scanning system**:

✅ **3 tools**: Camera test, GUI scanner, headless scanner
✅ **Fully integrated**: Uses existing pipeline and models
✅ **Production ready**: Real-time processing and results
✅ **Well documented**: Quick start + complete reference
✅ **Tested**: Camera detection confirmed

**Total setup time**: ~5 minutes to first results
**Demo ready**: Yes, with live video and statistics
**Innovation level**: High (continuous flow vs. static images)

Good luck with your presentation! 🚀
