#!/bin/bash

# YOLO Dependencies Setup Script

echo "Setting up YOLO dependencies..."
echo ""

# Activate virtual environment
source .venv/bin/activate

# Install PyTorch (CPU version for faster install)
echo "Installing PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install ultralytics (for YOLOv8)
echo "Installing ultralytics (YOLOv8)..."
pip install ultralytics

# Install additional dependencies for YOLOv5
echo "Installing YOLOv5 dependencies..."
pip install opencv-python

echo ""
echo "✅ Setup complete!"
echo ""
echo "Test with:"
echo '  python yolo_realtime.py --model "Downloaded models/best.pt"'
