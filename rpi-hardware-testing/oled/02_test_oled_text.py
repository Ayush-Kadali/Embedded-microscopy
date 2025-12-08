#!/usr/bin/env python3
"""
OLED Text Display Test
Tests multi-line text, scrolling, and formatting

Usage: python3 02_test_oled_text.py
"""

import time
import sys

try:
    from board import SCL, SDA
    import busio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
except ImportError as e:
    print(f"Error: {e}")
    print("Install: pip3 install adafruit-circuitpython-ssd1306 pillow")
    sys.exit(1)

# OLED Configuration
WIDTH = 128
HEIGHT = 64
ADDRESS = 0x3C

def init_oled():
    """Initialize OLED display"""
    try:
        i2c = busio.I2C(SCL, SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=ADDRESS)
        oled.fill(0)
        oled.show()
        return oled
    except Exception as e:
        print(f"Failed to initialize OLED: {e}")
        return None

def display_text(oled, lines, delay=2):
    """Display multiple lines of text"""
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    y_offset = 0
    for line in lines:
        draw.text((0, y_offset), line, fill=255)
        y_offset += 12

    oled.image(image)
    oled.show()
    time.sleep(delay)

def display_large_text(oled, text, delay=2):
    """Display large centered text"""
    image = Image.new("1", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)

    # Try to load larger font (may not be available)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except:
        font = ImageFont.load_default()

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2

    draw.text((x, y), text, font=font, fill=255)

    oled.image(image)
    oled.show()
    time.sleep(delay)

def scrolling_text(oled, text, iterations=3):
    """Scrolling text animation"""
    print(f"Scrolling: '{text}'")

    for _ in range(iterations):
        for x_offset in range(WIDTH, -len(text) * 8, -2):
            image = Image.new("1", (WIDTH, HEIGHT))
            draw = ImageDraw.Draw(image)
            draw.text((x_offset, HEIGHT // 2 - 4), text, fill=255)
            oled.image(image)
            oled.show()
            time.sleep(0.01)

def test_text_formats(oled):
    """Test different text formats"""
    tests = [
        {
            "name": "Multi-line Text",
            "lines": [
                "Line 1: Hello",
                "Line 2: RPi",
                "Line 3: OLED",
                "Line 4: Test",
                "Line 5: OK"
            ]
        },
        {
            "name": "Status Display",
            "lines": [
                "System Status",
                "---------------",
                "CPU: 45C",
                "MEM: 234MB",
                "DISK: 8.5GB"
            ]
        },
        {
            "name": "GPS Coordinates",
            "lines": [
                "GPS Data",
                "---------------",
                "Lat: 18.5204 N",
                "Lon: 73.8567 E",
                "Alt: 560m"
            ]
        },
        {
            "name": "Plankton Count",
            "lines": [
                "Last Scan",
                "---------------",
                "Copepods: 12",
                "Diatoms: 8",
                "Total: 20"
            ]
        }
    ]

    for test in tests:
        print(f"\nTest: {test['name']}")
        display_text(oled, test['lines'], delay=3)

def main():
    """Main test function"""
    print("=" * 50)
    print("OLED Text Display Test")
    print("=" * 50)

    # Initialize OLED
    oled = init_oled()
    if not oled:
        print("❌ Failed to initialize OLED")
        return 1

    print("✓ OLED initialized")

    try:
        # Test 1: Simple text
        print("\n1. Simple text display")
        display_text(oled, ["Hello, World!", "OLED is working!"])

        # Test 2: Large centered text
        print("\n2. Large centered text")
        for word in ["RPi", "OLED", "OK"]:
            display_large_text(oled, word, delay=1.5)

        # Test 3: Multi-line formats
        print("\n3. Testing various text formats...")
        test_text_formats(oled)

        # Test 4: Scrolling text
        print("\n4. Scrolling text")
        scrolling_text(oled, "Raspberry Pi Plankton Scanner", iterations=2)

        # Final message
        print("\n5. Final message")
        display_text(oled, [
            "All Tests",
            "Complete!",
            "",
            "Press Ctrl+C",
            "to exit"
        ], delay=0)

        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nText display is working correctly.")
        print("Press Ctrl+C to exit...")

        # Keep display on
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        # Clear display
        oled.fill(0)
        oled.show()
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
