# Hardware Shopping List - Marine Microscopy System
**Location: Pune, India**
**Delivery Target: 2-5 days**

**Note:** This list is for reference. The current implementation uses the Raspberry Pi HQ Camera directly attached to the microscope (not using the Waveshare 100x microscope lens, as it causes blur issues).

---

## Option A: High-Performance Setup (Recommended)

### 1. Embedded Computing Platform
**NVIDIA Jetson Orin Nano 8GB Developer Kit**
- Price: ₹32,000 - ₹38,000
- Links:
  - [robu.in - NVIDIA Jetson Orin Nano 8GB](https://robu.in/product/nvidia-jetson-orin-nano-developer-kit-8gb/)
  - [Amazon.in - Jetson Orin Nano](https://www.amazon.in/NVIDIA-Jetson-Orin-Developer-945-13766-0000-000/dp/B0BZJTQ5YP)
  - [ThinkRobotics](https://www.thinkrobotics.in/products/nvidia-jetson-orin-nano-developer-kit-8gb)
- Delivery: 2-3 days from robu.in (Pune warehouse available)

**Alternative: Raspberry Pi 5 (8GB) + AI Accelerator**
- RPi 5 8GB: ₹7,500 - ₹9,000
  - [robu.in - Raspberry Pi 5 8GB](https://robu.in/product/raspberry-pi-5-8gb/)
  - [Amazon.in - RPi 5](https://www.amazon.in/Raspberry-Pi-RAS-5-8GB/dp/B0CQ8N7L2R)
- Hailo-8L AI Kit: ₹8,000 - ₹10,000
  - [Amazon.in - Hailo-8L](https://www.amazon.in/s?k=hailo-8l+raspberry+pi) (Check availability)
  - Import from [Adafruit](https://www.adafruit.com/product/5925) if needed (7-10 days)

---

### 2. Digital Microscope Camera
**Celestron 5MP Digital Microscope Imager**
- Price: ₹12,000 - ₹15,000
- Resolution: 5MP (2592x1944)
- Magnification: Up to 1000x with adapter
- Links:
  - [Amazon.in - Celestron 5MP](https://www.amazon.in/Celestron-44421-Digital-Microscope-Imager/dp/B0042SNSSW)
  - [Moglix - Celestron Microscope](https://www.moglix.com/celestron-digital-microscope-imager/mp/mce3ybpquwjvf)

**Alternative Option (Budget-Friendly):**
**Jiusion 40X-1000X USB Digital Microscope**
- Price: ₹3,500 - ₹5,000
- Resolution: 2MP
- Built-in 8 LED lights
- Links:
  - [Amazon.in - Jiusion Microscope](https://www.amazon.in/Jiusion-Magnification-Endoscope-Microscope-Compatible/dp/B06WD843ZM)
  - Delivery: 1-2 days with Prime

**Premium Option:**
**AmScope 18MP USB 3.0 Microscope Camera**
- Price: ₹18,000 - ₹22,000
- Resolution: 18MP
- High frame rate for real-time processing
- Links:
  - [Amazon.in - AmScope Camera](https://www.amazon.in/s?k=amscope+usb+3.0+microscope+camera)
  - Import option: [Amazon.com](https://www.amazon.com/AmScope-MU1803-Microscope-Calibration-Software/dp/B00U5PWL5M) (10-15 days)

---

### 3. Storage
**Samsung 980 PRO NVMe SSD 256GB** (for Jetson Orin)
- Price: ₹3,500 - ₹4,500
- Links:
  - [Amazon.in - Samsung 980 PRO](https://www.amazon.in/SAMSUNG-980-PRO-Internal-MZ-V8P250B/dp/B08GLX7TNT)
  - [Flipkart - Samsung 980 PRO](https://www.flipkart.com/samsung-980-pro-256-gb-laptop-desktop-internal-solid-state-drive/p/itm7e5f5b5f5f5f5)
- Delivery: 1-2 days

**SanDisk Extreme PRO 128GB microSD** (for Raspberry Pi)
- Price: ₹1,500 - ₹2,000
- Links:
  - [Amazon.in - SanDisk Extreme PRO](https://www.amazon.in/SanDisk-Extreme-microSDXC-Memory-Adapter/dp/B09X7BK27V)
- Delivery: 1 day with Prime

---

### 4. Power Supply & Battery
**Anker PowerCore 20000mAh PD Power Bank**
- Price: ₹3,500 - ₹4,500
- USB-C PD output (supports Jetson/RPi)
- Links:
  - [Amazon.in - Anker PowerCore](https://www.amazon.in/Anker-PowerCore-20100mAh-Portable-Charger/dp/B00VJSGT2A)
- Delivery: 1-2 days

**Official Power Supply**
- For Jetson Orin: 19V 3A adapter (usually included)
- For RPi 5: 27W USB-C PD adapter
  - [robu.in - RPi 5 Power Supply](https://robu.in/product/raspberry-pi-27w-usb-c-power-supply-white-us/)
  - Price: ₹900 - ₹1,200

---

### 5. Display (Optional but Recommended)
**Waveshare 7inch HDMI LCD (H) 1024x600 IPS**
- Price: ₹3,500 - ₹4,500
- Touchscreen for field operation
- Links:
  - [robu.in - Waveshare 7" LCD](https://robu.in/product/7inch-hdmi-lcd-h-1024x600-ips-capacitive-touch-screen/)
  - [Amazon.in - Waveshare Display](https://www.amazon.in/Waveshare-Capacitive-Touch-Screen-1024x600/dp/B07FDYXPT7)
- Delivery: 2-3 days

---

### 6. Case & Cooling
**Custom Acrylic Case + Cooling Fan**
- Jetson Orin Nano Case: ₹1,500 - ₹2,500
  - [robu.in - Jetson Cases](https://robu.in/product-category/development-boards/nvidia-jetson-boards/)
- RPi 5 Case with Active Cooling: ₹800 - ₹1,500
  - [robu.in - RPi 5 Case](https://robu.in/product/raspberry-pi-5-active-cooler/)
  - [Amazon.in - RPi 5 Case](https://www.amazon.in/s?k=raspberry+pi+5+case+with+fan)

**Noctua 40mm 5V Fan** (for additional cooling)
- Price: ₹600 - ₹900
- Links:
  - [Amazon.in - Noctua Fan](https://www.amazon.in/Noctua-NF-A4x10-5V-Premium-Quality-Quiet/dp/B00NEMG62K)

---

### 7. Cables & Accessories
**USB 3.0 Cable (A to Micro-B/C)** for microscope
- Price: ₹200 - ₹400
- [Amazon.in - USB 3.0 Cables](https://www.amazon.in/s?k=usb+3.0+cable+micro+b)

**HDMI Cable** for display
- Price: ₹150 - ₹300
- [Amazon.in - HDMI Cable](https://www.amazon.in/s?k=hdmi+cable+1m)

**MicroSD Card Reader** (if using RPi)
- Price: ₹200 - ₹400
- [Amazon.in - Card Reader](https://www.amazon.in/s?k=usb+c+microsd+card+reader)

---

## Total Cost Breakdown

### Option A: Premium Setup (Jetson Orin + Good Microscope)
| Component | Cost (INR) |
|-----------|-----------|
| Jetson Orin Nano 8GB | ₹35,000 |
| Celestron 5MP Microscope | ₹13,000 |
| Samsung 256GB NVMe SSD | ₹4,000 |
| Anker 20000mAh Battery | ₹4,000 |
| 7" Touchscreen Display | ₹4,000 |
| Case + Cooling | ₹2,000 |
| Cables & Accessories | ₹1,000 |
| **TOTAL** | **₹63,000** |

### Option B: Budget Setup (RPi 5 + Budget Microscope)
| Component | Cost (INR) |
|-----------|-----------|
| Raspberry Pi 5 8GB | ₹8,500 |
| Jiusion USB Microscope | ₹4,000 |
| 128GB microSD Card | ₹1,800 |
| RPi Power Supply | ₹1,000 |
| Anker Power Bank | ₹4,000 |
| 7" Display | ₹4,000 |
| Case + Cooling | ₹1,200 |
| Cables & Accessories | ₹500 |
| **TOTAL** | **₹25,000** |

---

## Recommended Pune Local Stores (Same Day Pickup)

### 1. SP Road Electronics Market
**Lamington Electronics** - Raspberry Pi & accessories
- Address: Lamington Road, Mumbai (3hr drive) or order online
- Contact: Check online for Pune dealers

### 2. Pune Local Options
**robu.in** - Warehouse in Mumbai, 1-2 day delivery to Pune
- Best for: Development boards, sensors, displays
- Website: https://robu.in

**Campus Component** - Electronic components
- Pune locations available
- Contact for availability

### 3. Amazon Prime
- Most items available with 1-day delivery in Pune
- Recommended for immediate needs

---

## Priority Order (for 2-5 day delivery)

**Day 1 Orders (Amazon Prime - Next Day):**
1. Microscope (Jiusion or available option)
2. Power bank
3. Storage (SSD/microSD)
4. Cables

**Day 1-2 Orders (robu.in):**
1. Jetson Orin Nano / Raspberry Pi 5
2. Display
3. Case & cooling

**Backup if delays occur:**
- Visit Lamington Road, Mumbai (electronics hub)
- Campus Component in Pune for generic items

---

## Notes
- All Amazon.in links should show delivery estimate at checkout
- robu.in typically delivers to Pune in 2-3 days
- Consider ordering from multiple sources simultaneously to ensure 2-5 day delivery
- Check stock availability before ordering
- Some items may have longer delivery - order alternatives in parallel

**Last Updated:** November 2025
