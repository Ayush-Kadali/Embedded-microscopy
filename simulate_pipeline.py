#!/usr/bin/env python3
"""
Pipeline Simulation with Visual Output

Runs the complete pipeline and saves annotated images at each stage.
This helps verify the pipeline is working and visualize the processing steps.

Usage:
    python simulate_pipeline.py [--num-samples N] [--output-dir DIR]
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


def simulate_single_sample(
    manager: PipelineManager,
    visualizer: PipelineVisualizer,
    magnification: float = 2.5,
    exposure_ms: int = 150,
    sample_num: int = 1
) -> dict:
    """
    Simulate a single sample through the pipeline with visualization.

    Args:
        manager: Pipeline manager instance
        visualizer: Visualization utility instance
        magnification: Microscope magnification
        exposure_ms: Exposure time in milliseconds
        sample_num: Sample number for logging

    Returns:
        Dictionary with pipeline results and visualization paths
    """
    logger.info(f"=" * 80)
    logger.info(f"SAMPLE {sample_num}: Starting pipeline simulation")
    logger.info(f"=" * 80)

    # Prepare acquisition parameters
    acquisition_params = {
        'magnification': magnification,
        'exposure_ms': exposure_ms,
        'focus_position': None,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'gps_lat': None,
            'gps_lon': None,
            'operator_id': 'simulation'
        }
    }

    # Step 1: Acquisition
    logger.info("[1/7] Acquiring image...")
    acq_result = manager.modules['acquisition'].process(acquisition_params)

    if acq_result['status'] != 'success':
        logger.error(f"Acquisition failed: {acq_result.get('error_message')}")
        return None

    image = acq_result['image']
    metadata = acq_result['metadata']
    sample_id = metadata['capture_id']

    logger.info(f"  ✓ Image acquired: {image.shape}")
    logger.info(f"  ✓ Sample ID: {sample_id}")

    # Save original image
    vis_paths = {}
    vis_paths['original'] = visualizer.save_original_image(
        image, sample_id, metadata
    )
    logger.info(f"  ✓ Saved: {vis_paths['original']}")

    # Step 2: Preprocessing
    logger.info("[2/7] Preprocessing image...")
    prep_input = {
        'image': image,
        'preprocessing_config': manager.config['preprocessing']
    }
    prep_result = manager.modules['preprocessing'].process(prep_input)

    if prep_result['status'] != 'success':
        logger.error(f"Preprocessing failed: {prep_result.get('error_message')}")
        return None

    preprocessed_image = prep_result['processed_image']
    logger.info(f"  ✓ Preprocessing complete")

    # Save preprocessed image
    vis_paths['preprocessed'] = visualizer.save_preprocessed_image(
        preprocessed_image, sample_id, prep_result['preprocessing_stats']
    )
    logger.info(f"  ✓ Saved: {vis_paths['preprocessed']}")

    # Step 3: Segmentation
    logger.info("[3/7] Segmenting organisms...")
    seg_input = {
        'image': preprocessed_image,
        'segmentation_config': manager.config['segmentation']
    }
    seg_result = manager.modules['segmentation'].process(seg_input)

    if seg_result['status'] != 'success':
        logger.error(f"Segmentation failed: {seg_result.get('error_message')}")
        return None

    masks = seg_result['masks']
    bounding_boxes = seg_result['bounding_boxes']
    centroids = seg_result['centroids']
    areas_px = seg_result['areas_px']
    logger.info(f"  ✓ Detected: {len(masks)} organisms")

    # Save segmentation image
    vis_paths['segmentation'] = visualizer.save_segmentation_image(
        preprocessed_image, sample_id, masks, bounding_boxes, centroids
    )
    logger.info(f"  ✓ Saved: {vis_paths['segmentation']}")

    # Step 4: Classification
    logger.info("[4/7] Classifying organisms...")
    class_input = {
        'image': preprocessed_image,
        'masks': masks,
        'bounding_boxes': bounding_boxes,
        'classification_config': manager.config['classification']
    }
    class_result = manager.modules['classification'].process(class_input)

    if class_result['status'] != 'success':
        logger.error(f"Classification failed: {class_result.get('error_message')}")
        return None

    predictions = class_result['predictions']
    logger.info(f"  ✓ Classified: {len(predictions)} organisms")

    # Log class distribution
    class_counts = {}
    for pred in predictions:
        class_name = pred['class_name']
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    for class_name, count in sorted(class_counts.items()):
        logger.info(f"    - {class_name}: {count}")

    # Save classification image
    vis_paths['classification'] = visualizer.save_classification_image(
        preprocessed_image, sample_id, bounding_boxes, predictions
    )
    logger.info(f"  ✓ Saved: {vis_paths['classification']}")

    # Step 5: Counting
    logger.info("[5/7] Counting organisms...")
    count_input = {
        'predictions': predictions,
        'masks': masks,
        'bounding_boxes': bounding_boxes,
        'centroids': centroids,
        'areas_px': areas_px,
        'metadata': metadata,
        'counting_config': manager.config['counting']
    }
    count_result = manager.modules['counting'].process(count_input)

    if count_result['status'] != 'success':
        logger.error(f"Counting failed: {count_result.get('error_message')}")
        return None

    counts_by_class = count_result['counts_by_class']
    organisms = count_result['organisms']
    total_count = count_result['total_count']
    logger.info(f"  ✓ Total organisms: {total_count}")

    # Step 6: Analytics
    logger.info("[6/7] Computing diversity metrics...")
    analytics_input = {
        'counts_by_class': counts_by_class,
        'organisms': organisms,
        'metadata': metadata,
        'analytics_config': manager.config['analytics']
    }
    analytics_result = manager.modules['analytics'].process(analytics_input)

    if analytics_result['status'] != 'success':
        logger.error(f"Analytics failed: {analytics_result.get('error_message')}")
        return None

    diversity_indices = analytics_result['diversity_indices']
    bloom_alerts = analytics_result['bloom_alerts']

    logger.info(f"  ✓ Shannon diversity: {diversity_indices['shannon']:.3f}")
    logger.info(f"  ✓ Species richness: {diversity_indices['species_richness']}")
    logger.info(f"  ✓ Bloom alerts: {len(bloom_alerts)}")

    # Save final analysis
    vis_paths['final'] = visualizer.save_final_analysis(
        preprocessed_image, sample_id, counts_by_class,
        diversity_indices, bloom_alerts
    )
    logger.info(f"  ✓ Saved: {vis_paths['final']}")

    # Step 7: Export
    logger.info("[7/7] Exporting results...")
    export_input = {
        'metadata': metadata,
        'counts_by_class': counts_by_class,
        'organisms': organisms,
        'diversity_indices': diversity_indices,
        'bloom_alerts': bloom_alerts,
        'export_config': manager.config['export']
    }
    export_result = manager.modules['export'].process(export_input)

    if export_result['status'] != 'success':
        logger.error(f"Export failed: {export_result.get('error_message')}")
        return None

    logger.info(f"  ✓ Exported files:")
    for file_path in export_result['exported_files']:
        logger.info(f"    - {file_path}")

    # Create summary grid
    logger.info("Creating summary grid...")
    grid_path = visualizer.create_summary_grid(
        sample_id,
        [
            vis_paths['original'],
            vis_paths['preprocessed'],
            vis_paths['segmentation'],
            vis_paths['classification'],
            vis_paths['final']
        ]
    )
    vis_paths['grid'] = grid_path
    logger.info(f"  ✓ Saved: {grid_path}")

    # Save complete metadata
    complete_metadata = {
        'sample_id': sample_id,
        'acquisition': metadata,
        'preprocessing': prep_result['preprocessing_stats'],
        'segmentation': {
            'num_organisms': len(masks),
            'algorithm': seg_result.get('algorithm', 'unknown')
        },
        'classification': {
            'num_predictions': len(predictions),
            'model_metadata': class_result.get('model_metadata', {})
        },
        'counting': {
            'total_count': total_count,
            'counts_by_class': counts_by_class
        },
        'analytics': {
            'diversity_indices': diversity_indices,
            'bloom_alerts': bloom_alerts
        },
        'visualization_paths': vis_paths
    }

    metadata_path = visualizer.save_metadata_json(sample_id, complete_metadata)
    logger.info(f"  ✓ Saved metadata: {metadata_path}")

    logger.info(f"=" * 80)
    logger.info(f"SAMPLE {sample_num}: Pipeline simulation complete!")
    logger.info(f"=" * 80)
    logger.info("")

    return {
        'sample_id': sample_id,
        'results': complete_metadata,
        'visualization_paths': vis_paths
    }


def main():
    """Main simulation function."""
    parser = argparse.ArgumentParser(
        description='Simulate plankton analysis pipeline with visual output'
    )
    parser.add_argument(
        '--num-samples', '-n',
        type=int,
        default=1,
        help='Number of samples to simulate (default: 1)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='results/simulation',
        help='Output directory for visualization images (default: results/simulation)'
    )
    parser.add_argument(
        '--magnification', '-m',
        type=float,
        default=2.5,
        help='Microscope magnification (default: 2.5)'
    )
    parser.add_argument(
        '--exposure', '-e',
        type=int,
        default=150,
        help='Exposure time in ms (default: 150)'
    )

    args = parser.parse_args()

    # Load configuration
    logger.info("Loading configuration...")
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Validate configuration
    validator = ConfigValidator()
    validator.validate(config)
    logger.info("  ✓ Configuration validated")

    # Initialize pipeline
    logger.info("Initializing pipeline...")
    manager = PipelineManager(config)
    logger.info("  ✓ Pipeline initialized")

    # Initialize visualizer
    logger.info(f"Initializing visualizer (output: {args.output_dir})...")
    visualizer = PipelineVisualizer(output_dir=args.output_dir)
    logger.info("  ✓ Visualizer initialized")
    logger.info("")

    # Run simulations
    results = []
    for i in range(args.num_samples):
        result = simulate_single_sample(
            manager=manager,
            visualizer=visualizer,
            magnification=args.magnification,
            exposure_ms=args.exposure,
            sample_num=i + 1
        )

        if result:
            results.append(result)
        else:
            logger.error(f"Sample {i + 1} failed!")

    # Summary
    logger.info("=" * 80)
    logger.info("SIMULATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Samples simulated: {len(results)}/{args.num_samples}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info("")

    if results:
        logger.info("Generated visualizations:")
        for result in results:
            sample_id = result['sample_id']
            logger.info(f"\n  Sample: {sample_id}")
            for stage, path in result['visualization_paths'].items():
                logger.info(f"    - {stage}: {path}")

        logger.info("")
        logger.info("✓ Simulation complete! Check the output directory for images.")
        logger.info(f"  → Open {args.output_dir} to view results")

    else:
        logger.error("No successful simulations!")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
