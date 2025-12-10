#!/usr/bin/env python3
"""
Video Frame Inspector

Extract and save individual frames to manually inspect video quality
and see what's actually in the water sample.
"""

import cv2
import argparse
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_frames(video_path, output_dir, num_frames=20, interval='auto'):
    """
    Extract frames from video for manual inspection.

    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        num_frames: Number of frames to extract
        interval: 'auto' or specific frame interval
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    logger.info(f"Video: {total_frames} frames @ {fps} FPS")

    # Calculate frame interval
    if interval == 'auto':
        frame_interval = max(1, total_frames // num_frames)
    else:
        frame_interval = int(interval)

    logger.info(f"Extracting every {frame_interval}th frame ({num_frames} total)")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            # Save frame
            frame_file = output_path / f"frame_{frame_count:05d}.jpg"
            cv2.imwrite(str(frame_file), frame)
            logger.info(f"Saved: {frame_file.name}")
            saved_count += 1

            if saved_count >= num_frames:
                break

        frame_count += 1

    cap.release()

    logger.info(f"\n✅ Extracted {saved_count} frames to: {output_dir}")
    logger.info(f"Open the folder to manually inspect video quality")


def main():
    parser = argparse.ArgumentParser(description='Extract frames for manual inspection')
    parser.add_argument('--video', type=str, required=True, help='Video file')
    parser.add_argument('--output', type=str, default='results/extracted_frames',
                       help='Output directory')
    parser.add_argument('--num-frames', type=int, default=20,
                       help='Number of frames to extract')
    parser.add_argument('--interval', type=str, default='auto',
                       help='Frame interval (auto or number)')

    args = parser.parse_args()

    extract_frames(args.video, args.output, args.num_frames, args.interval)


if __name__ == '__main__':
    main()
