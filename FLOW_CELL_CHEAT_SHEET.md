# Flow Cell Scanner - Quick Reference

## 🚀 Quick Commands

### Test Camera (First!)
```bash
python test_flow_cell.py --camera 0
```
Press 'q' to quit

### Run Flow Cell Scan (Demo/Presentation)
```bash
python flow_cell_scanner.py --camera 0 --duration 120 --flow-rate 2.0
```
Press 'q' to stop early

### Headless Operation (No Display)
```bash
python flow_cell_headless.py --camera 0 --duration 120 --flow-rate 2.0
```
Ctrl+C to stop

## 📊 What You'll See

### Live Stats (Console)
```
─────────────────────────────────────────────
SESSION STATS - Elapsed: 45s
─────────────────────────────────────────────
Frames processed: 45
Total organisms: 234
Volume scanned: 0.750 mL
Concentration: 312.0 organisms/mL

Organisms by class:
  copepod: 108 (46.2%)
  diatom: 78 (33.3%)
  dinoflagellate: 48 (20.5%)
─────────────────────────────────────────────
```

### Live Window
- Camera feed
- Stats overlay
- Press 'q' to stop

## 🔧 Common Adjustments

### Change Flow Rate
```bash
--flow-rate 1.5    # For 1.5 mL/min
```

### Change Scan Duration
```bash
--duration 60      # 60 seconds
--duration 180     # 3 minutes
```

### Change Frame Capture Rate
```bash
--interval 1.0     # Every 1 second (default)
--interval 2.0     # Every 2 seconds (faster)
--interval 0.5     # Every 0.5 seconds (slower)
```

### Use Different Camera
```bash
--camera 0         # Default USB camera
--camera 1         # Second camera
--camera video.mp4 # Process video file
```

## 📁 Results Location
```bash
results/flow_cell_YYYYMMDD_HHMMSS/
├── session_summary.txt      # Main results
├── frame_000001.jpg         # Individual frames
├── frame_000002.jpg
└── preview_frame_10.jpg     # Preview images
```

View summary:
```bash
cat results/flow_cell_*/session_summary.txt
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera not found | `python test_flow_cell.py --list` |
| Too many detections | Edit `config/config.yaml`: increase `min_organism_size_px` |
| Missing organisms | Edit `config/config.yaml`: decrease `min_organism_size_px` |
| Too slow | Increase `--interval` to 2.0 or 3.0 |
| Blurry images | Adjust microscope focus manually |

## 📐 Flow Rate Calibration

1. Fill syringe with 10 mL
2. Start pump, time until empty
3. Calculate: `flow_rate = 10 / time_in_minutes`
4. Use calculated value: `--flow-rate X.X`

## 🎯 For Your Demo (4 hours)

### Setup Checklist (60 min)
- [ ] Assemble flow cell (slides + masking tape)
- [ ] Mount on microscope
- [ ] Connect camera
- [ ] Set up syringe pump
- [ ] Test camera: `python test_flow_cell.py --camera 0`
- [ ] Adjust focus

### Test Run (30 min)
```bash
# Short test
python flow_cell_scanner.py --camera 0 --duration 30

# Check results
cat results/flow_cell_*/session_summary.txt
```

### Calibration (30 min)
- [ ] Measure actual flow rate
- [ ] Adjust lighting
- [ ] Test different settings
- [ ] Practice start/stop

### Demo Preparation (60 min)
- [ ] Prepare water sample
- [ ] Clean flow cell
- [ ] Final test run
- [ ] Record backup video (if time)

### Final Demo Run (60 min)
```bash
# Recommended settings for demo
python flow_cell_scanner.py \
    --camera 0 \
    --duration 120 \
    --flow-rate 2.0 \
    --interval 1.5
```

## 🎓 Key Talking Points for Jury

### Innovation
✅ **Continuous flow** vs. static slide imaging
✅ **Real-time detection** with live feedback
✅ **Automated volume tracking** (organisms/mL)
✅ **Custom DIY flow cell** (low-cost innovation)
✅ **Scalable design** (works on laptop or Raspberry Pi)

### Technical Highlights
✅ Complete integration with existing ML pipeline
✅ Real-time computer vision processing
✅ Automated species classification
✅ Professional data export and logging
✅ Both GUI and headless operation modes

### Practical Benefits
✅ **Faster**: Continuous flow vs. slide-by-slide
✅ **More accurate**: Larger sample volume
✅ **Quantitative**: Concentration measurements
✅ **Field-ready**: Works on Raspberry Pi
✅ **Cost-effective**: DIY flow cell design

## 🆘 Emergency Commands

### If Something Goes Wrong
```bash
# Stop current scan
Press 'q' (in GUI mode)
Press Ctrl+C (in headless mode)

# Test camera again
python test_flow_cell.py --camera 0

# Restart scan
python flow_cell_scanner.py --camera 0 --duration 60
```

### Backup Plan: Use Video File
```bash
# If live camera fails, process pre-recorded video
python flow_cell_scanner.py --camera backup_video.mp4
```

## 📞 Quick Help

- **Quick Start Guide**: `FLOW_CELL_QUICK_START.md`
- **Complete Manual**: `FLOW_CELL_SYSTEM.md`
- **Main README**: `README.md`

## ⏱️ Timing for Demo

| Phase | Duration | Command |
|-------|----------|---------|
| Setup explanation | 2 min | (verbal) |
| Start scan | 30 sec | `python flow_cell_scanner.py --camera 0 --duration 120` |
| Show live processing | 2 min | (watch screen) |
| Explain results | 1 min | (point to stats) |
| Show final summary | 30 sec | `cat results/*/session_summary.txt` |
| **Total** | **6 min** | Perfect demo length! |

---

**Remember**:
- ✅ Camera 0 detected and working (1920x1080)
- ✅ All scripts ready and executable
- ✅ Documentation complete
- ✅ System tested and functional

**You're ready! Good luck! 🎉**
