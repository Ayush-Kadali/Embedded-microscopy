"""
Comprehensive Module Testing Suite

Tests all 7 modules for contract compliance.

Run with: pytest tests/test_all_modules.py -v
"""

import pytest
import numpy as np
from datetime import datetime
import uuid

from modules.acquisition import AcquisitionModule
from modules.preprocessing import PreprocessingModule
from modules.segmentation import SegmentationModule
from modules.classification import ClassificationModule
from modules.counting import CountingModule
from modules.analytics import AnalyticsModule
from modules.export import ExportModule


# ============================================================================
# Helper Functions for Validation
# ============================================================================

def validate_status(result):
    """Validate status field present and valid."""
    assert 'status' in result, "Missing 'status' field"
    assert result['status'] in ['success', 'error'], f"Invalid status: {result['status']}"
    if result['status'] == 'error':
        assert 'error_message' in result, "Missing error_message when status=error"
        assert result['error_message'] is not None


def validate_image(image):
    """Validate image is RGB numpy array."""
    assert isinstance(image, np.ndarray), "Image must be numpy array"
    assert len(image.shape) == 3, f"Image must be 3D, got shape {image.shape}"
    assert image.shape[2] == 3, f"Image must have 3 channels (RGB), got {image.shape[2]}"
    assert image.dtype == np.uint8, f"Image must be uint8, got {image.dtype}"
    assert image.shape[0] >= 100 and image.shape[1] >= 100, "Image too small"


def validate_lists_same_length(*lists):
    """Validate all lists have same length."""
    if len(lists) == 0:
        return
    first_len = len(lists[0])
    for i, lst in enumerate(lists[1:], 1):
        assert len(lst) == first_len, f"List {i} has length {len(lst)}, expected {first_len}"


# ============================================================================
# Module 1: Acquisition Tests
# ============================================================================

class TestAcquisitionModule:
    """Test acquisition module contract compliance."""

    def test_initialization(self):
        """Test module initializes with valid config."""
        config = {
            'camera_type': 'pi_hq',
            'sensor_pixel_size_um': 1.55,
        }
        module = AcquisitionModule(config)
        assert module is not None

    def test_valid_input(self):
        """Test module accepts valid input."""
        config = {'camera_type': 'pi_hq', 'sensor_pixel_size_um': 1.55}
        module = AcquisitionModule(config)

        input_data = {
            'magnification': 2.0,
            'exposure_ms': 100,
            'focus_position': None,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'gps_lat': 12.34,
                'gps_lon': 56.78,
                'operator_id': 'test_user',
            }
        }

        result = module.process(input_data)
        validate_status(result)
        assert result['status'] == 'success'

    def test_output_contract(self):
        """Test output matches contract specification."""
        config = {'camera_type': 'pi_hq', 'sensor_pixel_size_um': 1.55}
        module = AcquisitionModule(config)

        input_data = {
            'magnification': 2.5,
            'exposure_ms': 150,
            'capture_metadata': {'timestamp': datetime.now().isoformat()}
        }

        result = module.process(input_data)

        # Check required fields
        assert 'image' in result
        assert 'metadata' in result

        # Validate image
        validate_image(result['image'])

        # Validate metadata fields
        metadata = result['metadata']
        required_meta_fields = [
            'capture_id', 'timestamp', 'magnification', 'exposure_ms',
            'resolution_um_per_px', 'fov_mm'
        ]
        for field in required_meta_fields:
            assert field in metadata, f"Missing metadata field: {field}"

        # Validate types
        assert isinstance(metadata['capture_id'], str)
        assert isinstance(metadata['magnification'], float)
        assert isinstance(metadata['resolution_um_per_px'], float)
        assert isinstance(metadata['fov_mm'], list)
        assert len(metadata['fov_mm']) == 2

    def test_magnification_validation(self):
        """Test magnification range validation."""
        config = {'camera_type': 'pi_hq', 'sensor_pixel_size_um': 1.55}
        module = AcquisitionModule(config)

        # Valid magnification
        result = module.process({
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {'timestamp': datetime.now().isoformat()}
        })
        assert result['status'] == 'success'

        # Invalid magnification (too low)
        result = module.process({
            'magnification': 0.5,
            'exposure_ms': 100,
            'capture_metadata': {'timestamp': datetime.now().isoformat()}
        })
        assert result['status'] == 'error'

        # Invalid magnification (too high)
        result = module.process({
            'magnification': 5.0,
            'exposure_ms': 100,
            'capture_metadata': {'timestamp': datetime.now().isoformat()}
        })
        assert result['status'] == 'error'


