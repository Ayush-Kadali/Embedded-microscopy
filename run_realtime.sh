#!/bin/bash
# Launch optimized real-time plankton detection

echo "🔬 Real-Time Plankton Detection System"
echo "======================================"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found"
    exit 1
fi

echo "🎯 Running on: Real_Time_Vids/only_water_stream.mov"
echo "📊 Confidence: 0.10 (optimized for detection)"
echo ""
echo "Controls:"
echo "  'q' - Quit"
echo "  's' - Save screenshot"
echo ""
echo "Starting..."
echo ""

# Run detection
python realtime_plankton_detection.py \
    --video "Real_Time_Vids/only_water_stream.mov" \
    --model "Downloaded models/best.pt" \
    --conf 0.10 \
    --skip-frames 1 \
    --save

echo ""
echo "✅ Done!"
