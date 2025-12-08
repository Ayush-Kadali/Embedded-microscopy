#!/usr/bin/env python3
"""
Main entry point for Marine Plankton AI Microscopy System.

This demonstrates how to use the modular pipeline.
"""

import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path
from pipeline import PipelineManager, ConfigValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Marine Plankton AI Microscopy System'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--magnification',
        type=float,
        default=2.0,
        help='Microscope magnification (0.7-4.5)'
    )
    parser.add_argument(
        '--exposure',
        type=int,
        default=100,
        help='Exposure time in milliseconds'
    )
    parser.add_argument(
        '--gps-lat',
        type=float,
        help='GPS latitude'
    )
    parser.add_argument(
        '--gps-lon',
        type=float,
        help='GPS longitude'
    )
    parser.add_argument(
        '--operator',
        type=str,
        default='demo',
        help='Operator ID'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate configuration and exit'
    )

    args = parser.parse_args()

    # Load configuration
    logger.info(f"Loading configuration from {args.config}")
    config = load_config(args.config)

    # Validate configuration
    is_valid, errors = ConfigValidator.validate(config)
    if not is_valid:
        logger.error("Configuration validation failed!")
        for error in errors:
            logger.error(f"  - {error}")
        return 1

    if args.validate_only:
        logger.info("Configuration is valid!")
        return 0

    # Initialize pipeline
    logger.info("Initializing pipeline...")
    pipeline = PipelineManager(config)

    # Prepare acquisition parameters
    acquisition_params = {
        'magnification': args.magnification,
        'exposure_ms': args.exposure,
        'focus_position': None,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'gps_lat': args.gps_lat,
            'gps_lon': args.gps_lon,
            'operator_id': args.operator,
        },
    }

    # Execute pipeline
    logger.info("Executing pipeline...")
    result = pipeline.execute_pipeline(acquisition_params)

    # Check result
    if result['status'] == 'success':
        logger.info("\n" + "="*80)
        logger.info("PIPELINE EXECUTION SUCCESSFUL")
        logger.info("="*80)
        logger.info("\nSummary:")
        logger.info(f"  Capture ID: {result['summary']['capture_id']}")
        logger.info(f"  Timestamp: {result['summary']['timestamp']}")
        logger.info(f"  Total organisms: {result['summary']['total_organisms']}")
        logger.info(f"  Species richness: {result['summary']['species_richness']}")
        logger.info(f"  Shannon diversity: {result['summary']['shannon_diversity']:.3f}")
        logger.info(f"  Bloom alerts: {result['summary']['bloom_alerts']}")

        logger.info("\nCounts by class:")
        for class_name, count in result['summary']['counts_by_class'].items():
            logger.info(f"  {class_name}: {count}")

        logger.info("\nExported files:")
        for filepath in result['exported_files']:
            logger.info(f"  {filepath}")

        if result.get('dashboard_url'):
            logger.info(f"\nDashboard: {result['dashboard_url']}")

        logger.info("="*80)
        return 0
    else:
        logger.error("\n" + "="*80)
        logger.error("PIPELINE EXECUTION FAILED")
        logger.error("="*80)
        logger.error(f"Failed at: {result.get('failed_at')}")
        logger.error(f"Error: {result.get('error_message')}")
        logger.error("="*80)
        return 1


if __name__ == '__main__':
    exit(main())
