#!/bin/bash
# Quick launcher for live detection demo with bounding boxes

echo "🔬 Starting Live Detection Demo..."
echo "=================================="
echo ""
echo "This will show you:"
echo "✅ Real-time YOLO detection"
echo "✅ Bounding boxes on images"
echo "✅ Annotated visualizations"
echo "✅ Detection statistics"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found"
    exit 1
fi

# Set environment
export TF_CPP_MIN_LOG_LEVEL=2
export CUDA_VISIBLE_DEVICES=-1

echo "🚀 Launching Streamlit demo..."
echo ""
echo "   Access at: http://localhost:8501"
echo ""

# Run the demo
streamlit run demo_realtime_detection.py
