#!/usr/bin/env python3
"""
Simple test comparing Model 1 vs Model 2
Uses existing working pipeline infrastructure
"""

import sys
import numpy as np
from pathlib import Path
import tensorflow as tf

print("=" * 80)
print("SIMPLE TWO-MODEL COMPARISON TEST")
print("=" * 80)

# Check models exist
model_1_path = 'models/plankton_classifier.keras'
model_2_path = 'models/plankton_mobilenet_v2_best.keras'

if not Path(model_1_path).exists():
    print(f"✗ Model 1 not found: {model_1_path}")
    sys.exit(1)

if not Path(model_2_path).exists():
    print(f"✗ Model 2 not found: {model_2_path}")
    sys.exit(1)

print("\n[1/3] Loading models...")
model_1 = tf.keras.models.load_model(model_1_path)
print(f"  ✓ Model 1 loaded: {model_1_path}")

model_2 = tf.keras.models.load_model(model_2_path)
print(f"  ✓ Model 2 loaded: {model_2_path}")

# Class names
class_names = [
    'Alexandrium', 'Asterionellopsis glacialis', 'Cerataulina', 'Ceratium',
    'Chaetoceros', 'Entomoneis', 'Guinardia', 'Hemiaulus',
    'Lauderia annulata', 'Nitzschia', 'Noctiluca', 'Ornithocercus magnificus',
    'Pinnularia', 'Pleurosigma', 'Prorocentrum', 'Protoperidinium',
    'Pyrodinium', 'Thalassionema', 'Thalassiosira'
]

# Create test images (random for demonstration)
print("\n[2/3] Creating test images...")
test_image_224 = np.random.rand(5, 224, 224, 3).astype(np.float32)  # 5 test images for Model 1
test_image_128 = np.random.rand(5, 128, 128, 3).astype(np.float32)  # 5 test images for Model 2
print("  ✓ Test images created (5 samples)")

# Test Model 1
print("\n[3/3] Running predictions...")
print("\nModel 1 (EfficientNetB0 - 224x224 input):")
pred_1 = model_1.predict(test_image_224, verbose=0)
for i in range(5):
    class_idx = np.argmax(pred_1[i])
    conf = pred_1[i][class_idx]
    print(f"  Sample {i+1}: {class_names[class_idx]} ({conf*100:.1f}%)")

avg_conf_1 = np.mean([np.max(p) for p in pred_1])
print(f"  Average confidence: {avg_conf_1*100:.1f}%")

# Test Model 2
print("\nModel 2 (MobileNetV2 - 128x128 input):")

# Preprocess for MobileNetV2
test_image_128_preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(test_image_128 * 255)

pred_2 = model_2.predict(test_image_128_preprocessed, verbose=0)
for i in range(5):
    class_idx = np.argmax(pred_2[i])
    conf = pred_2[i][class_idx]
    print(f"  Sample {i+1}: {class_names[class_idx]} ({conf*100:.1f}%)")

avg_conf_2 = np.mean([np.max(p) for p in pred_2])
print(f"  Average confidence: {avg_conf_2*100:.1f}%")

# Ensemble test
print("\nEnsemble (50/50 weighted average):")
# Need to match sizes - use first 5 samples
ensemble_pred = (pred_1 + pred_2) / 2  # Simple average

for i in range(5):
    class_idx = np.argmax(ensemble_pred[i])
    conf = ensemble_pred[i][class_idx]
    print(f"  Sample {i+1}: {class_names[class_idx]} ({conf*100:.1f}%)")

avg_conf_ens = np.mean([np.max(p) for p in ensemble_pred])
print(f"  Average confidence: {avg_conf_ens*100:.1f}%")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
Both models loaded and working!

Model 1 (EfficientNetB0):
  - Input size: 224x224
  - Average confidence: {avg_conf_1*100:.1f}%
  - Status: ✓ Working

Model 2 (MobileNetV2):
  - Input size: 128x128
  - Average confidence: {avg_conf_2*100:.1f}%
  - Status: ✓ Working

Ensemble:
  - Combines both models
  - Average confidence: {avg_conf_ens*100:.1f}%
  - Status: ✓ Working

Next steps:
  1. Both models are ready to use
  2. Use ClassificationMultiModel in your pipeline
  3. Set mode in config: 'model_1', 'model_2', or 'ensemble'
  4. Test with real plankton images

To use with real images:
  python test_with_real_images.py
  (Update to use ClassificationMultiModel if needed)
""")
print("=" * 80)
