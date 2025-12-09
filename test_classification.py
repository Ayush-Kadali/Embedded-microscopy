#!/usr/bin/env python3
"""
Simple test script for plankton classification
Tests the model on individual images or folders
"""

import os
import sys
import numpy as np
import cv2
import tensorflow as tf
import pickle
from pathlib import Path


def load_model_and_metadata():
    """Load the best trained model and its metadata"""
    # Use the best checkpoint
    model_path = 'models/best_model_checkpoint.keras'
    metadata_path = 'models/model_metadata.pkl'

    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        sys.exit(1)

    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    # The best_model_checkpoint uses EfficientNetB0 which requires 224x224
    input_size = 224

    # Load class names
    if os.path.exists(metadata_path):
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        class_names = metadata.get('class_names', [])
    else:
        # Try alternate location
        class_names_path = 'models/class_names.pkl'
        if os.path.exists(class_names_path):
            with open(class_names_path, 'rb') as f:
                class_names = pickle.load(f)
        else:
            class_names = []

    print(f"✅ Model loaded successfully")
    print(f"   Architecture: EfficientNetB0 Transfer Learning")
    print(f"   Input size: {input_size}x{input_size}")
    print(f"   Classes: {len(class_names)}")

    return model, class_names, input_size


def preprocess_image(image_path, input_size):
    """Preprocess a single image for prediction"""
    img = cv2.imread(str(image_path))
    if img is None:
        return None

    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize
    img = cv2.resize(img, (input_size, input_size))

    # Normalize
    img = img.astype('float32') / 255.0

    return img


def predict_image(model, image_path, class_names, input_size, top_k=3):
    """Predict the class of a single image"""
    img = preprocess_image(image_path, input_size)
    if img is None:
        print(f"❌ Failed to load image: {image_path}")
        return None

    # Add batch dimension
    img_batch = np.expand_dims(img, axis=0)

    # Predict
    predictions = model.predict(img_batch, verbose=0)[0]

    # Get top-k predictions
    top_indices = np.argsort(predictions)[::-1][:top_k]

    results = []
    for idx in top_indices:
        class_name = class_names[idx] if idx < len(class_names) else f"Class_{idx}"
        confidence = float(predictions[idx])
        results.append((class_name, confidence))

    return results


def test_image(model, image_path, class_names, input_size):
    """Test a single image and print results"""
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print(f"{'='*60}")

    results = predict_image(model, image_path, class_names, input_size, top_k=5)

    if results:
        print("\nTop 5 Predictions:")
        for i, (class_name, confidence) in enumerate(results, 1):
            bar_length = int(confidence * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            print(f"{i}. {class_name:30s} {confidence*100:6.2f}% {bar}")

        # Best prediction
        best_class, best_conf = results[0]
        print(f"\n🎯 Predicted: {best_class} ({best_conf*100:.2f}% confidence)")

    return results


def test_folder(model, folder_path, class_names, input_size):
    """Test all images in a folder"""
    folder = Path(folder_path)

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [f for f in folder.iterdir()
                   if f.is_file() and f.suffix.lower() in image_extensions]

    if not image_files:
        print(f"❌ No images found in {folder_path}")
        return

    print(f"\n{'='*60}")
    print(f"Testing {len(image_files)} images from: {folder_path}")
    print(f"{'='*60}")

    # Test each image
    all_results = []
    for img_file in sorted(image_files):
        results = test_image(model, img_file, class_names, input_size)
        if results:
            all_results.append((img_file.name, results[0]))

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY - {len(all_results)} images tested")
    print(f"{'='*60}")

    # Count predictions by class
    class_counts = {}
    for img_name, (class_name, confidence) in all_results:
        if class_name not in class_counts:
            class_counts[class_name] = []
        class_counts[class_name].append(confidence)

    print("\nPredicted species distribution:")
    for class_name in sorted(class_counts.keys()):
        confidences = class_counts[class_name]
        count = len(confidences)
        avg_conf = np.mean(confidences) * 100
        print(f"  {class_name:30s}: {count:3d} images (avg confidence: {avg_conf:.1f}%)")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_classification.py <image_file>       # Test single image")
        print("  python test_classification.py <folder>           # Test all images in folder")
        print("\nExamples:")
        print("  python test_classification.py test_images/image1.png")
        print("  python test_classification.py test_images/")
        print("  python test_classification.py external_test_samples/")
        sys.exit(1)

    target = sys.argv[1]

    # Load model
    model, class_names, input_size = load_model_and_metadata()

    # Test
    target_path = Path(target)

    if target_path.is_file():
        test_image(model, target_path, class_names, input_size)
    elif target_path.is_dir():
        test_folder(model, target_path, class_names, input_size)
    else:
        print(f"❌ Not found: {target}")
        sys.exit(1)

    print("\n✅ Testing complete!")


if __name__ == '__main__':
    main()
