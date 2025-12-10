# YOLO Real-Time Detection - Quick Start

## Your YOLO Models

You have 3 YOLO models ready to use:

1. **`best.pt`** (5.9 MB) - Your custom trained model ⭐ **← USE THIS**
2. **`yolov5nu.pt`** (5.3 MB) - YOLOv5 nano
3. **`yolov8n.pt`** (6.2 MB) - YOLOv8 nano

## Quick Setup (2 Minutes)

### Step 1: Install Dependencies

```bash
# Run the setup script
./setup_yolo.sh
```

This installs:
- PyTorch (CPU version)
- ultralytics (YOLOv8 framework)
- Required dependencies

**Installation time**: 1-2 minutes

### Step 2: Test Your Model

```bash
# Test with your best model
python yolo_realtime.py --model "Downloaded models/best.pt"

# Press 'q' to quit
```

## Usage

### Basic Commands

```bash
# Use best.pt (recommended - your custom model)
python yolo_realtime.py --model "Downloaded models/best.pt"

# Use YOLOv8 model
python yolo_realtime.py --model "Downloaded models/yolov8n.pt"

# Use YOLOv5 model
python yolo_realtime.py --model "Downloaded models/yolov5nu.pt"
```

### With Different Cameras

```bash
# Camera 0 (default)
python yolo_realtime.py --model "Downloaded models/best.pt" --camera 0

# Camera 1
python yolo_realtime.py --model "Downloaded models/best.pt" --camera 1

# Video file
python yolo_realtime.py --model "Downloaded models/best.pt" --camera video.mp4
```

### Adjust Detection Sensitivity

```bash
# More sensitive (more detections, lower confidence needed)
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.15

# Less sensitive (fewer detections, higher confidence needed)
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.50

# Default confidence threshold is 0.25
```

### Save Output

```bash
# Save annotated video
python yolo_realtime.py --model "Downloaded models/best.pt" --save-video

# Output saved to: results/yolo_detection_TIMESTAMP.mp4
```

## What You'll See

**Live Window** with:
- 🎯 **Bounding boxes** around detected plankton (color-coded by class)
- 🏷️ **Class labels** with confidence scores
- 📊 **Stats overlay**:
  ```
  YOLOv8 Detection (or YOLOv5)
  FPS: 25.3
  Inference: 35ms
  Total: 142
  Detections:
    copepod: 68
    diatom: 51
    dinoflagellate: 23
  ```

**Controls**:
- `q` - Quit
- `s` - Save snapshot

## For Your Demo

### Recommended Command

```bash
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.20
```

**Why this is perfect for demo:**
- ✅ Uses your custom trained model
- ✅ Lower confidence (0.20) shows more detections
- ✅ Fast inference (30-50ms per frame)
- ✅ Professional looking output
- ✅ Real-time bounding boxes

### Demo Tips

1. **Good lighting** - Essential for clear detections
2. **Stable camera** - Mount or stabilize camera
3. **Point at plankton images** - Display on screen or print them
4. **White background** - Helps with detection contrast
5. **Practice once** - Run through before demo

### What to Say During Demo

**Opening**:
> "This is our YOLO-based real-time detection system. Watch as it automatically detects and classifies plankton species..."

**While Running**:
> "You can see bounding boxes appearing around each organism. The model is running at [X] FPS with only [Y]ms inference time. Each detection shows the species and confidence level."

**Technical**:
> "We're using YOLO, one of the fastest object detection architectures, optimized for real-time performance. This runs on a standard laptop, but can also deploy to Raspberry Pi or edge devices."

## Comparison: Which Model to Use?

| Model | Size | Speed | Use Case |
|-------|------|-------|----------|
| **best.pt** | 5.9MB | Fast | **Your custom model - BEST CHOICE** ⭐ |
| yolov5nu.pt | 5.3MB | Very Fast | Generic YOLOv5 |
| yolov8n.pt | 6.2MB | Fast | Generic YOLOv8 |

**Recommendation**: Use `best.pt` - it's trained on your specific data!

## Troubleshooting

### Dependencies Not Installed

```bash
# Run setup script
./setup_yolo.sh

# Or manually install:
pip install torch torchvision ultralytics opencv-python
```

### No Detections Appearing

```bash
# Lower confidence threshold
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.10
```

