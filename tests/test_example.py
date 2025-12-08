"""
Example test file demonstrating how to test pipeline modules.

Copy this template for testing your own modules.
"""

import pytest
import numpy as np
from modules.preprocessing import PreprocessingModule
from modules.segmentation import SegmentationModule


class TestPreprocessingModule:
    """Example tests for Preprocessing module."""

    def test_module_initialization(self):
        """Test that module initializes correctly with valid config."""
        config = {
            'denoise_method': 'bilateral',
            'normalize': True,
            'background_correction': True,
        }
        module = PreprocessingModule(config)
        assert module.config['denoise_method'] == 'bilateral'

    def test_invalid_denoise_method(self):
        """Test that invalid config raises error."""
        config = {'denoise_method': 'invalid_method'}
        with pytest.raises(ValueError):
            PreprocessingModule(config)

    def test_process_basic_image(self):
        """Test basic preprocessing on a simple image."""
        config = {
            'denoise_method': 'gaussian',
            'normalize': True,
            'background_correction': False,
        }
        module = PreprocessingModule(config)

        # Create test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        # Process
        result = module.process({
            'image': test_image,
            'preprocessing_config': config,
        })

        # Verify
        assert result['status'] == 'success'
        assert 'processed_image' in result
        assert result['processed_image'].shape == test_image.shape
        assert 'preprocessing_stats' in result

    def test_missing_input(self):
        """Test that missing input is caught."""
        config = {'denoise_method': 'bilateral'}
        module = PreprocessingModule(config)

        # Missing 'image' key
        result = module.process({})

        assert result['status'] == 'error'
        assert 'error_message' in result


class TestSegmentationModule:
    """Example tests for Segmentation module."""

    def test_threshold_segmentation(self):
        """Test threshold-based segmentation."""
        config = {
            'method': 'threshold',
            'min_area_px': 100,
            'max_area_px': 50000,
        }
        module = SegmentationModule(config)

        # Create synthetic image with a few blobs
        test_image = np.ones((200, 200, 3), dtype=np.uint8) * 200
        # Add a dark blob
        test_image[50:100, 50:100] = 50

        result = module.process({
            'image': test_image,
            'segmentation_config': config,
        })

        assert result['status'] == 'success'
        assert result['num_detected'] >= 0
        assert len(result['masks']) == result['num_detected']
        assert len(result['bounding_boxes']) == result['num_detected']

    def test_watershed_segmentation(self):
        """Test watershed-based segmentation."""
        config = {
            'method': 'watershed',
            'min_area_px': 50,
            'max_area_px': 10000,
        }
        module = SegmentationModule(config)

        # Create synthetic image
        test_image = np.ones((200, 200, 3), dtype=np.uint8) * 200
        test_image[50:100, 50:100] = 50
        test_image[120:150, 120:150] = 50

        result = module.process({
            'image': test_image,
            'segmentation_config': config,
        })

        assert result['status'] == 'success'
        assert 'masks' in result
        assert 'bounding_boxes' in result


class TestEndToEndContract:
    """Test that module outputs match next module's inputs."""

    def test_preprocessing_to_segmentation(self):
        """Test that preprocessing output is valid segmentation input."""
        # Preprocessing
        prep_config = {'denoise_method': 'bilateral'}
        prep_module = PreprocessingModule(prep_config)

        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        prep_result = prep_module.process({
            'image': test_image,
            'preprocessing_config': prep_config,
        })

        # Segmentation should accept preprocessing output
        seg_config = {'method': 'threshold', 'min_area_px': 100, 'max_area_px': 50000}
        seg_module = SegmentationModule(seg_config)

        seg_result = seg_module.process({
            'image': prep_result['processed_image'],
            'segmentation_config': seg_config,
        })

        assert seg_result['status'] == 'success'


# Run tests with: pytest tests/test_example.py -v
