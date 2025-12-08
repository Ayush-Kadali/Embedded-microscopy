#!/usr/bin/env python3
"""
Joystick Basic Test
Tests 5-way joystick (Up/Down/Left/Right/Center)

Hardware: 5-way digital joystick
Connections:
  VCC    → 3.3V
  GND    → GND
  UP     → GPIO 17 (Pin 11)
  DOWN   → GPIO 27 (Pin 13)
  LEFT   → GPIO 22 (Pin 15)
  RIGHT  → GPIO 23 (Pin 16)
  CENTER → GPIO 24 (Pin 18)

Usage: python3 01_test_joystick_basic.py
"""

import time
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Error: RPi.GPIO not installed")
    print("Install: pip3 install RPi.GPIO")
    sys.exit(1)

# GPIO Pin Configuration
PINS = {
    'UP': 17,
    'DOWN': 27,
    'LEFT': 22,
    'RIGHT': 23,
    'CENTER': 24
}

def setup_gpio():
    """Setup GPIO pins for joystick"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for direction, pin in PINS.items():
        # Setup as input with pull-up resistor
        # Joystick connects to GND when pressed
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("✓ GPIO pins configured")
    print("\nPin Configuration:")
    for direction, pin in PINS.items():
        print(f"  {direction:8} → GPIO {pin:2} (Pin {get_physical_pin(pin):2})")

def get_physical_pin(gpio_num):
    """Convert GPIO number to physical pin number"""
    pin_map = {
        17: 11, 27: 13, 22: 15, 23: 16, 24: 18,
        2: 3, 3: 5
    }
    return pin_map.get(gpio_num, '?')

def read_joystick():
    """Read current joystick state"""
    state = {}
    for direction, pin in PINS.items():
        # Button is pressed when pin reads LOW (0)
        state[direction] = not GPIO.input(pin)
    return state

def main():
    """Main test function"""
    print("=" * 50)
    print("Joystick Basic Test")
    print("=" * 50)

    try:
        # Setup GPIO
        setup_gpio()

        print("\n" + "=" * 50)
        print("Press joystick directions to test")
        print("Press Ctrl+C to exit")
        print("=" * 50)

        last_state = {direction: False for direction in PINS.keys()}
        press_count = {direction: 0 for direction in PINS.keys()}

        while True:
            current_state = read_joystick()

            # Detect state changes
            for direction in PINS.keys():
                if current_state[direction] and not last_state[direction]:
                    # Button pressed (transition from released to pressed)
                    press_count[direction] += 1
                    print(f"[{time.strftime('%H:%M:%S')}] {direction:8} pressed (count: {press_count[direction]})")

                    # Special message for CENTER button
                    if direction == 'CENTER':
                        print("  → Center button detected!")

            last_state = current_state
            time.sleep(0.05)  # 50ms polling

    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        total_presses = sum(press_count.values())

        if total_presses > 0:
            print(f"\n✅ Joystick is working!")
            print(f"\nTotal button presses: {total_presses}")
            print("\nPresses per direction:")
            for direction, count in press_count.items():
                if count > 0:
                    print(f"  {direction:8}: {count}")
        else:
            print("\n⚠️  No button presses detected")
            print("\nTroubleshooting:")
            print("1. Check wiring:")
            for direction, pin in PINS.items():
                print(f"   {direction:8} → GPIO {pin}")
            print("2. Check VCC connected to 3.3V")
            print("3. Check GND connected")
            print("4. Check joystick module power LED is on")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        GPIO.cleanup()
        print("\n✓ GPIO cleaned up")

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
