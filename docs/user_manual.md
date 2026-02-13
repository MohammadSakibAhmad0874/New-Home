# User Manual

Welcome to your Smart Home Automation System! This guide explains how to use all features.

## Getting Started

### Accessing Your Control Panel

**Local Network (Home WiFi):**
1. Connect your phone/computer to your home WiFi
2. Open any web browser
3. Enter the IP address shown in Serial Monitor (e.g., `192.168.1.150`)
4. Bookmark this page for quick access!

**Remote Access (From Anywhere):**
- Use your public URL (Ngrok/DDNS)
- See [Remote Access Guide](remote_access.md) for setup

## Control Panel Overview

Your web interface has a beautiful, modern design:

```
┌─────────────────────────────────┐
│     🏠 SmartHome                │
│     ● System Online             │
├─────────────────────────────────┤
│  💡 Living Room        [  ON ]  │
│  🌙 Bedroom            [ OFF ]  │
│  🔆 Kitchen            [  ON ]  │
│  🌀 Fan                [ OFF ]  │
└─────────────────────────────────┘
```

## Controlling Switches

### Using the Web Interface

**Turn ON/OFF:**
- Simply **tap/click** any switch card
- The button color changes:
  - **Green** = ON
  - **Gray** = OFF
- Relay activates instantly

**Visual Feedback:**
- Color change confirms command
- Smooth animations
- Status updates automatically

### Using Voice Commands

**Google Assistant:**
- "Hey Google, turn on living room light"
- "Hey Google, turn off bedroom"
- "Hey Google, activate fan"

See [Voice Integration Guide](voice_integration.md) for setup.

### Using API Calls

**For developers/advanced users:**

Turn ON:
```
http://192.168.1.150/api/relay1/on
http://192.168.1.150/api/relay2/on
http://192.168.1.150/api/relay3/on
http://192.168.1.150/api/relay4/on
```

Turn OFF:
```
http://192.168.1.150/api/relay1/off
http://192.168.1.150/api/relay2/off
http://192.168.1.150/api/relay3/off
http://192.168.1.150/api/relay4/off
```

Turn all OFF:
```
http://192.168.1.150/api/alloff
```

Get status (JSON):
```
http://192.168.1.150/api/status
```

Response:
```json
{
  "relay1": true,
  "relay2": false,
  "relay3": true,
  "relay4": false
}
```

## Advanced Features

### 1. Install as Mobile App (PWA)

Make the web interface work like a native app!

**iOS (iPhone/iPad):**
1. Open control panel in Safari
2. Tap **Share** button (square with arrow)
3. Scroll and tap **Add to Home Screen**
4. Name it "Smart Home" → **Add**
5. App icon appears on home screen!

**Android:**
1. Open control panel in Chrome
2. Tap **⋮** (three dots menu)
3. Tap **Add to Home Screen**
4. Name it "Smart Home" → **Add**
5. App appears in app drawer!

**Benefits:**
- One-tap access
- Full-screen mode
- Looks like native app
- No browser UI clutter

### 2. State Persistence

Your system **remembers** switch states even after power loss!

**Example:**
1. Turn on Living Room and Kitchen
2. Unplug ESP32
3. Plug it back in
4. Living Room and Kitchen are still ON ✓

**How it works:**
- States saved to ESP32 flash memory
- Loaded automatically on boot
- No configuration needed

**To disable:**
Edit `config.h`:
```cpp
#define ENABLE_STATE_PERSISTENCE false
```

### 3. Access Point Mode (No WiFi)

If ESP32 can't connect to WiFi, it creates its own network:

**Connect to:**
- **Network**: SmartHome_Setup
- **Password**: 12345678
- **IP Address**: 192.168.4.1

**Change AP credentials:**
Edit `config.h`:
```cpp
const char* AP_SSID = "MySmartHome";
const char* AP_PASSWORD = "mysecurepassword";
```

### 4. REST API Integration

Integrate with other systems:

**Home Assistant:**
```yaml
switch:
  - platform: rest
    name: Living Room Light
    resource: http://192.168.1.150/api/relay1/on
    body_on: ""
    body_off: ""
```

**Node-RED:**
Use HTTP request node to call `/api/relay1/on`

**Python Script:**
```python
import requests
requests.get("http://192.168.1.150/api/relay1/on")
```

## Customization

### Change Switch Names

**Method 1: Edit config.h (recommended)**
```cpp
const char* SWITCH_1_NAME = "Living Room";
const char* SWITCH_2_NAME = "Bedroom";
const char* SWITCH_3_NAME = "Kitchen";
const char* SWITCH_4_NAME = "Fan";
```

Re-upload to ESP32.

**Method 2: Edit HTML directly**
Edit `HomeControl.ino`, search for switch names in HTML, and modify.

### Change Switch Icons

In `HomeControl.ino`, find:
```html
<span class="switch-icon">💡</span>
```

Replace with other emojis:
- 🔌 Socket
- ⚡ Power
- 🌡️ Heater
- ❄️ AC
- 💦 Water pump
- 🚪 Door lock
- 📺 TV
- 🎵 Speaker

### Change Colors/Theme

Edit the CSS section in `HomeControl.ino`:

**Background gradient:**
```css
background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
```

