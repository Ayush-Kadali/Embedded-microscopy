#!/usr/bin/env python3
"""
Fast Command-Line Utility for Plankton Analysis
Optimized for speed and efficiency
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import sys
import argparse
from pathlib import Path
import cv2
import numpy as np
import pickle
from datetime import datetime

# Global variables for lazy loading
MODEL = None
CLASS_NAMES = None
INPUT_SIZE = 224


def load_model_once():
    """Load model only once (lazy loading)"""
    global MODEL, CLASS_NAMES, INPUT_SIZE

    if MODEL is not None:
        return MODEL, CLASS_NAMES, INPUT_SIZE

    import tensorflow as tf

    model_path = 'models/best_model_checkpoint.keras'
    metadata_path = 'models/model_metadata.pkl'

    if not Path(model_path).exists():
        print(f"❌ Model not found: {model_path}")
        sys.exit(1)

    # Load model
    MODEL = tf.keras.models.load_model(model_path)

    # Load metadata
    if Path(metadata_path).exists():
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        CLASS_NAMES = metadata['class_names']
    else:
        print("⚠️  Metadata not found, using default class names")
        CLASS_NAMES = []

    return MODEL, CLASS_NAMES, INPUT_SIZE


def classify_image_fast(image_path):
    """Fast classification of a single image"""
    model, class_names, input_size = load_model_once()

    # Read and preprocess
    img = cv2.imread(str(image_path))
    if img is None:
        return None, "Failed to read image"

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (input_size, input_size))
    img = img.astype('float32') / 255.0

    # Predict
    img_batch = np.expand_dims(img, axis=0)
    predictions = model.predict(img_batch, verbose=0)[0]

    # Get top predictions
    top_indices = np.argsort(predictions)[::-1][:5]

    results = []
    for idx in top_indices:
        class_name = class_names[idx] if idx < len(class_names) else f"Class_{idx}"
        confidence = float(predictions[idx])
        results.append((class_name, confidence))

    return results, None


def print_results(image_path, results):
    """Print results in a clean format"""
    print(f"\n{'='*60}")
    print(f"📷 Image: {image_path.name}")
    print(f"{'='*60}")

    if results:
        print("\nTop 5 Predictions:")
        for i, (class_name, confidence) in enumerate(results, 1):
            bar_length = int(confidence * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            print(f"{i}. {class_name:30s} {confidence*100:6.2f}% {bar}")

        best_class, best_conf = results[0]
        print(f"\n🎯 Best: {best_class} ({best_conf*100:.2f}%)")
    else:
        print("❌ No predictions")


def process_folder_fast(folder_path, output_file=None):
    """Process all images in a folder efficiently"""
    # Find images
    image_files = []
    for ext in ('.jpg', '.jpeg', '.png', '.bmp'):
        image_files.extend(Path(folder_path).glob(f'*{ext}'))
        image_files.extend(Path(folder_path).glob(f'*{ext.upper()}'))

    image_files = sorted(image_files)

    if not image_files:
        print(f"❌ No images found in {folder_path}")
        return

    print(f"🔍 Found {len(image_files)} images")
    print("🔬 Processing...\n")

    # Load model once
    load_model_once()

    # Process all images
    all_results = {}
    for image_path in image_files:
        results, error = classify_image_fast(image_path)
        if error:
            print(f"⚠️  {image_path.name}: {error}")
        else:
            all_results[image_path.name] = results
            print(f"✅ {image_path.name}: {results[0][0]} ({results[0][1]*100:.1f}%)")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    species_counts = {}
    for results in all_results.values():
        if results:
            species = results[0][0]
            species_counts[species] = species_counts.get(species, 0) + 1

    print(f"\nTotal Images: {len(all_results)}")
    print(f"Species Distribution:")
    for species in sorted(species_counts.keys()):
        count = species_counts[species]
        pct = count / len(all_results) * 100
        print(f"  {species:30s}: {count:3d} images ({pct:5.1f}%)")

    # Save to file if requested
    if output_file:
        import json
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_images': len(all_results),
            'results': {
                name: [{'species': r[0], 'confidence': r[1]} for r in results]
                for name, results in all_results.items()
            },
            'summary': species_counts
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Fast plankton classification CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify single image
  python plankton_cli.py image.png

  # Classify all images in folder
  python plankton_cli.py images/ -o results.json

  # Quick batch classification
  python plankton_cli.py test_images/
        """
    )

    parser.add_argument('input', type=str,
                       help='Image file or directory to process')
    parser.add_argument('-o', '--output', type=str,
                       help='Output JSON file (optional)')

    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ Not found: {input_path}")
        sys.exit(1)

    # Single image or folder?
    if input_path.is_file():
        print("🔬 Analyzing single image...")
        results, error = classify_image_fast(input_path)

        if error:
            print(f"❌ Error: {error}")
            sys.exit(1)

        print_results(input_path, results)

    elif input_path.is_dir():
        process_folder_fast(input_path, args.output)

    else:
        print(f"❌ Invalid input: {input_path}")
        sys.exit(1)

    print("\n✅ Done!\n")


if __name__ == '__main__':
    main()