### Camera Not Found

```bash
# List cameras
python test_flow_cell.py --list

# Try different camera index
python yolo_realtime.py --model "Downloaded models/best.pt" --camera 1
```

### Model Loading Error

The script auto-detects model type. If it fails:

```bash
# Force YOLOv5
python yolo_realtime.py --model "Downloaded models/best.pt" --model-type yolov5

# Force YOLOv8
python yolo_realtime.py --model "Downloaded models/best.pt" --model-type yolov8
```

### Slow Performance

```bash
# Check inference time in stats overlay
# If > 100ms, try:

# 1. Lower resolution camera
# 2. Skip frames (edit script)
# 3. Use buffered mode for high FPS recording
```

## Complete Demo Workflow

### Before Demo (10 minutes)

```bash
# 1. Install dependencies (one time)
./setup_yolo.sh

# 2. Test camera
python test_flow_cell.py --camera 0

# 3. Test YOLO detection
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.20

# 4. Verify bounding boxes appear
# 5. Press 'q' when satisfied
```

### During Demo (3-4 minutes)

```bash
# Launch detection
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.20

# Point camera at sample
# Explain what's happening
# Show live detections
# Press 'q' to stop
# Show summary statistics
```

## Advanced Options

### Save Snapshots During Demo

While running, press `s` to save current frame:
```
results/yolo_snapshot_0000.jpg
results/yolo_snapshot_0001.jpg
...
```

### Record Entire Session

```bash
python yolo_realtime.py --model "Downloaded models/best.pt" --save-video --conf 0.20

# Creates: results/yolo_detection_TIMESTAMP.mp4
```

### Hide Stats Overlay

```bash
python yolo_realtime.py --model "Downloaded models/best.pt" --no-stats
```

## Performance Expectations

**Typical Performance** (on laptop):
- **FPS**: 20-30 (camera speed)
- **Inference**: 30-50ms per frame
- **Latency**: Nearly real-time (< 100ms)
- **Quality**: Production-ready

**What Makes YOLO Great**:
- ✅ Very fast inference
- ✅ Accurate bounding boxes
- ✅ Multiple object detection per frame
- ✅ Real-time performance
- ✅ Easy to use

## Integration with Flow Cell

Once you have physical flow cell:

```bash
# Point camera at flow cell under microscope
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.20

# Everything else stays the same!
```

## Example Output

### Console During Detection

```
================================================================================
YOLOV8 REAL-TIME DETECTION
================================================================================
Model: best.pt
Camera: 0
Confidence threshold: 0.2

Camera: 1920x1080 @ 15.0 FPS
Press 'q' to quit, 's' to save snapshot

[Detection running...]
```

### After Session

```
================================================================================
SESSION COMPLETE
================================================================================
Model: best.pt
Duration: 45.3s
Frames: 678
Average FPS: 15.0
Total detections: 234

Class breakdown:
  copepod: 108 (46.2%)
  diatom: 78 (33.3%)
  dinoflagellate: 48 (20.5%)
================================================================================
```

## Why YOLO for Your Demo?

1. **Fast** - Real-time detection at 20-30 FPS
2. **Accurate** - Industry-standard object detection
3. **Visual** - Bounding boxes are impressive
4. **Professional** - Used in production systems worldwide
5. **Your Model** - `best.pt` is custom trained for your data

## Quick Commands Reference

```bash
# Setup (one time)
./setup_yolo.sh

# Run demo (recommended)
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.20

# Save video
python yolo_realtime.py --model "Downloaded models/best.pt" --save-video

# Different camera
python yolo_realtime.py --model "Downloaded models/best.pt" --camera 1

# Process video file
python yolo_realtime.py --model "Downloaded models/best.pt" --camera video.mp4
```

## Summary

**You now have:**
✅ 3 YOLO models ready to use
✅ Real-time detection script (`yolo_realtime.py`)
✅ Easy setup script (`setup_yolo.sh`)
✅ Complete documentation

**Time to first detection**: 3 minutes
- Install: 2 minutes
- Run: 1 command
- Demo ready!

**The ONE command for your demo:**
```bash
python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.20
```

**Wow factor**: Very High! 🎯
**Ease of use**: One command
**Performance**: Real-time, professional

Good luck with your demo! 🚀
