# 📦 Per-Device Firmware Folders

Each folder is a **self-contained Arduino project** — just open the `.ino` file in Arduino IDE and upload directly. No config swapping needed!

---

## Registered Devices

| Folder | Device ID | Name | Owner | Hotspot WiFi |
|--------|-----------|------|-------|--------------|
| `SH_001/` | `SH-001` | New Sakib | User 8 | `SmartHome_SH001` |
| `SH_002/` | `SH-002` | Mohammad Sakib Ahmad | User 10 | `SmartHome_SH002` |
| `SH_004/` | `SH-004` | NEW BREAK | User 2 | `SmartHome_SH004` |

---

## ⬆️ How to Upload to ESP32

1. **Open Arduino IDE**
2. **File → Open** → select the device folder's `.ino` file  
   e.g. `SH_001/SH_001.ino`
3. **Connect ESP32** via USB cable
4. **Tools → Board** → `ESP32 Dev Module`
5. **Tools → Port** → select your COM port  
6. **Click Upload** ⬆️
7. Open **Serial Monitor** at `115200` baud to see connection logs

---

## 📁 What's in Each Folder

```
SH_001/
├── SH_001.ino        ← Main sketch — OPEN THIS in Arduino IDE
├── config.h          ← Device-specific: ID, API key, pins, hotspot name
├── relayControl.h    ← Relay GPIO control + state persistence
├── websocketSync.h   ← Cloud WebSocket connection + auto-reconnect
├── wifiManager.h     ← WiFi captive portal setup wizard
└── firebaseSync.h    ← Legacy Firebase (disabled, kept for reference)
```

**Only `config.h` differs between devices.** All other files are identical.

---

## ⚙️ config.h Quick Reference

| Setting | What it does |
|---------|-------------|
| `DEVICE_ID` | Must match the ID registered in the database |
| `DEVICE_API_KEY` | Authentication key from database |
| `BACKEND_HOST` | Render backend URL (don't change) |
| `HOTSPOT_SSID` | Name of ESP32's always-on WiFi hotspot |
| `RELAY_PIN_1..4` | GPIO pins for your relay module |
| `ACTIVE_LOW` | `true` for most relay modules |
| `SWITCH_1..4_NAME` | Display names for the 4 switches |

---

## ➕ Adding a New Device

1. **Register in DB** — open this URL in browser (wait 30s if backend asleep):  
   `https://homecontrol-backend-8fbg.onrender.com/api/v1/setup/create-device?secret=homecontrol_setup_2024&device_id=SH-005&owner_id=2&name=My+Device`

2. **Get API key** — copy the `api_key` from the JSON response

3. **Copy a device folder**:
   ```
   Copy SH_001/ → SH_005/
   Rename SH_001.ino → SH_005.ino
   ```

4. **Edit `config.h`** inside the new folder:
   ```cpp
   const char* DEVICE_ID      = "SH-005";
   const char* DEVICE_API_KEY = "your-api-key-here";
   const char* HOTSPOT_SSID   = "SmartHome_SH005";
   ```

5. Upload to ESP32 — done! ✅

---

## 🐛 Bug Fixes Applied (v1.3)

All device folders include these fixes:

| # | Bug | Fix |
|---|-----|-----|
| 1 | State update sent **twice** per change | Removed duplicate `client.send()` |
| 2 | **No WebSocket reconnect** if connection drops | Added auto-reconnect every 10s |
| 3 | NaN sensor value sent as `"null"` string | Now sends proper JSON `null` |
| 4 | Sensor data sent **twice** in debug mode | Removed duplicate call |
| 5 | Local API relays didn't update cloud dashboard | Added `notifyCloudStateChange()` to all API endpoints |

---

## 📋 Required Arduino Libraries

Install via **Arduino IDE → Tools → Manage Libraries**:

| Library | Author |
|---------|--------|
| `ArduinoWebsockets` | Gil Maimon |
| `ArduinoJson` | Benoit Blanchon |
| `DHT sensor library` | Adafruit |

Board: **ESP32** — install via **Tools → Board Manager** → search `esp32` → install by Espressif
