"""
Module 2: Preprocessing

Responsibility: Denoise, normalize, and correct illumination.
"""

from typing import Dict, Any, Optional
import numpy as np
import cv2
from .base import PipelineModule


class PreprocessingModule(PipelineModule):
    """
    Preprocesses raw microscope images for segmentation.

    Input Contract:
        - image: np.ndarray[H, W, 3]
        - preprocessing_config: dict with denoise_method, normalize, etc.

    Output Contract:
        - status: str
        - error_message: str | None
        - processed_image: np.ndarray[H, W, 3]
        - preprocessing_stats: dict with mean, std, snr, background_level
    """

    def validate_config(self) -> None:
        """Validate preprocessing configuration."""
        valid_methods = ['gaussian', 'bilateral', 'nlm', 'none']
        denoise = self.config.get('denoise_method', 'bilateral')
        if denoise not in valid_methods:
            raise ValueError(f"denoise_method must be one of {valid_methods}")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        if 'image' not in input_data:
            raise ValueError("Missing required input: image")

        image = input_data['image']
        if not isinstance(image, np.ndarray):
            raise ValueError("image must be a numpy array")

        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError("image must be RGB (H, W, 3)")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply preprocessing pipeline."""
        try:
            image = input_data['image'].copy()
            config = input_data.get('preprocessing_config', self.config)

            # 1. Denoise
            denoise_method = config.get('denoise_method', 'bilateral')
            if denoise_method == 'gaussian':
                image = cv2.GaussianBlur(image, (5, 5), 0)
            elif denoise_method == 'bilateral':
                image = cv2.bilateralFilter(image, 9, 75, 75)
            elif denoise_method == 'nlm':
                image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

            # 2. Background correction
            if config.get('background_correction', True):
                image = self._correct_background(image)

            # 3. Normalize
            if config.get('normalize', True):
                image = self._normalize(image)

            # 4. Flatfield correction (if illumination profile provided)
            if config.get('flatfield_correction', False):
                illum_profile = config.get('illumination_profile')
                if illum_profile is not None:
                    image = self._flatfield_correct(image, illum_profile)

            # Compute statistics
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            stats = {
                'mean_intensity': float(np.mean(gray)),
                'std_intensity': float(np.std(gray)),
                'snr_db': self._compute_snr(gray),
                'background_level': float(np.percentile(gray, 10)),
            }

            self.logger.info(f"Preprocessing complete: mean={stats['mean_intensity']:.1f}, SNR={stats['snr_db']:.1f}dB")

            return {
                'status': 'success',
                'error_message': None,
                'processed_image': image,
                'preprocessing_stats': stats,
            }

        except Exception as e:
            return self.handle_error(e)

    def _correct_background(self, image: np.ndarray) -> np.ndarray:
        """Remove background using morphological operations."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Estimate background with large morphological opening
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
        background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

        # Subtract background
        corrected_gray = cv2.subtract(gray, background)
        corrected_gray = cv2.add(corrected_gray, 128)  # Add offset to avoid clipping

        # Convert back to RGB
        corrected = cv2.cvtColor(corrected_gray, cv2.COLOR_GRAY2RGB)
        return corrected

    def _normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize intensity to full dynamic range."""
        # Normalize each channel independently
        normalized = np.zeros_like(image)
        for i in range(3):
            channel = image[:, :, i]
            min_val = np.percentile(channel, 1)
            max_val = np.percentile(channel, 99)
            normalized[:, :, i] = np.clip((channel - min_val) * 255.0 / (max_val - min_val), 0, 255).astype(np.uint8)

        return normalized

    def _flatfield_correct(self, image: np.ndarray, illumination_profile: np.ndarray) -> np.ndarray:
        """Correct non-uniform illumination."""
        # Simple division by illumination profile
        corrected = (image.astype(np.float32) / (illumination_profile + 1e-6)) * 128
        return np.clip(corrected, 0, 255).astype(np.uint8)

    def _compute_snr(self, gray_image: np.ndarray) -> float:
        """Compute signal-to-noise ratio in dB."""
        signal = np.mean(gray_image)
        noise = np.std(gray_image)
        if noise == 0:
            return 100.0  # Perfect signal
        snr = 20 * np.log10(signal / noise)
        return float(snr)
