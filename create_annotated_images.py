#!/usr/bin/env python3
"""
Create annotated images showing detected organisms with bounding boxes and labels
"""

import cv2
import numpy as np
import yaml
from pathlib import Path
from datetime import datetime
from pipeline.manager import PipelineManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def draw_annotations(image, predictions, bboxes):
    """Draw bounding boxes and labels on image"""
    annotated = image.copy()

    colors = {
        'Asterionellopsis glacialis': (0, 255, 0),
        'default': (255, 0, 0)
    }

    for pred, bbox in zip(predictions, bboxes):
        x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
        class_name = pred['class_name']
        confidence = pred['confidence']

        # Get color
        color = colors.get(class_name, colors['default'])

        # Draw bounding box
        cv2.rectangle(annotated, (x, y), (x+w, y+h), color, 2)

        # Prepare label
        label = f"{class_name[:20]}: {confidence:.2f}"

        # Draw label background
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x, y-label_h-10), (x+label_w+10, y), color, -1)

        # Draw label text
        cv2.putText(annotated, label, (x+5, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw organism ID
        cv2.putText(annotated, f"#{pred['organism_id']}",
                   (x+5, y+h-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    return annotated

def main():
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)

    # Initialize pipeline
    logger.info("Initializing pipeline...")
    pipeline = PipelineManager(config)

    # Get all test images
    test_dir = Path('test_images')
    image_files = list(test_dir.glob('*.png')) + list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.jpeg'))
    image_files = sorted(image_files)

    # Create output directory
    output_dir = Path('results/annotated_images')
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Found {len(image_files)} test images")
    logger.info(f"Output directory: {output_dir}\n")

    for idx, img_path in enumerate(image_files, 1):
        logger.info("=" * 80)
        logger.info(f"Processing {idx}/{len(image_files)}: {img_path.name}")
        logger.info("=" * 80)

        try:
            # Get modules
            acq = pipeline.modules['acquisition']
            prep = pipeline.modules['preprocessing']
            seg = pipeline.modules['segmentation']
            clf = pipeline.modules['classification']

            # Stage 1: Acquisition
            r1 = acq.process({
                'mode': 'file',
                'image_path': str(img_path),
                'magnification': 2.0,
                'exposure_ms': 100,
                'capture_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'operator_id': 'annotation'
                }
            })

            # Stage 2: Preprocessing
            r2 = prep.process({
                'image': r1['image'],
                'preprocessing_config': config.get('preprocessing', {}),
            })

            # Stage 3: Segmentation
            r3 = seg.process({
                'image': r2['processed_image'],
                'segmentation_config': config.get('segmentation', {}),
            })

            # Stage 4: Classification
            r4 = clf.process({
                'image': r2['processed_image'],
                'masks': r3['masks'],
                'bounding_boxes': r3['bounding_boxes'],
                'classification_config': config.get('classification', {}),
            })

            # Draw annotations on original image
            annotated = draw_annotations(
                r1['image'],
                r4['predictions'],
                r3['bounding_boxes']
            )

            # Save annotated image
            output_path = output_dir / f"annotated_{img_path.stem}.jpg"
            cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

            logger.info(f"✅ Created: {output_path}")
            logger.info(f"   Organisms: {len(r4['predictions'])}")

            # Also create a side-by-side comparison
            original_rgb = r1['image']

            # Resize if needed to fit side by side
            h, w = original_rgb.shape[:2]
            max_width = 1920
            if w * 2 > max_width:
                scale = max_width / (w * 2)
                new_w = int(w * scale)
                new_h = int(h * scale)
                original_rgb = cv2.resize(original_rgb, (new_w, new_h))
                annotated = cv2.resize(annotated, (new_w, new_h))

            # Create side-by-side
            side_by_side = np.hstack([original_rgb, annotated])

            # Add titles
            title_height = 50
            titled = np.ones((side_by_side.shape[0] + title_height, side_by_side.shape[1], 3), dtype=np.uint8) * 255
            titled[title_height:] = side_by_side

            # Add text
            cv2.putText(titled, "Original", (10, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(titled, f"Detected: {len(r4['predictions'])} organisms",
                       (original_rgb.shape[1] + 10, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            comparison_path = output_dir / f"comparison_{img_path.stem}.jpg"
            cv2.imwrite(str(comparison_path), cv2.cvtColor(titled, cv2.COLOR_RGB2BGR))
            logger.info(f"✅ Created: {comparison_path}\n")

        except Exception as e:
            logger.error(f"❌ Failed: {img_path.name}")
            logger.error(f"   Error: {str(e)}\n")

    logger.info("=" * 80)
    logger.info("COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Annotated images saved to: {output_dir}/")
    logger.info("Files:")
    logger.info("  • annotated_*.jpg  - Images with bounding boxes")
    logger.info("  • comparison_*.jpg - Side-by-side original vs annotated")
    logger.info("=" * 80)

    return 0

if __name__ == '__main__':
    exit(main())
