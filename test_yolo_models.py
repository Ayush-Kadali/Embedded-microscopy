#!/usr/bin/env python3
"""
Quick test to verify YOLO models can be loaded.
Run this after installing dependencies.
"""

import sys
from pathlib import Path

print("="*80)
print("YOLO MODEL TEST")
print("="*80)
print()

# Check dependencies
print("1. Checking dependencies...")
print("-"*80)

try:
    import torch
    print(f"✅ PyTorch installed: {torch.__version__}")
except ImportError:
    print("❌ PyTorch not installed")
    print("   Run: ./setup_yolo.sh")
    sys.exit(1)

try:
    import cv2
    print(f"✅ OpenCV installed: {cv2.__version__}")
except ImportError:
    print("❌ OpenCV not installed")
    print("   Run: pip install opencv-python")
    sys.exit(1)

try:
    from ultralytics import YOLO
    print(f"✅ Ultralytics installed")
    has_ultralytics = True
except ImportError:
    print("⚠️  Ultralytics not installed (needed for YOLOv8)")
    print("   Run: pip install ultralytics")
    has_ultralytics = False

print()

# Check models
print("2. Checking models...")
print("-"*80)

models_dir = Path("Downloaded models")
if not models_dir.exists():
    print(f"❌ Directory not found: {models_dir}")
    sys.exit(1)

models = {
    'best.pt': models_dir / 'best.pt',
    'yolov5nu.pt': models_dir / 'yolov5nu.pt',
    'yolov8n.pt': models_dir / 'yolov8n.pt',
}

for name, path in models.items():
    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"✅ {name:<15} ({size_mb:.1f} MB)")
    else:
        print(f"❌ {name:<15} NOT FOUND")

print()

# Try loading a model
print("3. Testing model loading...")
print("-"*80)

test_model = models_dir / 'best.pt'

if test_model.exists():
    print(f"Attempting to load: {test_model.name}")

    try:
        if has_ultralytics:
            print("  Trying ultralytics (YOLOv8)...")
            model = YOLO(str(test_model))
            print(f"  ✅ Loaded successfully with ultralytics")
            print(f"  Model type: {type(model)}")
            if hasattr(model, 'names'):
                print(f"  Classes: {list(model.names.values())[:5]}...")
        else:
            print("  Trying torch.hub (YOLOv5)...")
            model = torch.hub.load('ultralytics/yolov5', 'custom',
                                  path=str(test_model), force_reload=False)
            print(f"  ✅ Loaded successfully with torch.hub")
            print(f"  Model type: {type(model)}")
            if hasattr(model, 'names'):
                print(f"  Classes: {model.names[:5]}...")

        print()
        print("="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print()
        print("You're ready to run:")
        print(f'  python yolo_realtime.py --model "Downloaded models/best.pt"')
        print()

    except Exception as e:
        print(f"  ❌ Error loading model: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure dependencies are installed: ./setup_yolo.sh")
        print("  2. Check model file is not corrupted")
        print("  3. Try different model type flag in yolo_realtime.py")
        sys.exit(1)
else:
    print(f"❌ Test model not found: {test_model}")
    sys.exit(1)
