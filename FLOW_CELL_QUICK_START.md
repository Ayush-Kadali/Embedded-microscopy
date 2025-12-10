# Flow Cell Scanner - Quick Start Guide

## Overview

The flow cell scanner enables **continuous real-time plankton monitoring** as water flows through your custom flow cell (microscope slides + masking tape walls).

## Hardware Setup

1. **Flow Cell**: 2 microscope slides + masking tape walls
2. **Syringe Pump**: Controls water flow rate
3. **Microscope**: With USB camera or Pi Camera attached
4. **Computer**: Running the scanner software

## Quick Start (5 minutes)

### Step 1: Test Your Camera

First, verify your camera is working:

```bash
# List available cameras
python test_flow_cell.py --list

# Test camera 0 (default USB camera)
python test_flow_cell.py --camera 0

# Test camera 1 if you have multiple cameras
python test_flow_cell.py --camera 1
```

Press 'q' to quit the camera test.

### Step 2: Run Flow Cell Scanner

#### Basic Usage (Default Settings)

```bash
# Use camera 0, 1 mL/min flow rate, capture every 1 second
python flow_cell_scanner.py --camera 0
```

#### Custom Settings

```bash
# Camera 1, 2.5 mL/min flow rate, capture every 2 seconds, run for 60 seconds
python flow_cell_scanner.py \
    --camera 1 \
    --flow-rate 2.5 \
    --interval 2 \
    --duration 60
```

#### Process Recorded Video

```bash
# If you recorded a video of your flow cell
python flow_cell_scanner.py --camera my_flow_video.mp4
```

Press 'q' to stop scanning at any time.

## Understanding the Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--camera` | Camera index (0, 1, 2...) or video file | `0` or `video.mp4` |
| `--flow-rate` | Flow rate in mL/min from syringe pump | `1.0` |
| `--interval` | Seconds between captures | `1.0` |
| `--duration` | Max duration in seconds (optional) | `60` |
| `--config` | Pipeline config file | `config/config.yaml` |

## What You'll See

### During Scanning

**Live Video Window** showing:
- Real-time camera feed
- Frame counter
- Total organisms detected
- Volume processed
- Press 'q' to stop

**Console Output** showing:
- Frame-by-frame processing
- Organism counts per frame
- Running statistics
- Organisms by species class

### Example Output

```
─────────────────────────────────────────────────────────────────────────
SESSION STATS - Elapsed: 30s
─────────────────────────────────────────────────────────────────────────
  Frames processed: 30
  Total organisms: 145
  Volume scanned: 0.500 mL
  Concentration: 290.0 organisms/mL
  Organisms by class:
    copepod: 67 (46.2%)
    diatom: 43 (29.7%)
    dinoflagellate: 35 (24.1%)
─────────────────────────────────────────────────────────────────────────
```

## After Scanning

Results are saved to: `results/flow_cell_YYYYMMDD_HHMMSS/`

Files generated:
- `session_summary.txt` - Complete session report
- `frame_XXXXXX.jpg` - Individual frame images
- CSV/JSON exports from pipeline (if enabled)

## Adjusting Settings for Your Setup

### Flow Rate

Measure your actual flow rate:
1. Fill syringe with known volume (e.g., 10 mL)
2. Time how long to empty (e.g., 5 minutes)
3. Calculate: `flow_rate = volume / time = 10 / 5 = 2.0 mL/min`

Use this value for `--flow-rate`

### Frame Interval

Balance between:
- **Faster (0.5s - 1s)**: More detailed monitoring, more processing
- **Slower (2s - 5s)**: Less processing, may miss organisms

For demo: **1-2 seconds** is good

### Camera Selection

If camera 0 doesn't work:
```bash
python test_flow_cell.py --list
```

Try each camera index shown.

## Troubleshooting

### Camera Not Found

```bash
# List available cameras
python test_flow_cell.py --list

# Try different indices
python test_flow_cell.py --camera 0
python test_flow_cell.py --camera 1
```

### Focus Issues

- Adjust microscope focus manually
- Watch the live feed while adjusting
- Press 'q' and restart after adjusting focus

### Too Many/Few Detections

Edit `config/config.yaml`:

```yaml
segmentation:
  min_organism_size_px: 50  # Increase to filter small noise
  max_organism_size_px: 500 # Decrease to filter large artifacts
```

### Processing Too Slow

- Increase `--interval` (e.g., from 1 to 2 seconds)
- Lower camera resolution in camera settings
- Process fewer frames, get same volume estimate

## Optimizing for Presentation

### For Demo/Presentation

```bash
# Good balance: real-time feel, manageable processing
python flow_cell_scanner.py \
    --camera 0 \
    --flow-rate 1.5 \
    --interval 1.5 \
    --duration 120
```

Shows:
- 120 seconds (2 minutes) of scanning
- ~80 frames processed
- Live stats updating
- Professional output

### For Actual Sampling

```bash
# Thorough sampling: process for full syringe volume
python flow_cell_scanner.py \
    --camera 0 \
    --flow-rate 2.0 \
    --interval 1.0 \
    --duration 300
```

Process entire 10 mL syringe at 2 mL/min = 5 minutes

## Tips for Success

1. **Focus First**: Get good focus before starting scan
2. **Stable Setup**: Minimize vibration during scanning
3. **Good Lighting**: Ensure even illumination
4. **Clean Flow Cell**: Remove bubbles, debris
5. **Calibrate Flow**: Measure actual flow rate from your pump
6. **Test Run**: Do a 30-second test before the real run

## Integration with Existing System

The flow cell scanner uses your existing:
- Pipeline configuration (`config/config.yaml`)
- Classification models (`models/`)
- Preprocessing settings
- All modules (segmentation, classification, etc.)

No changes needed to existing code!

## Command Reference

### Test camera
```bash
python test_flow_cell.py --camera 0
```

### Quick scan (auto-stop after 60s)
```bash
python flow_cell_scanner.py --camera 0 --duration 60
```

### Manual scan (stop with 'q')
```bash
python flow_cell_scanner.py --camera 0
```

### Process video file
```bash
python flow_cell_scanner.py --camera recording.mp4
```

### Custom flow rate
```bash
python flow_cell_scanner.py --camera 0 --flow-rate 2.5
```

## Next Steps

1. ✅ Test camera access
2. ✅ Run test scan (30-60 seconds)
3. ✅ Check results in `results/flow_cell_*/`
4. ✅ Adjust parameters as needed
5. ✅ Run full demonstration scan

Good luck with your presentation! 🎉
