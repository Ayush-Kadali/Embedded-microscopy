#!/usr/bin/env python3
"""
Enhanced YOLO Detection with Image Processing

Features:
- Image sharpening and denoising
- Size-based filtering (removes dust particles)
- Contrast enhancement
- Motion-based filtering (optional)
- Adjustable detection parameters
"""

import cv2
import numpy as np
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedYOLODetector:
    """YOLO with enhanced preprocessing and filtering."""

    def __init__(self, model_path, conf_threshold=0.30, min_box_size=50, max_box_size=500):
        """
        Initialize enhanced detector.

        Args:
            model_path: Path to YOLO model
            conf_threshold: Confidence threshold (higher = fewer false positives)
            min_box_size: Minimum bounding box size in pixels (filters dust)
            max_box_size: Maximum bounding box size in pixels (filters artifacts)
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.min_box_size = min_box_size
        self.max_box_size = max_box_size

        # Load model
        logger.info(f"Loading YOLO model: {model_path}")
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(model_path))
            self.model_type = 'ultralytics'
            logger.info("✅ Model loaded with ultralytics")
        except ImportError:
            import torch
            self.model = torch.hub.load('ultralytics/yolov5', 'custom',
                                       path=str(model_path), force_reload=False)
            self.model_type = 'yolov5'
            logger.info("✅ Model loaded with torch.hub")

        # Get classes
        if hasattr(self.model, 'names'):
            if isinstance(self.model.names, dict):
                self.class_names = list(self.model.names.values())
            else:
                self.class_names = self.model.names
        else:
            self.class_names = ["object"]

        logger.info(f"Classes: {self.class_names}")
        logger.info(f"Confidence threshold: {conf_threshold}")
        logger.info(f"Size filter: {min_box_size}-{max_box_size} pixels")

        # Colors
        np.random.seed(42)
        self.colors = {}
        for class_name in self.class_names:
            self.colors[class_name] = tuple(map(int, np.random.randint(50, 255, 3)))

        # Stats
        self.total_detections = 0
        self.filtered_detections = 0
        self.class_counts = defaultdict(int)

    def preprocess_frame(self, frame, sharpen=True, denoise=True, enhance_contrast=True):
        """
        Enhance frame quality for better detection.

        Args:
            frame: Input BGR frame
            sharpen: Apply sharpening
            denoise: Apply denoising
            enhance_contrast: Apply CLAHE contrast enhancement

        Returns:
            Enhanced frame
        """
        enhanced = frame.copy()

        # Denoise first
        if denoise:
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)

        # Enhance contrast (CLAHE)
        if enhance_contrast:
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

        # Sharpen
        if sharpen:
            kernel = np.array([[-1, -1, -1],
                             [-1,  9, -1],
                             [-1, -1, -1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)

        return enhanced

    def filter_detection(self, bbox, confidence, class_name):
        """
        Filter detection based on size and confidence.

        Returns:
            True if detection should be kept, False otherwise
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1

        # Size-based filtering (removes dust particles)
        if width < self.min_box_size or height < self.min_box_size:
            return False

        if width > self.max_box_size or height > self.max_box_size:
            return False

        # Aspect ratio filtering (very thin/wide boxes are usually artifacts)
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio < 0.2 or aspect_ratio > 5.0:
            return False

        return True

    def detect(self, frame, preprocess=True):
        """Run detection with preprocessing and filtering."""
        # Preprocess frame
        if preprocess:
            processed_frame = self.preprocess_frame(frame)
        else:
            processed_frame = frame

        # Run YOLO
        if self.model_type == 'ultralytics':
            results = self.model(processed_frame, conf=self.conf_threshold, verbose=False)
            raw_detections = []

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"

                    raw_detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': conf,
                        'class': class_name
                    })
        else:
            results = self.model(processed_frame)
            pred = results.xyxy[0].cpu().numpy()
            raw_detections = []

            for det in pred:
                x1, y1, x2, y2, conf, cls = det
                x1, y1, x2, y2, cls = map(int, [x1, y1, x2, y2, cls])
                conf = float(conf)
                class_name = self.class_names[cls] if cls < len(self.class_names) else f"class_{cls}"

                raw_detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class': class_name
                })

        # Filter detections
        filtered_detections = []
        for det in raw_detections:
            if self.filter_detection(det['bbox'], det['confidence'], det['class']):
                filtered_detections.append(det)
            else:
                self.filtered_detections += 1

        self.total_detections += len(filtered_detections)
        for det in filtered_detections:
            self.class_counts[det['class']] += 1

        return filtered_detections, processed_frame

    def draw_detections(self, frame, detections, show_filtered_count=True):
        """Draw bounding boxes and info."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class']
            conf = det['confidence']
            color = self.colors.get(class_name, (255, 255, 255))

            # Thicker boxes for better visibility
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

            # Label
            label = f"{class_name}: {conf:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2
            )

            cv2.rectangle(frame, (x1, y1 - label_h - 15),
                        (x1 + label_w + 10, y1), color, -1)
            cv2.putText(frame, label, (x1 + 5, y1 - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Info overlay
        y = 40
        cv2.putText(frame, f"Valid Detections: {self.total_detections}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        y += 40

        if show_filtered_count:
            cv2.putText(frame, f"Filtered (dust/noise): {self.filtered_detections}", (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            y += 40

        if self.class_counts:
            cv2.putText(frame, "Species:", (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y += 35

            for class_name, count in sorted(self.class_counts.items(),
                                           key=lambda x: x[1], reverse=True)[:5]:
                color = self.colors.get(class_name, (255, 255, 255))
                cv2.putText(frame, f"  {class_name}: {count}", (30, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                y += 30


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced YOLO Detection with Filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--model', type=str, required=True, help='Path to YOLO model')
    parser.add_argument('--video', type=str, required=True, help='Path to video')
    parser.add_argument('--conf', type=float, default=0.35,
                       help='Confidence threshold (higher = fewer false positives)')
    parser.add_argument('--min-size', type=int, default=60,
                       help='Minimum detection size in pixels (filters dust)')
    parser.add_argument('--max-size', type=int, default=400,
                       help='Maximum detection size in pixels (filters artifacts)')
    parser.add_argument('--delay', type=int, default=100,
                       help='Delay between frames in ms')
    parser.add_argument('--skip-frames', type=int, default=2,
                       help='Process every Nth frame')
    parser.add_argument('--save', action='store_true', help='Save output video')
    parser.add_argument('--no-preprocess', action='store_true',
                       help='Disable image preprocessing')

    args = parser.parse_args()

    # Create detector
    detector = EnhancedYOLODetector(
        model_path=args.model,
        conf_threshold=args.conf,
        min_box_size=args.min_size,
        max_box_size=args.max_size
    )

    # Open video
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {args.video}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f"Video: {width}x{height} @ {fps} FPS, {total_frames} frames")
    logger.info(f"Processing every {args.skip_frames} frame(s)")
    logger.info("")
    logger.info("Controls: SPACE=Pause, q=Quit, s=Snapshot, +/-=Speed")
    logger.info("")

    # Video writer
    video_writer = None
    if args.save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"results/yolo_enhanced_{timestamp}.mp4"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_fps = 1000 / args.delay if args.delay > 0 else 20
        video_writer = cv2.VideoWriter(output_path, fourcc, output_fps, (width * 2, height))
        logger.info(f"Saving to: {output_path}")

    frame_count = 0
    paused = False
    current_delay = args.delay

    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video")
                    break

                frame_count += 1

                # Process every Nth frame
                if frame_count % args.skip_frames == 0:
                    # Detect
                    detections, processed_frame = detector.detect(
                        frame,
                        preprocess=not args.no_preprocess
                    )

                    # Draw on both original and processed
                    annotated_frame = frame.copy()
                    detector.draw_detections(annotated_frame, detections)

                    annotated_processed = processed_frame.copy()
                    detector.draw_detections(annotated_processed, detections, show_filtered_count=False)

                    # Add frame counter
                    cv2.putText(annotated_frame, f"Frame: {frame_count}/{total_frames}",
                               (width - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(annotated_processed, "Enhanced",
                               (width - 200, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    # Side by side view
                    combined = np.hstack([annotated_frame, annotated_processed])
                else:
                    # Just show frame
                    combined = np.hstack([frame, frame])

                cv2.imshow('Enhanced YOLO Detection | Original vs Processed', combined)

                if video_writer:
                    video_writer.write(combined)

            # Keyboard
            key = cv2.waitKey(current_delay if not paused else 0) & 0xFF

            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused
                logger.info(f"{'Paused' if paused else 'Resumed'}")
            elif key == ord('s'):
                snapshot_path = f"results/enhanced_snapshot_{frame_count}.jpg"
                cv2.imwrite(snapshot_path, combined)
                logger.info(f"Saved: {snapshot_path}")
            elif key == ord('+'):
                current_delay = min(current_delay + 20, 1000)
            elif key == ord('-'):
                current_delay = max(current_delay - 20, 10)

    except KeyboardInterrupt:
        logger.info("\nInterrupted")

    finally:
        cap.release()
        if video_writer:
            video_writer.release()
        cv2.destroyAllWindows()

        # Summary
        logger.info("")
        logger.info("="*80)
        logger.info("PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"Frames processed: {frame_count // args.skip_frames}")
        logger.info(f"Valid detections: {detector.total_detections}")
        logger.info(f"Filtered out (dust/noise): {detector.filtered_detections}")
        logger.info("")

        if detector.class_counts:
            logger.info("Species breakdown:")
            for class_name, count in sorted(detector.class_counts.items(),
                                           key=lambda x: x[1], reverse=True):
                pct = (count / detector.total_detections * 100) if detector.total_detections > 0 else 0
                logger.info(f"  {class_name}: {count} ({pct:.1f}%)")

        logger.info("="*80)


if __name__ == '__main__':
    main()
