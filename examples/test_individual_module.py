#!/usr/bin/env python3
"""
Example: Testing Individual Modules

This script demonstrates how to test modules independently
without running the full pipeline.

Use this as a template when developing your assigned module.
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def example_1_preprocessing():
    """Example: Test preprocessing module independently."""
    print("=" * 70)
    print("Example 1: Testing Preprocessing Module")
    print("=" * 70)

    from modules.preprocessing import PreprocessingModule

    # Create module with config
    config = {
        'denoise_method': 'bilateral',
        'normalize': True,
        'background_correction': True,
    }
    module = PreprocessingModule(config)

    # Create synthetic test image
    test_image = np.random.randint(100, 200, (500, 500, 3), dtype=np.uint8)
    print(f"Input image shape: {test_image.shape}")

    # Process
    result = module.process({
        'image': test_image,
        'preprocessing_config': config,
    })

    # Check result
    if result['status'] == 'success':
        print("✓ Processing successful")
        print(f"  Output shape: {result['processed_image'].shape}")
        print(f"  Mean intensity: {result['preprocessing_stats']['mean_intensity']:.1f}")
        print(f"  SNR: {result['preprocessing_stats']['snr_db']:.1f} dB")
    else:
        print(f"✗ Processing failed: {result['error_message']}")

    print()


def example_2_segmentation():
    """Example: Test segmentation module independently."""
    print("=" * 70)
    print("Example 2: Testing Segmentation Module")
    print("=" * 70)

    from modules.segmentation import SegmentationModule

    # Create module
    config = {
        'method': 'watershed',
        'min_area_px': 100,
        'max_area_px': 50000,
    }
    module = SegmentationModule(config)

    # Create synthetic image with blobs
    test_image = np.ones((500, 500, 3), dtype=np.uint8) * 220

    # Add some dark blobs (simulating organisms)
    for i in range(5):
        x = np.random.randint(50, 450)
        y = np.random.randint(50, 450)
        r = np.random.randint(20, 60)
        yy, xx = np.ogrid[-y:500-y, -x:500-x]
        mask = xx*xx + yy*yy <= r*r
        test_image[mask] = np.random.randint(50, 100, 3)

    print(f"Input image shape: {test_image.shape}")

    # Process
    result = module.process({
        'image': test_image,
        'segmentation_config': config,
    })

    # Check result
    if result['status'] == 'success':
        print("✓ Segmentation successful")
        print(f"  Organisms detected: {result['num_detected']}")
        print(f"  Bounding boxes: {len(result['bounding_boxes'])}")
        print(f"  Masks: {len(result['masks'])}")

        # Show details of first organism
        if result['num_detected'] > 0:
            print(f"\n  First organism:")
            print(f"    Centroid: {result['centroids'][0]}")
            print(f"    Area: {result['areas_px'][0]} pixels")
            print(f"    Bbox: {result['bounding_boxes'][0]}")
    else:
        print(f"✗ Segmentation failed: {result['error_message']}")

    print()


def example_3_counting():
    """Example: Test counting module independently."""
    print("=" * 70)
    print("Example 3: Testing Counting Module")
    print("=" * 70)

    from modules.counting import CountingModule

    # Create module
    config = {
        'confidence_threshold': 0.7,
        'size_range_um': [10, 1000],
    }
    module = CountingModule(config)

    # Create mock input data (as if from previous modules)
    predictions = [
        {'organism_id': 0, 'class_name': 'Copepod', 'confidence': 0.85},
        {'organism_id': 1, 'class_name': 'Diatom', 'confidence': 0.92},
        {'organism_id': 2, 'class_name': 'Copepod', 'confidence': 0.78},
        {'organism_id': 3, 'class_name': 'Dinoflagellate', 'confidence': 0.65},  # Below threshold
        {'organism_id': 4, 'class_name': 'Copepod', 'confidence': 0.88},
    ]

    areas_px = [1500, 2000, 1200, 800, 1800]
    centroids = [(100, 100), (200, 150), (300, 200), (150, 250), (400, 300)]

    metadata = {
        'resolution_um_per_px': 0.775,  # From 2.0x magnification
        'magnification': 2.0,
    }

    # Process
    result = module.process({
        'predictions': predictions,
        'areas_px': areas_px,
        'centroids': centroids,
        'metadata': metadata,
        'counting_config': config,
    })

    # Check result
    if result['status'] == 'success':
        print("✓ Counting successful")
        print(f"  Total organisms: {result['total_count']}")
        print(f"  Counts by class: {result['counts_by_class']}")
        print(f"\n  Size distribution:")
        for class_name, stats in result['size_distribution'].items():
            print(f"    {class_name}: mean={stats['mean_um']:.1f}µm, std={stats['std_um']:.1f}µm")
    else:
        print(f"✗ Counting failed: {result['error_message']}")

    print()


def example_4_analytics():
    """Example: Test analytics module independently."""
    print("=" * 70)
    print("Example 4: Testing Analytics Module")
    print("=" * 70)

    from modules.analytics import AnalyticsModule

    # Create module
    config = {
        'compute_diversity': True,
        'compute_composition': True,
        'bloom_thresholds': {
            'Dinoflagellate': 100,
            'Diatom': 200,
        }
    }
    module = AnalyticsModule(config)

    # Mock input data
    counts_by_class = {
        'Copepod': 45,
        'Diatom': 230,  # Above threshold - should trigger bloom alert
        'Dinoflagellate': 12,
        'Ciliate': 8,
    }

    organisms = []  # Can be empty for diversity calculation

    # Process
    result = module.process({
        'counts_by_class': counts_by_class,
        'organisms': organisms,
        'analytics_config': config,
    })

    # Check result
    if result['status'] == 'success':
        print("✓ Analytics successful")
        print(f"\n  Diversity Indices:")
        print(f"    Shannon: {result['diversity_indices']['shannon']:.3f}")
        print(f"    Simpson: {result['diversity_indices']['simpson']:.3f}")
        print(f"    Species richness: {result['diversity_indices']['species_richness']}")

        print(f"\n  Composition:")
        for class_name, percentage in result['composition'].items():
            print(f"    {class_name}: {percentage:.1f}%")

        print(f"\n  Bloom Alerts: {len(result['bloom_alerts'])}")
        for alert in result['bloom_alerts']:
            print(f"    ⚠️  {alert['class_name']}: {alert['count']} (threshold: {alert['threshold']})")
    else:
        print(f"✗ Analytics failed: {result['error_message']}")

    print()


def example_5_custom_module_template():
    """Template for testing your own module."""
    print("=" * 70)
    print("Example 5: Template for Your Module")
    print("=" * 70)

    print("""
    # Template for testing your module:

    from modules.your_module import YourModule

    # 1. Create configuration
    config = {
        'param1': 'value1',
        'param2': 'value2',
    }

    # 2. Initialize module
    module = YourModule(config)

    # 3. Prepare input data (following your module's input contract)
    input_data = {
        'required_field_1': value1,
        'required_field_2': value2,
    }

    # 4. Process
    result = module.process(input_data)

    # 5. Check result
    if result['status'] == 'success':
        print("✓ Success!")
        # Access output fields from your module's output contract
        print(f"Output field: {result['output_field']}")
    else:
        print(f"✗ Failed: {result['error_message']}")
    """)


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "Individual Module Testing Examples" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    examples = [
        example_1_preprocessing,
        example_2_segmentation,
        example_3_counting,
        example_4_analytics,
        example_5_custom_module_template,
    ]

    for example in examples:
        example()

    print("=" * 70)
    print("All examples completed!")
    print()
    print("Next steps:")
    print("  1. Modify these examples to test your module")
    print("  2. Create unit tests in tests/test_<module_name>.py")
    print("  3. See docs/DEVELOPER_GUIDE.md for more details")
    print("=" * 70)


if __name__ == '__main__':
    main()
