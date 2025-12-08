# Deployment Guide: Copy-Paste Method for Raspberry Pi

Since Claude cannot be installed on the Raspberry Pi, this guide provides the best workflow for deploying and running code on your RPi.

---

## 🎯 Deployment Methods

### Method 1: Copy-Paste via SSH (Recommended for Quick Testing)
### Method 2: SCP File Transfer (Recommended for Multiple Files)
### Method 3: Git Clone on RPi (Best for Full Project)

---

## Method 1: Copy-Paste via SSH ⭐ EASIEST

### Step-by-Step

1. **Open SSH Connection**
   ```bash
   # From your laptop
   ssh pi@raspberrypi.local
   # Or if .local doesn't work:
   ssh pi@192.168.x.x
   ```

2. **Create Directory Structure**
   ```bash
   mkdir -p ~/rpi-testing/{oled,joystick,integrated_demo,utils}
   cd ~/rpi-testing
   ```

3. **Create File on RPi**
   ```bash
   nano oled/test_oled.py
   ```

4. **Copy Code from Laptop**
   - On your laptop, open the file (e.g., `01_test_oled_basic.py`)
   - Select all (Cmd+A on Mac, Ctrl+A on Windows)
   - Copy (Cmd+C or Ctrl+C)

5. **Paste into Nano**
   - In the SSH terminal with nano open
   - Paste: **Cmd+Shift+V** (Mac) or **Ctrl+Shift+V** or **Right-click → Paste**

6. **Save and Exit**
   - Press **Ctrl+O** (save)
   - Press **Enter** (confirm filename)
   - Press **Ctrl+X** (exit)

7. **Run the Script**
   ```bash
   python3 oled/test_oled.py
   ```

### Pros
✅ Simple, no tools needed
✅ Works even without git on RPi
✅ Good for quick tests

### Cons
❌ Tedious for many files
❌ Easy to make copy-paste errors
❌ No version control

---

## Method 2: SCP File Transfer ⭐ RECOMMENDED

### Step-by-Step

1. **From Your Laptop Terminal**
   ```bash
   cd /Users/ayushkadali/Documents/university/SIH/plank-1

   # Copy single file
   scp rpi-hardware-testing/oled/01_test_oled_basic.py pi@raspberrypi.local:~/test_oled.py

   # Or copy entire directory
   scp -r rpi-hardware-testing pi@raspberrypi.local:~/
   ```

2. **SSH into RPi**
   ```bash
   ssh pi@raspberrypi.local
   ```

3. **Verify Files**
   ```bash
   ls -la ~/rpi-hardware-testing
   ```

4. **Run Scripts**
   ```bash
   cd ~/rpi-hardware-testing
   python3 oled/01_test_oled_basic.py
   ```

### Pros
✅ Fast for multiple files
✅ Preserves file structure
✅ Can update quickly

### Cons
❌ Need SSH key setup for ease of use
❌ Need to remember SCP syntax

---

## Method 3: Git Clone on RPi ⭐ BEST FOR PROJECT

### Step-by-Step

1. **Ensure Git is Installed on RPi**
   ```bash
   ssh pi@raspberrypi.local
   sudo apt update
   sudo apt install -y git
   ```

2. **Clone Repository**
   ```bash
   cd ~
   git clone <your-repo-url>
   # Or if already cloned, just pull:
   cd ~/plank-1
   git pull origin rpi-hardware-testing
   ```

3. **Checkout RPi Branch**
   ```bash
   git checkout rpi-hardware-testing
   ```

4. **Navigate and Run**
   ```bash
   cd rpi-hardware-testing
   python3 oled/01_test_oled_basic.py
   ```

### Pros
✅ Full version control
✅ Easy to update (git pull)
✅ Best for collaboration

### Cons
❌ Requires git setup
❌ Need to push/pull for changes

---

## 🚀 Quick Start Workflow (Recommended)

### Initial Setup (One-time)

```bash
# 1. SSH into RPi
ssh pi@raspberrypi.local

# 2. Install dependencies
sudo apt update
sudo apt install -y python3-pip i2c-tools git

# 3. Enable I2C
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable → Finish

# 4. Reboot
sudo reboot
```

### Deploying a Single Script (Fast Testing)

```bash
# On laptop: Copy file contents
# (Open file, Cmd+A, Cmd+C)

# On RPi via SSH:
ssh pi@raspberrypi.local
nano ~/test_script.py
# Paste: Cmd+Shift+V or Ctrl+Shift+V
# Save: Ctrl+O, Enter, Ctrl+X

# Run
python3 ~/test_script.py
```

### Deploying Full Directory (Project Work)

```bash
# On laptop:
cd /Users/ayushkadali/Documents/university/SIH/plank-1
scp -r rpi-hardware-testing pi@raspberrypi.local:~/

# On RPi:
ssh pi@raspberrypi.local
cd ~/rpi-hardware-testing
bash utils/install_deps.sh
python3 integrated_demo/demo_main.py
```

---

## 📋 File-by-File Deployment Checklist

For each script you want to test:

### Before Deployment
- [ ] Test script logic on laptop (if possible)
- [ ] Remove any laptop-specific paths
- [ ] Verify all imports are available on RPi
- [ ] Add error handling for hardware failures

### Deployment
- [ ] Copy/SCP file to RPi
- [ ] Verify file is on RPi (`ls -la`)
- [ ] Check file permissions (`chmod +x` if needed)
- [ ] Install any missing dependencies

### Testing
- [ ] Run script: `python3 script.py`
- [ ] Check for errors
- [ ] Verify hardware responds
- [ ] Document results

---

