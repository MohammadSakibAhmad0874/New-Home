# Quick Start Checklist

Use this checklist to get your smart home system up and running!

## ☑️ Pre-Flight Checklist

### Hardware
- [ ] ESP32 Development Board
- [ ] 4-Channel Relay Module (5V, active-LOW recommended)
- [ ] Jumper wires (male-to-female)
- [ ] 5V 2A power supply for relays
- [ ] USB cable for ESP32
- [ ] Multimeter (for testing)

### Software
- [ ] Arduino IDE installed
- [ ] ESP32 board support added
- [ ] Computer with USB port

### Network
- [ ] WiFi router (2.4GHz required)
- [ ] WiFi name (SSID) and password ready
- [ ] Phone or computer to run the WiFi setup wizard

## 📋 Setup Steps

### Phase 1: Hardware (⏱️ 30 min)

- [ ] **Step 1**: Wire ESP32 to relay module
  - [ ] GPIO 23 → Relay IN1
  - [ ] GPIO 22 → Relay IN2
  - [ ] GPIO 21 → Relay IN3
  - [ ] GPIO 19 → Relay IN4
  - [ ] ESP32 GND → Relay GND → External Power GND (**CRITICAL!**)
  - [ ] External 5V → Relay VCC

- [ ] **Step 2**: Power ESP32 via USB (don't connect mains yet)

- [ ] **Step 3**: Verify relay module has power (VCC LED on)

### Phase 2: Firmware (⏱️ 15 min)

- [ ] **Step 4**: Install Arduino IDE
  - Download from: https://www.arduino.cc/

- [ ] **Step 5**: Add ESP32 board support
  - File → Preferences
  - Add URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
  - Tools → Board → Boards Manager
  - Install "ESP32 by Espressif Systems"

- [ ] **Step 6**: Open firmware
  - File → Open → `C:\Users\Ghosty\Desktop\HomeControl\HomeControlSketch\HomeControlSketch.ino`
  - All files (`config.h`, `relayControl.h`, `wifiManager.h`) load automatically

- [ ] **Step 7**: Select board
  - Tools → Board → ESP32 Arduino → ESP32 Dev Module

- [ ] **Step 8**: Select port
  - Tools → Port → (select your ESP32's COM port)

- [ ] **Step 9**: Upload firmware
  - Click Upload button (→)
  - Wait for "Done uploading"

### Phase 3: WiFi Setup Wizard (⏱️ 2 min)

- [ ] **Step 10**: Open Serial Monitor
  - Tools → Serial Monitor
  - Set baud rate: 115200
  - You should see: `Connect to WiFi: SmartHome_Setup`

- [ ] **Step 11**: Connect your phone to the setup hotspot
  - Open WiFi settings on your phone
  - Connect to **`SmartHome_Setup`** (password: `12345678`)
  - A setup wizard will **auto-open** in your browser
  - If it doesn't, go to **`192.168.4.1`** manually

- [ ] **Step 12**: Select your home WiFi
  - The wizard scans and shows nearby networks
  - Tap your home WiFi network
  - Enter your WiFi password
  - Click **🔗 Connect**

- [ ] **Step 13**: Note the dashboard IP
  - After connecting, the wizard shows the new IP address
  - Write it down: ___________________
  - You'll be redirected to the dashboard automatically

**🎉 WiFi is configured! No code editing needed!**

### Phase 4: Test Switches (⏱️ 5 min)

- [ ] **Step 14**: Open the dashboard
  - On your phone/computer, open browser
  - Enter the IP address from Step 13
  - Bookmark the page!

- [ ] **Step 15**: Test switches
  - [ ] Click Switch 1 - does relay 1 click? ✓
  - [ ] Click Switch 2 - does relay 2 click? ✓
  - [ ] Click Switch 3 - does relay 3 click? ✓
  - [ ] Click Switch 4 - does relay 4 click? ✓

- [ ] **Step 16**: Test Settings page
  - Click **⚙️ Settings** at the bottom of the dashboard
  - Verify WiFi status shows "Connected"
  - Verify your network name and IP are correct

**🎉 If all relays click, you're ready for Phase 5!**

### Phase 5: Remote Access (⏱️ 20 min) - OPTIONAL

> **Skip this if you only want local control**

#### Option A: Ngrok (Easiest)

- [ ] **Step 16**: Download Ngrok
  - Visit: https://ngrok.com/download
  - Sign up for free account

- [ ] **Step 17**: Install and configure
  - Extract ngrok
  - Run: `ngrok config add-authtoken YOUR_TOKEN`

- [ ] **Step 18**: Start tunnel
  - Run: `ngrok http YOUR_ESP32_IP:80`
  - Copy public URL (e.g., `https://abc123.ngrok-free.app`)

- [ ] **Step 19**: Test remotely
  - Disconnect from home WiFi (use mobile data)
  - Open public URL in browser
  - Test switches

#### Option B: Port Forwarding

- [ ] **Step 16**: Set static IP for ESP32 in router
- [ ] **Step 17**: Forward port 8080 → ESP32 port 80
- [ ] **Step 18**: Set up DDNS (No-IP, DuckDNS)
- [ ] **Step 19**: Test from outside network

### Phase 6: Voice Control (⏱️ 15 min) - OPTIONAL

- [ ] **Step 20**: Create IFTTT account
  - Visit: https://ifttt.com
  - Sign up with Google account

- [ ] **Step 21**: Connect Google Assistant
  - https://ifttt.com/google_assistant
  - Click "Connect"

- [ ] **Step 22**: Create applet for Switch 1 ON
  - If This: Google Assistant → "Say a simple phrase"
  - Phrase: "turn on living room light"
  - Then That: Webhooks → Make a web request
  - URL: `https://YOUR_URL/api/relay1/on`
  - Method: GET

- [ ] **Step 23**: Repeat for other switches
  - Create 8 total applets (4 switches × ON/OFF)

- [ ] **Step 24**: Test voice command
  - Say: "Hey Google, turn on living room light"
  - Verify relay activates

### Phase 7: Mobile App (⏱️ 2 min) - OPTIONAL

- [ ] **Step 25**: Install as PWA
  
  **iOS:**
  - Open control panel in Safari
  - Tap Share → Add to Home Screen
  
  **Android:**
  - Open control panel in Chrome
  - Tap ⋮ → Add to Home Screen

- [ ] **Step 26**: Launch from home screen icon

## ✅ Final Verification

- [ ] WiFi setup wizard works on first boot
- [ ] All 4 relays respond to web interface
- [ ] Web interface loads on phone
- [ ] WiFi reconnects after ESP32 reboot
- [ ] States persist after power cycle
- [ ] Settings page shows correct info
- [ ] Can change WiFi from Settings page
- [ ] Factory reset restarts setup wizard
- [ ] Remote access works (if enabled)
- [ ] Voice commands work (if enabled)
- [ ] PWA installed on phone (if enabled)

## 🔧 Troubleshooting Quick Fixes

### ESP32 won't connect to WiFi
- [ ] Re-enter password in the setup wizard (use "Show password" to verify)
- [ ] Make sure WiFi is 2.4GHz (not 5GHz)
- [ ] Move ESP32 closer to router
- [ ] Factory reset from Settings page and try again

### Relays don't respond
- [ ] Check common ground connection
- [ ] Verify external power to relays
- [ ] Test relay manually (touch IN to GND)
- [ ] Check GPIO pin numbers in config.h

### Can't access web interface
- [ ] Verify IP address from Serial Monitor
- [ ] Make sure you're on same WiFi
- [ ] Try `ping 192.168.X.XXX`
- [ ] Clear browser cache

### Upload failed
- [ ] Hold BOOT button while uploading
- [ ] Try different USB cable
- [ ] Select correct board and port

## 📞 Help Resources

| Issue | Check Document |
|-------|----------------|
| Wiring questions | [hardware_setup.md](docs/hardware_setup.md) |
| Upload problems | [installation_guide.md](docs/installation_guide.md) |
| WiFi setup help | [wifi_setup.md](docs/wifi_setup.md) |
| Using the system | [user_manual.md](docs/user_manual.md) |
| Remote access | [remote_access.md](docs/remote_access.md) |
| Voice control | [voice_integration.md](docs/voice_integration.md) |

## 🎯 Success Criteria

You're done when:
- ✅ WiFi setup wizard configured your network (no code editing!)
- ✅ Web interface loads and looks good
- ✅ All 4 switches toggle relays correctly
- ✅ You can control from your phone
- ✅ Settings page works and shows device info
- ✅ System reconnects after power loss
- ✅ (Optional) Remote access works
- ✅ (Optional) Voice commands work

## 🚀 Next Steps After Setup

1. **Customize switch names** to match your devices
2. **Wire to actual loads** (SAFETY FIRST - get help if unsure!)
3. **Add authentication** for remote access
4. **Share your build** with friends!

---

**Estimated Total Time:**
- Basic system: ~1 hour
- With remote access: ~1.5 hours
- With voice control: ~2 hours

**Congratulations on building your smart home!** 🏠✨
