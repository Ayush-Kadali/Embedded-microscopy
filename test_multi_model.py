#!/usr/bin/env python3
"""
Test Multi-Model Classification System

Tests three modes:
1. Model 1 only (original classifier)
2. Model 2 only (MobileNetV2)
3. Ensemble (both models voting)

Shows comparison of results
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
import numpy as np

# Import pipeline components
from modules.acquisition import AcquisitionModule
from modules.preprocessing import PreprocessingModule
from modules.segmentation import SegmentationModule
from modules.classification_multi import ClassificationMultiModel
from modules.counting import CountingModule

print("=" * 80)
print("MULTI-MODEL CLASSIFICATION TEST")
print("=" * 80)

# Test image
test_image_path = 'datasets/processed/samples/1_0.png'

if not Path(test_image_path).exists():
    print(f"\n✗ Test image not found: {test_image_path}")
    print("  Please ensure test images exist in datasets/processed/samples/")
    sys.exit(1)

print(f"\nTest image: {test_image_path}")
print("=" * 80)

# Load base config
with open('config/config_multi_model.yaml') as f:
    base_config = yaml.safe_load(f)

# Prepare acquisition parameters
acq_params = {
    'mode': 'file',
    'image_path': test_image_path,
    'magnification': 2.0,
    'exposure_ms': 100,
    'capture_metadata': {
        'timestamp': datetime.now().isoformat(),
        'operator_id': 'test_user'
    }
}

def run_pipeline_with_mode(mode_name, config):
    """Run pipeline with specified classification mode"""
    print(f"\n{'=' * 80}")
    print(f"MODE: {mode_name.upper()}")
    print(f"{'=' * 80}")

    try:
        # Initialize modules
        acquisition = AcquisitionModule(config['acquisition'])
        preprocessing = PreprocessingModule(config['preprocessing'])
        segmentation = SegmentationModule(config['segmentation'])
        classification = ClassificationMultiModel(config['classification'])
        counting = CountingModule(config['counting'])

        # Step 1: Acquire
        print("\n[1/5] Acquiring image...")
        acq_result = acquisition.process(acq_params)
        if acq_result['status'] != 'success':
            print(f"  ✗ Acquisition failed: {acq_result.get('error')}")
            return None
        print("  ✓ Image acquired")

        # Step 2: Preprocess
        print("[2/5] Preprocessing...")
        prep_result = preprocessing.process(acq_result)
        if prep_result['status'] != 'success':
            print(f"  ✗ Preprocessing failed: {prep_result.get('error')}")
            return None
        print("  ✓ Preprocessed")

        # Step 3: Segment
        print("[3/5] Segmenting...")
        seg_result = segmentation.process(prep_result)
        if seg_result['status'] != 'success':
            print(f"  ✗ Segmentation failed: {seg_result.get('error')}")
            return None
        print(f"  ✓ Found {seg_result['num_organisms']} organisms")

        # Step 4: Classify
        print(f"[4/5] Classifying with {mode_name}...")
        class_result = classification.process(seg_result)
        if class_result['status'] != 'success':
            print(f"  ✗ Classification failed: {class_result.get('error')}")
            return None

        model_info = class_result['model_metadata']
        print(f"  ✓ Classified using: {model_info['active_models']}")
        if model_info['mode'] == 'ensemble':
            print(f"    Ensemble weights: {model_info['weights']}")

        # Step 5: Count
        print("[5/5] Counting...")
        count_result = counting.process(class_result)
        if count_result['status'] != 'success':
            print(f"  ✗ Counting failed: {count_result.get('error')}")
            return None
        print("  ✓ Counted")

        return count_result

    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test Mode 1: Original Model
print("\n\n" + "=" * 80)
print("TEST 1: MODEL 1 (Original Classifier)")
print("=" * 80)

config_mode1 = base_config.copy()
config_mode1['classification']['mode'] = 'model_1'

result_mode1 = run_pipeline_with_mode("Model 1 (Original)", config_mode1)

# Test Mode 2: MobileNetV2
print("\n\n" + "=" * 80)
print("TEST 2: MODEL 2 (MobileNetV2)")
print("=" * 80)

config_mode2 = base_config.copy()
config_mode2['classification']['mode'] = 'model_2'

result_mode2 = run_pipeline_with_mode("Model 2 (MobileNetV2)", config_mode2)

# Test Mode 3: Ensemble
print("\n\n" + "=" * 80)
print("TEST 3: ENSEMBLE (Both Models)")
print("=" * 80)

config_ensemble = base_config.copy()
config_ensemble['classification']['mode'] = 'ensemble'

result_ensemble = run_pipeline_with_mode("Ensemble", config_ensemble)

# Compare Results
print("\n\n" + "=" * 80)
print("COMPARISON OF RESULTS")
print("=" * 80)

if result_mode1 and result_mode2 and result_ensemble:

    def show_results(result, mode_name):
        print(f"\n{mode_name}:")
        print(f"  Total organisms: {result['summary']['total_organisms']}")
        print(f"  Above threshold: {result['summary']['organisms_above_threshold']}")
        print(f"  Species richness: {result['summary']['species_richness']}")

        print(f"\n  Top species:")
        counts = result['summary']['counts_by_class']
        sorted_species = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for species, count in sorted_species:
            print(f"    {species}: {count}")

        # Average confidence
        organisms = result['organisms']
        if organisms:
            avg_conf = np.mean([org['confidence'] for org in organisms])
            print(f"\n  Average confidence: {avg_conf*100:.1f}%")

            # Show individual predictions
            print(f"\n  Individual predictions:")
            for i, org in enumerate(organisms[:3]):  # Show first 3
                print(f"    Organism {i+1}: {org['class_name']} ({org['confidence']*100:.1f}%)")

    show_results(result_mode1, "Model 1 (Original)")
    show_results(result_mode2, "Model 2 (MobileNetV2)")
    show_results(result_ensemble, "Ensemble")

    # Agreement analysis
    print(f"\n{'=' * 80}")
    print("AGREEMENT ANALYSIS")
    print(f"{'=' * 80}")

    orgs_m1 = result_mode1['organisms']
    orgs_m2 = result_mode2['organisms']
    orgs_ens = result_ensemble['organisms']

    agreements = 0
    for i in range(len(orgs_m1)):
        if orgs_m1[i]['class_name'] == orgs_m2[i]['class_name']:
            agreements += 1

    agreement_rate = agreements / len(orgs_m1) * 100 if orgs_m1 else 0
    print(f"\nModel 1 vs Model 2 agreement: {agreement_rate:.1f}% ({agreements}/{len(orgs_m1)} organisms)")

    # Show disagreements
    if agreements < len(orgs_m1):
        print(f"\nDisagreements (first 3):")
        count = 0
        for i in range(len(orgs_m1)):
            if orgs_m1[i]['class_name'] != orgs_m2[i]['class_name'] and count < 3:
                print(f"  Organism {i+1}:")
                print(f"    Model 1: {orgs_m1[i]['class_name']} ({orgs_m1[i]['confidence']*100:.1f}%)")
                print(f"    Model 2: {orgs_m2[i]['class_name']} ({orgs_m2[i]['confidence']*100:.1f}%)")
                print(f"    Ensemble: {orgs_ens[i]['class_name']} ({orgs_ens[i]['confidence']*100:.1f}%)")
                count += 1

else:
    print("\n⚠ Some tests failed. Cannot compare results.")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
Multi-model system successfully created!

You can now switch between models by changing the 'mode' in config:

  config/config_multi_model.yaml:
    classification:
      mode: 'model_1'     # Use original model
      mode: 'model_2'     # Use MobileNetV2
      mode: 'ensemble'    # Use both (recommended)

Ensemble weights can be adjusted:
  ensemble_weights: [0.5, 0.5]  # Equal
  ensemble_weights: [0.7, 0.3]  # Favor Model 1
  ensemble_weights: [0.3, 0.7]  # Favor Model 2

To use in your pipeline:
  1. Update pipeline/manager.py to import ClassificationMultiModel
  2. Use config_multi_model.yaml
  3. Run: python main.py --config config/config_multi_model.yaml
""")

print("=" * 80)
