"""
Module 5: Counting & Sizing

Responsibility: Aggregate counts per class and compute sizes in micrometers.
"""

from typing import Dict, Any, List
import numpy as np
from collections import defaultdict
from .base import PipelineModule


class CountingModule(PipelineModule):
    """
    Counts organisms by class and computes size statistics.

    Input Contract:
        - predictions: list of dict (from classification)
        - areas_px: list of int (from segmentation)
        - centroids: list of tuple (from segmentation)
        - metadata: dict (from acquisition)
        - counting_config: dict with confidence_threshold, size_range_um, etc.

    Output Contract:
        - status: str
        - error_message: str | None
        - counts_by_class: dict[str, int]
        - total_count: int
        - size_distribution: dict per class
        - organisms: list of detailed organism info
    """

    def validate_config(self) -> None:
        """Validate counting configuration."""
        pass  # No required config for counting

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        required = ['predictions', 'areas_px', 'centroids', 'metadata']
        for key in required:
            if key not in input_data:
                raise ValueError(f"Missing required input: {key}")

        # Check lengths match
        n_preds = len(input_data['predictions'])
        if len(input_data['areas_px']) != n_preds or len(input_data['centroids']) != n_preds:
            raise ValueError("predictions, areas_px, and centroids must have same length")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Count and size organisms."""
        try:
            predictions = input_data['predictions']
            areas_px = input_data['areas_px']
            centroids = input_data['centroids']
            metadata = input_data['metadata']
            config = input_data.get('counting_config', self.config)

            confidence_threshold = config.get('confidence_threshold', 0.7)
            size_range_um = config.get('size_range_um', [10, 1000])

            # Get resolution from metadata
            um_per_px = metadata.get('resolution_um_per_px', 1.0)

            # Count by class and collect size info
            counts_by_class = defaultdict(int)
            sizes_by_class = defaultdict(list)
            organisms = []

            for i, pred in enumerate(predictions):
                # Filter by confidence
                if pred['confidence'] < confidence_threshold:
                    continue

                class_name = pred['class_name']
                area_px = areas_px[i]
                centroid_px = centroids[i]

                # Compute equivalent diameter in micrometers
                # Area = π r² => r = sqrt(A/π) => d = 2*sqrt(A/π)
                diameter_um = 2 * np.sqrt(area_px / np.pi) * um_per_px

                # Filter by size range
                if not (size_range_um[0] <= diameter_um <= size_range_um[1]):
                    continue

                # Increment count
                counts_by_class[class_name] += 1
                sizes_by_class[class_name].append(diameter_um)

                # Compute centroid in micrometers (relative to image origin)
                centroid_um = (
                    centroid_px[0] * um_per_px,
                    centroid_px[1] * um_per_px
                )

                organisms.append({
                    'organism_id': i,
                    'class_name': class_name,
                    'confidence': pred['confidence'],
                    'size_um': float(diameter_um),
                    'centroid_px': centroid_px,
                    'centroid_um': centroid_um,
                })

            # Compute size distribution statistics
            size_distribution = {}
            for class_name, sizes in sizes_by_class.items():
                if sizes:
                    # Create histogram
                    hist, _ = np.histogram(sizes, bins=10)

                    size_distribution[class_name] = {
                        'mean_um': float(np.mean(sizes)),
                        'std_um': float(np.std(sizes)),
                        'min_um': float(np.min(sizes)),
                        'max_um': float(np.max(sizes)),
                        'histogram': hist.tolist(),
                    }

            total_count = sum(counts_by_class.values())

            self.logger.info(
                f"Counting complete: {total_count} organisms across {len(counts_by_class)} classes"
            )

            return {
                'status': 'success',
                'error_message': None,
                'counts_by_class': dict(counts_by_class),
                'total_count': total_count,
                'size_distribution': size_distribution,
                'organisms': organisms,
            }

        except Exception as e:
            return self.handle_error(e)
