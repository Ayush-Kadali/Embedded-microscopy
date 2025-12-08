#!/usr/bin/env python3
"""
I2C Device Scanner
Scans and displays all I2C devices connected to Raspberry Pi

This is useful for:
- Finding the address of your OLED display (usually 0x3C or 0x3D)
- Verifying I2C is enabled and working
- Debugging connection issues

Usage: python3 i2c_scanner.py
"""

import sys

try:
    import smbus2 as smbus
    SMBUS_VERSION = 2
except ImportError:
    try:
        import smbus
        SMBUS_VERSION = 1
    except ImportError:
        print("Error: smbus not installed")
        print("Install: pip3 install smbus2")
        sys.exit(1)

def scan_i2c_bus(bus_number):
    """
    Scan I2C bus for devices

    Args:
        bus_number: I2C bus number (usually 1 for RPi, 0 for older models)

    Returns:
        List of device addresses found
    """
    devices = []

    try:
        bus = smbus.SMBus(bus_number)

        print(f"\nScanning I2C bus {bus_number}...")
        print("     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")

        for row in range(0x00, 0x80, 0x10):
            print(f"{row:02x}: ", end='')

            for col in range(0x10):
                address = row + col

                # Skip reserved addresses
                if address < 0x03 or address > 0x77:
                    print("   ", end='')
                    continue

                try:
                    # Try to read a byte from the device
                    bus.read_byte(address)
                    print(f"{address:02x} ", end='')
                    devices.append(address)
                except:
                    print("-- ", end='')

            print()  # New line after each row

        bus.close()

    except FileNotFoundError:
        print(f"Error: I2C bus {bus_number} not found")
        print("\nTroubleshooting:")
        print("1. Enable I2C:")
        print("   sudo raspi-config → Interface Options → I2C → Enable")
        print("2. Reboot: sudo reboot")
        print("3. Check kernel module: lsmod | grep i2c")
        return None

    except PermissionError:
        print(f"Error: Permission denied accessing I2C bus {bus_number}")
        print("\nTroubleshooting:")
        print("1. Add user to i2c group:")
        print("   sudo usermod -a -G i2c $USER")
        print("2. Reboot: sudo reboot")
        print("3. Or run with sudo: sudo python3 i2c_scanner.py")
        return None

    except Exception as e:
        print(f"Error scanning bus {bus_number}: {e}")
        return None

    return devices

def identify_device(address):
    """
    Try to identify common I2C devices by address

    Args:
        address: I2C address (int)

    Returns:
        String describing likely device
    """
    common_devices = {
        0x3C: "OLED Display (SSD1306) - Common address",
        0x3D: "OLED Display (SSD1306) - Alternate address",
        0x48: "ADS1115 ADC / TMP102 Temperature Sensor",
        0x50: "EEPROM / AT24C256",
        0x51: "EEPROM",
        0x52: "EEPROM",
        0x53: "ADXL345 Accelerometer",
        0x68: "DS1307 RTC / MPU6050 IMU",
        0x76: "BMP280/BME280 Pressure/Temp/Humidity Sensor",
        0x77: "BMP280/BME280 Pressure/Temp/Humidity Sensor (Alt)",
    }

    return common_devices.get(address, "Unknown device")

def main():
    """Main function"""
    print("=" * 70)
    print("I2C Device Scanner for Raspberry Pi")
    print("=" * 70)
    print(f"\nUsing smbus{SMBUS_VERSION}")

    # Scan both possible I2C buses
    buses_to_scan = [1, 0]  # Try bus 1 first (standard for RPi), then bus 0

    all_devices = {}

    for bus_num in buses_to_scan:
        devices = scan_i2c_bus(bus_num)

        if devices is not None and len(devices) > 0:
            all_devices[bus_num] = devices

    # Summary
    print("\n" + "=" * 70)
    print("SCAN SUMMARY")
    print("=" * 70)

    if not all_devices:
        print("\n⚠️  No I2C devices found")
        print("\nPossible reasons:")
        print("  1. I2C not enabled (run: sudo raspi-config)")
        print("  2. No devices connected")
        print("  3. Wiring issue (check VCC, GND, SCL, SDA)")
        print("  4. Wrong I2C bus")
        print("\nVerification commands:")
        print("  i2cdetect -y 1   # Scan bus 1")
        print("  i2cdetect -y 0   # Scan bus 0")
        print("  lsmod | grep i2c # Check I2C module loaded")

    else:
        for bus_num, devices in all_devices.items():
            print(f"\n✓ Found {len(devices)} device(s) on bus {bus_num}:")

            for address in devices:
                device_name = identify_device(address)
                print(f"\n  Address: 0x{address:02X} (decimal {address})")
                print(f"  Likely:  {device_name}")

                # Special notes for OLED
                if address in [0x3C, 0x3D]:
                    print(f"  → Use this address in your OLED code!")
                    print(f"     oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x{address:02X})")

    print("\n" + "=" * 70)

    # Additional tips
    if all_devices:
        print("\n💡 TIPS:")
        print("  • Save this address for your OLED scripts")
        print("  • Most OLEDs use 0x3C, some use 0x3D")
        print("  • If device not detected, check wiring:")
        print("    - VCC → 3.3V (Pin 1 or 17)")
        print("    - GND → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)")
        print("    - SCL → GPIO 3 (Pin 5)")
        print("    - SDA → GPIO 2 (Pin 3)")

    print()

    return 0 if all_devices else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
