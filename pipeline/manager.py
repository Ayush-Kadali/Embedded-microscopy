"""
Pipeline Manager - Orchestrates all modules in the processing pipeline.
"""

from typing import Dict, Any
import logging
from modules import (
    AcquisitionModule,
    PreprocessingModule,
    SegmentationModule,
    CountingModule,
    AnalyticsModule,
    ExportModule,
)
from modules.classification_real import ClassificationModuleReal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineManager:
    """
    Orchestrates the complete processing pipeline.

    The manager wires modules together using standardized contracts
    and handles error propagation. It never touches module internals,
    only their input/output interfaces.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pipeline with configuration.

        Args:
            config: Complete pipeline configuration dict
        """
        self.config = config
        self.modules = {}
        self._initialize_modules()

    def _initialize_modules(self) -> None:
        """Initialize all pipeline modules."""
        logger.info("Initializing pipeline modules...")

        try:
            self.modules = {
                'acquisition': AcquisitionModule(self.config.get('acquisition', {})),
                'preprocessing': PreprocessingModule(self.config.get('preprocessing', {})),
                'segmentation': SegmentationModule(self.config.get('segmentation', {})),
                'classification': ClassificationModuleReal(self.config.get('classification', {})),
                'counting': CountingModule(self.config.get('counting', {})),
                'analytics': AnalyticsModule(self.config.get('analytics', {})),
                'export': ExportModule(self.config.get('export', {})),
            }
            logger.info("All modules initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")
            raise

    def execute_pipeline(self, acquisition_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete pipeline.

        Args:
            acquisition_params: Parameters for image acquisition

        Returns:
            Complete pipeline result with status and outputs
        """
        logger.info("=" * 80)
        logger.info("Starting pipeline execution")
        logger.info("=" * 80)

        # Stage 1: Acquisition
        logger.info("\n[1/7] Image Acquisition")
        r1 = self.modules['acquisition'].process(acquisition_params)
        if r1['status'] != 'success':
            return self._build_error_response('acquisition', r1)

        # Stage 2: Preprocessing
        logger.info("\n[2/7] Preprocessing")
        r2 = self.modules['preprocessing'].process({
            'image': r1['image'],
            'preprocessing_config': self.config.get('preprocessing', {}),
        })
        if r2['status'] != 'success':
            return self._build_error_response('preprocessing', r2)

        # Stage 3: Segmentation
        logger.info("\n[3/7] Segmentation")
        r3 = self.modules['segmentation'].process({
            'image': r2['processed_image'],
            'segmentation_config': self.config.get('segmentation', {}),
        })
        if r3['status'] != 'success':
            return self._build_error_response('segmentation', r3)

        # Stage 4: Classification
        logger.info("\n[4/7] Classification")
        r4 = self.modules['classification'].process({
            'image': r2['processed_image'],
            'masks': r3['masks'],
            'bounding_boxes': r3['bounding_boxes'],
            'classification_config': self.config.get('classification', {}),
        })
        if r4['status'] != 'success':
            return self._build_error_response('classification', r4)

        # Stage 5: Counting
        logger.info("\n[5/7] Counting & Sizing")
        r5 = self.modules['counting'].process({
            'predictions': r4['predictions'],
            'areas_px': r3['areas_px'],
            'centroids': r3['centroids'],
            'metadata': r1['metadata'],
            'counting_config': self.config.get('counting', {}),
        })
        if r5['status'] != 'success':
            return self._build_error_response('counting', r5)

        # Stage 6: Analytics
        logger.info("\n[6/7] Analytics")
        r6 = self.modules['analytics'].process({
            'counts_by_class': r5['counts_by_class'],
            'organisms': r5['organisms'],
            'analytics_config': self.config.get('analytics', {}),
        })
        if r6['status'] != 'success':
            return self._build_error_response('analytics', r6)

        # Stage 7: Export
        logger.info("\n[7/7] Export")
        r7 = self.modules['export'].process({
            'metadata': r1['metadata'],
            'counts_by_class': r5['counts_by_class'],
            'organisms': r5['organisms'],
            'diversity_indices': r6['diversity_indices'],
            'bloom_alerts': r6['bloom_alerts'],
            'export_config': self.config.get('export', {}),
        })

        # Build final result
        result = {
            'status': r7['status'],
            'csv_path': r7.get('csv_path'),
            'dashboard_url': r7.get('dashboard_url'),
            'exported_files': r7.get('exported_files', []),
            'summary': {
                'capture_id': r1['metadata']['capture_id'],
                'timestamp': r1['metadata']['timestamp'],
                'total_organisms': r5['total_count'],
                'species_richness': r6['diversity_indices']['species_richness'],
                'shannon_diversity': r6['diversity_indices']['shannon'],
                'bloom_alerts': len(r6['bloom_alerts']),
                'counts_by_class': r5['counts_by_class'],
            },
            'detailed_results': {
                'acquisition': {
                    'magnification': r1['metadata']['magnification'],
                    'resolution_um_per_px': r1['metadata']['resolution_um_per_px'],
                    'fov_mm': r1['metadata']['fov_mm'],
                },
                'preprocessing': r2['preprocessing_stats'],
                'segmentation': {
                    'num_detected': r3['num_detected'],
                },
                'classification': {
                    'model_name': r4['model_metadata']['model_name'],
                    'inference_time_ms': r4['model_metadata']['inference_time_ms'],
                },
                'diversity': r6['diversity_indices'],
                'composition': r6['composition'],
                'bloom_alerts': r6['bloom_alerts'],
            },
        }

        logger.info("\n" + "=" * 80)
        logger.info("Pipeline execution complete!")
        logger.info(f"Total organisms detected: {result['summary']['total_organisms']}")
        logger.info(f"Species richness: {result['summary']['species_richness']}")
        logger.info(f"Shannon diversity: {result['summary']['shannon_diversity']:.3f}")
        logger.info(f"Results exported to: {result['csv_path']}")
        logger.info("=" * 80)

        return result

    def _build_error_response(self, failed_stage: str, error_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized error response."""
        logger.error(f"Pipeline failed at stage: {failed_stage}")
        logger.error(f"Error: {error_result.get('error_message')}")

        return {
            'status': 'error',
            'failed_at': failed_stage,
            'error_message': error_result.get('error_message'),
            'error_type': error_result.get('error_type'),
        }

    def get_module(self, module_name: str):
        """Get a specific module (for testing or debugging)."""
        return self.modules.get(module_name)

    def validate_config(self) -> bool:
        """Validate the complete pipeline configuration."""
        # This would call ConfigValidator
        # For now, just check that all required sections exist
        required_sections = [
            'acquisition', 'preprocessing', 'segmentation',
            'classification', 'counting', 'analytics', 'export'
        ]

        for section in required_sections:
            if section not in self.config:
                logger.warning(f"Missing config section: {section} (using defaults)")

        return True
