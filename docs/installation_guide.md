# Installation Guide

This guide will walk you through installing the Smart Home Automation firmware on your ESP32.

## Prerequisites

### 1. Install Arduino IDE

Download and install from: https://www.arduino.cc/en/software

**Recommended version**: 2.0 or newer

### 2. Install ESP32 Board Support

1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click **OK**
5. Go to **Tools → Board → Boards Manager**
6. Search for "esp32"
7. Install **"ESP32 by Espressif Systems"**
8. Wait for installation to complete

### 3. No Additional Libraries Needed! ✓

All required libraries are built into the ESP32 board package:
- WiFi.h
- WebServer.h
- Preferences.h

## Upload Firmware to ESP32

### Step 1: Connect ESP32 to Computer

1. Connect ESP32 to your computer via USB cable
2. Wait for drivers to install (Windows may take a moment)
3. Check Device Manager (Windows) or About This Mac → System Report → USB (Mac) to confirm

### Step 2: Open the Project

1. Open Arduino IDE
2. Go to **File → Open**
3. Navigate to: `C:\Users\Ghosty\Desktop\HomeControl\firmware\`
4. Open **HomeControl.ino**

All three files should open in tabs:
- HomeControl.ino
- config.h
- relayControl.h

### Step 3: Configure WiFi Settings

1. Click on the **config.h** tab
2. Edit these lines with your WiFi credentials:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_NAME";      // ← Your WiFi name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // ← Your WiFi password
```

3. **Optional**: Customize switch names:
```cpp
const char* SWITCH_1_NAME = "Living Room";
const char* SWITCH_2_NAME = "Bedroom";
const char* SWITCH_3_NAME = "Kitchen";
const char* SWITCH_4_NAME = "Fan";
```

4. **Save** the file (Ctrl+S or Cmd+S)

### Step 4: Select Board and Port

1. Go to **Tools → Board → ESP32 Arduino**
2. Select your ESP32 board (common options):
   - **ESP32 Dev Module** (most common)
   - **NodeMCU-32S**
   - **DOIT ESP32 DEVKIT V1**

3. Go to **Tools → Port**
4. Select the COM port showing your ESP32 (e.g., COM3, COM4)
   - On Mac/Linux: /dev/cu.usbserial-xxxxx

### Step 5: Configure Upload Settings

Set these in **Tools** menu:

| Setting | Value |
|---------|-------|
| Upload Speed | 115200 |
| CPU Frequency | 240MHz (WiFi/BT) |
| Flash Frequency | 80MHz |
| Flash Mode | QIO |
| Flash Size | 4MB (32Mb) |
| Partition Scheme | Default 4MB with spiffs |

### Step 6: Upload!

1. Click the **Upload** button (→ arrow icon)
2. Wait for "Connecting...." message
3. If stuck on "Connecting":
   - **Hold the BOOT button** on ESP32
   - **Keep holding** until upload starts
   - Release when you see upload progress

4. Wait for upload to complete (30-60 seconds)
5. You should see: **"Hard resetting via RTS pin..."**

## First Connection

### Step 1: Open Serial Monitor

1. Go to **Tools → Serial Monitor**
2. Set baud rate to **115200** (bottom right)
3. Press the **RESET** button on ESP32

### Step 2: Check Connection Status

You should see output like this:

```
========================================
  Smart Home Automation System v1.0
========================================

Relay 1 initialized: OFF
Relay 2 initialized: OFF
Relay 3 initialized: OFF
Relay 4 initialized: OFF

Connecting to WiFi: YourWiFiName
.....
✓ WiFi connected successfully!
  IP Address: 192.168.1.150
  Signal Strength: -45 dBm

✓ Web server started!
========================================
  Local IP: 192.168.1.150
========================================
```

**COPY THE IP ADDRESS!** You'll need this to access your control panel.

### Step 3: Access Web Interface

1. Make sure your phone/computer is connected to the **same WiFi network**
2. Open a web browser
3. Type the IP address (e.g., `192.168.1.150`)
4. You should see your beautiful control panel! 🎉

## Troubleshooting

### ESP32 Won't Connect to WiFi

**Shows Access Point mode instead:**
```
✗ WiFi connection failed!
Starting Access Point mode...
✓ Access Point started!
  SSID: SmartHome_Setup
  Password: 12345678
  IP Address: 192.168.4.1
```

**Solutions:**
1. Check WiFi name and password in config.h
2. Make sure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
3. Move ESP32 closer to router
4. Check for special characters in WiFi password

**Using Access Point mode (temporary):**
1. Connect your phone to WiFi: **SmartHome_Setup**
2. Password: **12345678**
3. Open browser and go to: **192.168.4.1**

### Upload Failed

**Error: "Failed to connect to ESP32"**

1. Hold **BOOT** button while uploading
2. Try a different USB cable (data cable, not charge-only)
3. Try a different USB port
4. Install CH340/CP2102 drivers if needed

### Web Page Won't Load

1. Verify IP address from Serial Monitor
2. Make sure you're on the same WiFi network
3. Try pinging the IP: `ping 192.168.1.150`
4. Disable VPN if enabled
5. Clear browser cache

### Relays Don't Respond

1. Check wiring (see Hardware Setup Guide)
2. Verify common ground connection
3. Check if relay has external power supply
4. Test relay manually (touch IN pin to GND)
5. Verify `ACTIVE_LOW` setting in config.h

## Next Steps

✅ System is working locally!

Now you can:
- 🌍 Enable **Remote Access** - [Remote Access Guide](remote_access.md)
- 🎤 Add **Voice Control** - [Voice Integration Guide](voice_integration.md)
- 📱 Install as **Mobile App** - [User Manual](user_manual.md)

---

## Quick Reference

### Re-upload with Changes

1. Edit config.h or HomeControl.ino
2. Click Upload button
3. Wait for completion

### Find IP Address Again

1. Open Serial Monitor (115200 baud)
2. Press RESET on ESP32
3. IP shows in startup message

### Change WiFi Network

1. Edit config.h with new credentials
2. Upload again
3. Check Serial Monitor for new IP

---

Need help? Check the [User Manual](user_manual.md) or review the [Hardware Setup](hardware_setup.md).
