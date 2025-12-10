#!/usr/bin/env python3
"""
YOLO Detection with Slow Motion Playback

Processes video frame by frame with adjustable delay,
perfect for seeing detections clearly.
"""

import cv2
import argparse
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='YOLO Slow Motion Detection')
    parser.add_argument('--model', type=str, required=True, help='Path to YOLO model')
    parser.add_argument('--video', type=str, required=True, help='Path to video file')
    parser.add_argument('--delay', type=int, default=50, help='Delay between frames in ms (default: 50ms = ~20 FPS)')
    parser.add_argument('--conf', type=float, default=0.20, help='Confidence threshold')
    parser.add_argument('--save', action='store_true', help='Save annotated video')
    parser.add_argument('--skip-frames', type=int, default=1, help='Process every Nth frame (1=all, 2=every other, etc)')

    args = parser.parse_args()

    # Load YOLO model
    logger.info(f"Loading YOLO model: {args.model}")
    try:
        from ultralytics import YOLO
        model = YOLO(args.model)
        logger.info("✅ Model loaded with ultralytics")
    except ImportError:
        import torch
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=args.model, force_reload=False)
        logger.info("✅ Model loaded with torch.hub")

    # Get class names
    if hasattr(model, 'names'):
        if isinstance(model.names, dict):
            class_names = list(model.names.values())
        else:
            class_names = model.names
    else:
        class_names = ["object"]

    logger.info(f"Classes: {class_names}")

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
    logger.info(f"Playback delay: {args.delay}ms (~{1000/args.delay:.1f} FPS)")
    logger.info(f"Processing every {args.skip_frames} frame(s)")
    logger.info("")
    logger.info("Controls:")
    logger.info("  SPACE - Pause/Resume")
    logger.info("  q - Quit")
    logger.info("  s - Save snapshot")
    logger.info("  + - Slower (increase delay)")
    logger.info("  - - Faster (decrease delay)")
    logger.info("")

    # Video writer
    video_writer = None
    if args.save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"results/yolo_slow_{timestamp}.mp4"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_fps = 1000 / args.delay if args.delay > 0 else 20
        video_writer = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
        logger.info(f"Saving to: {output_path}")

    # Stats
    frame_count = 0
    processed_count = 0
    total_detections = 0
    class_counts = defaultdict(int)
    paused = False
    current_delay = args.delay
    snapshot_count = 0

    # Colors
    import numpy as np
    np.random.seed(42)
    colors = {}
    for i, class_name in enumerate(class_names):
        colors[class_name] = tuple(map(int, np.random.randint(50, 255, 3)))

    logger.info("Processing video...")
    logger.info("")

    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video reached")
                    break

                frame_count += 1

                # Process only every Nth frame
                if frame_count % args.skip_frames == 0:
                    processed_count += 1

                    # Run detection
                    try:
                        if hasattr(model, 'predict'):  # ultralytics
                            results = model(frame, conf=args.conf, verbose=False)
                            detections = []

                            for result in results:
                                boxes = result.boxes
                                for box in boxes:
                                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                                    conf = float(box.conf[0])
                                    cls = int(box.cls[0])
                                    class_name = class_names[cls] if cls < len(class_names) else f"class_{cls}"

                                    detections.append({
                                        'bbox': [x1, y1, x2, y2],
                                        'confidence': conf,
                                        'class': class_name
                                    })
                        else:  # YOLOv5
                            results = model(frame)
                            pred = results.xyxy[0].cpu().numpy()
                            detections = []

                            for det in pred:
                                x1, y1, x2, y2, conf, cls = det
                                x1, y1, x2, y2, cls = map(int, [x1, y1, x2, y2, cls])
                                conf = float(conf)
                                class_name = class_names[cls] if cls < len(class_names) else f"class_{cls}"

                                detections.append({
                                    'bbox': [x1, y1, x2, y2],
                                    'confidence': conf,
                                    'class': class_name
                                })

                        # Update stats
                        total_detections += len(detections)
                        for det in detections:
                            class_counts[det['class']] += 1

                        # Draw detections
                        for det in detections:
                            x1, y1, x2, y2 = det['bbox']
                            class_name = det['class']
                            conf = det['confidence']

                            color = colors.get(class_name, (255, 255, 255))

                            # Box
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

                            # Label
                            label = f"{class_name}: {conf:.2f}"
                            (label_w, label_h), baseline = cv2.getTextSize(
                                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                            )

                            cv2.rectangle(frame, (x1, y1 - label_h - 15),
                                        (x1 + label_w + 10, y1), color, -1)
                            cv2.putText(frame, label, (x1 + 5, y1 - 8),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    except Exception as e:
                        logger.error(f"Detection error on frame {frame_count}: {e}")

                # Draw info overlay
                info_y = 40
                cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (20, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                info_y += 35

                cv2.putText(frame, f"Detections: {total_detections}", (20, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                info_y += 35

                cv2.putText(frame, f"Speed: {1000/current_delay:.1f} FPS", (20, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                info_y += 35

                if class_counts:
                    cv2.putText(frame, "Species:", (20, info_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    info_y += 30

                    for class_name, count in sorted(class_counts.items(),
                                                   key=lambda x: x[1], reverse=True)[:5]:
                        color = colors.get(class_name, (255, 255, 255))
                        cv2.putText(frame, f"  {class_name}: {count}", (30, info_y),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        info_y += 25

                # Show frame
                cv2.imshow('YOLO Slow Motion Detection', frame)

                # Save if enabled
                if video_writer:
                    video_writer.write(frame)

            # Handle keyboard
            key = cv2.waitKey(current_delay if not paused else 0) & 0xFF

            if key == ord('q'):
                logger.info("Quit requested")
                break
            elif key == ord(' '):  # Space
                paused = not paused
                logger.info(f"{'Paused' if paused else 'Resumed'}")
            elif key == ord('s'):
                snapshot_path = f"results/snapshot_{snapshot_count:04d}.jpg"
                cv2.imwrite(snapshot_path, frame)
                logger.info(f"Saved: {snapshot_path}")
                snapshot_count += 1
            elif key == ord('+') or key == ord('='):
                current_delay = min(current_delay + 10, 1000)
                logger.info(f"Slower: {1000/current_delay:.1f} FPS")
            elif key == ord('-') or key == ord('_'):
                current_delay = max(current_delay - 10, 1)
                logger.info(f"Faster: {1000/current_delay:.1f} FPS")

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
        logger.info(f"Total frames: {frame_count}")
        logger.info(f"Processed frames: {processed_count}")
        logger.info(f"Total detections: {total_detections}")
        logger.info("")

        if class_counts:
            logger.info("Species breakdown:")
            for class_name, count in sorted(class_counts.items(),
                                           key=lambda x: x[1], reverse=True):
                pct = (count / total_detections * 100) if total_detections > 0 else 0
                logger.info(f"  {class_name}: {count} ({pct:.1f}%)")

        logger.info("="*80)


if __name__ == '__main__':
    main()
