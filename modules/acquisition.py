"""
Module 1: Image Acquisition

Responsibility: Capture raw microscope images plus physical metadata.
"""

from typing import Dict, Any, Optional
import numpy as np
from datetime import datetime
import uuid
import cv2
from pathlib import Path
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
        # Check for mode (optional, defaults to synthetic)
        mode = input_data.get('mode', 'synthetic')

        if mode == 'file':
            # For file mode, we need image_path
            if 'image_path' not in input_data:
                raise ValueError("File mode requires 'image_path' parameter")
            if not Path(input_data['image_path']).exists():
                raise ValueError(f"Image file not found: {input_data['image_path']}")
        else:
            # For synthetic/camera modes, we need standard params
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

        Supports multiple modes:
        - 'synthetic': Generate synthetic test image
        - 'file': Load from image file
        - 'camera': Capture from Pi HQ Camera (requires Picamera2)
        - 'video': Extract frame from video file
        """
        try:
            mode = input_data.get('mode', 'synthetic')
            capture_meta = input_data.get('capture_metadata', {})

            # Acquire image based on mode
            if mode == 'file':
                image = self._load_from_file(input_data['image_path'])
                # Use default values for file mode
                magnification = input_data.get('magnification', 2.0)
                exposure_ms = input_data.get('exposure_ms', 100)
                focus_position = input_data.get('focus_position')
            elif mode == 'camera':
                magnification = input_data['magnification']
                exposure_ms = input_data['exposure_ms']
                focus_position = input_data.get('focus_position')
                image = self._capture_from_camera(exposure_ms)
            elif mode == 'video':
                image = self._extract_from_video(
                    input_data['video_path'],
                    input_data.get('frame_number', 0)
                )
                magnification = input_data.get('magnification', 2.0)
                exposure_ms = input_data.get('exposure_ms', 100)
                focus_position = input_data.get('focus_position')
            else:  # synthetic
                magnification = input_data['magnification']
                exposure_ms = input_data['exposure_ms']
                focus_position = input_data.get('focus_position')
                image = self._generate_synthetic(exposure_ms)

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

    def _load_from_file(self, image_path: str) -> np.ndarray:
        """
        Load image from file.

        Args:
            image_path: Path to image file

        Returns:
            RGB image as numpy array
        """
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Failed to load image from {image_path}")

        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Ensure grayscale images are converted to 3-channel
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        self.logger.info(f"Loaded image from file: {image_path}, shape: {img.shape}")
        return img

    def _capture_from_camera(self, exposure_ms: int) -> np.ndarray:
        """
        Capture image from Raspberry Pi HQ Camera.

        Args:
            exposure_ms: Exposure time in milliseconds

        Returns:
            RGB image as numpy array
        """
        try:
            from picamera2 import Picamera2

            picam2 = Picamera2()
            config = picam2.create_still_configuration()
            picam2.configure(config)
            picam2.start()

            # Set exposure if supported
            # picam2.set_controls({"ExposureTime": exposure_ms * 1000})

            image = picam2.capture_array()
            picam2.stop()

            self.logger.info(f"Captured from camera: {image.shape}")
            return image

        except ImportError:
            raise RuntimeError(
                "Picamera2 not available. Install with: pip install picamera2"
            )
        except Exception as e:
            raise RuntimeError(f"Camera capture failed: {e}")

    def _extract_from_video(self, video_path: str, frame_number: int = 0) -> np.ndarray:
        """
        Extract a frame from video file.

        Args:
            video_path: Path to video file
            frame_number: Frame index to extract (0-based)

        Returns:
            RGB image as numpy array
        """
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        # Seek to frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError(f"Failed to read frame {frame_number} from {video_path}")

        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.logger.info(f"Extracted frame {frame_number} from video: {video_path}")
        return frame

    def _generate_synthetic(self, exposure_ms: int) -> np.ndarray:
        """
        Generate synthetic microscope-like image for testing.

        Args:
            exposure_ms: Simulated exposure time (affects brightness)

        Returns:
            RGB image as numpy array
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

        self.logger.info(f"Generated synthetic image: {img.shape}")
        return img
