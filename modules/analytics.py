"""
Module 6: Edge Analytics

Responsibility: Compute ecological metrics and bloom detection.
"""

from typing import Dict, Any, List
import numpy as np
from .base import PipelineModule


class AnalyticsModule(PipelineModule):
    """
    Computes diversity indices and detects harmful algal blooms.

    Input Contract:
        - counts_by_class: dict[str, int]
        - organisms: list of dict
        - historical_data: list | None (optional)
        - analytics_config: dict with compute_diversity, bloom_thresholds, etc.

    Output Contract:
        - status: str
        - error_message: str | None
        - diversity_indices: dict (shannon, simpson, species_richness)
        - composition: dict[str, float] (percentage per class)
        - bloom_alerts: list of dict
        - trends: dict | None
    """

    def validate_config(self) -> None:
        """Validate analytics configuration."""
        pass  # No required config

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        required = ['counts_by_class', 'organisms']
        for key in required:
            if key not in input_data:
                raise ValueError(f"Missing required input: {key}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute analytics and metrics."""
        try:
            counts_by_class = input_data['counts_by_class']
            organisms = input_data['organisms']
            config = input_data.get('analytics_config', self.config)

            # Compute diversity indices if requested
            diversity_indices = None
            if config.get('compute_diversity', True):
                diversity_indices = self._compute_diversity(counts_by_class)

            # Compute composition if requested
            composition = None
            if config.get('compute_composition', True):
                composition = self._compute_composition(counts_by_class)

            # Check for bloom alerts
            bloom_thresholds = config.get('bloom_thresholds', {})
            bloom_alerts = self._detect_blooms(counts_by_class, bloom_thresholds)

            # Compute trends (if historical data provided)
            historical_data = input_data.get('historical_data')
            trends = None
            if historical_data:
                trends = self._compute_trends(counts_by_class, historical_data)

            self.logger.info(
                f"Analytics complete: Shannon={diversity_indices['shannon']:.2f}, "
                f"Richness={diversity_indices['species_richness']}, "
                f"Blooms={len(bloom_alerts)}"
            )

            return {
                'status': 'success',
                'error_message': None,
                'diversity_indices': diversity_indices,
                'composition': composition,
                'bloom_alerts': bloom_alerts,
                'trends': trends,
            }

        except Exception as e:
            return self.handle_error(e)

    def _compute_diversity(self, counts_by_class: Dict[str, int]) -> Dict[str, Any]:
        """
        Compute biodiversity indices.

        Shannon index: H = -Σ(p_i * ln(p_i))
        Simpson index: D = 1 - Σ(p_i²)
        Species richness: Number of unique species
        """
        if not counts_by_class:
            return {
                'shannon': 0.0,
                'simpson': 0.0,
                'species_richness': 0,
            }

        total = sum(counts_by_class.values())
        proportions = np.array([count / total for count in counts_by_class.values()])

        # Shannon diversity index
        shannon = -np.sum(proportions * np.log(proportions + 1e-10))

        # Simpson diversity index
        simpson = 1.0 - np.sum(proportions ** 2)

        # Species richness
        richness = len(counts_by_class)

        return {
            'shannon': float(shannon),
            'simpson': float(simpson),
            'species_richness': richness,
        }

    def _compute_composition(self, counts_by_class: Dict[str, int]) -> Dict[str, float]:
        """Compute percentage composition of each class."""
        if not counts_by_class:
            return {}

        total = sum(counts_by_class.values())
        composition = {
            class_name: (count / total) * 100
            for class_name, count in counts_by_class.items()
        }

        return composition

    def _detect_blooms(
        self,
        counts_by_class: Dict[str, int],
        bloom_thresholds: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Detect harmful algal blooms based on threshold counts.

        Args:
            counts_by_class: Current counts by class
            bloom_thresholds: Dict mapping class names to threshold counts

        Returns:
            List of bloom alerts
        """
        bloom_alerts = []

        for class_name, threshold in bloom_thresholds.items():
            count = counts_by_class.get(class_name, 0)
            if count >= threshold:
                bloom_alerts.append({
                    'class_name': class_name,
                    'count': count,
                    'threshold': threshold,
                    'severity': self._compute_severity(count, threshold),
                })

        return bloom_alerts

    def _compute_severity(self, count: int, threshold: int) -> str:
        """Compute bloom severity level."""
        ratio = count / threshold

        if ratio >= 3.0:
            return 'critical'
        elif ratio >= 2.0:
            return 'high'
        elif ratio >= 1.5:
            return 'moderate'
        else:
            return 'low'

    def _compute_trends(
        self,
        current_counts: Dict[str, int],
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Compute trends by comparing with historical data.

        Args:
            current_counts: Current sample counts
            historical_data: List of previous samples with counts_by_class

        Returns:
            Trend analysis dict
        """
        if not historical_data:
            return None

        # Simple trend: compare with most recent historical sample
        last_sample = historical_data[-1]
        last_counts = last_sample.get('counts_by_class', {})

        trends = {}
        for class_name in set(current_counts.keys()) | set(last_counts.keys()):
            current = current_counts.get(class_name, 0)
            previous = last_counts.get(class_name, 0)

            if previous > 0:
                change_pct = ((current - previous) / previous) * 100
            else:
                change_pct = 100.0 if current > 0 else 0.0

            trends[class_name] = {
                'current': current,
                'previous': previous,
                'change_pct': float(change_pct),
                'direction': 'increasing' if change_pct > 0 else 'decreasing' if change_pct < 0 else 'stable',
            }

        return trends
