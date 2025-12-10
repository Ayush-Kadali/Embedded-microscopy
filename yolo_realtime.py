#!/usr/bin/env python3
"""
Real-Time YOLO Detection for Plankton

Runs YOLOv5 or YOLOv8 models on live video feed with bounding boxes.
Perfect for jury demonstrations!
"""

import cv2
import torch
import numpy as np
import argparse
import time
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YOLORealtimeDetector:
    """Real-time detection using YOLO models."""

    def __init__(self, model_path, model_type='auto', conf_threshold=0.25, iou_threshold=0.45):
        """
        Initialize YOLO detector.

        Args:
            model_path: Path to .pt model file
            model_type: 'yolov5', 'yolov8', or 'auto' (auto-detect)
            conf_threshold: Confidence threshold for detections
            iou_threshold: IOU threshold for NMS
        """
        self.model_path = Path(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        # Auto-detect model type
        if model_type == 'auto':
            model_name = self.model_path.name.lower()
            if 'yolov8' in model_name or 'v8' in model_name:
                self.model_type = 'yolov8'
            elif 'yolov5' in model_name or 'v5' in model_name:
                self.model_type = 'yolov5'
            else:
                # Try YOLOv8 first (newer)
                self.model_type = 'yolov8'
        else:
            self.model_type = model_type

        logger.info(f"Loading {self.model_type.upper()} model: {self.model_path}")

        # Load model
        self.model = self._load_model()
        self.class_names = self._get_class_names()

        logger.info(f"Model loaded successfully")
        logger.info(f"Classes: {self.class_names}")

        # Stats tracking
        self.total_detections = 0
        self.class_counts = defaultdict(int)
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        self.inference_time = 0

        # Colors for bounding boxes (BGR)
        np.random.seed(42)
        self.colors = {}
        for i, class_name in enumerate(self.class_names):
            self.colors[class_name] = tuple(map(int, np.random.randint(50, 255, 3)))

    def _load_model(self):
        """Load YOLO model based on type."""
        try:
            if self.model_type == 'yolov8':
                # Try ultralytics YOLOv8
                try:
                    from ultralytics import YOLO
                    model = YOLO(str(self.model_path))
                    logger.info("Loaded with ultralytics (YOLOv8)")
                    return model
                except ImportError:
                    logger.warning("ultralytics not installed, trying torch.hub for YOLOv5...")
                    self.model_type = 'yolov5'  # Fall back to YOLOv5

            if self.model_type == 'yolov5':
                # Load with torch hub (works for both YOLOv5 and some YOLOv8)
                model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(self.model_path), force_reload=False)
                model.conf = self.conf_threshold
                model.iou = self.iou_threshold
                logger.info("Loaded with torch.hub (YOLOv5)")
                return model

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Trying direct torch load...")

            # Last resort: direct torch load
            try:
                model = torch.load(str(self.model_path))
                return model
            except Exception as e2:
                logger.error(f"Failed to load model: {e2}")
                raise

    def _get_class_names(self):
        """Extract class names from model."""
        try:
            if self.model_type == 'yolov8' and hasattr(self.model, 'names'):
                # YOLOv8 ultralytics
                return list(self.model.names.values())
            elif hasattr(self.model, 'names'):
                # YOLOv5 torch.hub
                return self.model.names
            elif hasattr(self.model, 'module') and hasattr(self.model.module, 'names'):
                return self.model.module.names
            else:
                logger.warning("Could not extract class names, using generic names")
                return [f"class_{i}" for i in range(10)]
        except Exception as e:
            logger.warning(f"Error getting class names: {e}")
            return ["plankton"]

    def detect(self, frame):
        """
        Run detection on frame.

        Args:
            frame: BGR image from camera

        Returns:
            detections: List of detections with bbox, class, confidence
        """
        start_time = time.time()

        try:
            if self.model_type == 'yolov8':
                # YOLOv8 ultralytics inference
                results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold, verbose=False)
                detections = []

                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        class_name = self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"

                        detections.append({
                            'bbox': [x1, y1, x2 - x1, y2 - y1],  # [x, y, w, h]
                            'xyxy': [x1, y1, x2, y2],
                            'confidence': conf,
                            'class': class_name,
                            'class_id': cls
                        })

            else:
                # YOLOv5 inference
                results = self.model(frame)
                detections = []

                # Parse results
                pred = results.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2, conf, cls]

                for det in pred:
                    x1, y1, x2, y2, conf, cls = det
                    x1, y1, x2, y2, cls = map(int, [x1, y1, x2, y2, cls])
                    conf = float(conf)
                    class_name = self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"

                    detections.append({
                        'bbox': [x1, y1, x2 - x1, y2 - y1],  # [x, y, w, h]
                        'xyxy': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class': class_name,
                        'class_id': cls
                    })

            self.inference_time = (time.time() - start_time) * 1000  # ms
            return detections

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []

    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on frame."""
        for det in detections:
            x1, y1, x2, y2 = det['xyxy']
            class_name = det['class']
            conf = det['confidence']

            # Get color for this class
            color = self.colors.get(class_name, (255, 255, 255))

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Prepare label
            label = f"{class_name}: {conf:.2f}"

            # Get label size
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )

            # Draw label background
            cv2.rectangle(
                frame,
                (x1, y1 - label_h - 10),
                (x1 + label_w + 5, y1),
                color,
                -1
            )

            # Draw label text
            cv2.putText(
                frame,
                label,
                (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

    def draw_stats(self, frame):
        """Draw statistics overlay."""
        h, w = frame.shape[:2]

        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw text
        font = cv2.FONT_HERSHEY_SIMPLEX
        y = 35
        line_height = 30

        # Title
        cv2.putText(frame, f"{self.model_type.upper()} Detection", (20, y),
                   font, 0.7, (0, 255, 255), 2)
        y += line_height

        # FPS and inference time
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        cv2.putText(frame, f"Inference: {self.inference_time:.0f}ms", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        # Total detections
        cv2.putText(frame, f"Total: {self.total_detections}", (20, y),
                   font, 0.7, (0, 255, 0), 2)
        y += line_height

        # Class breakdown
        if self.class_counts:
            cv2.putText(frame, "Detections:", (20, y),
                       font, 0.6, (255, 255, 0), 1)
            y += line_height

            for class_name, count in sorted(self.class_counts.items(),
                                           key=lambda x: x[1], reverse=True)[:4]:
                color = self.colors.get(class_name, (255, 255, 255))
                cv2.putText(frame, f"  {class_name}: {count}", (30, y),
                           font, 0.5, color, 1)
                y += line_height - 5

        # Controls
        y = h - 20
        cv2.putText(frame, "Press 'q' to quit | 's' to save", (20, y),
                   font, 0.5, (255, 255, 0), 1)

    def run(self, camera_source=0, save_video=False, show_fps=True):
        """
        Run real-time detection.

        Args:
            camera_source: Camera index or video file
            save_video: Save annotated video
            show_fps: Show FPS in overlay
        """
        logger.info("="*80)
        logger.info(f"{self.model_type.upper()} REAL-TIME DETECTION")
        logger.info("="*80)
        logger.info(f"Model: {self.model_path.name}")
        logger.info(f"Camera: {camera_source}")
        logger.info(f"Confidence threshold: {self.conf_threshold}")
        logger.info("")

        cap = cv2.VideoCapture(camera_source)

        if not cap.isOpened():
            logger.error(f"Failed to open camera: {camera_source}")
            return

        # Camera properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"Camera: {width}x{height} @ {fps} FPS")
        logger.info("Press 'q' to quit, 's' to save snapshot")
        logger.info("")

        # Video writer
        video_writer = None
        if save_video:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/yolo_detection_{timestamp}.mp4"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))
            logger.info(f"Saving to: {output_path}")

        self.start_time = time.time()
        snapshot_count = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    break

                # Detect
                detections = self.detect(frame)

                # Update stats
                self.frame_count += 1
                self.total_detections += len(detections)

                for det in detections:
                    self.class_counts[det['class']] += 1

                # Calculate FPS
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.fps = self.frame_count / elapsed

                # Draw detections
                self.draw_detections(frame, detections)

                # Draw stats
                if show_fps:
                    self.draw_stats(frame)

                # Display
                cv2.imshow(f'{self.model_type.upper()} Detection', frame)

                # Save video
                if video_writer:
                    video_writer.write(frame)

                # Handle keys
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    logger.info("Quit requested")
                    break
                elif key == ord('s'):
                    snapshot_path = f"results/yolo_snapshot_{snapshot_count:04d}.jpg"
                    cv2.imwrite(snapshot_path, frame)
                    logger.info(f"Saved: {snapshot_path}")
                    snapshot_count += 1

        except KeyboardInterrupt:
            logger.info("\nInterrupted")

        finally:
            cap.release()
            if video_writer:
                video_writer.release()
            cv2.destroyAllWindows()

            self._print_summary()

    def _print_summary(self):
        """Print session summary."""
        elapsed = time.time() - self.start_time

        logger.info("")
        logger.info("="*80)
        logger.info("SESSION COMPLETE")
        logger.info("="*80)
        logger.info(f"Model: {self.model_path.name}")
        logger.info(f"Duration: {elapsed:.1f}s")
        logger.info(f"Frames: {self.frame_count}")
        logger.info(f"Average FPS: {self.fps:.1f}")
        logger.info(f"Total detections: {self.total_detections}")
        logger.info("")

        if self.class_counts:
            logger.info("Class breakdown:")
            for class_name, count in sorted(self.class_counts.items(),
                                           key=lambda x: x[1], reverse=True):
                pct = (count / self.total_detections * 100) if self.total_detections > 0 else 0
                logger.info(f"  {class_name}: {count} ({pct:.1f}%)")

        logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Real-Time YOLO Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with best.pt model
  python yolo_realtime.py --model "Downloaded models/best.pt"

  # Run with YOLOv8 model
  python yolo_realtime.py --model "Downloaded models/yolov8n.pt"

  # Run with YOLOv5 model
  python yolo_realtime.py --model "Downloaded models/yolov5nu.pt"

  # Use different camera
  python yolo_realtime.py --model "Downloaded models/best.pt" --camera 1

  # Save output video
  python yolo_realtime.py --model "Downloaded models/best.pt" --save-video

  # Lower confidence threshold (more detections)
  python yolo_realtime.py --model "Downloaded models/best.pt" --conf 0.15

Controls:
  q - Quit
  s - Save snapshot
        """
    )

    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to YOLO .pt model file'
    )

    parser.add_argument(
        '--camera',
        type=str,
        default='0',
        help='Camera index (0, 1...) or video file path'
    )

    parser.add_argument(
        '--model-type',
        type=str,
        default='auto',
        choices=['auto', 'yolov5', 'yolov8'],
        help='Model type (auto-detect by default)'
    )

    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='Confidence threshold (0.0-1.0)'
    )

    parser.add_argument(
        '--iou',
        type=float,
        default=0.45,
        help='IOU threshold for NMS'
    )

    parser.add_argument(
        '--save-video',
        action='store_true',
        help='Save annotated video'
    )

    parser.add_argument(
        '--no-stats',
        action='store_true',
        help='Hide statistics overlay'
    )

    args = parser.parse_args()

    # Convert camera
    try:
        camera_source = int(args.camera)
    except ValueError:
        camera_source = args.camera

    # Create detector
    detector = YOLORealtimeDetector(
        model_path=args.model,
        model_type=args.model_type,
        conf_threshold=args.conf,
        iou_threshold=args.iou
    )

    # Run detection
    detector.run(
        camera_source=camera_source,
        save_video=args.save_video,
        show_fps=not args.no_stats
    )


if __name__ == '__main__':
    main()
