#!/usr/bin/env python3
"""
Debug script to check classification predictions
"""

import yaml
from pathlib import Path
from datetime import datetime
from pipeline.manager import PipelineManager

def main():
    # Load config
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)

    # Initialize pipeline
    pipeline = PipelineManager(config)

    # Test with one image
    test_image = 'datasets/processed/samples/1_0.png'

    acquisition_params = {
        'mode': 'file',
        'image_path': test_image,
        'magnification': 2.0,
        'exposure_ms': 100,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'operator_id': 'debug_test'
        }
    }

    # Execute pipeline
    print(f"\nTesting with: {test_image}")
    print("=" * 80)

    # Get individual module results
    acq = pipeline.modules['acquisition']
    prep = pipeline.modules['preprocessing']
    seg = pipeline.modules['segmentation']
    clf = pipeline.modules['classification']

    # Stage 1: Acquisition
    r1 = acq.process(acquisition_params)
    print(f"\n[Acquisition] Status: {r1['status']}")
    print(f"  Image shape: {r1['image'].shape}")

    # Stage 2: Preprocessing
    r2 = prep.process({
        'image': r1['image'],
        'preprocessing_config': config.get('preprocessing', {}),
    })
    print(f"\n[Preprocessing] Status: {r2['status']}")

    # Stage 3: Segmentation
    r3 = seg.process({
        'image': r2['processed_image'],
        'segmentation_config': config.get('segmentation', {}),
    })
    print(f"\n[Segmentation] Status: {r3['status']}")
    print(f"  Organisms detected: {r3['num_detected']}")

    # Stage 4: Classification
    r4 = clf.process({
        'image': r2['processed_image'],
        'masks': r3['masks'],
        'bounding_boxes': r3['bounding_boxes'],
        'classification_config': config.get('classification', {}),
    })
    print(f"\n[Classification] Status: {r4['status']}")
    print(f"  Organisms classified: {r4['num_classified']}")
    print(f"  Model: {r4['model_metadata']['model_name']}")

    print("\n" + "=" * 80)
    print("PREDICTIONS:")
    print("=" * 80)
    for pred in r4['predictions']:
        print(f"  Organism {pred['organism_id']}:")
        print(f"    Class: {pred['class_name']}")
        print(f"    Confidence: {pred['confidence']:.4f}")
        print(f"    BBox: {pred['bounding_box']}")
        print()

    # Check confidence threshold
    threshold = config.get('counting', {}).get('confidence_threshold', 0.7)
    print(f"Confidence threshold: {threshold}")
    above_threshold = [p for p in r4['predictions'] if p['confidence'] >= threshold]
    print(f"Predictions above threshold: {len(above_threshold)}/{len(r4['predictions'])}")

    return 0

if __name__ == '__main__':
    exit(main())
