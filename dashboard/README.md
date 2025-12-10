# Marine Plankton AI Dashboard

Comprehensive web-based GUI for the Marine Plankton AI Microscopy System.

## 🚀 Quick Start

### Option 1: Use the Launcher Script (Recommended)

```bash
# From project root
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Option 2: Manual Launch

```bash
# Activate environment
source .venv/bin/activate

# Install requirements (if needed)
pip install streamlit plotly pandas

# Run dashboard
streamlit run dashboard/app_comprehensive.py
```

The dashboard will open automatically at `http://localhost:8501`

## 📋 Features

### 1. 🏠 Home Page
- System overview and capabilities
- Quick stats and metrics
- Recent activity log
- Model performance comparison
- Getting started guide

### 2. 📸 Single Image Analysis
- **Camera capture** or file upload
- **Multiple analysis methods:**
  - Full pipeline (7-stage processing)
  - Quick classification
  - YOLO detection
- Real-time results visualization
- Species distribution charts
- Diversity metrics
- Bloom detection alerts

### 3. 📹 Video Analysis
- **YOLO-based object detection** on videos
- **Three processing modes:**
  - Real-time
  - Slow motion
  - Enhanced
- Video upload or use test videos
- Adjustable confidence thresholds
- Output video download
- Processing log viewing

### 4. 🔬 Flow Cell Scanner
- **Real-time continuous scanning**
- System diagnostics
- Camera testing
- **Two scanner modes:**
  - GUI (with live display)
  - Headless (background operation)
- Configurable flow rate and duration
- Session results and summaries
- Concentration calculations

### 5. 📦 Batch Processing
- **Process multiple images** at once
- Upload 10s or 100s of images
- Parallel processing option
- Progress tracking
- Batch summary statistics
- Individual result saving

### 6. 📊 Results Dashboard
- **Visualize all past analyses**
- Browse result files
- Flow cell session history
- Video results gallery
- Cumulative analytics
- Species distribution trends
- Download capabilities

### 7. 🤖 Model Management
- **View all available models**
- YOLO models (detection)
- Classification models (species ID)
- Model metadata
- Size and modification dates
- Model download instructions

### 8. ⚙️ Settings
- **System configuration**
- Classification parameters
- Analytics settings
- Bloom thresholds
- Export preferences
- Raw config viewer
- System information

## 🎯 Use Cases

### For Demonstrations

1. **Quick Demo (2 minutes):**
   - Go to "Single Image" tab
   - Upload test image
   - Run analysis
   - Show results charts

2. **Flow Cell Demo (5 minutes):**
   - Go to "Flow Cell" tab
   - Run diagnostics
   - Start 2-minute scan
   - Show session summary

3. **Video Demo (3 minutes):**
   - Go to "Video Analysis"
   - Select test video
   - Process with YOLO
   - Download annotated video

### For Research

1. **Batch Analysis:**
   - Upload field samples
   - Process in batch mode
   - Export results to CSV
   - Analyze trends

2. **Flow Cell Monitoring:**
   - Set up camera
   - Run extended scans
   - Track concentration
   - Log session data

### For Development

1. **Model Testing:**
   - Try different models
   - Compare performance
   - Adjust thresholds
   - Validate results

2. **Results Review:**
   - Browse past analyses
   - Check accuracy
   - Find edge cases
   - Export for training

## 🎨 User Interface

### Navigation
- **8 main tabs** for different functions
- **Sidebar** with system status and quick actions
- **Expandable sections** for detailed info
- **Responsive design** works on different screens

### Visual Features
- **Gradient headers** and modern styling
- **Color-coded metrics** for quick scanning
- **Interactive charts** with Plotly
- **Progress indicators** for long operations
- **Success/warning/error** message boxes

### Data Visualization
- **Pie charts** for species distribution
- **Bar charts** for counts and comparisons
- **Data tables** with sorting/filtering
- **Video playback** inline
- **Image galleries** for results

## 🔧 Technical Details

### Architecture

```
app_comprehensive.py
├── Main Navigation (8 tabs)
├── Sidebar (system info)
└── Pages:
    ├── Home (overview)
    ├── Single Image (pipeline/YOLO/classification)
    ├── Video Analysis (YOLO detection)
    ├── Flow Cell (continuous scanning)
    ├── Batch Processing (multiple images)
    ├── Results Dashboard (visualizations)
    ├── Model Management (model info)
    └── Settings (configuration)
```

