#!/usr/bin/env python3
"""
Batch Processing Script for Multiple Images
Efficiently processes multiple plankton images with the full pipeline
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
from tqdm import tqdm

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from pipeline.manager import PipelineManager
from config.config_loader import load_config


def find_images(directory, extensions=('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
    """Find all image files in directory"""
    image_files = []
    for ext in extensions:
        image_files.extend(Path(directory).glob(f'*{ext}'))
        image_files.extend(Path(directory).glob(f'*{ext.upper()}'))
    return sorted(image_files)


def process_single_image(pipeline, image_path, output_dir):
    """Process a single image through the pipeline"""
    try:
        # Prepare acquisition parameters
        acquisition_params = {
            'mode': 'file',
            'image_path': str(image_path),
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'operator_id': 'batch_process',
                'source_file': image_path.name
            }
        }

        # Execute pipeline
        results = pipeline.execute_pipeline(acquisition_params)

        # Check status
        if results.get('status') != 'success':
            return None, f"Pipeline failed: {results.get('error_message', 'Unknown error')}"

        return results, None

    except Exception as e:
        return None, f"Error processing {image_path.name}: {str(e)}"


def summarize_results(all_results):
    """Create summary statistics from all results"""
    summary = {
        'total_images': len(all_results),
        'total_organisms': 0,
        'species_detected': set(),
        'species_counts': {},
        'average_diversity': {'shannon': 0, 'simpson': 0},
        'blooms_detected': []
    }

    shannon_sum = 0
    simpson_sum = 0

    for result in all_results:
        if result['status'] != 'success':
            continue

        # Extract from new pipeline output structure
        result_summary = result.get('summary', {})
        detailed = result.get('detailed_results', {})

        # Counting
        summary['total_organisms'] += result_summary.get('total_organisms', 0)

        # Species
        class_counts = result_summary.get('counts_by_class', {})
        for species, count in class_counts.items():
            summary['species_detected'].add(species)
            summary['species_counts'][species] = summary['species_counts'].get(species, 0) + count

        # Diversity
        shannon_sum += result_summary.get('shannon_diversity', 0)
        diversity = detailed.get('diversity', {})
        simpson_sum += diversity.get('simpson', 0)

        # Blooms
        bloom_alerts = detailed.get('bloom_alerts', [])
        for bloom in bloom_alerts:
            summary['blooms_detected'].append({
                'image': result_summary.get('capture_id', 'Unknown'),
                'species': bloom.get('species', 'Unknown'),
                'dominance': bloom.get('dominance', 0)
            })

    # Calculate averages
    if summary['total_images'] > 0:
        summary['average_diversity']['shannon'] = shannon_sum / summary['total_images']
        summary['average_diversity']['simpson'] = simpson_sum / summary['total_images']

    summary['species_detected'] = list(summary['species_detected'])

    return summary


def main():
    parser = argparse.ArgumentParser(
        description='Batch process multiple plankton images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all images in a folder
  python batch_process.py images/

  # Process with custom output directory
  python batch_process.py images/ -o results/batch_1/

  # Process and skip failed images
  python batch_process.py images/ --continue-on-error
        """
    )

    parser.add_argument('input_dir', type=str, help='Directory containing images to process')
    parser.add_argument('-o', '--output', type=str, default='results/batch',
                       help='Output directory for results (default: results/batch)')
    parser.add_argument('--continue-on-error', action='store_true',
                       help='Continue processing if an image fails')
    parser.add_argument('--no-export', action='store_true',
                       help='Skip exporting individual results (faster)')

    args = parser.parse_args()

    # Validate input directory
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"❌ Error: Directory not found: {input_dir}")
        sys.exit(1)

    # Find images
    print(f"🔍 Scanning directory: {input_dir}")
    image_files = find_images(input_dir)

    if not image_files:
        print(f"❌ No images found in {input_dir}")
        sys.exit(1)

    print(f"✅ Found {len(image_files)} images\n")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize pipeline
    print("⚙️  Initializing pipeline...")
    config = load_config()
    pipeline = PipelineManager(config)
    print("✅ Pipeline ready\n")

    # Process images
    print(f"🔬 Processing {len(image_files)} images...\n")

    all_results = []
    failed_images = []

    for image_path in tqdm(image_files, desc="Processing", unit="image"):
        result, error = process_single_image(pipeline, image_path, output_dir)

        if error:
            failed_images.append({'file': image_path.name, 'error': error})
            if not args.continue_on_error:
                print(f"\n❌ {error}")
                print("Use --continue-on-error to skip failed images")
                sys.exit(1)
        else:
            all_results.append(result)

    print(f"\n✅ Processing complete!")
    print(f"   Successful: {len(all_results)}/{len(image_files)}")
    if failed_images:
        print(f"   Failed: {len(failed_images)}")

    # Generate summary
    print("\n📊 Generating summary...")
    summary = summarize_results(all_results)

    # Print summary
    print(f"\n{'='*60}")
    print("BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total Images Processed: {summary['total_images']}")
    print(f"Total Organisms Detected: {summary['total_organisms']}")
    print(f"Unique Species: {len(summary['species_detected'])}")
    print(f"\nAverage Shannon Diversity: {summary['average_diversity']['shannon']:.3f}")
    print(f"Average Simpson Diversity: {summary['average_diversity']['simpson']:.3f}")

    if summary['blooms_detected']:
        print(f"\n⚠️  Blooms Detected: {len(summary['blooms_detected'])}")
        for bloom in summary['blooms_detected']:
            print(f"   - {bloom['image']}: {bloom['species']} ({bloom['dominance']:.1f}%)")

    print(f"\nSpecies Distribution:")
    for species in sorted(summary['species_counts'].keys()):
        count = summary['species_counts'][species]
        percentage = (count / summary['total_organisms'] * 100) if summary['total_organisms'] > 0 else 0
        print(f"   {species:30s}: {count:4d} ({percentage:5.1f}%)")

    print(f"{'='*60}\n")

    # Save summary
    summary_file = output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Convert set to list for JSON serialization
    summary_json = summary.copy()

    with open(summary_file, 'w') as f:
        json.dump(summary_json, f, indent=2)

    print(f"💾 Summary saved to: {summary_file}")

    # Save detailed CSV
    csv_file = output_dir / f"batch_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    rows = []
    for result in all_results:
        # Extract from new pipeline output structure
        result_summary = result.get('summary', {})
        detailed = result.get('detailed_results', {})
        diversity = detailed.get('diversity', {})

        row = {
            'filename': result_summary.get('capture_id', 'Unknown'),
            'total_organisms': result_summary.get('total_organisms', 0),
            'species_richness': result_summary.get('species_richness', 0),
            'shannon_diversity': result_summary.get('shannon_diversity', 0),
            'simpson_diversity': diversity.get('simpson', 0),
        }

        # Add species counts
        class_counts = result_summary.get('counts_by_class', {})
        for species in summary['species_detected']:
            row[f'count_{species}'] = class_counts.get(species, 0)

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False)

    print(f"💾 Detailed results saved to: {csv_file}")

    # Save failed images list
    if failed_images:
        failed_file = output_dir / f"failed_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(failed_file, 'w') as f:
            json.dump(failed_images, f, indent=2)
        print(f"⚠️  Failed images list saved to: {failed_file}")

    print(f"\n✅ All results saved to: {output_dir}/")


if __name__ == '__main__':
    main()
