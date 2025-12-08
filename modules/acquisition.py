"""
Module 1: Image Acquisition

Responsibility: Capture raw microscope images plus physical metadata.
"""

from typing import Dict, Any, Optional
import numpy as np
from datetime import datetime
import uuid
from .base import PipelineModule


class AcquisitionModule(PipelineModule):
    """
    Handles image acquisition from microscope camera with metadata.

    Input Contract:
        - magnification: float (0.7-4.5)
        - exposure_ms: int
        - focus_position: int | None
        - capture_metadata: dict with timestamp, gps_lat, gps_lon, operator_id

    Output Contract:
        - status: str ('success' | 'error')
        - error_message: str | None
        - image: np.ndarray[H, W, 3] uint8 RGB
        - metadata: dict with capture details
    """

    def validate_config(self) -> None:
        """Validate acquisition configuration."""
        required = ['camera_type', 'sensor_pixel_size_um']
        for key in required:
            if key not in self.config:
                raise ValueError(f"Missing required config: {key}")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input parameters."""
        required = ['magnification', 'exposure_ms']
        for key in required:
            if key not in input_data:
                raise ValueError(f"Missing required input: {key}")

        mag = input_data['magnification']
        if not (0.7 <= mag <= 4.5):
            raise ValueError(f"Magnification {mag} out of range [0.7, 4.5]")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture image and generate metadata.

        For now, this is a stub that generates synthetic data.
        Replace with actual camera interface (Picamera2) in production.
        """
        try:
            magnification = input_data['magnification']
            exposure_ms = input_data['exposure_ms']
            focus_position = input_data.get('focus_position')
            capture_meta = input_data.get('capture_metadata', {})

            # STUB: Generate synthetic image (replace with actual camera capture)
            # In production: use Picamera2/libcamera
            image = self._capture_image(exposure_ms)

            # Calculate resolution and FOV
            sensor_pixel_size = self.config.get('sensor_pixel_size_um', 1.55)
            resolution_um_per_px = sensor_pixel_size / magnification

            # Calculate field of view in mm
            h, w = image.shape[:2]
            fov_width_mm = (w * resolution_um_per_px) / 1000
            fov_height_mm = (h * resolution_um_per_px) / 1000

            # Build metadata
            metadata = {
                'capture_id': str(uuid.uuid4()),
                'timestamp': capture_meta.get('timestamp', datetime.now().isoformat()),
                'gps_coordinates': [
                    capture_meta.get('gps_lat'),
                    capture_meta.get('gps_lon')
                ] if capture_meta.get('gps_lat') else None,
                'magnification': magnification,
                'exposure_ms': exposure_ms,
                'resolution_um_per_px': resolution_um_per_px,
                'fov_mm': [fov_width_mm, fov_height_mm],
                'sensor_temp_c': None,  # Add sensor temp reading in production
                'focus_position': focus_position,
                'operator_id': capture_meta.get('operator_id'),
            }

            self.logger.info(f"Image acquired: {image.shape}, FOV: {fov_width_mm:.2f}x{fov_height_mm:.2f}mm")

            return {
                'status': 'success',
                'error_message': None,
                'image': image,
                'metadata': metadata,
            }

        except Exception as e:
            return self.handle_error(e)

    def _capture_image(self, exposure_ms: int) -> np.ndarray:
        """
        Stub method for image capture.

        In production, replace with:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            config = picam2.create_still_configuration()
            picam2.configure(config)
            picam2.start()
            image = picam2.capture_array()
            picam2.stop()
            return image

        For now, generate synthetic microscope-like image.
        """
        # Generate synthetic grayscale image with some random blobs (simulating organisms)
        img = np.random.randint(200, 230, (2028, 2028, 3), dtype=np.uint8)

        # Add some random "organisms" (dark blobs)
        num_organisms = np.random.randint(5, 20)
        for _ in range(num_organisms):
            center_x = np.random.randint(100, 1928)
            center_y = np.random.randint(100, 1928)
            radius = np.random.randint(20, 80)
            y, x = np.ogrid[-center_y:2028-center_y, -center_x:2028-center_x]
            mask = x*x + y*y <= radius*radius
            img[mask] = np.random.randint(50, 150, 3)

        return img
