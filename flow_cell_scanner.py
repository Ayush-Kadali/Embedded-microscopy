#!/usr/bin/env python3
"""
Flow Cell Scanner for Continuous Plankton Monitoring

This module handles real-time scanning of plankton as water flows through
a custom flow cell (made from microscope slides and masking tape).

Features:
- Continuous video capture from microscope camera
- Real-time frame processing and plankton detection
- Flow rate and volume tracking
- Live results display
- Session summary and export
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

from pipeline import PipelineManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FlowCellScanner:
    """
    Handles continuous scanning of plankton through a flow cell.
    """

    def __init__(self, config_path: str, camera_source: int = 0,
                 flow_rate_ml_min: float = 1.0, frame_interval: float = 1.0):
        """
        Initialize the flow cell scanner.

        Args:
            config_path: Path to pipeline configuration YAML
            camera_source: Camera index (0 for default USB cam, or video file path)
            flow_rate_ml_min: Flow rate in mL/min (from syringe pump)
            frame_interval: Time between frame captures in seconds
        """
        # Load pipeline configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize pipeline
        self.pipeline = PipelineManager(self.config)

        # Flow parameters
        self.camera_source = camera_source
        self.flow_rate_ml_min = flow_rate_ml_min
        self.frame_interval = frame_interval

        # Session tracking
        self.session_start_time = None
        self.total_organisms = 0
        self.organisms_by_class = defaultdict(int)
        self.frames_processed = 0
        self.total_volume_ml = 0.0

        # Results storage
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path(f"results/flow_cell_{self.session_id}")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Flow Cell Scanner initialized")
        logger.info(f"  Camera source: {camera_source}")
        logger.info(f"  Flow rate: {flow_rate_ml_min} mL/min")
        logger.info(f"  Frame interval: {frame_interval}s")
        logger.info(f"  Results dir: {self.results_dir}")

    def start_scanning(self, duration_seconds: int = None):
        """
        Start continuous scanning session.

        Args:
            duration_seconds: Maximum scanning duration (None = manual stop)
        """
        logger.info("="*80)
        logger.info("STARTING FLOW CELL SCANNING SESSION")
        logger.info("="*80)
        logger.info("Press 'q' to stop scanning")
        logger.info("")

        # Open camera/video
        cap = cv2.VideoCapture(self.camera_source)

        if not cap.isOpened():
            logger.error(f"Failed to open camera source: {self.camera_source}")
            return

        # Get camera properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"Camera: {width}x{height} @ {fps} FPS")
        logger.info("")

        self.session_start_time = time.time()
        last_process_time = 0

        try:
            while True:
                # Check duration limit
                elapsed = time.time() - self.session_start_time
                if duration_seconds and elapsed > duration_seconds:
                    logger.info(f"Duration limit reached ({duration_seconds}s)")
                    break

                # Read frame
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame, stopping")
                    break

                # Check if it's time to process a frame
                current_time = time.time()
                if current_time - last_process_time >= self.frame_interval:
                    # Process this frame
                    self._process_frame(frame, elapsed)
                    last_process_time = current_time

                    # Display live stats
                    self._display_stats(elapsed)

                # Display frame (optional - comment out for headless operation)
                display_frame = frame.copy()
                self._add_overlay(display_frame, elapsed)
                cv2.imshow('Flow Cell Scanner', display_frame)

                # Check for quit command
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("User requested stop")
                    break

        except KeyboardInterrupt:
            logger.info("\nKeyboard interrupt received")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            self._generate_summary()

    def _process_frame(self, frame: np.ndarray, elapsed_time: float):
        """
        Process a single frame through the pipeline.

        Args:
            frame: BGR image from camera
            elapsed_time: Time elapsed since session start (seconds)
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Save frame for processing
        frame_path = self.results_dir / f"frame_{self.frames_processed:06d}.jpg"
        cv2.imwrite(str(frame_path), frame)

        # Prepare acquisition parameters
        acquisition_params = {
            'mode': 'file',
            'image_path': str(frame_path),
            'magnification': 2.0,  # Adjust based on your setup
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'operator_id': 'flow_cell',
                'session_id': self.session_id,
                'frame_number': self.frames_processed,
                'elapsed_seconds': elapsed_time,
            }
        }

        # Execute pipeline
        result = self.pipeline.execute_pipeline(acquisition_params)

        if result['status'] == 'success':
            # Update counters
            organisms_in_frame = result['summary']['total_organisms']
            self.total_organisms += organisms_in_frame

            # Update class counts
            for class_name, count in result['summary']['counts_by_class'].items():
                self.organisms_by_class[class_name] += count

            # Calculate volume processed
            # Volume = flow_rate (mL/min) * time_interval (s) / 60 (s/min)
            volume_increment = (self.flow_rate_ml_min * self.frame_interval) / 60.0
            self.total_volume_ml += volume_increment

            logger.info(f"Frame {self.frames_processed}: {organisms_in_frame} organisms detected")
        else:
            logger.warning(f"Frame {self.frames_processed}: Processing failed - {result.get('error_message')}")

        self.frames_processed += 1

    def _display_stats(self, elapsed_time: float):
        """Display current scanning statistics."""
        logger.info("")
        logger.info("─" * 80)
        logger.info(f"SESSION STATS - Elapsed: {int(elapsed_time)}s")
        logger.info("─" * 80)
        logger.info(f"  Frames processed: {self.frames_processed}")
        logger.info(f"  Total organisms: {self.total_organisms}")
        logger.info(f"  Volume scanned: {self.total_volume_ml:.3f} mL")

        if self.total_volume_ml > 0:
            concentration = self.total_organisms / self.total_volume_ml
            logger.info(f"  Concentration: {concentration:.1f} organisms/mL")

        if self.organisms_by_class:
            logger.info("  Organisms by class:")
            for class_name, count in sorted(self.organisms_by_class.items(),
                                           key=lambda x: x[1], reverse=True):
                percentage = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
                logger.info(f"    {class_name}: {count} ({percentage:.1f}%)")
        logger.info("─" * 80)
        logger.info("")

    def _add_overlay(self, frame: np.ndarray, elapsed_time: float):
        """Add information overlay to frame for display."""
        h, w = frame.shape[:2]

        # Semi-transparent overlay background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = 40
        line_height = 25

        cv2.putText(frame, f"Flow Cell Scanner", (20, y_offset),
                   font, 0.7, (0, 255, 0), 2)
        y_offset += line_height

        cv2.putText(frame, f"Time: {int(elapsed_time)}s", (20, y_offset),
                   font, 0.5, (255, 255, 255), 1)
        y_offset += line_height

        cv2.putText(frame, f"Frames: {self.frames_processed}", (20, y_offset),
                   font, 0.5, (255, 255, 255), 1)
        y_offset += line_height

        cv2.putText(frame, f"Organisms: {self.total_organisms}", (20, y_offset),
                   font, 0.5, (255, 255, 255), 1)
        y_offset += line_height

        cv2.putText(frame, f"Volume: {self.total_volume_ml:.2f} mL", (20, y_offset),
                   font, 0.5, (255, 255, 255), 1)
        y_offset += line_height

        cv2.putText(frame, "Press 'q' to stop", (20, y_offset),
                   font, 0.5, (255, 255, 0), 1)

    def _generate_summary(self):
        """Generate and save session summary."""
        session_duration = time.time() - self.session_start_time

        logger.info("")
        logger.info("="*80)
        logger.info("FLOW CELL SCANNING SESSION COMPLETE")
        logger.info("="*80)
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Duration: {int(session_duration)}s ({session_duration/60:.1f} min)")
        logger.info(f"Frames processed: {self.frames_processed}")
        logger.info(f"Total organisms detected: {self.total_organisms}")
        logger.info(f"Total volume scanned: {self.total_volume_ml:.3f} mL")

        if self.total_volume_ml > 0:
            concentration = self.total_organisms / self.total_volume_ml
            logger.info(f"Average concentration: {concentration:.2f} organisms/mL")

        logger.info("\nOrganisms by class:")
        for class_name, count in sorted(self.organisms_by_class.items(),
                                       key=lambda x: x[1], reverse=True):
            percentage = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
            logger.info(f"  {class_name}: {count} ({percentage:.1f}%)")

        # Save summary to file
        summary_path = self.results_dir / "session_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(f"Flow Cell Scanning Session Summary\n")
            f.write(f"=" * 80 + "\n\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Start time: {datetime.fromtimestamp(self.session_start_time).isoformat()}\n")
            f.write(f"Duration: {int(session_duration)}s ({session_duration/60:.1f} min)\n")
            f.write(f"Flow rate: {self.flow_rate_ml_min} mL/min\n")
            f.write(f"Frame interval: {self.frame_interval}s\n")
            f.write(f"\nResults:\n")
            f.write(f"  Frames processed: {self.frames_processed}\n")
            f.write(f"  Total organisms: {self.total_organisms}\n")
            f.write(f"  Volume scanned: {self.total_volume_ml:.3f} mL\n")

            if self.total_volume_ml > 0:
                concentration = self.total_organisms / self.total_volume_ml
                f.write(f"  Concentration: {concentration:.2f} organisms/mL\n")

            f.write(f"\nOrganisms by class:\n")
            for class_name, count in sorted(self.organisms_by_class.items(),
                                           key=lambda x: x[1], reverse=True):
                percentage = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
                f.write(f"  {class_name}: {count} ({percentage:.1f}%)\n")

        logger.info(f"\nSummary saved to: {summary_path}")
        logger.info(f"Frame images saved to: {self.results_dir}")
        logger.info("="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Flow Cell Scanner for Continuous Plankton Monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan using default USB camera (camera 0) for 60 seconds
  python flow_cell_scanner.py --camera 0 --duration 60

  # Scan using camera 1 with custom flow rate
  python flow_cell_scanner.py --camera 1 --flow-rate 2.5 --interval 2

  # Scan from recorded video file
  python flow_cell_scanner.py --camera flow_cell_video.mp4

  # Run until manually stopped (press 'q')
  python flow_cell_scanner.py --camera 0
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to pipeline configuration file'
    )

    parser.add_argument(
        '--camera',
        type=str,
        default='0',
        help='Camera source: 0 for default USB camera, or path to video file'
    )

    parser.add_argument(
        '--flow-rate',
        type=float,
        default=1.0,
        help='Flow rate in mL/min (adjust based on your syringe pump speed)'
    )

    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Time between frame captures in seconds'
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Maximum scanning duration in seconds (default: run until stopped)'
    )

    args = parser.parse_args()

    # Convert camera argument
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera  # It's a file path

    # Create scanner
    scanner = FlowCellScanner(
        config_path=args.config,
        camera_source=camera_source,
        flow_rate_ml_min=args.flow_rate,
        frame_interval=args.interval
    )

    # Start scanning
    scanner.start_scanning(duration_seconds=args.duration)


if __name__ == '__main__':
    main()
