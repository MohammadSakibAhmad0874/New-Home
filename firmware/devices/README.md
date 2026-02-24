# 📦 Per-Device Firmware Folders

Each folder is a **self-contained Arduino project** — open it in Arduino IDE and upload directly!

## Devices

| Folder | Device ID | Name | Owner |
|--------|-----------|------|-------|
| `SH_001/` | SH-001 | New Sakib | User 8 |
| `SH_004/` | SH-004 | NEW BREAK | User 2 |

## How to Upload

1. **Open Arduino IDE**
2. **File → Open** → select `SH_001/SH_001.ino` or `SH_004/SH_004.ino`
3. **Connect your ESP32** via USB
4. **Tools → Board** → ESP32 Dev Module
5. **Tools → Port** → Select your COM port
6. **Click Upload** ⬆️

## Adding a New Device

1. Copy any existing folder (e.g. `SH_001/`)
2. Rename the folder and `.ino` file to match (e.g. `SH_005/SH_005.ino`)
3. Edit `config.h` inside:
   - `DEVICE_ID` → your new device ID
   - `DEVICE_API_KEY` → get it from: `/api/v1/setup/device-key?secret=homecontrol_setup_2024&device_id=SH-005`
   - `HOTSPOT_SSID` → unique name like `SmartHome_SH005`

## What's in Each Folder

```
SH_001/
├── SH_001.ino        ← Main sketch (open this in Arduino IDE)
├── config.h          ← Device-specific settings (ID, API key, pins)
├── relayControl.h    ← Relay on/off logic
├── wifiManager.h     ← WiFi setup portal
├── websocketSync.h   ← Cloud connection via WebSocket
└── firebaseSync.h    ← Firebase sync (legacy)
```
