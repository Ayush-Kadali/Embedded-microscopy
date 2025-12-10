#!/usr/bin/env python3
"""
Buffered Video Processing for High Frame Rate Recording

Two-phase approach:
1. Record video at high frame rate
2. Process frames when CPU is available (queue-based)

Perfect for scenarios where real-time processing is too slow.
"""

import cv2
import numpy as np
import yaml
import time
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
from threading import Thread, Lock
import queue
import logging

from modules.preprocessing import PreprocessingModule
from modules.segmentation import SegmentationModule
from modules.classification import ClassificationModule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BufferedDetector:
    """Buffered detection with frame queue for high-speed recording."""

    def __init__(self, config_path='config/config.yaml', queue_size=100):
        """Initialize buffered detector."""
        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize modules
        self.preprocessor = PreprocessingModule(self.config.get('preprocessing', {}))
        self.segmenter = SegmentationModule(self.config.get('segmentation', {}))
        self.classifier = ClassificationModule(self.config.get('classification', {}))

        # Frame queue for processing
        self.frame_queue = queue.Queue(maxsize=queue_size)
        self.results_queue = queue.Queue()

        # Stats
        self.frames_captured = 0
        self.frames_processed = 0
        self.total_organisms = 0
        self.species_counts = defaultdict(int)

        # Threading
        self.processing = False
        self.lock = Lock()

        # Colors for visualization
        self.colors = {
            'copepod': (0, 255, 0),
            'diatom': (255, 0, 0),
            'dinoflagellate': (0, 165, 255),
            'radiolarian': (255, 0, 255),
            'other': (128, 128, 128),
        }

        logger.info(f"Buffered detector initialized (queue size: {queue_size})")

    def process_frame(self, frame, frame_number):
        """Process single frame."""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Preprocessing
            prep_result = self.preprocessor.process({
                'image': frame_rgb,
                'metadata': {'timestamp': datetime.now().isoformat()}
            })

            if prep_result['status'] != 'success':
                return None

            # Segmentation
            seg_result = self.segmenter.process({
                'preprocessed_image': prep_result['preprocessed_image'],
                'original_image': frame_rgb,
                'metadata': prep_result['metadata']
            })

            if seg_result['status'] != 'success' or len(seg_result['organisms']) == 0:
                return None

            # Classification
            class_result = self.classifier.process({
                'organisms': seg_result['organisms'],
                'metadata': seg_result['metadata']
            })

            if class_result['status'] != 'success':
                return None

            return {
                'frame_number': frame_number,
                'organisms': class_result['classified_organisms'],
                'frame': frame
            }

        except Exception as e:
            logger.error(f"Error processing frame {frame_number}: {e}")
            return None

    def processing_worker(self):
        """Worker thread for processing frames from queue."""
        logger.info("Processing worker started")

        while self.processing:
            try:
                # Get frame from queue (with timeout to allow checking self.processing)
                try:
                    frame, frame_number = self.frame_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                # Process frame
                result = self.process_frame(frame, frame_number)

                if result:
                    # Update stats
                    with self.lock:
                        self.frames_processed += 1
                        self.total_organisms += len(result['organisms'])

                        for org in result['organisms']:
                            species = org.get('predicted_class', 'unknown')
                            self.species_counts[species] += 1

                    # Put result in results queue
                    self.results_queue.put(result)

                    # Log progress
                    if self.frames_processed % 10 == 0:
                        logger.info(f"Processed: {self.frames_processed}/{self.frames_captured} frames, "
                                  f"{self.total_organisms} organisms")

                self.frame_queue.task_done()

            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)

        logger.info("Processing worker stopped")

    def record_and_process(self, camera_source=0, duration=None,
                          process_live=True, save_video=True):
        """
        Record video and process frames.

        Args:
            camera_source: Camera index or video file
            duration: Recording duration in seconds (None = until stopped)
            process_live: Process frames during recording
            save_video: Save raw video
        """
        logger.info("="*80)
        logger.info("BUFFERED VIDEO PROCESSING")
        logger.info("="*80)
        logger.info(f"Camera: {camera_source}")
        logger.info(f"Live processing: {process_live}")
        logger.info(f"Save video: {save_video}")
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

        # Setup video writer
        video_writer = None
        output_path = None
        if save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/recorded_{timestamp}.mp4"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            logger.info(f"Recording to: {output_path}")

        # Start processing worker if live processing
        if process_live:
            self.processing = True
            worker = Thread(target=self.processing_worker, daemon=True)
            worker.start()
            logger.info("Live processing enabled")

        start_time = time.time()
        frames_to_process = []

        try:
            logger.info("\nRecording... (press 'q' to stop)")

            while True:
                elapsed = time.time() - start_time

                # Check duration limit
                if duration and elapsed > duration:
                    logger.info(f"Duration limit reached ({duration}s)")
                    break

                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    break

                self.frames_captured += 1

                # Save to video file
                if video_writer:
                    video_writer.write(frame)

                # Add to processing queue or save for later
                if process_live:
                    try:
                        self.frame_queue.put((frame.copy(), self.frames_captured), block=False)
                    except queue.Full:
                        logger.warning(f"Queue full, skipping frame {self.frames_captured}")
                else:
                    # Save frame for post-processing
                    frames_to_process.append((frame.copy(), self.frames_captured))

                # Show live feed
                display = frame.copy()
                self._add_recording_overlay(display, elapsed)
                cv2.imshow('Recording', display)

                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Recording stopped by user")
                    break

        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")

        finally:
            cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()

            logger.info(f"\nRecording complete: {self.frames_captured} frames captured")

            # Wait for live processing to complete
            if process_live:
                logger.info("Waiting for processing to complete...")
                self.frame_queue.join()
                self.processing = False
                worker.join()

            # Post-process if not done live
            elif frames_to_process:
                logger.info(f"\nPost-processing {len(frames_to_process)} frames...")
                self._post_process_frames(frames_to_process)

            # Generate annotated video from results
            if self.frames_processed > 0:
                self._generate_annotated_video(output_path)

            self._print_summary()

    def _post_process_frames(self, frames):
        """Process saved frames after recording."""
        total = len(frames)

        for idx, (frame, frame_number) in enumerate(frames):
            result = self.process_frame(frame, frame_number)

            if result:
                self.frames_processed += 1
                self.total_organisms += len(result['organisms'])

                for org in result['organisms']:
                    species = org.get('predicted_class', 'unknown')
                    self.species_counts[species] += 1

                self.results_queue.put(result)

            # Progress update
            if (idx + 1) % 10 == 0:
                progress = (idx + 1) / total * 100
                logger.info(f"Progress: {idx+1}/{total} ({progress:.1f}%) - "
                          f"{self.total_organisms} organisms detected")

    def _generate_annotated_video(self, original_video_path):
        """Generate annotated video from results."""
        logger.info("\nGenerating annotated video...")

        # Collect all results
        results_by_frame = {}
        while not self.results_queue.empty():
            result = self.results_queue.get()
            results_by_frame[result['frame_number']] = result

        if not results_by_frame:
            logger.warning("No results to annotate")
            return

        # Read original video and annotate
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"results/annotated_{timestamp}.mp4"

        cap = cv2.VideoCapture(original_video_path) if original_video_path else None

        if cap and cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            frame_num = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_num += 1

                # Annotate if we have results for this frame
                if frame_num in results_by_frame:
                    result = results_by_frame[frame_num]
                    self._annotate_frame(frame, result['organisms'])

                writer.write(frame)

            cap.release()
            writer.release()

            logger.info(f"Annotated video saved: {output_path}")
        else:
            logger.warning("Could not read original video for annotation")

    def _annotate_frame(self, frame, organisms):
        """Add bounding boxes and labels to frame."""
        for org in organisms:
            bbox = org['bbox']
            x, y, w, h = bbox

            class_name = org.get('predicted_class', 'unknown')
            confidence = org.get('confidence', 0.0)

            color = self.colors.get(class_name.lower(), (255, 255, 255))

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(frame, label, (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    def _add_recording_overlay(self, frame, elapsed):
        """Add recording status overlay."""
        h, w = frame.shape[:2]

        # Recording indicator
        cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (50, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Time
        cv2.putText(frame, f"Time: {int(elapsed)}s", (120, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # Frame count
        cv2.putText(frame, f"Frames: {self.frames_captured}", (30, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Processing status
        with self.lock:
            status = f"Processed: {self.frames_processed} | Detected: {self.total_organisms}"
        cv2.putText(frame, status, (30, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

    def _print_summary(self):
        """Print final summary."""
        logger.info("")
        logger.info("="*80)
        logger.info("PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"Frames captured: {self.frames_captured}")
        logger.info(f"Frames processed: {self.frames_processed}")
        logger.info(f"Total organisms: {self.total_organisms}")
        logger.info("")

        if self.species_counts:
            logger.info("Species breakdown:")
            for species, count in sorted(self.species_counts.items(),
                                        key=lambda x: x[1], reverse=True):
                pct = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
                logger.info(f"  {species}: {count} ({pct:.1f}%)")

        logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Buffered Video Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record and process live (default)
  python buffered_detection.py --camera 0 --duration 60

  # Record first, process later (for high frame rate)
  python buffered_detection.py --camera 0 --duration 30 --no-live

  # Process existing video file
  python buffered_detection.py --camera video.mp4 --no-live
        """
    )

    parser.add_argument('--config', default='config/config.yaml')
    parser.add_argument('--camera', type=str, default='0')
    parser.add_argument('--duration', type=int, default=None,
                       help='Recording duration in seconds')
    parser.add_argument('--no-live', action='store_true',
                       help='Disable live processing (record only, process after)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save raw video')
    parser.add_argument('--queue-size', type=int, default=100,
                       help='Processing queue size')

    args = parser.parse_args()

    # Convert camera
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera

    detector = BufferedDetector(
        config_path=args.config,
        queue_size=args.queue_size
    )

    detector.record_and_process(
        camera_source=camera_source,
        duration=args.duration,
        process_live=not args.no_live,
        save_video=not args.no_save
    )


if __name__ == '__main__':
    main()
