"""
Base module interface for the Marine Plankton AI Microscopy pipeline.

This module defines the abstract base class that all pipeline modules must inherit from,
ensuring consistent interfaces and error handling across the entire system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineModule(ABC):
    """
    Abstract base class for all pipeline modules.

    All modules must implement:
    - validate_config: Validate module configuration
    - validate_input: Validate input data against the module's input contract
    - process: Main processing logic that transforms input to output

    All modules inherit:
    - handle_error: Standardized error handling
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the module with configuration.

        Args:
            config: Module-specific configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.validate_config()
            self.logger.info(f"{self.__class__.__name__} initialized successfully")
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise

    @abstractmethod
    def validate_config(self) -> None:
        """
        Validate the module configuration.

        Should raise ValueError if configuration is invalid.
        Each module implements its own config validation logic.
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Validate input data against the module's input contract.

        Args:
            input_data: Input data dictionary

        Raises:
            ValueError: If input data doesn't match the contract
        """
        pass

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method that transforms input to output.

        Args:
            input_data: Input data dictionary matching the module's input contract

        Returns:
            Output dictionary matching the module's output contract
            Must always include 'status' field: 'success' or 'error'
        """
        pass

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Standardized error handling for all modules.

        Args:
            error: Exception that occurred during processing

        Returns:
            Standardized error response dictionary
        """
        self.logger.error(f"Error in {self.__class__.__name__}: {error}")
        return {
            "status": "error",
            "error_message": str(error),
            "error_type": type(error).__name__,
        }

    def __call__(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience method to call process with automatic error handling.

        Args:
            input_data: Input data dictionary

        Returns:
            Output dictionary or error dictionary
        """
        try:
            self.validate_input(input_data)
            return self.process(input_data)
        except Exception as e:
            return self.handle_error(e)
