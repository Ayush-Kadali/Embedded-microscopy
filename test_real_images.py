#!/usr/bin/env python3
"""
Test pipeline with real plankton images from dataset.

This script allows you to test the pipeline with actual plankton images
to verify segmentation, classification, and analysis work with real data.

Usage:
    # Test with single image
    python test_real_images.py --image path/to/image.jpg

    # Test with directory (processes all images)
    python test_real_images.py --directory datasets/processed/

    # Test with specific number of images
    python test_real_images.py --directory datasets/processed/ --limit 5
"""

import argparse
import yaml
import logging
from pathlib import Path
from datetime import datetime

from pipeline.manager import PipelineManager
from pipeline.validators import ConfigValidator
from utils.visualization import PipelineVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_single_image(
    image_path: Path,
    manager: PipelineManager,
    visualizer: PipelineVisualizer
):
    """Test pipeline with a single image."""
    logger.info(f"Processing: {image_path}")

    # Prepare acquisition parameters for file mode
    acquisition_params = {
        'mode': 'file',
        'image_path': str(image_path),
        'magnification': 2.0,  # Default value
        'exposure_ms': 100,    # Default value
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'gps_lat': None,
            'gps_lon': None,
            'operator_id': 'test'
        }
    }

    # Step 1: Acquisition
    logger.info("[1/7] Loading image...")
    acq_result = manager.modules['acquisition'].process(acquisition_params)

    if acq_result['status'] != 'success':
        logger.error(f"Failed to load image: {acq_result.get('error_message')}")
        return None

    image = acq_result['image']
    metadata = acq_result['metadata']
    sample_id = metadata['capture_id']

    logger.info(f"  ✓ Loaded: {image.shape}")

    # Save original image
    vis_paths = {}
    vis_paths['original'] = visualizer.save_original_image(
        image, sample_id, metadata
    )

    # Step 2: Preprocessing
    logger.info("[2/7] Preprocessing...")
    prep_input = {
        'image': image,
        'preprocessing_config': manager.config['preprocessing']
    }
    prep_result = manager.modules['preprocessing'].process(prep_input)

    if prep_result['status'] != 'success':
        logger.error(f"Preprocessing failed: {prep_result.get('error_message')}")
        return None

    preprocessed = prep_result['processed_image']
    prep_stats = prep_result['preprocessing_stats']
    vis_paths['preprocessed'] = visualizer.save_preprocessed_image(
        preprocessed, sample_id, prep_stats
    )

    # Step 3: Segmentation
    logger.info("[3/7] Segmenting...")
    seg_input = {
        'image': preprocessed,
        'metadata': metadata,
        'segmentation_config': manager.config['segmentation']
    }
    seg_result = manager.modules['segmentation'].process(seg_input)

    if seg_result['status'] != 'success':
        logger.error(f"Segmentation failed: {seg_result.get('error_message')}")
        return None

    logger.info(f"  ✓ Found {len(seg_result['segments'])} organisms")
    vis_paths['segmented'] = visualizer.save_segmented_image(
        preprocessed, seg_result['segments'], sample_id
    )

    # Step 4: Classification
    logger.info("[4/7] Classifying...")
    class_input = {
        'segments': seg_result,
        'image': preprocessed,
        'classification_config': manager.config['classification']
    }
    class_result = manager.modules['classification'].process(class_input)

    if class_result['status'] != 'success':
        logger.error(f"Classification failed: {class_result.get('error_message')}")
        return None

    vis_paths['classified'] = visualizer.save_classified_image(
        preprocessed, class_result['classified_segments'], sample_id
    )

    # Step 5: Counting
    logger.info("[5/7] Counting...")
    count_input = {
        'classified_segments': class_result['classified_segments'],
        'metadata': metadata,
        'counting_config': manager.config['counting']
    }
    count_result = manager.modules['counting'].process(count_input)

    if count_result['status'] != 'success':
        logger.error(f"Counting failed: {count_result.get('error_message')}")
        return None

    logger.info(f"  ✓ Total organisms: {count_result['total_organisms']}")
    for class_name, count in count_result['counts_by_class'].items():
        logger.info(f"    {class_name}: {count}")

    # Step 6: Analytics
    logger.info("[6/7] Analyzing...")
    analytics_input = {
        'counts_by_class': count_result['counts_by_class'],
        'organisms': count_result['organisms'],
        'analytics_config': manager.config['analytics']
    }
    analytics_result = manager.modules['analytics'].process(analytics_input)

    if analytics_result['status'] != 'success':
        logger.error(f"Analytics failed: {analytics_result.get('error_message')}")
        return None

    logger.info(f"  ✓ Shannon diversity: {analytics_result['shannon_diversity']:.3f}")
    logger.info(f"  ✓ Simpson diversity: {analytics_result['simpson_diversity']:.3f}")
    if analytics_result['bloom_alerts']:
        logger.warning(f"  ⚠ Bloom alerts: {analytics_result['bloom_alerts']}")

    # Step 7: Export
    logger.info("[7/7] Exporting...")
    export_input = {
        'counts_by_class': count_result['counts_by_class'],
        'organisms': count_result['organisms'],
        'diversity_metrics': analytics_result,
        'metadata': metadata,
        'export_config': manager.config['export']
    }
    export_result = manager.modules['export'].process(export_input)

    if export_result['status'] != 'success':
        logger.error(f"Export failed: {export_result.get('error_message')}")
        return None

    # Create summary visualization
    summary_path = visualizer.create_summary_grid(
        sample_id,
        vis_paths,
        count_result,
        analytics_result
    )

    logger.info(f"\n{'='*80}")
    logger.info(f"SUCCESS: {image_path.name}")
    logger.info(f"{'='*80}")
    logger.info(f"Sample ID: {sample_id}")
    logger.info(f"Organisms: {count_result['total_organisms']}")
    logger.info(f"Species: {count_result['species_richness']}")
    logger.info(f"Diversity: {analytics_result['shannon_diversity']:.3f}")
    logger.info(f"Summary: {summary_path}")
    logger.info(f"{'='*80}\n")

    return {
        'image_path': image_path,
        'sample_id': sample_id,
        'results': count_result,
        'analytics': analytics_result,
        'exported_files': export_result['exported_files'],
        'visualization': summary_path
    }


