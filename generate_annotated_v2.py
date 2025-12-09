#!/usr/bin/env python3
"""
Generate annotated images with bounding boxes - Version 2
Directly accesses pipeline modules to get bounding boxes
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import cv2
import numpy as np
from pathlib import Path
import pickle
from config.config_loader import load_config

# Import individual modules
from modules.acquisition import AcquisitionModule
from modules.preprocessing import PreprocessingModule
from modules.segmentation import SegmentationModule
from modules.classification_real import ClassificationModuleReal


def draw_bounding_boxes(image, predictions, class_names):
    """
    Draw bounding boxes and labels on image

    Args:
        image: Original image
        predictions: List of prediction dicts from classification (includes bounding_box)
        class_names: List of class names

    Returns:
        Annotated image
    """
    annotated = image.copy()

    # Color palette
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 128, 0),
        (0, 128, 255), (128, 255, 0), (255, 128, 128), (128, 255, 128)
    ]

    for idx, pred in enumerate(predictions):
        bbox = pred['bounding_box']
        x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
        class_name = pred['class_name']
        confidence = pred['confidence']

        # Find class_id for color selection
        try:
            class_id = class_names.index(class_name)
        except:
            class_id = idx

        # Select color
        color = colors[class_id % len(colors)]

        # Draw bounding box
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 3)

        # Prepare label
        label = f"{class_name} {confidence*100:.1f}%"
        label_id = f"[{idx+1}]"

        # Draw label background and text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2

        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        (id_width, id_height), _ = cv2.getTextSize(label_id, font, font_scale, thickness)

        # Background for main label
        cv2.rectangle(annotated, (x, y - text_height - 15), (x + text_width + 10, y), color, -1)
        # Background for ID
        cv2.rectangle(annotated, (x + w - id_width - 10, y - id_height - 15), (x + w, y), color, -1)

        # Draw text
        cv2.putText(annotated, label, (x + 5, y - 8), font, font_scale, (255, 255, 255), thickness)
        cv2.putText(annotated, label_id, (x + w - id_width - 5, y - 8), font, font_scale, (255, 255, 255), thickness)

    return annotated


def process_image_with_boxes(image_path, config, class_names):
    """
    Process single image through pipeline and get bounding boxes

    Returns:
        (annotated_image, num_organisms) or (None, 0) if failed
    """
    # Initialize modules
    acquisition = AcquisitionModule(config.get('acquisition', {}))
    preprocessing = PreprocessingModule(config.get('preprocessing', {}))
    segmentation = SegmentationModule(config.get('segmentation', {}))
    classification = ClassificationModuleReal(config.get('classification', {}))

    # Step 1: Acquisition
    acq_result = acquisition.process({
        'mode': 'file',
        'image_path': str(image_path),
        'magnification': 2.0,
        'exposure_ms': 100
    })

    if acq_result['status'] != 'success':
        print(f"    ❌ Acquisition failed")
        return None, 0

    original_image = acq_result['image']

    # Step 2: Preprocessing
    prep_result = preprocessing.process({
        'image': original_image,
        'preprocessing_config': config.get('preprocessing', {})
    })

    if prep_result['status'] != 'success':
        print(f"    ❌ Preprocessing failed")
        return None, 0

    # Step 3: Segmentation
    seg_result = segmentation.process({
        'image': prep_result['processed_image'],
        'segmentation_config': config.get('segmentation', {})
    })

    if seg_result['status'] != 'success':
        print(f"    ❌ Segmentation failed")
        return None, 0

    num_detected = seg_result['num_detected']

    if num_detected == 0:
        print(f"    ℹ️  No organisms detected")
        return None, 0

    # Step 4: Classification
    class_result = classification.process({
        'image': prep_result['processed_image'],
        'masks': seg_result['masks'],
        'bounding_boxes': seg_result['bounding_boxes'],
        'classification_config': config.get('classification', {})
    })

    if class_result['status'] != 'success':
        print(f"    ❌ Classification failed")
        return None, 0

    predictions = class_result['predictions']

    # Filter by confidence threshold
    threshold = config.get('counting', {}).get('confidence_threshold', 0.3)
    filtered_predictions = []

    for pred in predictions:
        if pred['confidence'] >= threshold:
            filtered_predictions.append(pred)

    if not filtered_predictions:
        print(f"    ℹ️  No organisms passed confidence threshold")
        return None, 0

    # Draw annotations
    annotated = draw_bounding_boxes(original_image, filtered_predictions, class_names)

    return annotated, len(filtered_predictions)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate annotated images with bounding boxes (v2)')
    parser.add_argument('input_dir', type=str, help='Directory containing images')
    parser.add_argument('-o', '--output', type=str, default='results/annotated',
                       help='Output directory (default: results/annotated)')

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Load class names
    metadata_path = 'models/model_metadata.pkl'
    if Path(metadata_path).exists():
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        class_names = metadata['class_names']
    else:
        print("⚠️  Warning: Model metadata not found")
        class_names = []

    # Find images
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(args.input_dir).glob(f'*{ext}'))
        image_files.extend(Path(args.input_dir).glob(f'*{ext.upper()}'))

    image_files = sorted(image_files)

    if not image_files:
        print(f"❌ No images found in {args.input_dir}")
        return

    print(f"🔍 Found {len(image_files)} images")
    print(f"📁 Output directory: {args.output}\n")

    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Process each image
    total_annotated = 0

    for img_num, image_path in enumerate(image_files, 1):
        print(f"[{img_num}/{len(image_files)}] Processing: {image_path.name}")

        try:
            annotated, num_organisms = process_image_with_boxes(image_path, config, class_names)

            if annotated is not None:
                # Save annotated image
                output_filename = f"annotated_{image_path.name}"
                output_filepath = output_path / output_filename
                cv2.imwrite(str(output_filepath), annotated)

                print(f"    ✅ {num_organisms} organisms annotated")
                print(f"    💾 Saved: {output_filepath}\n")
                total_annotated += 1
            else:
                print()

        except Exception as e:
            print(f"    ❌ Error: {str(e)}\n")

    # Print summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total images processed: {len(image_files)}")
    print(f"Annotated images generated: {total_annotated}")
    print(f"\nAnnotated images saved in: {args.output}/")
    print("="*60)


if __name__ == '__main__':
    main()
