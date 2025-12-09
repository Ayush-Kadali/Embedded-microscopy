#!/usr/bin/env python3
"""
Generate annotated images with bounding boxes and species labels
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from pipeline.manager import PipelineManager
from config.config_loader import load_config
import json

def draw_annotated_image(image, organisms, class_names):
    """
    Draw bounding boxes and labels on image

    Args:
        image: Original image
        organisms: List of detected organisms with predictions
        class_names: List of class names from model

    Returns:
        Annotated image with bounding boxes and labels
    """
    annotated = image.copy()

    # Color palette for different classes
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 128, 0),
        (0, 128, 255), (128, 255, 0)
    ]

    for idx, organism in enumerate(organisms):
        # Get bounding box
        bbox = organism.get('bounding_box', [0, 0, 10, 10])
        x, y, w, h = bbox

        # Get prediction
        class_id = organism.get('class_id', 0)
        confidence = organism.get('confidence', 0.0)

        # Get class name
        if class_id < len(class_names):
            class_name = class_names[class_id]
        else:
            class_name = f"Class_{class_id}"

        # Select color
        color = colors[class_id % len(colors)]

        # Draw bounding box
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

        # Prepare label
        label = f"{class_name} {confidence*100:.1f}% [ID:{idx+1}]"

        # Calculate text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)

        # Draw label background
        cv2.rectangle(annotated, (x, y - text_height - 10), (x + text_width + 5, y), color, -1)

        # Draw label text
        cv2.putText(annotated, label, (x + 2, y - 5), font, font_scale, (255, 255, 255), thickness)

    return annotated


def process_images_with_annotation(input_dir, output_dir="results/annotated"):
    """
    Process all images in a directory and generate annotated versions

    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save annotated images
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all images
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(input_dir).glob(f'*{ext}'))
        image_files.extend(Path(input_dir).glob(f'*{ext.upper()}'))

    image_files = sorted(image_files)

    if not image_files:
        print(f"❌ No images found in {input_dir}")
        return

    print(f"🔍 Found {len(image_files)} images")
    print(f"📁 Output directory: {output_dir}\n")

    # Initialize pipeline
    print("⚙️  Initializing pipeline...")
    config = load_config()
    pipeline = PipelineManager(config)

    # Load model metadata to get class names
    import pickle
    metadata_path = 'models/model_metadata.pkl'
    if Path(metadata_path).exists():
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        class_names = metadata['class_names']
    else:
        class_names = []
        print("⚠️  Warning: Model metadata not found, class names may be incorrect")

    print(f"✅ Pipeline ready\n")

    # Process each image
    results_summary = []

    for img_num, image_path in enumerate(image_files, 1):
        print(f"[{img_num}/{len(image_files)}] Processing: {image_path.name}")

        try:
            # Read original image
            original_image = cv2.imread(str(image_path))
            if original_image is None:
                print(f"  ❌ Failed to read image\n")
                continue

            # Run pipeline
            acquisition_params = {
                'mode': 'file',
                'image_path': str(image_path),
                'magnification': 2.0,
                'exposure_ms': 100,
                'capture_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'operator_id': 'annotation',
                    'source_file': image_path.name
                }
            }

            result = pipeline.execute_pipeline(acquisition_params)

            if result['status'] != 'success':
                print(f"  ❌ Pipeline failed: {result.get('error_message')}\n")
                continue

            # Get organisms from results JSON
            capture_id = result['summary']['capture_id']
            json_file = Path(f"./results/results_{capture_id}.json")

            if json_file.exists():
                with open(json_file, 'r') as f:
                    detailed_results = json.load(f)
                organisms = detailed_results.get('organisms', [])
            else:
                organisms = []

            # Generate annotated image
            if organisms:
                annotated_image = draw_annotated_image(original_image, organisms, class_names)

                # Save annotated image
                output_filename = f"annotated_{image_path.name}"
                output_filepath = output_path / output_filename
                cv2.imwrite(str(output_filepath), annotated_image)

                print(f"  ✅ {result['summary']['total_organisms']} organisms detected")
                print(f"  💾 Saved: {output_filepath}\n")

                results_summary.append({
                    'file': image_path.name,
                    'organisms': result['summary']['total_organisms'],
                    'species': result['summary']['species_richness'],
                    'annotated_file': output_filename
                })
            else:
                print(f"  ℹ️  No organisms detected\n")
                results_summary.append({
                    'file': image_path.name,
                    'organisms': 0,
                    'species': 0,
                    'annotated_file': None
                })

        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")

    # Print summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total images processed: {len(results_summary)}")
    annotated_count = sum(1 for r in results_summary if r['annotated_file'])
    print(f"Annotated images generated: {annotated_count}")
    print(f"\nAnnotated images saved in: {output_dir}/")
    print("="*60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate annotated images with bounding boxes')
    parser.add_argument('input_dir', type=str, help='Directory containing images to process')
    parser.add_argument('-o', '--output', type=str, default='results/annotated',
                       help='Output directory for annotated images (default: results/annotated)')

    args = parser.parse_args()

    process_images_with_annotation(args.input_dir, args.output)