def main():
    parser = argparse.ArgumentParser(
        description='Test pipeline with real plankton images'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--image',
        type=str,
        help='Path to single image file'
    )
    parser.add_argument(
        '--directory',
        type=str,
        help='Path to directory containing images'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of images to process'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        default='*.jpg',
        help='File pattern for directory mode (default: *.jpg)'
    )

    args = parser.parse_args()

    if not args.image and not args.directory:
        parser.error("Must specify either --image or --directory")

    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    # Validate configuration
    is_valid, errors = ConfigValidator.validate(config)
    if not is_valid:
        logger.error("Configuration validation failed!")
        for error in errors:
            logger.error(f"  - {error}")
        return 1

    # Initialize pipeline
    logger.info("Initializing pipeline...")
    manager = PipelineManager(config)

    # Initialize visualizer
    output_dir = Path('results/real_images')
    output_dir.mkdir(parents=True, exist_ok=True)
    visualizer = PipelineVisualizer(output_dir)

    # Collect images to process
    if args.image:
        images = [Path(args.image)]
    else:
        image_dir = Path(args.directory)
        images = sorted(image_dir.glob(args.pattern))

        if args.limit:
            images = images[:args.limit]

    logger.info(f"Found {len(images)} images to process\n")

    # Process images
    results = []
    for i, image_path in enumerate(images, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"IMAGE {i}/{len(images)}: {image_path.name}")
        logger.info(f"{'='*80}")

        result = test_single_image(image_path, manager, visualizer)
        if result:
            results.append(result)

    # Summary
    logger.info(f"\n{'='*80}")
    logger.info(f"BATCH COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"Processed: {len(results)}/{len(images)} images")
    logger.info(f"Failed: {len(images) - len(results)}")

    if results:
        total_organisms = sum(r['results']['total_organisms'] for r in results)
        avg_diversity = sum(r['analytics']['shannon_diversity'] for r in results) / len(results)

        logger.info(f"\nAggregate Statistics:")
        logger.info(f"  Total organisms: {total_organisms}")
        logger.info(f"  Average diversity: {avg_diversity:.3f}")
        logger.info(f"\nResults saved to: {output_dir}")

    logger.info(f"{'='*80}\n")

    return 0 if len(results) == len(images) else 1


if __name__ == '__main__':
    exit(main())