# ============================================================================
# Module 2: Preprocessing Tests
# ============================================================================

class TestPreprocessingModule:
    """Test preprocessing module contract compliance."""

    def test_initialization(self):
        """Test module initializes."""
        config = {'denoise_method': 'bilateral'}
        module = PreprocessingModule(config)
        assert module is not None

    def test_output_contract(self):
        """Test output matches contract."""
        config = {'denoise_method': 'bilateral', 'normalize': True}
        module = PreprocessingModule(config)

        test_image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)

        result = module.process({
            'image': test_image,
            'preprocessing_config': config
        })

        validate_status(result)
        assert result['status'] == 'success'

        # Check required fields
        assert 'processed_image' in result
        assert 'preprocessing_stats' in result

        # Validate processed image
        validate_image(result['processed_image'])
        assert result['processed_image'].shape == test_image.shape

        # Validate stats
        stats = result['preprocessing_stats']
        required_stats = ['mean_intensity', 'std_intensity', 'snr_db']
        for field in required_stats:
            assert field in stats

        # Validate ranges
        assert 0 <= stats['mean_intensity'] <= 255
        assert 0 <= stats['std_intensity'] <= 255

    def test_invalid_denoise_method(self):
        """Test invalid denoise method raises error."""
        with pytest.raises(ValueError):
            config = {'denoise_method': 'invalid_method'}
            module = PreprocessingModule(config)


# ============================================================================
# Module 3: Segmentation Tests
# ============================================================================

class TestSegmentationModule:
    """Test segmentation module contract compliance."""

    def test_initialization(self):
        """Test module initializes."""
        config = {'method': 'watershed', 'min_area_px': 100, 'max_area_px': 50000}
        module = SegmentationModule(config)
        assert module is not None

    def test_output_contract(self):
        """Test output matches contract."""
        config = {'method': 'threshold', 'min_area_px': 100, 'max_area_px': 50000}
        module = SegmentationModule(config)

        # Create test image with blobs
        test_image = np.ones((500, 500, 3), dtype=np.uint8) * 220
        test_image[100:150, 100:150] = 50  # Dark blob

        result = module.process({
            'image': test_image,
            'segmentation_config': config
        })

        validate_status(result)
        assert result['status'] == 'success'

        # Check required fields
        required_fields = ['masks', 'bounding_boxes', 'centroids', 'areas_px', 'num_detected']
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Validate list lengths match
        validate_lists_same_length(
            result['masks'],
            result['bounding_boxes'],
            result['centroids'],
            result['areas_px']
        )

        # Validate num_detected
        assert result['num_detected'] == len(result['masks'])

        # Validate bounding boxes structure
        for bbox in result['bounding_boxes']:
            assert 'x' in bbox and 'y' in bbox and 'w' in bbox and 'h' in bbox
            assert bbox['w'] > 0 and bbox['h'] > 0

        # Validate centroids
        for centroid in result['centroids']:
            assert isinstance(centroid, tuple)
            assert len(centroid) == 2

        # Validate areas
        for area in result['areas_px']:
            assert isinstance(area, int)
            assert area >= config['min_area_px']


# ============================================================================
# Module 4: Classification Tests
# ============================================================================

class TestClassificationModule:
    """Test classification module contract compliance."""

    def test_initialization(self):
        """Test module initializes."""
        config = {
            'class_names': ['Copepod', 'Diatom', 'Dinoflagellate'],
            'confidence_threshold': 0.7,
            'top_k': 3
        }
        module = ClassificationModule(config)
        assert module is not None

    def test_output_contract(self):
        """Test output matches contract."""
        config = {
            'class_names': ['Copepod', 'Diatom', 'Dinoflagellate'],
            'confidence_threshold': 0.7,
            'top_k': 3
        }
        module = ClassificationModule(config)

        test_image = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
        masks = [np.zeros((500, 500), dtype=bool)]
        masks[0][100:150, 100:150] = True
        bboxes = [{'x': 100, 'y': 100, 'w': 50, 'h': 50}]

        result = module.process({
            'image': test_image,
            'masks': masks,
            'bounding_boxes': bboxes,
            'classification_config': config
        })

        validate_status(result)
        assert result['status'] == 'success'

        # Check required fields
        assert 'predictions' in result
        assert 'model_metadata' in result

        # Validate predictions
        assert len(result['predictions']) == len(masks)

        for pred in result['predictions']:
            assert 'organism_id' in pred
            assert 'class_name' in pred
            assert 'confidence' in pred
            assert 'top_k_predictions' in pred

            # Validate confidence range
            assert 0.0 <= pred['confidence'] <= 1.0

            # Validate class name in allowed list
            assert pred['class_name'] in config['class_names']

            # Validate top_k
            assert len(pred['top_k_predictions']) <= config['top_k']

            for top_pred in pred['top_k_predictions']:
                assert 'class_name' in top_pred
                assert 'score' in top_pred
                assert 0.0 <= top_pred['score'] <= 1.0

        # Validate model metadata
        metadata = result['model_metadata']
        required_meta = ['model_name', 'version', 'input_size', 'inference_time_ms']
        for field in required_meta:
            assert field in metadata


