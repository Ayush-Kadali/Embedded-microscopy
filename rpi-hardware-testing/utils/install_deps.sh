#!/bin/bash
# Install dependencies for RPi hardware testing

set -e  # Exit on error

echo "======================================"
echo "RPi Hardware Testing - Dependency Setup"
echo "======================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Some packages may not work correctly"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Step 1: Updating system packages..."
sudo apt update

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt install -y python3-pip python3-dev i2c-tools

echo ""
echo "Step 3: Installing Python packages..."

# OLED display
echo "  - Installing OLED display libraries..."
pip3 install adafruit-circuitpython-ssd1306 pillow --user

# GPIO
echo "  - Installing GPIO library..."
pip3 install RPi.GPIO --user

# I2C
echo "  - Installing I2C library..."
pip3 install smbus2 --user

# Optional: GPS
read -p "Install GPS libraries? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  - Installing GPS libraries..."
    pip3 install gps gpsd-py3 --user
fi

echo ""
echo "Step 4: Checking I2C configuration..."
if lsmod | grep -q i2c_dev; then
    echo "✓ I2C kernel module loaded"
else
    echo "⚠️  I2C kernel module not loaded"
    echo "   Enable I2C: sudo raspi-config → Interface Options → I2C"
fi

echo ""
echo "Step 5: Checking permissions..."
if groups | grep -q i2c; then
    echo "✓ User is in i2c group"
else
    echo "⚠️  User not in i2c group"
    echo "   Adding user to i2c group..."
    sudo usermod -a -G i2c $USER
    echo "   ⚠️  You need to reboot for this to take effect"
fi

if groups | grep -q gpio; then
    echo "✓ User is in gpio group"
else
    echo "⚠️  User not in gpio group"
    echo "   Adding user to gpio group..."
    sudo usermod -a -G gpio $USER
    echo "   ⚠️  You need to reboot for this to take effect"
fi

echo ""
echo "======================================"
echo "✅ Installation Complete!"
echo "======================================"

echo ""
echo "Next steps:"
echo "  1. If you added user to groups, reboot:"
echo "     sudo reboot"
echo ""
echo "  2. Check I2C devices:"
echo "     i2cdetect -y 1"
echo ""
echo "  3. Run hardware check:"
echo "     python3 utils/hardware_check.py"
echo ""
echo "  4. Test OLED:"
echo "     python3 oled/01_test_oled_basic.py"
echo ""
echo "  5. Test joystick:"
echo "     python3 joystick/01_test_joystick_basic.py"
echo ""
echo "======================================"
