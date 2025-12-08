#!/usr/bin/env python3
"""
Quick test with real plankton images using existing pipeline infrastructure
"""

import yaml
import logging
from pathlib import Path
from datetime import datetime

from pipeline.manager import PipelineManager
from pipeline.validators import ConfigValidator
from utils.visualization import PipelineVisualizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)

    # Validate
    is_valid, errors = ConfigValidator.validate(config)
    if not is_valid:
        logger.error("Config validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1

    # Initialize pipeline
    logger.info("Initializing pipeline...")
    pipeline = PipelineManager(config)

    # Initialize visualizer
    output_dir = Path('results/real_images_test')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find real images
    sample_dir = Path('datasets/processed/samples')
    images = list(sample_dir.glob('*.png'))[:3]  # Test with 3 images

    logger.info(f"Found {len(images)} test images\n")

    for i, img_path in enumerate(images, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST {i}/{len(images)}: {img_path.name}")
        logger.info(f"{'='*80}")

        # Modify acquisition to use file mode
        acquisition_params = {
            'mode': 'file',
            'image_path': str(img_path),
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'gps_lat': None,
                'gps_lon': None,
                'operator_id': 'real_image_test'
            }
        }

        # Execute pipeline
        result = pipeline.execute_pipeline(acquisition_params)

        if result['status'] == 'success':
            logger.info(f"\n✅ SUCCESS: {img_path.name}")
            logger.info(f"  Organisms detected: {result['summary']['total_organisms']}")
            logger.info(f"  Species richness: {result['summary']['species_richness']}")
            logger.info(f"  Shannon diversity: {result['summary']['shannon_diversity']:.3f}")

            logger.info(f"\n  Counts by class:")
            for class_name, count in result['summary']['counts_by_class'].items():
                logger.info(f"    {class_name}: {count}")

            logger.info(f"\n  Exported files:")
            for filepath in result['exported_files']:
                logger.info(f"    {filepath}")
        else:
            logger.error(f"\n❌ FAILED: {img_path.name}")
            logger.error(f"  Failed at: {result.get('failed_at')}")
            logger.error(f"  Error: {result.get('error_message')}")

    logger.info(f"\n{'='*80}")
    logger.info("ALL TESTS COMPLETE")
    logger.info(f"{'='*80}\n")

    return 0


if __name__ == '__main__':
    exit(main())