## 🔧 Installing Dependencies on RPi

### Method A: Using install script (Recommended)

```bash
# Copy install script first
scp rpi-hardware-testing/utils/install_deps.sh pi@raspberrypi.local:~/

# On RPi:
bash ~/install_deps.sh
```

### Method B: Manual installation

```bash
# System packages
sudo apt update
sudo apt install -y python3-pip python3-dev i2c-tools

# Python packages for OLED
pip3 install adafruit-circuitpython-ssd1306 pillow
# Or alternative:
pip3 install luma.oled

# Python packages for GPIO
pip3 install RPi.GPIO

# Python packages for I2C
pip3 install smbus2

# Optional: GPS
pip3 install gps gpsd-py3
```

---

## 🎮 Testing Workflow

### Test 1: OLED Display

```bash
# Deploy file
scp rpi-hardware-testing/oled/01_test_oled_basic.py pi@raspberrypi.local:~/test_oled.py

# SSH and run
ssh pi@raspberrypi.local
python3 ~/test_oled.py

# Expected: OLED shows "Hello RPi!"
```

### Test 2: Joystick

```bash
# Deploy file
scp rpi-hardware-testing/joystick/01_test_joystick_basic.py pi@raspberrypi.local:~/test_joystick.py

# SSH and run
ssh pi@raspberrypi.local
python3 ~/test_joystick.py

# Expected: Prints joystick directions when pressed
```

### Test 3: Integrated Demo

```bash
# Deploy all demo files
scp -r rpi-hardware-testing/integrated_demo pi@raspberrypi.local:~/

# SSH and run
ssh pi@raspberrypi.local
cd ~/integrated_demo
python3 demo_main.py

# Expected: Full UI with navigation
```

---

## 🐛 Troubleshooting

### Problem: SSH Connection Refused

**Solution**:
```bash
# Enable SSH on RPi (from RPi desktop):
sudo raspi-config
# Interface Options → SSH → Enable

# Or enable manually:
sudo systemctl enable ssh
sudo systemctl start ssh

# Find RPi IP address:
hostname -I
```

### Problem: Permission Denied for GPIO/I2C

**Solution**:
```bash
# Add user to groups
sudo usermod -a -G i2c,gpio,spi pi

# Reboot
sudo reboot

# Or run with sudo (not recommended):
sudo python3 script.py
```

### Problem: Module Not Found

**Solution**:
```bash
# Check pip installation
pip3 list | grep -i ssd1306

# Install missing module
pip3 install adafruit-circuitpython-ssd1306

# Or use system package:
sudo apt install python3-smbus
```

### Problem: OLED Not Detected

**Solution**:
```bash
# Check I2C devices
i2cdetect -y 1

# Should show device at 0x3C or 0x3D
# If nothing appears, check wiring

# Try different I2C bus (older RPis use bus 0):
i2cdetect -y 0
```

---

## 📝 Quick Reference Commands

### SSH
```bash
# Connect
ssh pi@raspberrypi.local
ssh pi@192.168.x.x

# Copy file TO RPi
scp local_file.py pi@raspberrypi.local:~/remote_file.py

# Copy file FROM RPi
scp pi@raspberrypi.local:~/remote_file.py ./local_file.py

# Copy directory
scp -r local_dir pi@raspberrypi.local:~/remote_dir
```

### File Editing on RPi
```bash
# Nano (simple)
nano file.py
# Save: Ctrl+O, Enter
# Exit: Ctrl+X

# Vim (advanced)
vim file.py
# Insert mode: i
# Save and exit: Esc, :wq
```

### Running Scripts
```bash
# Run Python script
python3 script.py

# Run in background
python3 script.py &

# Run and log output
python3 script.py 2>&1 | tee output.log

# Make script executable
chmod +x script.py
./script.py
```

---

## 🔄 Iterative Development Workflow

### Recommended Flow

1. **Write code on laptop** (with Claude's help)
2. **Test logic** without hardware (if possible)
3. **Copy to RPi** (SCP or copy-paste)
4. **Run and test** hardware
5. **Note any issues**
6. **Fix on laptop**
7. **Repeat**

### Example Session

```bash
# Terminal 1 (Laptop - for editing)
cd /Users/ayushkadali/Documents/university/SIH/plank-1/rpi-hardware-testing

# Edit file in VS Code
code oled/01_test_oled_basic.py

# Copy to RPi when ready
scp oled/01_test_oled_basic.py pi@raspberrypi.local:~/test.py

# Terminal 2 (SSH to RPi - for testing)
ssh pi@raspberrypi.local
python3 ~/test.py

# See error? Go back to Terminal 1, fix, and SCP again
```

---

## 🎯 Ready-to-Copy Commands

### Full Project Deployment

```bash
# On laptop:
cd /Users/ayushkadali/Documents/university/SIH/plank-1
scp -r rpi-hardware-testing pi@raspberrypi.local:~/

# On RPi:
ssh pi@raspberrypi.local
cd ~/rpi-hardware-testing
bash utils/install_deps.sh
python3 utils/hardware_check.py
python3 oled/01_test_oled_basic.py
python3 joystick/01_test_joystick_basic.py
python3 integrated_demo/demo_main.py
```

---

## 📞 Need Help?

1. **Check hardware**: `python3 utils/hardware_check.py`
2. **Verify wiring**: See `docs/WIRING_DIAGRAM.md`
3. **Test I2C**: `i2cdetect -y 1`
4. **Check GPIO**: `gpio readall`
5. **View logs**: Add print statements or use logging module

---

**Status**: Ready for deployment
**Last Updated**: 2025-12-09
