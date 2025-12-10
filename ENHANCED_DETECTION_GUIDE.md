# Enhanced YOLO Detection - Fixing Dust and Blur Issues

## The Problem

❌ **Dust particles** being detected as plankton (false positives)
❌ **Blurry video** making real plankton hard to detect
❌ **Sensor noise** creating false detections

## The Solution

✅ **Image Enhancement**: Sharpening, denoising, contrast adjustment
✅ **Size Filtering**: Remove detections too small (dust) or too large (artifacts)
✅ **Higher Confidence**: Only show high-confidence detections
✅ **Aspect Ratio Filtering**: Remove weird-shaped detections

## Current Run

The enhanced detector is running with:
- **Confidence**: 0.40 (higher = fewer false positives)
- **Min size**: 80 pixels (filters dust)
- **Max size**: 350 pixels (filters artifacts)
- **Processing**: Every 3rd frame (faster)
- **Output**: `results/yolo_enhanced_20251211_031559.mp4`

## What You Should See

**Window layout**:
```
┌─────────────────┬─────────────────┐
│   Original      │   Enhanced      │
│   (Blurry)      │   (Sharpened)   │
│                 │                 │
│  [Detections]   │  [Detections]   │
│                 │                 │
│  Stats:         │                 │
│  Valid: X       │                 │
│  Filtered: Y    │                 │
└─────────────────┴─────────────────┘
```

**Stats explanation**:
- **Valid Detections**: Real plankton (passed all filters)
- **Filtered (dust/noise)**: Removed because too small, low confidence, or wrong shape

## Adjusting Settings

### Too Many False Positives Still?

**Increase confidence** (fewer detections, higher quality):
```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.50 \
    --min-size 100 \
    --delay 150 \
    --save
```

### Missing Real Plankton?

**Decrease confidence, smaller min-size** (more detections):
```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.25 \
    --min-size 50 \
    --delay 150 \
    --save
```

### Video Too Blurry - Disable Preprocessing

Sometimes preprocessing makes it worse:
```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.35 \
    --min-size 80 \
    --no-preprocess \
    --save
```

### Very Slow Playback for Inspection

```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.30 \
    --min-size 70 \
    --delay 300 \
    --skip-frames 5 \
    --save
```

## Parameter Guide

| Parameter | What It Does | Recommended Range |
|-----------|--------------|-------------------|
| `--conf` | Confidence threshold | 0.25 - 0.50 |
| `--min-size` | Minimum detection size (filters dust) | 50 - 120 pixels |
| `--max-size` | Maximum detection size (filters artifacts) | 300 - 500 pixels |
| `--delay` | ms between frames (higher = slower) | 100 - 500 ms |
| `--skip-frames` | Process every Nth frame | 1 - 5 |

## Understanding the Filters

### Size Filter

Dust particles are usually **very small** (< 50 pixels)
Real plankton are typically **50-300 pixels** at your magnification

**Current setting**: 80-350 pixels

**Adjust if**:
- Dust still getting through → Increase `--min-size`
- Real plankton being filtered → Decrease `--min-size`

### Confidence Filter

Lower confidence (0.15-0.25) = More detections, more false positives
Higher confidence (0.40-0.60) = Fewer detections, more accurate

**Current setting**: 0.40

**Adjust if**:
- Too many dust detections → Increase `--conf`
- Missing real plankton → Decrease `--conf`

### Aspect Ratio Filter

Automatically filters:
- Very thin boxes (aspect ratio < 0.2)
- Very wide boxes (aspect ratio > 5.0)

These are usually artifacts, not real organisms.

## Image Enhancement Features

### 1. Sharpening
Makes blurry edges clearer
**Good for**: Improving detection of edges

### 2. Denoising
Reduces sensor noise/grain
**Good for**: Reducing false detections from noise

### 3. CLAHE (Contrast Enhancement)
Improves local contrast
**Good for**: Seeing low-contrast organisms

**If these make it worse**, use `--no-preprocess`

## Expected Results

**Good scenario**:
- Valid detections: Actual moving organisms
- Filtered: Dust, sensor noise, static artifacts
- Clean bounding boxes around real objects

**Problem scenario**:
- All detections filtered → Settings too strict
- Still detecting dust → Settings too loose
- No detections at all → Model not suitable for this video

## Alternative: Try Different Model

Your `best.pt` model might be trained on clearer images. Try:

```bash
# Try YOLOv8n (general purpose)
python yolo_enhanced.py \
    --model "Downloaded models/yolov8n.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.30 \
    --min-size 70 \
    --save

# Or YOLOv5nu
python yolo_enhanced.py \
    --model "Downloaded models/yolov5nu.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.30 \
    --min-size 70 \
    --save
```

## Recommended Settings for Your Case

Based on your description (dust detection, blurry organisms):

**Conservative (fewer false positives)**:
```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.45 \
    --min-size 90 \
    --max-size 300 \
    --delay 200 \
    --skip-frames 2 \
    --save
```

**Balanced (try this first)**:
```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.35 \
    --min-size 75 \
    --max-size 350 \
    --delay 150 \
    --skip-frames 3 \
    --save
```

**Sensitive (catch more, may have some false positives)**:
```bash
python yolo_enhanced.py \
    --model "Downloaded models/best.pt" \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --conf 0.25 \
    --min-size 60 \
    --max-size 400 \
    --delay 150 \
    --skip-frames 2 \
    --save
```

## Next Steps

1. **Watch the current output** - See if filtering helps
2. **Check the stats** - How many filtered vs valid?
3. **Adjust settings** - Based on what you see
4. **Try different models** - If best.pt doesn't work well
5. **Let me know** - I can help tune the parameters further

## Output Files

- **Side-by-side video**: `results/yolo_enhanced_*.mp4`
- Shows original vs enhanced side by side
- Green text = valid detections kept
- Orange text = filtered out (dust/noise)

## Key Insight

**The model might not be well-suited for this video** if:
- Video quality is very different from training data
- Organisms are much blurrier than training images
- Model was trained on different magnification/clarity

**Solutions**:
1. Enhance the video more aggressively
2. Retrain the model on blurry/noisy examples
3. Use a more general object detection model
4. Improve video capture quality (better focus, lighting, camera)

Let me know how it looks and I can help adjust further!
