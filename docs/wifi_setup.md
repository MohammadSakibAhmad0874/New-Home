# 📶 WiFi Setup Guide

How to connect your SmartHome device to WiFi — no coding required!

## First-Time Setup

### Step 1: Connect to the Setup Hotspot

After uploading the firmware and powering on your ESP32:

1. Open WiFi settings on your **phone or laptop**
2. Look for a WiFi network called **`SmartHome_Setup`**
3. Connect using password: **`12345678`**
4. A setup page will automatically open in your browser

> If the page doesn't open automatically, open your browser and go to **`192.168.4.1`**

### Step 2: Select Your WiFi Network

1. The setup wizard will automatically scan for nearby WiFi networks
2. Tap **🔄 Scan for Networks** if networks don't appear
3. Select your home WiFi network from the list
4. Click **Next →**

### Step 3: Enter WiFi Password

1. Type your WiFi password
2. Check **Show password** to verify you typed it correctly
3. Click **🔗 Connect**

### Step 4: Connected! 🎉

1. The ESP32 will connect to your WiFi
2. You'll see a **success screen** with the new IP address
3. You'll be automatically redirected to the **SmartHome Dashboard**
4. Bookmark this IP address for future access!

## Changing WiFi Network

If you need to switch to a different WiFi network:

1. Open the SmartHome dashboard in your browser
2. Click **⚙️ Settings** at the bottom of the page
3. Click **📡 Change WiFi Network**
4. Follow the setup wizard again with your new network

## Factory Reset

To erase all saved WiFi credentials and start fresh:

1. Open **⚙️ Settings** on the dashboard
2. Click **🗑️ Factory Reset WiFi**
3. Confirm the reset
4. The device will restart in setup mode
5. Follow the first-time setup steps again

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't find `SmartHome_Setup` WiFi | Make sure ESP32 is powered on. Wait 10 seconds after boot. |
| Setup page doesn't open | Navigate to `192.168.4.1` manually in your browser |
| Wrong WiFi password error | Re-enter your WiFi password carefully. Use "Show password" checkbox. |
| ESP32 won't connect to WiFi | Make sure your WiFi is 2.4GHz (ESP32 doesn't support 5GHz) |
| Lost the dashboard IP | Connect to `SmartHome_Setup` again — it will show when WiFi isn't configured |
| Settings page not loading | Go to `http://<ESP32-IP>/settings` |

## How It Works

```
Power On → Check saved WiFi credentials
  ├── Credentials found → Try connecting
  │   ├── Success → Dashboard available at local IP
  │   └── Failed → Start Setup Wizard ↓
  └── No credentials → Start Setup Wizard
      └── AP Mode (SmartHome_Setup) → Captive Portal
          → User selects WiFi & enters password
          → Credentials saved to flash memory
          → Connect to WiFi → Dashboard ready!
```

The WiFi credentials are stored in the ESP32's **flash memory**, so they survive power outages and reboots!