**Button colors:**
```css
.toggle-btn.on {
    background: linear-gradient(135deg, #22c55e, #16a34a);  /* Green */
}
```

**Try different color schemes:**
- Blue theme: `#3b82f6, #2563eb`
- Purple theme: `#a855f7, #9333ea`
- Orange theme: `#f97316, #ea580c`

## Troubleshooting

### Can't Access Control Panel

**Problem**: Browser shows "Cannot connect" or "Site unreachable"

**Solutions:**
1. Verify ESP32 is powered on (check LED)
2. Check Serial Monitor for IP address
3. Make sure you're on same WiFi network
4. Try pinging IP: `ping 192.168.1.150`
5. Clear browser cache and retry
6. Try different browser
7. Disable VPN if running

### Switch Turns ON then Immediately OFF

**Problem**: Relay clicks but doesn't stay on

**Solutions:**
1. Check relay power supply (insufficient power)
2. Add external 5V power supply for relays
3. Check for loose wiring
4. Verify common ground connection

### ESP32 Keeps Rebooting

**Problem**: System restarts constantly

**Solutions:**
1. Relays drawing too much current
2. Use external power for relays (not from ESP32 5V pin)
3. Check for short circuits
4. Use better power supply (2A recommended)

### Wrong Switch Activates

**Problem**: Click switch 1, but switch 3 activates

**Solutions:**
1. Check GPIO pin wiring
2. Verify pin configuration in `config.h`
3. Check for crossed wires

### Slow Response Time

**Problem**: Delay between click and relay activation

**Solutions:**
1. Check WiFi signal strength (move ESP32 closer to router)
2. Reduce other WiFi traffic
3. Use 5GHz router if possible (but ESP32 connects to 2.4GHz)
4. Restart router and ESP32

### Voice Commands Don't Work

See [Voice Integration Guide](voice_integration.md) troubleshooting section.

## Safety Guidelines

> [!CAUTION]
> This system controls mains electricity. Always follow safety rules:

**DO:**
- ✅ Turn off power before wiring
- ✅ Use proper wire gauge for load
- ✅ Install in electrical enclosure
- ✅ Keep manual override switches
- ✅ Test with multimeter before connecting load
- ✅ Add fuses for each load
- ✅ Follow local electrical codes

**DON'T:**
- ❌ Work on live circuits
- ❌ Exceed relay current rating
- ❌ Use damaged wires
- ❌ Install in wet locations without proper protection
- ❌ Override safety features

## Maintenance

### Regular Checks

**Monthly:**
- Test all switches
- Check for loose connections
- Verify relay operation
- Test manual override

**Quarterly:**
- Check wire insulation
- Clean relay contacts if needed
- Update firmware if new version available
- Backup configuration

### Firmware Updates

1. Edit code in Arduino IDE
2. Upload new firmware
3. Settings in `config.h` persist (WiFi, pins, etc.)
4. Test thoroughly

## Tips & Tricks

### 1. Quick Access Shortcuts

**Create phone widget:**
- iOS: Use Shortcuts widget
- Android: Use Chrome shortcuts widget

**Browser bookmark:**
Save as bookmark for one-tap access

### 2. Multi-Device Control

Access from unlimited devices:
- Your phone
- Partner's phone
- Tablet
- Computer
- Smart watch browser

### 3. Backup Power

Add UPS (Uninterruptible Power Supply):
- Keeps system running during power outage
- Prevents state loss
- Recommended for critical applications

### 4. Multiple ESP32 Boards

Control more than 4 switches:
- Deploy multiple ESP32s
- Each gets own IP address
- Combine in one dashboard later

### 5. Scheduling (Future Feature)

Add timer functionality by:
- Using IFTTT scheduled applets
- Node-RED flows
- Home Assistant automations

## Frequently Asked Questions

**Q: Can I control more than 4 switches?**
A: Yes! Use an 8-channel relay module and add more GPIO pins in config.h.

**Q: Does it work without internet?**
A: Yes! Local control works anytime. Only remote access and voice need internet.

**Q: Can I use with 220V/240V?**
A: Yes! Relays are voltage-independent. Ensure relay rating matches your voltage.

**Q: How secure is this system?**
A: Local network is secure. For remote access, use HTTPS and authentication.

**Q: Can I integrate with existing smart home?**
A: Yes! Works with Home Assistant, Node-RED, IFTTT, etc.

**Q: Will it work if my phone dies?**
A: Yes! Use any device with web browser, or use physical switches.

**Q: Can multiple people control it?**
A: Yes! Any device on the network can access it simultaneously.

**Q: Does it drain ESP32 battery?**
A: ESP32 must stay powered. Use external power supply, not battery.

**Q: Can I add sensors (temperature, motion)?**
A: Yes! Add sensors to ESP32 GPIO pins and modify code.

---

## Getting Help

**Check documentation:**
- [Hardware Setup](hardware_setup.md)
- [Installation Guide](installation_guide.md)
- [Remote Access](remote_access.md)
- [Voice Integration](voice_integration.md)

**Debug with Serial Monitor:**
- Most errors show in Serial Monitor
- Set baud rate to 115200
- Check connection status and errors

---

**Enjoy your smart home!** 🏠✨

Made any cool modifications? Share them with the community!
