"""
Visualization utilities for pipeline simulation and debugging.

Provides functions to save and annotate images at each pipeline stage.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json


class PipelineVisualizer:
    """Visualizes pipeline stages with annotations."""

    def __init__(self, output_dir: str = 'results/simulation'):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save visualization images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Color scheme
        self.colors = {
            'Copepod': (0, 255, 0),      # Green
            'Diatom': (255, 0, 0),        # Blue
            'Dinoflagellate': (0, 0, 255), # Red
            'Ciliate': (255, 255, 0),     # Cyan
            'Other': (128, 128, 128),     # Gray
        }

    def save_original_image(
        self,
        image: np.ndarray,
        sample_id: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save original captured image with metadata overlay.

        Args:
            image: Original RGB image
            sample_id: Unique sample identifier
            metadata: Capture metadata

        Returns:
            Path to saved image
        """
        # Create annotated copy
        annotated = image.copy()

        # Add metadata text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        color = (0, 0, 255)  # Red

        # Add text overlay
        texts = [
            f"Sample ID: {sample_id[:8]}...",
            f"Timestamp: {metadata.get('timestamp', 'N/A')[:19]}",
            f"Magnification: {metadata.get('magnification', 0):.1f}x",
            f"FOV: {metadata.get('fov_mm', [0, 0])[0]:.2f}x{metadata.get('fov_mm', [0, 0])[1]:.2f}mm",
        ]

        y_offset = 30
        for text in texts:
            cv2.putText(
                annotated, text, (10, y_offset),
                font, font_scale, color, thickness
            )
            y_offset += 30

        # Save
        output_path = self.output_dir / f'{sample_id}_01_original.jpg'
        cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

        return str(output_path)

    def save_preprocessed_image(
        self,
        image: np.ndarray,
        sample_id: str,
        stats: Dict[str, Any]
    ) -> str:
        """
        Save preprocessed image with statistics.

        Args:
            image: Preprocessed RGB image
            sample_id: Unique sample identifier
            stats: Preprocessing statistics

        Returns:
            Path to saved image
        """
        annotated = image.copy()

        # Add statistics text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        color = (0, 255, 0)  # Green

        texts = [
            f"Mean Intensity: {stats.get('mean_intensity', 0):.1f}",
            f"Std Dev: {stats.get('std_intensity', 0):.1f}",
            f"SNR: {stats.get('snr_db', 0):.1f} dB",
            f"Denoise: {stats.get('denoise_method', 'none')}",
        ]

        y_offset = 30
        for text in texts:
            cv2.putText(
                annotated, text, (10, y_offset),
                font, font_scale, color, thickness
            )
            y_offset += 30

        # Save
        output_path = self.output_dir / f'{sample_id}_02_preprocessed.jpg'
        cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

        return str(output_path)

    def save_segmentation_image(
        self,
        image: np.ndarray,
        sample_id: str,
        masks: List[np.ndarray],
        bounding_boxes: List[Dict[str, int]],
        centroids: List[Tuple[int, int]]
    ) -> str:
        """
        Save segmentation results with masks and bounding boxes.

        Args:
            image: Original RGB image
            sample_id: Unique sample identifier
            masks: List of binary masks
            bounding_boxes: List of bounding box dicts
            centroids: List of (x, y) centroid coordinates

        Returns:
            Path to saved image
        """
        annotated = image.copy()

        # Draw all detections
        for i, (mask, bbox, centroid) in enumerate(zip(masks, bounding_boxes, centroids)):
            # Draw bounding box
            x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
            cv2.rectangle(
                annotated,
                (x, y), (x + w, y + h),
                (255, 0, 0), 2
            )

            # Draw centroid
            cv2.circle(annotated, centroid, 5, (0, 0, 255), -1)

            # Draw organism ID
            cv2.putText(
                annotated, f"#{i}",
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
            )

            # Overlay mask (semi-transparent)
            mask_rgb = np.zeros_like(image)
            mask_rgb[mask] = [0, 255, 255]  # Yellow
            annotated = cv2.addWeighted(annotated, 1.0, mask_rgb, 0.3, 0)

        # Add count
        cv2.putText(
            annotated, f"Detected: {len(masks)} organisms",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
        )

        # Save
        output_path = self.output_dir / f'{sample_id}_03_segmentation.jpg'
        cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

        return str(output_path)

    def save_classification_image(
        self,
        image: np.ndarray,
        sample_id: str,
        bounding_boxes: List[Dict[str, int]],
        predictions: List[Dict[str, Any]]
    ) -> str:
        """
        Save classification results with labels and confidence.

        Args:
            image: Original RGB image
            sample_id: Unique sample identifier
            bounding_boxes: List of bounding box dicts
            predictions: List of classification predictions

        Returns:
            Path to saved image
        """
        annotated = image.copy()

        # Draw each classified organism
        for i, (bbox, pred) in enumerate(zip(bounding_boxes, predictions)):
            class_name = pred['class_name']
            confidence = pred['confidence']

            # Get color for this class
            color = self.colors.get(class_name, (255, 255, 255))

            # Draw bounding box
            x, y, w, h = bbox['x'], bbox['y'], bbox['w'], bbox['h']
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            # Draw label background
            label = f"{class_name} {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            cv2.rectangle(
                annotated,
                (x, y - label_h - 10), (x + label_w + 10, y),
                color, -1
            )

            # Draw label text
            cv2.putText(
                annotated, label,
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2
            )

        # Add legend
        self._draw_legend(annotated, predictions)

        # Save
        output_path = self.output_dir / f'{sample_id}_04_classification.jpg'
        cv2.imwrite(str(output_path), cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

        return str(output_path)

    def save_final_analysis(
        self,
        image: np.ndarray,
        sample_id: str,
        counts_by_class: Dict[str, int],
        diversity_indices: Dict[str, float],
        bloom_alerts: List[Dict[str, Any]]
    ) -> str:
        """
        Save final analysis with complete statistics.

        Args:
            image: Original RGB image
            sample_id: Unique sample identifier
            counts_by_class: Organism counts by class
            diversity_indices: Diversity metrics
            bloom_alerts: List of bloom alerts

        Returns:
            Path to saved image
        """
        # Create side-by-side visualization
        h, w = image.shape[:2]

        # Create stats panel (right side)
        stats_panel = np.ones((h, w // 2, 3), dtype=np.uint8) * 255

        # Draw stats
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = 50

        # Title
        cv2.putText(
            stats_panel, "Analysis Results",
            (20, y_offset),
            font, 1.0, (0, 0, 0), 2
        )
        y_offset += 50

        # Counts by class
        cv2.putText(
            stats_panel, "Organism Counts:",
            (20, y_offset),
            font, 0.7, (0, 0, 255), 2
        )
        y_offset += 35

        for class_name, count in sorted(counts_by_class.items()):
            color = self.colors.get(class_name, (0, 0, 0))
            cv2.putText(
                stats_panel, f"  {class_name}: {count}",
                (20, y_offset),
                font, 0.6, color, 2
            )
            y_offset += 30

        y_offset += 20

        # Diversity indices
        cv2.putText(
            stats_panel, "Diversity Metrics:",
            (20, y_offset),
            font, 0.7, (0, 0, 255), 2
        )
        y_offset += 35

        metrics = [
            f"Shannon: {diversity_indices.get('shannon', 0):.3f}",
            f"Simpson: {diversity_indices.get('simpson', 0):.3f}",
            f"Richness: {diversity_indices.get('species_richness', 0)}",
            f"Evenness: {diversity_indices.get('evenness', 0):.3f}",
        ]

        for metric in metrics:
            cv2.putText(
                stats_panel, f"  {metric}",
                (20, y_offset),
                font, 0.6, (0, 0, 0), 2
            )
            y_offset += 30

        y_offset += 20

        # Bloom alerts
        cv2.putText(
            stats_panel, "Bloom Alerts:",
            (20, y_offset),
            font, 0.7, (0, 0, 255), 2
        )
        y_offset += 35

        if bloom_alerts:
            for alert in bloom_alerts:
                cv2.putText(
                    stats_panel, f"  {alert['class_name']}",
                    (20, y_offset),
                    font, 0.6, (0, 0, 255), 2
                )
                y_offset += 30
        else:
            cv2.putText(
                stats_panel, "  None detected",
                (20, y_offset),
                font, 0.6, (0, 128, 0), 2
            )

        # Combine image and stats
        combined = np.hstack([image, stats_panel])

        # Save
        output_path = self.output_dir / f'{sample_id}_05_final_analysis.jpg'
        cv2.imwrite(str(output_path), cv2.cvtColor(combined, cv2.COLOR_RGB2BGR))

        return str(output_path)

    def _draw_legend(self, image: np.ndarray, predictions: List[Dict[str, Any]]):
        """Draw class legend on image."""
        # Get unique classes
        unique_classes = set(pred['class_name'] for pred in predictions)

        # Draw legend box
        legend_x = image.shape[1] - 250
        legend_y = 30
        box_height = len(unique_classes) * 30 + 40

        # Semi-transparent background
        overlay = image.copy()
        cv2.rectangle(
            overlay,
            (legend_x - 10, legend_y - 10),
            (legend_x + 240, legend_y + box_height),
            (255, 255, 255), -1
        )
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)

        # Legend title
        cv2.putText(
            image, "Classes:",
            (legend_x, legend_y + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
        )

        # Draw each class
        y_offset = legend_y + 50
        for class_name in sorted(unique_classes):
            color = self.colors.get(class_name, (255, 255, 255))

            # Color box
            cv2.rectangle(
                image,
                (legend_x, y_offset - 15), (legend_x + 20, y_offset - 5),
                color, -1
            )

            # Class name
            cv2.putText(
                image, class_name,
                (legend_x + 30, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )

            y_offset += 30

    def create_summary_grid(
        self,
        sample_id: str,
        stage_images: List[str]
    ) -> str:
        """
        Create a grid view of all pipeline stages.

        Args:
            sample_id: Unique sample identifier
            stage_images: List of paths to stage images

        Returns:
            Path to grid image
        """
        # Load all images
        images = [cv2.imread(path) for path in stage_images if Path(path).exists()]

        if not images:
            return None

        # Resize all to same height
        target_height = 800
        resized = []
        for img in images:
            h, w = img.shape[:2]
            new_w = int(w * target_height / h)
            resized.append(cv2.resize(img, (new_w, target_height)))

        # Create grid (2 rows)
        row1 = np.hstack(resized[:3]) if len(resized) >= 3 else np.hstack(resized)
        row2 = np.hstack(resized[3:]) if len(resized) > 3 else row1

        # Pad if needed
        if row2.shape[1] < row1.shape[1]:
            padding = np.ones((target_height, row1.shape[1] - row2.shape[1], 3), dtype=np.uint8) * 255
            row2 = np.hstack([row2, padding])

        # Stack rows
        grid = np.vstack([row1, row2])

        # Save
        output_path = self.output_dir / f'{sample_id}_grid_summary.jpg'
        cv2.imwrite(str(output_path), grid)

        return str(output_path)

    def save_metadata_json(
        self,
        sample_id: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Save complete metadata as JSON.

        Args:
            sample_id: Unique sample identifier
            metadata: Complete pipeline metadata

        Returns:
            Path to JSON file
        """
        output_path = self.output_dir / f'{sample_id}_metadata.json'

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

        return str(output_path)
