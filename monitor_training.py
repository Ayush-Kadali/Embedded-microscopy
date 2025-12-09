#!/usr/bin/env python3
"""
Monitor training progress in real-time
Usage: python monitor_training.py
"""

import time
import os
from pathlib import Path

def monitor_training():
    log_file = "model_training_output.log"

    print("=" * 80)
    print("TRAINING PROGRESS MONITOR")
    print("=" * 80)
    print("\nPress Ctrl+C to stop monitoring\n")

    last_size = 0
    epoch_history = []

    try:
        while True:
            if Path(log_file).exists():
                with open(log_file, 'r') as f:
                    content = f.read()

                    # Only show new content
                    if len(content) > last_size:
                        new_content = content[last_size:]

                        # Extract epoch summaries
                        for line in new_content.split('\n'):
                            if 'val_accuracy:' in line and 'step' in line:
                                # Parse epoch info
                                try:
                                    parts = line.split()
                                    for i, part in enumerate(parts):
                                        if 'val_accuracy:' in part:
                                            val_acc = float(parts[i+1])
                                            epoch_history.append(val_acc)

                                            print(f"Epoch {len(epoch_history):2d}/50 | "
                                                  f"Val Acc: {val_acc*100:5.2f}% | "
                                                  f"Best: {max(epoch_history)*100:5.2f}%")
                                            break
                                except:
                                    pass

                            # Show phase transitions
                            if 'Training Phase' in line:
                                print(f"\n{'=' * 60}")
                                print(f"  {line.strip()}")
                                print(f"{'=' * 60}\n")

                        last_size = len(content)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        if epoch_history:
            print(f"\nFinal Statistics:")
            print(f"  Total epochs completed: {len(epoch_history)}")
            print(f"  Best validation accuracy: {max(epoch_history)*100:.2f}%")
            print(f"  Latest validation accuracy: {epoch_history[-1]*100:.2f}%")

if __name__ == "__main__":
    monitor_training()