### Integration Points

The dashboard integrates with:
- `pipeline/manager.py` - Full 7-stage pipeline
- `yolo_realtime.py` - Real-time YOLO detection
- `yolo_slow_motion.py` - Slow-motion processing
- `yolo_enhanced.py` - Enhanced video analysis
- `flow_cell_scanner.py` - GUI flow cell scanner
- `flow_cell_headless.py` - Headless scanner
- `diagnose_flow_cell.py` - System diagnostics
- `config/config.yaml` - System configuration

### Dependencies

```python
streamlit>=1.28.0      # Web framework
plotly>=5.17.0         # Interactive charts
pandas>=2.1.0          # Data handling
opencv-python>=4.8.0   # Image processing
numpy>=1.24.0          # Numerical operations
pillow>=10.0.0         # Image I/O
pyyaml>=6.0            # Config loading
```

## 📊 Dashboard Files

```
dashboard/
├── app_comprehensive.py   # Main comprehensive dashboard (NEW)
├── app.py                 # Original pipeline dashboard
├── app_simple.py          # Simplified version
└── README.md              # This file
```

## 🎓 Tips for Best Experience

### Performance
1. **Use test images first** to verify setup
2. **Start with small batches** before processing many images
3. **Close unused tabs** to save memory
4. **Use headless mode** for long flow cell scans

### Workflow
1. **Test camera/video** before main analysis
2. **Run diagnostics** if flow cell issues
3. **Check Results tab** for past analyses
4. **Adjust confidence** if too many/few detections

### Troubleshooting
1. **If model loading fails**: Check Models tab
2. **If processing is slow**: Use quick mode
3. **If video won't play**: Check format (MP4/MOV)
4. **If results missing**: Check results/ directory

## 🚧 Known Limitations

1. **TensorFlow mutex lock** on some macOS systems
   - Workaround: Use command-line tools
   - Or reinstall TensorFlow for macOS

2. **Webcam support** not yet implemented
   - Use file upload instead
   - Or use flow cell camera mode

3. **Real-time preview** limited for flow cell
   - Use GUI mode for live view
   - Or check session results after

4. **Large batch processing** may timeout
   - Process in smaller batches
   - Or use parallel mode

## 📱 Mobile/Tablet Support

The dashboard is **responsive** and works on:
- Desktop browsers (Chrome, Firefox, Safari)
- Tablet devices (iPad, Android tablets)
- Large phones (landscape mode)

For best experience, use desktop with:
- **Screen size:** 1920x1080 or larger
- **Browser:** Chrome or Firefox
- **RAM:** 8GB+ for video processing

## 🎯 For Demo/Presentation

### Before the Demo
1. Run diagnostics: Check all systems working
2. Prepare test data: Have good quality images/videos
3. Practice workflow: Run through each tab once
4. Check results folder: Clean up or showcase past work

### During the Demo
1. **Start with Home:** Show system overview
2. **Single Image:** Quick analysis demonstration
3. **Video Analysis:** Show YOLO in action
4. **Flow Cell:** Explain real-time capability
5. **Results:** Show cumulative data/trends

### After the Demo
1. Export results for attendees
2. Show model management
3. Discuss settings/customization
4. Answer questions with live demos

## 📚 Related Documentation

- `FLOW_CELL_QUICK_START.md` - Flow cell setup
- `YOLO_QUICK_START.md` - YOLO detection guide
- `README.md` - Main project README
- `docs/DEVELOPER_GUIDE.md` - Development info

## 🤝 Support

For issues or questions:
1. Check system diagnostics in Flow Cell tab
2. Review logs in terminal where dashboard runs
3. Check `results/` directory for output files
4. Refer to main project documentation

## 🎉 Credits

Built for **Smart India Hackathon 2025**

**Features include:**
- Real-time plankton detection
- Multi-model support (YOLO + CNNs)
- Flow cell scanning capability
- Batch processing
- Comprehensive analytics
- Professional visualization

---

**Version:** 1.0.0
**Last Updated:** December 2025
**Status:** Production Ready ✅
