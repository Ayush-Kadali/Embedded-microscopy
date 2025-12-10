#!/usr/bin/env python3
"""
Real-Time Plankton Detection with Visual Feedback

Shows live video feed with:
- Bounding boxes around detected organisms
- Species labels and confidence scores
- Live count statistics
- Real-time processing

Perfect for demos without microscope setup.
"""

import cv2
import numpy as np
import yaml
import time
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import logging

from modules.preprocessing import PreprocessingModule
from modules.segmentation import SegmentationModule
from modules.classification import ClassificationModule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealtimeDetector:
    """Real-time plankton detection with visual overlay."""

    def __init__(self, config_path='config/config.yaml'):
        """Initialize detector with pipeline modules."""
        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize modules
        self.preprocessor = PreprocessingModule(self.config.get('preprocessing', {}))
        self.segmenter = SegmentationModule(self.config.get('segmentation', {}))
        self.classifier = ClassificationModule(self.config.get('classification', {}))

        # Session stats
        self.total_detected = 0
        self.species_counts = defaultdict(int)
        self.frame_count = 0
        self.start_time = time.time()

        # Processing stats
        self.fps = 0
        self.processing_time = 0

        # Colors for bounding boxes (BGR format)
        self.colors = {
            'copepod': (0, 255, 0),      # Green
            'diatom': (255, 0, 0),        # Blue
            'dinoflagellate': (0, 165, 255),  # Orange
            'radiolarian': (255, 0, 255),     # Magenta
            'other': (128, 128, 128),     # Gray
        }

        logger.info("Real-time detector initialized")

    def process_frame(self, frame):
        """
        Process single frame and return annotated image.

        Args:
            frame: BGR image from camera

        Returns:
            annotated_frame: Frame with bounding boxes and labels
            organisms: List of detected organisms with metadata
        """
        start_time = time.time()

        # Convert BGR to RGB for pipeline
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create annotated frame (copy of original)
        annotated = frame.copy()

        try:
            # 1. Preprocessing
            prep_result = self.preprocessor.process({
                'image': frame_rgb,
                'metadata': {'timestamp': datetime.now().isoformat()}
            })

            if prep_result['status'] != 'success':
                return annotated, []

            # 2. Segmentation
            seg_result = self.segmenter.process({
                'preprocessed_image': prep_result['preprocessed_image'],
                'original_image': frame_rgb,
                'metadata': prep_result['metadata']
            })

            if seg_result['status'] != 'success':
                return annotated, []

            organisms = seg_result['organisms']

            if len(organisms) == 0:
                return annotated, []

            # 3. Classification
            class_result = self.classifier.process({
                'organisms': organisms,
                'metadata': seg_result['metadata']
            })

            if class_result['status'] != 'success':
                return annotated, organisms

            classified_organisms = class_result['classified_organisms']

            # 4. Draw bounding boxes and labels
            for org in classified_organisms:
                bbox = org['bbox']  # [x, y, width, height]
                x, y, w, h = bbox

                # Get class and confidence
                class_name = org.get('predicted_class', 'unknown')
                confidence = org.get('confidence', 0.0)

                # Get color for this class
                color = self.colors.get(class_name.lower(), (255, 255, 255))

                # Draw bounding box
                cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

                # Prepare label
                label = f"{class_name}: {confidence:.2f}"

                # Get label size for background
                (label_w, label_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )

                # Draw label background
                cv2.rectangle(
                    annotated,
                    (x, y - label_h - 10),
                    (x + label_w + 5, y),
                    color,
                    -1
                )

                # Draw label text
                cv2.putText(
                    annotated,
                    label,
                    (x + 2, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )

                # Update counts
                self.species_counts[class_name] += 1

            self.total_detected += len(classified_organisms)
            self.processing_time = time.time() - start_time

            return annotated, classified_organisms

        except Exception as e:
            logger.error(f"Error processing frame: {e}", exc_info=True)
            return annotated, []

    def draw_stats_overlay(self, frame):
        """Draw statistics overlay on frame."""
        h, w = frame.shape[:2]

        # Calculate stats
        elapsed = time.time() - self.start_time
        self.frame_count += 1

        if elapsed > 0:
            self.fps = self.frame_count / elapsed

        # Create semi-transparent overlay background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 280), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw stats
        font = cv2.FONT_HERSHEY_SIMPLEX
        y = 40
        line_height = 30

        # Title
        cv2.putText(frame, "Real-Time Detection", (20, y),
                   font, 0.8, (0, 255, 255), 2)
        y += line_height

        # FPS and processing time
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        cv2.putText(frame, f"Process: {self.processing_time*1000:.0f}ms", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        # Total detected
        cv2.putText(frame, f"Total: {self.total_detected}", (20, y),
                   font, 0.7, (0, 255, 0), 2)
        y += line_height

        # Species breakdown
        if self.species_counts:
            cv2.putText(frame, "Species:", (20, y),
                       font, 0.6, (255, 255, 0), 1)
            y += line_height

            for species, count in sorted(self.species_counts.items(),
                                        key=lambda x: x[1], reverse=True)[:4]:
                color = self.colors.get(species.lower(), (255, 255, 255))
                cv2.putText(frame, f"  {species}: {count}", (30, y),
                           font, 0.5, color, 1)
                y += line_height - 5

        # Instructions
        y = h - 40
        cv2.putText(frame, "Press 'q' to quit | 's' to save snapshot", (20, y),
                   font, 0.5, (255, 255, 0), 1)

    def run(self, camera_source=0, show_original=False, save_video=False):
        """
        Run real-time detection.

        Args:
            camera_source: Camera index or video file
            show_original: Show original alongside processed
            save_video: Save annotated video to file
        """
        logger.info("="*80)
        logger.info("REAL-TIME PLANKTON DETECTION")
        logger.info("="*80)
        logger.info(f"Camera source: {camera_source}")
        logger.info("Press 'q' to quit, 's' to save snapshot")
        logger.info("")

        cap = cv2.VideoCapture(camera_source)

        if not cap.isOpened():
            logger.error(f"Failed to open camera: {camera_source}")
            return

        # Get camera properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"Camera: {width}x{height} @ {fps} FPS")

        # Setup video writer if saving
        video_writer = None
        if save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/realtime_detection_{timestamp}.mp4"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))
            logger.info(f"Saving video to: {output_path}")

        self.start_time = time.time()
        snapshot_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    break

                # Process frame
                annotated_frame, organisms = self.process_frame(frame)

                # Add stats overlay
                self.draw_stats_overlay(annotated_frame)

                # Show windows
                if show_original:
                    combined = np.hstack([frame, annotated_frame])
                    cv2.imshow('Original | Detected', combined)
                else:
                    cv2.imshow('Real-Time Detection', annotated_frame)

                # Save video if enabled
                if video_writer:
                    video_writer.write(annotated_frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    logger.info("Quit requested")
                    break
                elif key == ord('s'):
                    # Save snapshot
                    snapshot_path = f"results/snapshot_{snapshot_count:04d}.jpg"
                    cv2.imwrite(snapshot_path, annotated_frame)
                    logger.info(f"Saved snapshot: {snapshot_path}")
                    snapshot_count += 1

        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")

        finally:
            cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()

            # Print final stats
            self._print_summary()

    def _print_summary(self):
        """Print final session summary."""
        elapsed = time.time() - self.start_time

        logger.info("")
        logger.info("="*80)
        logger.info("SESSION COMPLETE")
        logger.info("="*80)
        logger.info(f"Duration: {elapsed:.1f}s")
        logger.info(f"Frames processed: {self.frame_count}")
        logger.info(f"Average FPS: {self.fps:.1f}")
        logger.info(f"Total organisms detected: {self.total_detected}")
        logger.info("")

        if self.species_counts:
            logger.info("Species breakdown:")
            for species, count in sorted(self.species_counts.items(),
                                        key=lambda x: x[1], reverse=True):
                pct = (count / self.total_detected * 100) if self.total_detected > 0 else 0
                logger.info(f"  {species}: {count} ({pct:.1f}%)")

        logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Real-Time Plankton Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with webcam
  python realtime_detection.py

  # Use specific camera
  python realtime_detection.py --camera 1

  # Process video file
  python realtime_detection.py --camera video.mp4

  # Show original and processed side-by-side
  python realtime_detection.py --show-original

  # Save output video
  python realtime_detection.py --save-video

Controls:
  q - Quit
  s - Save snapshot
        """
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Pipeline configuration file'
    )

    parser.add_argument(
        '--camera',
        type=str,
        default='0',
        help='Camera index (0, 1...) or video file path'
    )

    parser.add_argument(
        '--show-original',
        action='store_true',
        help='Show original and processed side-by-side'
    )

    parser.add_argument(
        '--save-video',
        action='store_true',
        help='Save annotated video to file'
    )

    args = parser.parse_args()

    # Convert camera argument
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera

    # Create detector and run
    detector = RealtimeDetector(config_path=args.config)
    detector.run(
        camera_source=camera_source,
        show_original=args.show_original,
        save_video=args.save_video
    )


if __name__ == '__main__':
    main()
