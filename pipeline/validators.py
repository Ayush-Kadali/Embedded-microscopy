"""
Configuration validation utilities.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates pipeline configuration."""

    @staticmethod
    def validate(config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate complete pipeline configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for required top-level sections
        required_sections = [
            'pipeline', 'acquisition', 'preprocessing', 'segmentation',
            'classification', 'counting', 'analytics', 'export'
        ]

        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")

        # Validate classification config
        if 'classification' in config:
            if 'class_names' not in config['classification']:
                errors.append("classification.class_names is required")
            elif not isinstance(config['classification']['class_names'], list):
                errors.append("classification.class_names must be a list")

        # Validate segmentation config
        if 'segmentation' in config:
            seg_config = config['segmentation']
            if 'min_area_px' in seg_config and seg_config['min_area_px'] <= 0:
                errors.append("segmentation.min_area_px must be positive")

        is_valid = len(errors) == 0

        if not is_valid:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
        else:
            logger.info("Configuration validated successfully")

        return is_valid, errors
