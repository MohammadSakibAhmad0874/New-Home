# 🏠 Smart Home Automation System v1.3

A custom ESP32-based platform for controlling home electrical switches via WiFi — **zero-code setup**, **local hotspot control**, and **cloud access from anywhere in the world**.

## ✨ Features

- 📱 **WiFi Setup Wizard** - Configure WiFi from your phone, no code changes needed
- 📡 **Always-On Hotspot** - ESP32 creates its own WiFi (`SmartHome_Control`) — connect from ANY device!
- ☁️ **Cloud Dashboard** - Control from **anywhere in the world** via `https://apnaghar-3f865.web.app`
- 🔐 **Login System** - Unique Device ID + password authentication
- 👑 **Admin Panel** - Monitor and control ALL devices from one place
- 🔄 **AP+STA Dual Mode** - Connected to WiFi AND broadcasting its own hotspot
- 📱 **Beautiful Web Interface** - Modern, responsive dark theme on all pages
- 🔄 **Real-time Updates** - Instant status feedback (local + cloud)
- 💾 **State Persistence** - Remembers switch states and WiFi after power loss
- ⚙️ **Settings Page** - Change WiFi network or factory reset anytime
- 🔒 **Secure** - Firebase Authentication, HTTPS

## 🛠 Hardware Requirements

- ESP32 Development Board
- 4-Channel Relay Module (5V)
- Jumper Wires
- 5V Power Supply (2A recommended)
- Electrical wiring and safety equipment

## 🚀 Quick Start

1. **Hardware Setup** - See [Hardware Setup Guide](docs/hardware_setup.md)
2. **Upload Firmware** - Upload `HomeControlSketch/` files via Arduino IDE
3. **Connect to Setup WiFi** - On your phone, connect to WiFi `SmartHome_Setup` (password: `12345678`)
4. **Setup Wizard Opens** - Pick your home WiFi network and enter the password
5. **Done!** - The ESP32 connects to your WiFi and creates a **hotspot** for any device to connect
6. **Access from ANY device** ↓

### 📡 Access from Any Phone / Laptop / Tablet

| Step | Action |
|------|--------|
| 1️⃣ | On your phone/laptop, connect to WiFi: **`SmartHome_Control`** (password: `12345678`) |
| 2️⃣ | Open browser and go to: **`http://192.168.4.1`** |
| 3️⃣ | Done! Control your switches 🎉 |

> **No code editing required!** Everything is configured through the web interface.
>
> **Works everywhere!** The ESP32 creates its own WiFi hotspot — no need to be on the same network. Just connect to `SmartHome_Control` and open `192.168.4.1`.

---

## ☁️ Cloud Setup (Control from Anywhere in the World)

### Step 1: Firebase Login (One-time)

```bash
cd C:\Users\Ghosty\Desktop\HomeControl
firebase login
```
A browser window opens → login with your Google account.

### Step 2: Enable Realtime Database

1. Go to **https://console.firebase.google.com** → open your project
2. **Build → Realtime Database → Create Database**
3. Select any location → **Start in test mode** → Enable

### Step 3: Deploy the Web App

```bash
firebase deploy
```
You'll get a URL like: **`https://apnaghar-3f865.web.app`**

### Step 4: Register Your Device

1. Open the deployed URL on any phone/laptop
2. Click **Register Device** tab
3. Fill in: Name, Device ID (`SH-001`), Email, Password, Switches (`4`)
4. Click **Register** → Dashboard opens!

### Step 5: Upload ESP32 Firmware

1. Install **ArduinoJson** library: `Sketch → Include Library → Manage Libraries → search "ArduinoJson" → Install`
2. Open `HomeControlSketch/HomeControlSketch.ino`
3. Click **Upload**
4. Serial Monitor should show: `☁ Firebase Cloud Sync active!`

### Step 6: Control from Anywhere! 🌍

| What | URL |
|------|-----|
| **Cloud Dashboard** (global) | `https://apnaghar-3f865.web.app` |
| **Admin Panel** | `https://apnaghar-3f865.web.app/admin.html` |
| **Local Hotspot** | Connect to `SmartHome_Control` WiFi → `http://192.168.4.1` |

---

## 📖 Documentation

- [Hardware Setup](docs/hardware_setup.md) - Wiring and safety guidelines
- [Installation Guide](docs/installation_guide.md) - Step-by-step firmware installation
- [WiFi Setup Guide](docs/wifi_setup.md) - How to configure WiFi through the wizard
- [Network Access](docs/network_access.md) - Access from any device on your network
- [User Manual](docs/user_manual.md) - How to use the system
- [Voice Integration](docs/voice_integration.md) - Google Assistant setup
- [Remote Access](docs/remote_access.md) - Control from anywhere

## 🎯 Project Structure

```
HomeControl/
├── cloud/                 # ☁️ Cloud web app (Firebase hosted)
│   ├── index.html         # Login / Register page
│   ├── dashboard.html     # Remote switch control
│   ├── admin.html         # Admin panel (all devices)
│   ├── style.css          # Design system
│   ├── app.js             # App logic
│   └── firebase-config.js # Firebase credentials
├── HomeControlSketch/     # ESP32 Arduino code
│   ├── HomeControlSketch.ino
│   ├── config.h
│   ├── firebaseSync.h     # ← Cloud sync module
│   ├── relayControl.h
│   └── wifiManager.h
├── firmware/              # Backup copy of firmware
├── firebase.json          # Firebase hosting config
└── docs/                  # Documentation
```

## 🔧 Customization

- **WiFi Settings**: Configured automatically through the setup wizard!
- **Hotspot Name**: Change `HOTSPOT_SSID` in `config.h` (default: `SmartHome_Control`)
- **Hotspot Password**: Change `HOTSPOT_PASSWORD` in `config.h` (default: `12345678`)
- **Device ID**: Change `DEVICE_ID` in `firebaseSync.h` (must match registration)
- **Firebase Project**: Update `firebase-config.js` and `firebaseSync.h` with your Firebase credentials
- **Switch Names**: Edit labels in `config.h`
- **GPIO Pins**: Change pin mappings in `config.h`
- **AP Settings**: Change setup portal name/password in `config.h`

## ⚠️ Safety Warning

This project controls mains electricity. Always:
- Work with power disconnected
- Use proper isolation
- Follow local electrical codes
- Consider professional installation verification

## 📝 License

Open source - use and modify as you wish!

---

**Built with ❤️ for complete control of your smart home**
