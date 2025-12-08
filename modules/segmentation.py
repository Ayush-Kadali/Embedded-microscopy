"""
Module 3: Segmentation

Responsibility: Detect and isolate individual organisms.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import cv2
from .base import PipelineModule


class SegmentationModule(PipelineModule):
    """
    Segments individual organisms from preprocessed images.

    Input Contract:
        - image: np.ndarray[H, W, 3]
        - segmentation_config: dict with method, min_area_px, max_area_px, etc.

    Output Contract:
        - status: str
        - error_message: str | None
        - masks: list of boolean masks
        - bounding_boxes: list of dict(x, y, w, h)
        - centroids: list of (x, y)
        - areas_px: list of int
        - num_detected: int
    """

    def validate_config(self) -> None:
        """Validate segmentation configuration."""
        valid_methods = ['threshold', 'watershed', 'instance_seg']
        method = self.config.get('method', 'watershed')
        if method not in valid_methods:
            raise ValueError(f"method must be one of {valid_methods}")

        if self.config.get('min_area_px', 100) <= 0:
            raise ValueError("min_area_px must be positive")

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data."""
        if 'image' not in input_data:
            raise ValueError("Missing required input: image")

        image = input_data['image']
        if not isinstance(image, np.ndarray):
            raise ValueError("image must be a numpy array")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform segmentation."""
        try:
            image = input_data['image']
            config = input_data.get('segmentation_config', self.config)

            method = config.get('method', 'watershed')
            min_area = config.get('min_area_px', 100)
            max_area = config.get('max_area_px', 50000)

            # Choose segmentation method
            if method == 'threshold':
                masks, bboxes, centroids, areas = self._threshold_segment(image, min_area, max_area)
            elif method == 'watershed':
                masks, bboxes, centroids, areas = self._watershed_segment(image, min_area, max_area)
            else:
                # instance_seg would go here (model-based)
                masks, bboxes, centroids, areas = self._threshold_segment(image, min_area, max_area)

            num_detected = len(masks)
            self.logger.info(f"Segmentation complete: {num_detected} organisms detected")

            return {
                'status': 'success',
                'error_message': None,
                'masks': masks,
                'bounding_boxes': bboxes,
                'centroids': centroids,
                'areas_px': areas,
                'num_detected': num_detected,
            }

        except Exception as e:
            return self.handle_error(e)

    def _threshold_segment(
        self,
        image: np.ndarray,
        min_area: int,
        max_area: int
    ) -> Tuple[List[np.ndarray], List[Dict], List[Tuple], List[int]]:
        """Simple threshold-based segmentation."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Apply adaptive threshold
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

        return self._extract_components(labels, stats, centroids, min_area, max_area)

    def _watershed_segment(
        self,
        image: np.ndarray,
        min_area: int,
        max_area: int
    ) -> Tuple[List[np.ndarray], List[Dict], List[Tuple], List[int]]:
        """Watershed-based segmentation (better for overlapping organisms)."""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

        # Sure background area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # Sure foreground area
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.3 * dist_transform.max(), 255, 0)

        # Unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0

        # Apply watershed
        markers = cv2.watershed(image, markers)

        # Extract components from watershed result
        labels = markers.copy()
        labels[labels == -1] = 0  # Remove boundaries
        labels[labels == 1] = 0   # Remove background

        # Compute stats for each region
        unique_labels = np.unique(labels)
        unique_labels = unique_labels[unique_labels > 1]  # Skip background

        masks = []
        bboxes = []
        centroids_list = []
        areas = []

        for label_id in unique_labels:
            mask = (labels == label_id).astype(np.uint8)
            area = np.sum(mask)

            if min_area <= area <= max_area:
                # Compute bounding box
                coords = np.column_stack(np.where(mask > 0))
                y_min, x_min = coords.min(axis=0)
                y_max, x_max = coords.max(axis=0)

                # Compute centroid
                M = cv2.moments(mask)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                else:
                    cx, cy = (x_min + x_max) // 2, (y_min + y_max) // 2

                masks.append(mask.astype(bool))
                bboxes.append({'x': int(x_min), 'y': int(y_min), 'w': int(x_max - x_min), 'h': int(y_max - y_min)})
                centroids_list.append((int(cx), int(cy)))
                areas.append(int(area))

        return masks, bboxes, centroids_list, areas

    def _extract_components(
        self,
        labels: np.ndarray,
        stats: np.ndarray,
        centroids: np.ndarray,
        min_area: int,
        max_area: int
    ) -> Tuple[List[np.ndarray], List[Dict], List[Tuple], List[int]]:
        """Extract valid components based on area constraints."""
        masks = []
        bboxes = []
        centroids_list = []
        areas = []

        # Skip label 0 (background)
        for i in range(1, len(stats)):
            area = stats[i, cv2.CC_STAT_AREA]

            if min_area <= area <= max_area:
                # Create mask for this component
                mask = (labels == i).astype(bool)

                # Extract bounding box
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]

                masks.append(mask)
                bboxes.append({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)})
                centroids_list.append((int(centroids[i][0]), int(centroids[i][1])))
                areas.append(int(area))

        return masks, bboxes, centroids_list, areas
