"""
Pipeline modules for Marine Plankton AI Microscopy system.

Each module implements a specific stage of the processing pipeline with
standardized input/output contracts.
"""

from .base import PipelineModule
from .acquisition import AcquisitionModule
from .preprocessing import PreprocessingModule
from .segmentation import SegmentationModule
from .classification import ClassificationModule
from .counting import CountingModule
from .analytics import AnalyticsModule
from .export import ExportModule

__all__ = [
    'PipelineModule',
    'AcquisitionModule',
    'PreprocessingModule',
    'SegmentationModule',
    'ClassificationModule',
    'CountingModule',
    'AnalyticsModule',
    'ExportModule',
]
