# 📱 Access from Any Device

Your SmartHome system can be controlled from **any phone, laptop, or tablet** connected to the same WiFi network — no app installation needed!

## Quick Access

After your ESP32 connects to WiFi, open any browser and go to:

```
http://smarthome.local
```

That's it! Works on iPhone, Android, Windows, Mac, tablets — any device with a browser.

## How It Works

The ESP32 uses **mDNS** (Multicast DNS), a built-in technology that broadcasts a friendly hostname on your local network. Instead of remembering an IP like `192.168.1.105`, you just type `smarthome.local`.

## Device Compatibility

| Device      | `.local` Support | Notes                        |
|-------------|------------------|------------------------------|
| iPhone/iPad | ✅ Built-in       | Works in Safari & Chrome    |
| Mac         | ✅ Built-in       | Works in all browsers       |
| Windows 10+ | ✅ Built-in       | Works in all browsers       |
| Android     | ⚠️ Partial       | Chrome works; use IP if not |
| Linux       | ✅ With avahi     | Most distros include it     |

> **Android note:** If `smarthome.local` doesn't work on your Android device, use the IP address instead. The dashboard always shows both the hostname and IP address.

## Finding the IP Address

If you need the IP address (e.g., for Android), you can find it:

1. **Dashboard footer** — Shows the IP below the switch controls
2. **Settings page** — Go to `http://smarthome.local/settings`
3. **Serial Monitor** — Printed on startup when connected via USB

## Changing the Hostname

To change from `smarthome.local` to something else:

1. Open `firmware/config.h`
2. Change this line:
   ```cpp
   const char* MDNS_HOSTNAME = "smarthome";  // → smarthome.local
   ```
3. For example, change to `"bedroom"` to access via `http://bedroom.local`
4. Re-upload the firmware

## Multiple ESP32 Devices

If you have multiple ESP32s, give each a **unique hostname**:

- Device 1: `MDNS_HOSTNAME = "living-room"` → `http://living-room.local`
- Device 2: `MDNS_HOSTNAME = "bedroom"` → `http://bedroom.local`
- Device 3: `MDNS_HOSTNAME = "kitchen"` → `http://kitchen.local`

## Global Access (Internet)

> ⚠️ mDNS only works on your **local WiFi network**. For internet access from outside your home, you have these options:

### Option 1: Router Port Forwarding
1. Log into your router admin panel (usually `192.168.1.1`)
2. Find "Port Forwarding" settings
3. Forward **port 80** to the ESP32's local IP
4. Access from outside using your public IP

### Option 2: Cloud Tunnel (Recommended)
Use a service like **ngrok** or **Cloudflare Tunnel** on a Raspberry Pi to expose your ESP32 to the internet securely.

### Option 3: IoT Platforms
Integrate with platforms like **Blynk**, **Home Assistant**, or **MQTT** for cloud-based remote access with mobile apps.

## Troubleshooting

### "smarthome.local" doesn't load
1. Make sure your device and ESP32 are on the **same WiFi network**
2. Try the IP address instead (shown in Serial Monitor)
3. Restart the ESP32
4. On Android, try Chrome browser specifically

### Works on one device but not another
- The other device might be on a different WiFi network (e.g., 5GHz vs 2.4GHz)
- Some corporate/public WiFi networks block mDNS — use your home WiFi

### IP address keeps changing
- The hostname `smarthome.local` won't change even if the IP does
- Or: set a "static IP" in your router settings for the ESP32's MAC address
