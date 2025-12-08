# Raspberry Pi Hardware Testing

This directory contains standalone scripts for testing Raspberry Pi hardware components before full system integration.

**Branch**: `rpi-hardware-testing`

---

## 🎯 Goals

1. Test **OLED display** (128x64 or 128x32)
2. Test **joystick** input
3. Create **integrated demo** showing:
   - Start/Stop scan
   - GPS coordinates (lat/lon)
   - Status messages
   - Live sensor data

---

## 🔧 Hardware Components

### Required
- Raspberry Pi 4/5
- OLED Display (I2C)
  - Common: SSD1306 (128x64 or 128x32)
  - I2C address: Usually 0x3C or 0x3D
- Joystick Module
  - 5-way joystick (Up/Down/Left/Right/Center)
  - Or analog joystick with GPIO

### Optional
- GPS Module (for lat/lon testing)
- HQ Camera (for later integration)

---

## 📁 Directory Structure

```
rpi-hardware-testing/
├── README.md                    # This file
├── DEPLOYMENT_GUIDE.md          # How to deploy to RPi
├── oled/
│   ├── 01_test_oled_basic.py   # Basic OLED test
│   ├── 02_test_oled_text.py    # Display text
│   └── 03_test_oled_ui.py      # UI elements (boxes, lines)
├── joystick/
│   ├── 01_test_joystick_basic.py  # Basic joystick input
│   └── 02_test_joystick_events.py # Event-driven input
├── integrated_demo/
│   ├── demo_main.py            # Main demo script
│   ├── display_manager.py      # OLED display management
│   ├── input_handler.py        # Joystick input handling
│   └── gps_simulator.py        # Simulated GPS (for testing)
├── utils/
│   ├── i2c_scanner.py          # Scan for I2C devices (find OLED address)
│   ├── hardware_check.py       # Check if hardware is connected
│   └── install_deps.sh         # Install dependencies
└── docs/
    └── WIRING_DIAGRAM.md       # Hardware wiring guide
```

---

## 🚀 Quick Start

### Step 1: Deploy Files to Raspberry Pi

**Option A: Copy-Paste via SSH**
```bash
# On your laptop, SSH into RPi
ssh pi@raspberrypi.local

# Create directory
mkdir -p ~/rpi-hardware-testing
cd ~/rpi-hardware-testing

# Then copy-paste file contents one by one
```

**Option B: Git Clone on RPi**
```bash
ssh pi@raspberrypi.local
cd ~
git clone <your-repo-url>
cd plank-1
git checkout rpi-hardware-testing
cd rpi-hardware-testing
```

**Option C: SCP from Laptop**
```bash
# From your laptop
cd /Users/ayushkadali/Documents/university/SIH/plank-1
scp -r rpi-hardware-testing pi@raspberrypi.local:~/
```

### Step 2: Install Dependencies
```bash
cd ~/rpi-hardware-testing/utils
bash install_deps.sh
```

### Step 3: Run Tests
```bash
# Test OLED
python3 oled/01_test_oled_basic.py

# Test Joystick
python3 joystick/01_test_joystick_basic.py

# Run integrated demo
python3 integrated_demo/demo_main.py
```

---

## 📋 Testing Sequence

### Phase 1: OLED Display (15-20 min)
1. **Basic Connection Test**
   ```bash
   python3 oled/01_test_oled_basic.py
   ```
   - Should display "Hello RPi!"
   - Verifies I2C connection

2. **Text Display Test**
   ```bash
   python3 oled/02_test_oled_text.py
   ```
   - Displays multi-line text
   - Tests different fonts

3. **UI Elements Test**
   ```bash
   python3 oled/03_test_oled_ui.py
   ```
   - Draws boxes, lines, progress bars
   - Tests graphics capabilities

### Phase 2: Joystick (10-15 min)
1. **Basic Input Test**
   ```bash
   python3 joystick/01_test_joystick_basic.py
   ```
   - Press joystick directions
   - Prints detected inputs

2. **Event-Driven Test**
   ```bash
   python3 joystick/02_test_joystick_events.py
   ```
   - Real-time event handling
   - Tests responsiveness

### Phase 3: Integrated Demo (20-30 min)
```bash
python3 integrated_demo/demo_main.py
```

**Features**:
- Display GPS coordinates (simulated)
- Start/Stop scan with joystick
- Status messages on OLED
- Navigation with joystick (Up/Down/Left/Right)
- Center button to select

---

## 🎮 Demo Controls

| Joystick Action | Function |
|-----------------|----------|
| **Center Press** | Start/Stop Scan |
| **Up** | Navigate menu up |
| **Down** | Navigate menu down |
| **Left** | Previous screen |
| **Right** | Next screen |

---

## 📊 Expected Demo Screens

### Screen 1: Main Status
```
┌────────────────────┐
│ Plankton Scanner   │
├────────────────────┤
│ Status: Ready      │
│ Samples: 0         │
│                    │
│ [Press to Start]   │
└────────────────────┘
```

### Screen 2: Scanning
```
┌────────────────────┐
│ Scanning...        │
├────────────────────┤
│ Progress: ████░░░  │
│ Time: 3.2s         │
│                    │
│ [Press to Stop]    │
└────────────────────┘
```