# ============================================================================
# Module 5: Counting Tests
# ============================================================================

class TestCountingModule:
    """Test counting module contract compliance."""

    def test_initialization(self):
        """Test module initializes."""
        config = {'confidence_threshold': 0.7, 'size_range_um': [10, 1000]}
        module = CountingModule(config)
        assert module is not None

    def test_output_contract(self):
        """Test output matches contract."""
        config = {'confidence_threshold': 0.7, 'size_range_um': [10, 1000]}
        module = CountingModule(config)

        predictions = [
            {'organism_id': 0, 'class_name': 'Copepod', 'confidence': 0.85},
            {'organism_id': 1, 'class_name': 'Diatom', 'confidence': 0.92},
            {'organism_id': 2, 'class_name': 'Copepod', 'confidence': 0.78},
        ]
        areas_px = [1500, 2000, 1200]
        centroids = [(100, 100), (200, 150), (300, 200)]
        metadata = {'resolution_um_per_px': 0.775}

        result = module.process({
            'predictions': predictions,
            'areas_px': areas_px,
            'centroids': centroids,
            'metadata': metadata,
            'counting_config': config
        })

        validate_status(result)
        assert result['status'] == 'success'

        # Check required fields
        required_fields = ['counts_by_class', 'total_count', 'size_distribution', 'organisms']
        for field in required_fields:
            assert field in result

        # Validate counts
        assert isinstance(result['counts_by_class'], dict)
        assert isinstance(result['total_count'], int)
        assert result['total_count'] == sum(result['counts_by_class'].values())

        # Validate organisms list
        assert len(result['organisms']) == result['total_count']

        for org in result['organisms']:
            required_org_fields = ['organism_id', 'class_name', 'confidence', 'size_um', 'centroid_px', 'centroid_um']
            for field in required_org_fields:
                assert field in org

            assert org['confidence'] >= config['confidence_threshold']
            assert config['size_range_um'][0] <= org['size_um'] <= config['size_range_um'][1]


# ============================================================================
# Module 6: Analytics Tests
# ============================================================================

class TestAnalyticsModule:
    """Test analytics module contract compliance."""

    def test_initialization(self):
        """Test module initializes."""
        config = {'compute_diversity': True, 'bloom_thresholds': {}}
        module = AnalyticsModule(config)
        assert module is not None

    def test_output_contract(self):
        """Test output matches contract."""
        config = {
            'compute_diversity': True,
            'compute_composition': True,
            'bloom_thresholds': {'Diatom': 200}
        }
        module = AnalyticsModule(config)

        counts_by_class = {
            'Copepod': 45,
            'Diatom': 230,
            'Dinoflagellate': 12,
        }

        result = module.process({
            'counts_by_class': counts_by_class,
            'organisms': [],
            'analytics_config': config
        })

        validate_status(result)
        assert result['status'] == 'success'

        # Check required fields
        assert 'diversity_indices' in result
        assert 'composition' in result
        assert 'bloom_alerts' in result

        # Validate diversity indices
        diversity = result['diversity_indices']
        assert 'shannon' in diversity
        assert 'simpson' in diversity
        assert 'species_richness' in diversity

        assert diversity['shannon'] >= 0
        assert 0 <= diversity['simpson'] <= 1
        assert diversity['species_richness'] == len(counts_by_class)

        # Validate composition sums to 100
        composition = result['composition']
        total_pct = sum(composition.values())
        assert abs(total_pct - 100.0) < 0.01  # Allow floating point error

        # Validate bloom alerts
        assert len(result['bloom_alerts']) > 0  # Diatom should trigger
        for alert in result['bloom_alerts']:
            assert 'class_name' in alert
            assert 'count' in alert
            assert 'threshold' in alert
            assert 'severity' in alert
            assert alert['count'] >= alert['threshold']


# ============================================================================
# Module 7: Export Tests
# ============================================================================

