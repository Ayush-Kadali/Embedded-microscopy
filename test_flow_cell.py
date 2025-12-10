#!/usr/bin/env python3
"""
Quick test script for flow cell scanner.

Tests camera access and basic functionality without running full pipeline.
"""

import cv2
import argparse
import time


def test_camera(camera_source=0):
    """Test camera access and display live feed."""
    print(f"Testing camera source: {camera_source}")
    print("Press 'q' to quit\n")

    cap = cv2.VideoCapture(camera_source)

    if not cap.isOpened():
        print(f"ERROR: Could not open camera source: {camera_source}")
        print("\nTroubleshooting:")
        print("  - Check camera is connected")
        print("  - Try different camera index (0, 1, 2...)")
        print("  - Check camera permissions")
        return False

    # Get camera properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"✓ Camera opened successfully")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"\nDisplaying live feed... (press 'q' to quit)")

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("ERROR: Failed to read frame")
                break

            # Add frame counter overlay
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Calculate actual FPS
            elapsed = time.time() - start_time
            if elapsed > 0:
                actual_fps = frame_count / elapsed
                cv2.putText(frame, f"FPS: {actual_fps:.1f}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Camera Test', frame)

            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()

    elapsed = time.time() - start_time
    print(f"\n✓ Test complete")
    print(f"  Frames captured: {frame_count}")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Average FPS: {frame_count/elapsed:.1f}")

    return True


def list_cameras():
    """Try to detect available cameras."""
    print("Scanning for available cameras...\n")

    available = []
    for i in range(10):  # Check first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            available.append((i, width, height))
            cap.release()

    if available:
        print("Found cameras:")
        for idx, width, height in available:
            print(f"  Camera {idx}: {width}x{height}")
    else:
        print("No cameras found")

    return available


def main():
    parser = argparse.ArgumentParser(description='Test camera for flow cell scanner')
    parser.add_argument(
        '--camera',
        type=str,
        default='0',
        help='Camera index (0, 1, 2...) or video file path'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available cameras'
    )

    args = parser.parse_args()

    if args.list:
        list_cameras()
    else:
        # Convert camera argument
        try:
            camera_source = int(args.camera)
        except ValueError:
            camera_source = args.camera  # It's a file path

        test_camera(camera_source)


if __name__ == '__main__':
    main()
