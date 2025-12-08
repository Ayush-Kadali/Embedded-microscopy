# Quick Start Guide - RPi Hardware Testing

**Get up and running in 15 minutes!**

---

## 🚀 Fastest Path (Copy-Paste Method)

### Step 1: SSH into Raspberry Pi (2 min)

```bash
ssh pi@raspberrypi.local
# Default password: raspberry (change it!)
```

### Step 2: Create Directory (1 min)

```bash
mkdir -p ~/rpi-test
cd ~/rpi-test
```

### Step 3: Install Dependencies (5-10 min)

```bash
# System packages
sudo apt update
sudo apt install -y python3-pip i2c-tools

# Python packages
pip3 install adafruit-circuitpython-ssd1306 pillow RPi.GPIO smbus2 --user

# Enable I2C
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable → Finish
# Reboot: sudo reboot
```

### Step 4: Copy Test Scripts (2 min)

**Option A: Copy-paste individual files**

```bash
# On RPi:
nano ~/rpi-test/test_oled.py

# Then paste the contents of oled/01_test_oled_basic.py
# Save: Ctrl+O, Enter, Ctrl+X
```

**Option B: SCP from laptop**

```bash
# On your laptop:
cd /Users/ayushkadali/Documents/university/SIH/plank-1
scp rpi-hardware-testing/oled/01_test_oled_basic.py pi@raspberrypi.local:~/rpi-test/test_oled.py
scp rpi-hardware-testing/joystick/01_test_joystick_basic.py pi@raspberrypi.local:~/rpi-test/test_joystick.py
```

### Step 5: Test Hardware (5 min)

```bash
# Test OLED
python3 ~/rpi-test/test_oled.py

# Test Joystick
python3 ~/rpi-test/test_joystick.py
```

---

## 📋 Quick Reference - File Contents

### Test OLED (Minimal Version)

If you want a super minimal test, copy-paste this into `nano ~/test_oled_minimal.py`:

```python
#!/usr/bin/env python3
import time
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw
import adafruit_ssd1306

# Init
i2c = busio.I2C(SCL, SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Clear
oled.fill(0)
oled.show()

# Draw
image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)
draw.text((0, 0), "Hello RPi!", fill=255)
draw.text((0, 20), "OLED Works!", fill=255)

# Show
oled.image(image)
oled.show()

print("OLED should show text now!")
time.sleep(10)
```

### Test Joystick (Minimal Version)

Copy-paste this into `nano ~/test_joystick_minimal.py`:

```python
#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Pins
PINS = {'UP': 17, 'DOWN': 27, 'LEFT': 22, 'RIGHT': 23, 'CENTER': 24}

# Setup
GPIO.setmode(GPIO.BCM)
for name, pin in PINS.items():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Press joystick directions. Ctrl+C to exit.")

try:
    while True:
        for name, pin in PINS.items():
            if not GPIO.input(pin):  # Button pressed (LOW)
                print(f"{name} pressed!")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nDone!")
```

---

## 🔌 Hardware Wiring Quick Reference

### OLED (I2C)
```
OLED → RPi
────────────
VCC  → 3.3V (Pin 1)
GND  → GND (Pin 6)
SCL  → GPIO 3 (Pin 5)
SDA  → GPIO 2 (Pin 3)
```

### Joystick (GPIO)
```
Joystick → RPi
─────────────────
VCC    → 3.3V (Pin 1)
GND    → GND (Pin 6)
UP     → GPIO 17 (Pin 11)
DOWN   → GPIO 27 (Pin 13)
LEFT   → GPIO 22 (Pin 15)
RIGHT  → GPIO 23 (Pin 16)
CENTER → GPIO 24 (Pin 18)
```

---

## ✅ Verification Commands

```bash
# Check I2C devices (OLED should appear at 0x3C)
i2cdetect -y 1

# Check GPIO status
gpio readall

# Check Python packages
pip3 list | grep -i ssd1306
pip3 list | grep -i gpio
```

---

## 🐛 Quick Troubleshooting

### OLED not working?
```bash
# 1. Enable I2C
sudo raspi-config  # Interface → I2C → Enable

# 2. Reboot
sudo reboot

# 3. Check device
i2cdetect -y 1  # Should show 3c or 3d
```

### Joystick not working?
```bash
# 1. Check permissions
sudo usermod -a -G gpio pi
sudo reboot

# 2. Test individual pin
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); import time; time.sleep(0.1); print('GPIO 17:', GPIO.input(17))"
```

### Permission denied?
```bash
# Add user to groups
sudo usermod -a -G i2c,gpio pi
sudo reboot
```

---

## 📦 Full Project Deployment

If you want to deploy the entire project:

```bash
# On laptop:
cd /Users/ayushkadali/Documents/university/SIH/plank-1
scp -r rpi-hardware-testing pi@raspberrypi.local:~/

# On RPi:
ssh pi@raspberrypi.local
cd ~/rpi-hardware-testing
bash utils/install_deps.sh
python3 oled/01_test_oled_basic.py
```

---

## 🎯 Next Steps

After hardware verification:
1. ✅ Test OLED display
2. ✅ Test joystick input
3. ✅ Understand copy-paste workflow
4. 🔜 Build integrated demo
5. 🔜 Add camera integration
6. 🔜 Add GPS module
7. 🔜 Connect to main plankton pipeline

---

**Time to first test**: 15 minutes
**Difficulty**: Easy ⭐
**What you need**: RPi, OLED, Joystick, SSH access

---

For detailed guides, see:
- `README.md` - Full documentation
- `DEPLOYMENT_GUIDE.md` - Deployment options
- `docs/WIRING_DIAGRAM.md` - Detailed wiring
