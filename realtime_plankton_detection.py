#!/usr/bin/env python3
"""
OPTIMIZED Real-Time Plankton Detection
Best performance for video analysis with bounding boxes and counts
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import time
from datetime import datetime
import argparse

class RealtimePlanktonDetector:
    """Optimized real-time plankton detection system"""

    def __init__(self, model_path, confidence=0.10, display_width=1280):
        """
        Initialize detector

        Args:
            model_path: Path to YOLO model
            confidence: Detection confidence threshold (lower = more detections)
            display_width: Width for display (smaller = faster)
        """
        print("🔬 Initializing Real-Time Plankton Detector...")
        print(f"   Model: {model_path}")
        print(f"   Confidence: {confidence}")
        print(f"   Display width: {display_width}px")

        # Load model
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.display_width = display_width

        # Get class names
        self.class_names = list(self.model.names.values())
        print(f"   Species: {', '.join(self.class_names)}")

        # Statistics
        self.total_detections = 0
        self.species_counts = {name: 0 for name in self.class_names}
        self.frame_count = 0
        self.start_time = None

        # Display settings
        self.colors = self._generate_colors()

        print("✅ Detector ready!")

    def _generate_colors(self):
        """Generate distinct colors for each class"""
        np.random.seed(42)
        colors = {}
        for name in self.class_names:
            colors[name] = tuple(np.random.randint(0, 255, 3).tolist())
        return colors

    def process_frame(self, frame):
        """
        Process a single frame

        Returns:
            annotated_frame, detections_count, species_dict
        """
        # Run detection
        results = self.model(frame, conf=self.confidence, verbose=False)

        # Get detections
        boxes = results[0].boxes
        detections_count = len(boxes)

        # Count by species
        species_in_frame = {name: 0 for name in self.class_names}

        # Draw on frame
        annotated = frame.copy()

        for box in boxes:
            # Get box info
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.class_names[cls_id]

            # Update counts
            species_in_frame[cls_name] += 1

            # Draw bounding box
            color = self.colors[cls_name]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{cls_name} {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]

            # Label background
            cv2.rectangle(
                annotated,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1
            )

            # Label text
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

        return annotated, detections_count, species_in_frame

    def add_stats_overlay(self, frame, current_detections, species_in_frame, fps):
        """Add statistics overlay to frame"""
        overlay = frame.copy()
        h, w = frame.shape[:2]

        # Semi-transparent background for stats
        cv2.rectangle(overlay, (10, 10), (400, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Title
        cv2.putText(frame, "REAL-TIME PLANKTON DETECTION", (20, 35),
                   cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)

        # Current stats
        y_pos = 60
        cv2.putText(frame, f"Frame: {self.frame_count}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_pos += 25
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y_pos += 25
        cv2.putText(frame, f"Detections: {current_detections}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        y_pos += 25
        cv2.putText(frame, f"Total: {self.total_detections}", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Species breakdown
        y_pos += 30
        cv2.putText(frame, "Species in frame:", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        for name, count in species_in_frame.items():
            if count > 0:
                y_pos += 20
                color = self.colors[name]
                cv2.putText(frame, f"  {name}: {count}", (20, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        return frame

    def process_video(self, video_path, output_path=None, max_frames=None,
                     skip_frames=1, show_display=True):
        """
        Process video with real-time detection

        Args:
            video_path: Path to input video
            output_path: Path to save output video (optional)
            max_frames: Maximum frames to process (None = all)
            skip_frames: Process every Nth frame (1 = all frames)
            show_display: Show live display window
        """
        print(f"\n📹 Processing video: {video_path}")

        # Open video
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            print("❌ Could not open video")
            return

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps:.2f}")
        print(f"   Total frames: {total_frames}")
        print(f"   Processing every {skip_frames} frame(s)")

        # Setup output video
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(output_path), fourcc, fps/skip_frames,
                                    (width, height))
            print(f"   Output: {output_path}")

        # Processing
        self.start_time = time.time()
        frame_idx = 0

        print("\n🔍 Processing... (Press 'q' to stop)")
        print("=" * 60)

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # Skip frames if needed
            if frame_idx % skip_frames != 0:
                frame_idx += 1
                continue

            # Check max frames
            if max_frames and self.frame_count >= max_frames:
                break

            # Process frame
            process_start = time.time()
            annotated, count, species = self.process_frame(frame)
            process_time = time.time() - process_start

            # Update statistics
            self.frame_count += 1
            self.total_detections += count
            for name, cnt in species.items():
                self.species_counts[name] += cnt

            # Calculate FPS
            elapsed = time.time() - self.start_time
            current_fps = self.frame_count / elapsed if elapsed > 0 else 0

            # Add overlay
            display_frame = self.add_stats_overlay(annotated, count, species, current_fps)

            # Resize for display if needed
            if show_display and width > self.display_width:
                scale = self.display_width / width
                new_width = self.display_width
                new_height = int(height * scale)
                display_frame = cv2.resize(display_frame, (new_width, new_height))

            # Show display
            if show_display:
                cv2.imshow('Real-Time Plankton Detection', display_frame)

                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n⏹️  Stopped by user")
                    break
                elif key == ord('s'):
                    # Save screenshot
                    screenshot_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(screenshot_path, annotated)
                    print(f"📸 Screenshot saved: {screenshot_path}")

            # Write output video
            if writer:
                writer.write(annotated)

            # Progress
            if self.frame_count % 30 == 0:
                print(f"Frame {self.frame_count}/{total_frames//skip_frames} | "
                      f"FPS: {current_fps:.1f} | "
                      f"Detections: {count} | "
                      f"Process time: {process_time*1000:.1f}ms")

            frame_idx += 1

        # Cleanup
        cap.release()
        if writer:
            writer.release()
        if show_display:
            cv2.destroyAllWindows()

        # Final statistics
        self.print_summary()

    def print_summary(self):
        """Print final summary statistics"""
        print("\n" + "=" * 60)
        print("📊 DETECTION SUMMARY")
        print("=" * 60)

        elapsed = time.time() - self.start_time if self.start_time else 0

        print(f"Frames processed: {self.frame_count}")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average FPS: {self.frame_count/elapsed:.2f}" if elapsed > 0 else "N/A")
        print(f"\nTotal detections: {self.total_detections}")
        print(f"Detections per frame: {self.total_detections/self.frame_count:.2f}" if self.frame_count > 0 else "N/A")

        print("\n🦠 Species Breakdown:")
        for name, count in sorted(self.species_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / self.total_detections * 100) if self.total_detections > 0 else 0
                print(f"   {name:20s}: {count:4d} ({percentage:5.1f}%)")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Real-time plankton detection')
    parser.add_argument('--video', default='Real_Time_Vids/only_water_stream.mov',
                       help='Path to input video')
    parser.add_argument('--model', default='Downloaded models/best.pt',
                       help='Path to YOLO model')
    parser.add_argument('--conf', type=float, default=0.10,
                       help='Confidence threshold (0.01-0.50)')
    parser.add_argument('--output', default=None,
                       help='Path to save output video')
    parser.add_argument('--max-frames', type=int, default=None,
                       help='Maximum frames to process')
    parser.add_argument('--skip-frames', type=int, default=1,
                       help='Process every N frames (1=all, 2=half, etc.)')
    parser.add_argument('--width', type=int, default=1280,
                       help='Display width (smaller = faster)')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable live display window')
    parser.add_argument('--save', action='store_true',
                       help='Save output video')

    args = parser.parse_args()

    # Auto-generate output path if --save is used
    if args.save and not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f"results/plankton_detection_{timestamp}.mp4"
        Path("results").mkdir(exist_ok=True)

    # Create detector
    detector = RealtimePlanktonDetector(
        model_path=args.model,
        confidence=args.conf,
        display_width=args.width
    )

    # Process video
    detector.process_video(
        video_path=args.video,
        output_path=args.output,
        max_frames=args.max_frames,
        skip_frames=args.skip_frames,
        show_display=not args.no_display
    )


if __name__ == "__main__":
    main()
