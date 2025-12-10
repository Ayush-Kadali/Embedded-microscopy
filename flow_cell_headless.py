#!/usr/bin/env python3
"""
Headless Flow Cell Scanner (No Display)

Use this version for:
- Remote/SSH operation
- Systems without display
- Automated operation
- Raspberry Pi without monitor
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
import signal
import sys

from pipeline import PipelineManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HeadlessFlowScanner:
    """Headless flow cell scanner for remote operation."""

    def __init__(self, config_path: str, camera_source: int = 0,
                 flow_rate_ml_min: float = 1.0, frame_interval: float = 1.0):
        """Initialize scanner."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.pipeline = PipelineManager(self.config)
        self.camera_source = camera_source
        self.flow_rate_ml_min = flow_rate_ml_min
        self.frame_interval = frame_interval

        # Session tracking
        self.session_start_time = None
        self.total_organisms = 0
        self.organisms_by_class = defaultdict(int)
        self.frames_processed = 0
        self.total_volume_ml = 0.0
        self.running = True

        # Results
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path(f"results/flow_cell_{self.session_id}")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(f"Headless Flow Cell Scanner initialized")
        logger.info(f"  Camera: {camera_source}")
        logger.info(f"  Flow rate: {flow_rate_ml_min} mL/min")
        logger.info(f"  Frame interval: {frame_interval}s")
        logger.info(f"  Results: {self.results_dir}")

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        logger.info(f"\nReceived signal {signum}, stopping...")
        self.running = False

    def start_scanning(self, duration_seconds: int = None, max_frames: int = None):
        """
        Start scanning session.

        Args:
            duration_seconds: Max duration (None = unlimited)
            max_frames: Max frames to process (None = unlimited)
        """
        logger.info("="*80)
        logger.info("STARTING HEADLESS FLOW CELL SCAN")
        logger.info("="*80)
        logger.info("Send SIGINT (Ctrl+C) or SIGTERM to stop")
        logger.info("")

        cap = cv2.VideoCapture(self.camera_source)

        if not cap.isOpened():
            logger.error(f"Failed to open camera: {self.camera_source}")
            return False

        # Get camera info
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera: {width}x{height} @ {fps} FPS")
        logger.info("")

        self.session_start_time = time.time()
        last_process_time = 0
        last_stats_time = 0
        stats_interval = 10  # Print stats every 10 seconds

        try:
            while self.running:
                # Check limits
                elapsed = time.time() - self.session_start_time

                if duration_seconds and elapsed > duration_seconds:
                    logger.info(f"Duration limit reached ({duration_seconds}s)")
                    break

                if max_frames and self.frames_processed >= max_frames:
                    logger.info(f"Frame limit reached ({max_frames} frames)")
                    break

                # Read frame
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame, stopping")
                    break

                # Process frame at intervals
                current_time = time.time()
                if current_time - last_process_time >= self.frame_interval:
                    self._process_frame(frame, elapsed)
                    last_process_time = current_time

                    # Save preview image every 10 frames
                    if self.frames_processed % 10 == 0:
                        preview_path = self.results_dir / f"preview_frame_{self.frames_processed}.jpg"
                        cv2.imwrite(str(preview_path), frame)

                # Print stats periodically
                if current_time - last_stats_time >= stats_interval:
                    self._display_stats(elapsed)
                    last_stats_time = current_time

        except Exception as e:
            logger.error(f"Error during scanning: {e}", exc_info=True)
            return False

        finally:
            cap.release()
            self._generate_summary()

        return True

    def _process_frame(self, frame: np.ndarray, elapsed_time: float):
        """Process single frame."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Save frame
        frame_path = self.results_dir / f"frame_{self.frames_processed:06d}.jpg"
        cv2.imwrite(str(frame_path), frame)

        # Pipeline parameters
        acquisition_params = {
            'mode': 'file',
            'image_path': str(frame_path),
            'magnification': 2.0,
            'exposure_ms': 100,
            'capture_metadata': {
                'timestamp': datetime.now().isoformat(),
                'operator_id': 'flow_cell_headless',
                'session_id': self.session_id,
                'frame_number': self.frames_processed,
                'elapsed_seconds': elapsed_time,
            }
        }

        # Execute pipeline
        result = self.pipeline.execute_pipeline(acquisition_params)

        if result['status'] == 'success':
            organisms_in_frame = result['summary']['total_organisms']
            self.total_organisms += organisms_in_frame

            for class_name, count in result['summary']['counts_by_class'].items():
                self.organisms_by_class[class_name] += count

            volume_increment = (self.flow_rate_ml_min * self.frame_interval) / 60.0
            self.total_volume_ml += volume_increment

            logger.info(f"Frame {self.frames_processed}: {organisms_in_frame} organisms, "
                       f"{self.total_volume_ml:.3f} mL total")
        else:
            logger.warning(f"Frame {self.frames_processed}: Failed - {result.get('error_message')}")

        self.frames_processed += 1

    def _display_stats(self, elapsed_time: float):
        """Print current statistics."""
        logger.info("")
        logger.info("─" * 80)
        logger.info(f"SESSION STATUS - {int(elapsed_time)}s elapsed")
        logger.info("─" * 80)
        logger.info(f"  Frames: {self.frames_processed}")
        logger.info(f"  Organisms: {self.total_organisms}")
        logger.info(f"  Volume: {self.total_volume_ml:.3f} mL")

        if self.total_volume_ml > 0:
            conc = self.total_organisms / self.total_volume_ml
            logger.info(f"  Concentration: {conc:.1f} org/mL")

        if self.organisms_by_class:
            logger.info("  Top classes:")
            top_classes = sorted(self.organisms_by_class.items(),
                               key=lambda x: x[1], reverse=True)[:5]
            for class_name, count in top_classes:
                pct = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
                logger.info(f"    {class_name}: {count} ({pct:.1f}%)")

        logger.info("─" * 80)
        logger.info("")

    def _generate_summary(self):
        """Generate final summary."""
        duration = time.time() - self.session_start_time

        logger.info("")
        logger.info("="*80)
        logger.info("SCAN COMPLETE")
        logger.info("="*80)
        logger.info(f"Session: {self.session_id}")
        logger.info(f"Duration: {int(duration)}s ({duration/60:.1f} min)")
        logger.info(f"Frames: {self.frames_processed}")
        logger.info(f"Organisms: {self.total_organisms}")
        logger.info(f"Volume: {self.total_volume_ml:.3f} mL")

        if self.total_volume_ml > 0:
            conc = self.total_organisms / self.total_volume_ml
            logger.info(f"Concentration: {conc:.2f} org/mL")

        logger.info("\nBreakdown:")
        for class_name, count in sorted(self.organisms_by_class.items(),
                                       key=lambda x: x[1], reverse=True):
            pct = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
            logger.info(f"  {class_name}: {count} ({pct:.1f}%)")

        # Save summary
        summary_path = self.results_dir / "summary.txt"
        with open(summary_path, 'w') as f:
            f.write(f"Flow Cell Scan Summary\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Start: {datetime.fromtimestamp(self.session_start_time).isoformat()}\n")
            f.write(f"Duration: {int(duration)}s\n")
            f.write(f"Flow rate: {self.flow_rate_ml_min} mL/min\n\n")
            f.write(f"Results:\n")
            f.write(f"  Frames: {self.frames_processed}\n")
            f.write(f"  Organisms: {self.total_organisms}\n")
            f.write(f"  Volume: {self.total_volume_ml:.3f} mL\n")

            if self.total_volume_ml > 0:
                conc = self.total_organisms / self.total_volume_ml
                f.write(f"  Concentration: {conc:.2f} org/mL\n")

            f.write(f"\nBreakdown:\n")
            for class_name, count in sorted(self.organisms_by_class.items(),
                                           key=lambda x: x[1], reverse=True):
                pct = (count / self.total_organisms * 100) if self.total_organisms > 0 else 0
                f.write(f"  {class_name}: {count} ({pct:.1f}%)\n")

        logger.info(f"\nSaved to: {self.results_dir}")
        logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Headless Flow Cell Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for 120 seconds
  python flow_cell_headless.py --camera 0 --duration 120

  # Process exactly 100 frames
  python flow_cell_headless.py --camera 0 --max-frames 100

  # Custom flow rate, run until stopped
  python flow_cell_headless.py --camera 0 --flow-rate 2.5

  # Process video file
  python flow_cell_headless.py --camera video.mp4
        """
    )

    parser.add_argument('--config', default='config/config.yaml',
                       help='Pipeline config')
    parser.add_argument('--camera', type=str, default='0',
                       help='Camera index or video file')
    parser.add_argument('--flow-rate', type=float, default=1.0,
                       help='Flow rate (mL/min)')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Seconds between captures')
    parser.add_argument('--duration', type=int, default=None,
                       help='Max duration (seconds)')
    parser.add_argument('--max-frames', type=int, default=None,
                       help='Max frames to process')

    args = parser.parse_args()

    # Convert camera
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera

    # Create and run scanner
    scanner = HeadlessFlowScanner(
        config_path=args.config,
        camera_source=camera_source,
        flow_rate_ml_min=args.flow_rate,
        frame_interval=args.interval
    )

    success = scanner.start_scanning(
        duration_seconds=args.duration,
        max_frames=args.max_frames
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