### Screen 3: GPS Info
```
┌────────────────────┐
│ GPS Data           │
├────────────────────┤
│ Lat: 18.5204 N     │
│ Lon: 73.8567 E     │
│ Alt: 560m          │
│ Sats: 8            │
└────────────────────┘
```

### Screen 4: Results
```
┌────────────────────┐
│ Last Scan          │
├────────────────────┤
│ Copepods: 12       │
│ Diatoms: 8         │
│ Others: 3          │
│ Total: 23          │
└────────────────────┘
```

---

## 🔌 Hardware Connections

### OLED Display (I2C)
```
OLED Pin  →  RPi Pin
────────────────────
VCC       →  3.3V (Pin 1 or 17)
GND       →  GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
SCL       →  GPIO 3 (SCL, Pin 5)
SDA       →  GPIO 2 (SDA, Pin 3)
```

### Joystick (GPIO)
**Option A: 5-way digital joystick**
```
Joystick   →  RPi Pin
─────────────────────
VCC        →  3.3V
GND        →  GND
UP         →  GPIO 17 (Pin 11)
DOWN       →  GPIO 27 (Pin 13)
LEFT       →  GPIO 22 (Pin 15)
RIGHT      →  GPIO 23 (Pin 16)
CENTER     →  GPIO 24 (Pin 18)
```

**Option B: Analog joystick** (requires ADC)
- Use MCP3008 ADC for analog reading
- See detailed wiring in `docs/WIRING_DIAGRAM.md`

### GPS Module (UART)
```
GPS Pin   →  RPi Pin
────────────────────
VCC       →  5V (Pin 2 or 4)
GND       →  GND
TX        →  GPIO 15 (RXD, Pin 10)
RX        →  GPIO 14 (TXD, Pin 8)
```

---

## 📦 Dependencies

All scripts use standard Python libraries when possible:
- `Adafruit_SSD1306` or `luma.oled` for OLED
- `RPi.GPIO` for joystick
- `smbus2` or `smbus` for I2C
- `Pillow` (PIL) for graphics

Install with:
```bash
bash utils/install_deps.sh
```

Or manually:
```bash
sudo apt update
sudo apt install -y python3-pip i2c-tools
pip3 install adafruit-circuitpython-ssd1306 pillow RPi.GPIO smbus2
# Or alternative OLED library:
pip3 install luma.oled
```

---

## 🧪 Hardware Verification

Before running scripts, verify hardware:

```bash
# Scan for I2C devices (recommended - finds OLED address)
python3 utils/i2c_scanner.py

# Or use system command
i2cdetect -y 1

# Run full hardware check (if available)
python3 utils/hardware_check.py
```

---

## 🐛 Troubleshooting

### OLED not detected
1. Check I2C is enabled: `sudo raspi-config` → Interface Options → I2C → Enable
2. Check wiring: VCC to 3.3V, GND to GND, SCL to GPIO 3, SDA to GPIO 2
3. Run `i2cdetect -y 1` to see address
4. Try different I2C address in code (0x3C or 0x3D)

### Joystick not responding
1. Check GPIO connections
2. Enable pull-up resistors in code: `GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)`
3. Test individual pins: `gpio readall`

### Permission errors
```bash
sudo usermod -a -G i2c,gpio,spi pi
sudo reboot
```

---

## 📝 Development Workflow

### On Your Laptop (This Machine)
1. Edit code in VS Code
2. Test logic (without hardware dependencies)
3. Commit changes
4. Push to branch

### On Raspberry Pi (via SSH)
1. Pull latest changes OR copy-paste file contents
2. Run tests
3. Verify hardware works
4. Document results

### Copy-Paste Workflow (Recommended)
Since you can't install Claude on RPi:

1. **Open file on laptop** (e.g., `oled/01_test_oled_basic.py`)
2. **Copy entire contents**
3. **SSH into RPi**: `ssh pi@raspberrypi.local`
4. **Create file**: `nano ~/test_oled.py`
5. **Paste contents**: Ctrl+Shift+V (or right-click paste)
6. **Save**: Ctrl+O, Enter, Ctrl+X
7. **Run**: `python3 ~/test_oled.py`

---

## 🎯 Testing Checklist

- [ ] OLED displays text correctly
- [ ] OLED draws graphics (boxes, lines)
- [ ] Joystick detects all 5 directions
- [ ] Joystick center button works
- [ ] Integrated demo starts/stops
- [ ] Demo shows simulated GPS data
- [ ] Demo shows scan progress
- [ ] Demo is responsive (no lag)
- [ ] All scripts are standalone (no external dependencies beyond standard libs)

---

## 🔗 Next Steps After Testing

Once hardware is verified:
1. Integrate with camera module
2. Add real GPS reading (not simulated)
3. Connect to main plankton classification pipeline
4. Add data logging to SD card
5. Create field-ready system

---

## 📚 Reference

- **Adafruit OLED Guide**: https://learn.adafruit.com/monochrome-oled-breakouts
- **RPi.GPIO Docs**: https://sourceforge.net/projects/raspberry-gpio-python/
- **I2C on RPi**: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

---

**Status**: Ready for deployment to Raspberry Pi
**Branch**: `rpi-hardware-testing`
**Last Updated**: 2025-12-09