class TestExportModule:
    """Test export module contract compliance."""

    def test_initialization(self):
        """Test module initializes."""
        config = {'output_dir': './results'}
        module = ExportModule(config)
        assert module is not None

    def test_output_contract(self):
        """Test output matches contract."""
        config = {'output_dir': './results', 'generate_dashboard': False}
        module = ExportModule(config)

        metadata = {
            'capture_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'magnification': 2.0
        }
        counts_by_class = {'Copepod': 3, 'Diatom': 1}
        organisms = [
            {'organism_id': 0, 'class_name': 'Copepod', 'confidence': 0.85, 'size_um': 50, 'centroid_px': (100, 100), 'centroid_um': (50.0, 50.0)},
        ]
        diversity = {'shannon': 0.562, 'simpson': 0.5, 'species_richness': 2}
        blooms = []

        result = module.process({
            'metadata': metadata,
            'counts_by_class': counts_by_class,
            'organisms': organisms,
            'diversity_indices': diversity,
            'bloom_alerts': blooms,
            'export_config': config
        })

        validate_status(result)
        assert result['status'] == 'success'

        # Check required fields
        assert 'csv_path' in result
        assert 'exported_files' in result

        # Validate files exist
        import os
        assert os.path.exists(result['csv_path'])

        for filepath in result['exported_files']:
            assert os.path.exists(filepath)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test module integration."""

    def test_full_pipeline_integration(self):
        """Test that all modules integrate correctly."""
        # This test runs the full pipeline to ensure all contracts are compatible

        from pipeline import PipelineManager
        import yaml

        # Load config
        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)

        # Initialize pipeline
        pipeline = PipelineManager(config)

        # Run pipeline
        acquisition_params = {
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'gps_lat': None,
                'gps_lon': None,
                'operator_id': 'test',
            }
        }

        result = pipeline.execute_pipeline(acquisition_params)

        # Validate final result
        assert result['status'] in ['success', 'error']

        if result['status'] == 'success':
            assert 'summary' in result
            assert 'total_organisms' in result['summary']
            assert 'csv_path' in result

    def test_module_chain_contracts(self):
        """Test that each module's output is valid input for next module."""
        # This verifies the contract chain works

        import yaml

        with open('config/config.yaml') as f:
            config = yaml.safe_load(f)

        # 1. Acquisition
        acq_module = AcquisitionModule(config.get('acquisition', {}))
        acq_result = acq_module.process({
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {'timestamp': datetime.now().isoformat()}
        })
        assert acq_result['status'] == 'success'

        # 2. Preprocessing (takes acquisition output)
        prep_module = PreprocessingModule(config.get('preprocessing', {}))
        prep_result = prep_module.process({
            'image': acq_result['image'],
            'preprocessing_config': config.get('preprocessing', {})
        })
        assert prep_result['status'] == 'success'

        # 3. Segmentation (takes preprocessing output)
        seg_module = SegmentationModule(config.get('segmentation', {}))
        seg_result = seg_module.process({
            'image': prep_result['processed_image'],
            'segmentation_config': config.get('segmentation', {})
        })
        assert seg_result['status'] == 'success'

        # 4. Classification (takes segmentation output)
        class_module = ClassificationModule(config.get('classification', {}))
        class_result = class_module.process({
            'image': prep_result['processed_image'],
            'masks': seg_result['masks'],
            'bounding_boxes': seg_result['bounding_boxes'],
            'classification_config': config.get('classification', {})
        })
        assert class_result['status'] == 'success'

        # 5. Counting (takes classification + segmentation outputs)
        count_module = CountingModule(config.get('counting', {}))
        count_result = count_module.process({
            'predictions': class_result['predictions'],
            'areas_px': seg_result['areas_px'],
            'centroids': seg_result['centroids'],
            'metadata': acq_result['metadata'],
            'counting_config': config.get('counting', {})
        })
        assert count_result['status'] == 'success'

        # 6. Analytics (takes counting output)
        analytics_module = AnalyticsModule(config.get('analytics', {}))
        analytics_result = analytics_module.process({
            'counts_by_class': count_result['counts_by_class'],
            'organisms': count_result['organisms'],
            'analytics_config': config.get('analytics', {})
        })
        assert analytics_result['status'] == 'success'

        # 7. Export (takes all outputs)
        export_module = ExportModule(config.get('export', {}))
        export_result = export_module.process({
            'metadata': acq_result['metadata'],
            'counts_by_class': count_result['counts_by_class'],
            'organisms': count_result['organisms'],
            'diversity_indices': analytics_result['diversity_indices'],
            'bloom_alerts': analytics_result['bloom_alerts'],
            'export_config': config.get('export', {})
        })
        assert export_result['status'] == 'success'

        # All modules integrated successfully!


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
