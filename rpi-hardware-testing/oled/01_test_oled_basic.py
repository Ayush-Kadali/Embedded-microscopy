#!/usr/bin/env python3
"""
OLED Basic Test - Displays "Hello RPi!"
Tests basic OLED connectivity and display

Hardware: SSD1306 OLED Display (128x64 or 128x32) via I2C
Connections:
  VCC → 3.3V
  GND → GND
  SCL → GPIO 3 (Pin 5)
  SDA → GPIO 2 (Pin 3)
"""

import time
import sys

print("=" * 50)
print("OLED Basic Test")
print("=" * 50)

# Try to import required libraries
try:
    from board import SCL, SDA
    import busio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    print("✓ Libraries imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nInstall dependencies:")
    print("  pip3 install adafruit-circuitpython-ssd1306 pillow")
    sys.exit(1)

def test_oled_128x64():
    """Test 128x64 OLED"""
    print("\nTrying 128x64 OLED...")

    try:
        # Create I2C interface
        i2c = busio.I2C(SCL, SDA)

        # Create OLED display object (128x64)
        oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

        # Clear display
        oled.fill(0)
        oled.show()
        print("✓ OLED initialized (128x64)")

        # Create image
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)

        # Draw text
        draw.text((0, 0), "Hello RPi!", fill=255)
        draw.text((0, 20), "OLED Test", fill=255)
        draw.text((0, 40), "128x64", fill=255)

        # Display image
        oled.image(image)
        oled.show()

        print("✓ Text displayed successfully!")
        print("\nIf you see 'Hello RPi!' on the OLED, the test passed!")
        return True

    except ValueError as e:
        print(f"✗ Device not found at 0x3C: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_oled_128x32():
    """Test 128x32 OLED"""
    print("\nTrying 128x32 OLED...")

    try:
        # Create I2C interface
        i2c = busio.I2C(SCL, SDA)

        # Create OLED display object (128x32)
        oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)

        # Clear display
        oled.fill(0)
        oled.show()
        print("✓ OLED initialized (128x32)")

        # Create image
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)

        # Draw text
        draw.text((0, 0), "Hello RPi!", fill=255)
        draw.text((0, 16), "128x32 OK", fill=255)

        # Display image
        oled.image(image)
        oled.show()

        print("✓ Text displayed successfully!")
        print("\nIf you see 'Hello RPi!' on the OLED, the test passed!")
        return True

    except ValueError as e:
        print(f"✗ Device not found at 0x3C: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_alternate_address():
    """Try alternate I2C address 0x3D"""
    print("\nTrying alternate address 0x3D...")

    try:
        i2c = busio.I2C(SCL, SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3D)

        oled.fill(0)
        oled.show()

        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), "Hello RPi!", fill=255)
        draw.text((0, 20), "Address: 0x3D", fill=255)

        oled.image(image)
        oled.show()

        print("✓ OLED found at 0x3D!")
        return True

    except Exception as e:
        print(f"✗ Not at 0x3D: {e}")
        return False

def main():
    """Main function"""
    print("\nTesting OLED display...")
    print("Make sure I2C is enabled: sudo raspi-config → Interface → I2C\n")

    # Try different configurations
    success = False

    # Try 128x64 first (most common)
    if test_oled_128x64():
        success = True
    elif test_oled_128x32():
        success = True
    elif test_alternate_address():
        success = True

    if success:
        print("\n" + "=" * 50)
        print("✅ TEST PASSED!")
        print("=" * 50)
        print("\nOLED display is working correctly.")
        print("You should see 'Hello RPi!' on the display.")
        print("\nPress Ctrl+C to exit...")

        # Keep display on
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nExiting...")

    else:
        print("\n" + "=" * 50)
        print("❌ TEST FAILED!")
        print("=" * 50)
        print("\nTroubleshooting:")
        print("1. Check I2C is enabled:")
        print("   sudo raspi-config → Interface Options → I2C → Enable")
        print("\n2. Check wiring:")
        print("   VCC → 3.3V (Pin 1 or 17)")
        print("   GND → GND (Pin 6, 9, 14, etc.)")
        print("   SCL → GPIO 3 (Pin 5)")
        print("   SDA → GPIO 2 (Pin 3)")
        print("\n3. Detect I2C devices:")
        print("   i2cdetect -y 1")
        print("   (Should show device at 0x3C or 0x3D)")
        print("\n4. Check permissions:")
        print("   sudo usermod -a -G i2c pi")
        print("   sudo reboot")

        return 1

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
