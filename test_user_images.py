#!/usr/bin/env python3
"""
Test classification with user's test images from test_images folder
"""

import yaml
from pathlib import Path
from datetime import datetime
from pipeline.manager import PipelineManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    logger.info(f"Found {len(image_files)} test images\n")

    results_summary = []

    for idx, img_path in enumerate(image_files, 1):
        logger.info("=" * 80)
        logger.info(f"TEST {idx}/{len(image_files)}: {img_path.name}")
        logger.info("=" * 80)

        acquisition_params = {
            'mode': 'file',
            'image_path': str(img_path),
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'operator_id': 'user_test',
                'source_file': img_path.name
            }
        }

        try:
            # Execute pipeline
            result = pipeline.execute_pipeline(acquisition_params)

            if result['status'] == 'success':
                logger.info(f"\n✅ SUCCESS: {img_path.name}")
                logger.info(f"  Organisms detected: {result['summary']['total_organisms']}")
                logger.info(f"  Species richness: {result['summary']['species_richness']}")
                logger.info(f"  Shannon diversity: {result['summary']['shannon_diversity']:.3f}")

                if result['summary']['counts_by_class']:
                    logger.info("\n  Counts by class:")
                    for class_name, count in result['summary']['counts_by_class'].items():
                        logger.info(f"    {class_name}: {count}")
                else:
                    logger.info("\n  No organisms passed confidence threshold")

                logger.info("\n  Exported files:")
                for file_path in result.get('exported_files', []):
                    logger.info(f"    {file_path}")

                results_summary.append({
                    'file': img_path.name,
                    'status': 'success',
                    'organisms': result['summary']['total_organisms'],
                    'species': result['summary']['species_richness'],
                    'counts': result['summary']['counts_by_class']
                })
            else:
                logger.error(f"\n❌ FAILED: {img_path.name}")
                logger.error(f"  Error: {result.get('error_message')}")
                results_summary.append({
                    'file': img_path.name,
                    'status': 'failed',
                    'error': result.get('error_message')
                })

        except Exception as e:
            logger.error(f"\n❌ EXCEPTION: {img_path.name}")
            logger.error(f"  Error: {str(e)}")
            results_summary.append({
                'file': img_path.name,
                'status': 'exception',
                'error': str(e)
            })

        logger.info("")

    # Print final summary
    logger.info("=" * 80)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 80)

    successful = [r for r in results_summary if r['status'] == 'success']
    failed = [r for r in results_summary if r['status'] != 'success']

    logger.info(f"\nTotal images: {len(image_files)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")

    if successful:
        total_organisms = sum(r['organisms'] for r in successful)
        logger.info(f"\nTotal organisms detected: {total_organisms}")

        # Aggregate species counts
        all_species = {}
        for r in successful:
            for species, count in r.get('counts', {}).items():
                all_species[species] = all_species.get(species, 0) + count

        if all_species:
            logger.info("\nSpecies summary across all images:")
            for species, count in sorted(all_species.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {species}: {count}")

    logger.info("\nResults saved in: ./results/")
    logger.info("=" * 80)

    return 0 if len(failed) == 0 else 1

if __name__ == '__main__':
    exit(main())
