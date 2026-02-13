# Voice Control Integration Guide

Control your smart home with voice commands using Google Assistant!

## Overview

After completing this guide, you'll be able to say:
- **"Hey Google, turn on living room light"**
- **"Hey Google, turn off kitchen"**
- **"Hey Google, activate bedroom"**

And your ESP32 will respond instantly! 🎤

## Prerequisites

- ✅ ESP32 system working with remote access
- ✅ Google Assistant on your phone
- ✅ IFTTT account (free)

---

## Method 1: Google Assistant + IFTTT (Recommended)

This is the **easiest and most reliable** method for voice control.

### Step 1: Setup Remote Access

First, ensure you have remote access working. You need a public URL:
- Using Ngrok: `https://abc123.ngrok-free.app`
- Using Port Forwarding + DDNS: `http://myhome.ddns.net:8080`
- Using Cloudflare: `https://myhome.yourdomain.com`

### Step 2: Create IFTTT Account

1. Go to: https://ifttt.com/
2. Sign up for free account
3. Connect your Google account

### Step 3: Connect Google Assistant

1. Go to: https://ifttt.com/google_assistant
2. Click **Connect**
3. Allow IFTTT to access Google Assistant

### Step 4: Create Applet for Each Switch

We'll create 8 applets (4 switches × ON/OFF = 8 commands)

#### Example: Living Room Light ON

1. Click **Create** → https://ifttt.com/create
2. Click **If This** (trigger)
3. Search and select **Google Assistant**
4. Choose **Say a simple phrase**
5. Configure the trigger:
   - **What do you want to say?**: `turn on living room light`
   - **What's another way to say it?** (optional): `activate living room`
   - **What's another way to say it?** (optional): `living room on`
   - **What do you want the Assistant to say?**: `Turning on living room light`
   - **Language**: English
6. Click **Create trigger**

7. Click **Then That** (action)
8. Search and select **Webhooks**
9. Choose **Make a web request**
10. Configure the action:
    - **URL**: `https://your-public-url.com/api/relay1/on`
      - Replace with your actual URL (Ngrok/DDNS)
      - Use `/api/relay1/on` for Switch 1 ON
    - **Method**: `GET`
    - **Content Type**: `application/json`
    - **Body**: Leave empty
11. Click **Create action**
12. Click **Continue** → **Finish**

#### Repeat for All Switches

Create applets for:

| Voice Command | Webhook URL |
|---------------|-------------|
| "turn on living room light" | `/api/relay1/on` |
| "turn off living room light" | `/api/relay1/off` |
| "turn on bedroom" | `/api/relay2/on` |
| "turn off bedroom" | `/api/relay2/off` |
| "turn on kitchen light" | `/api/relay3/on` |
| "turn off kitchen light" | `/api/relay3/off` |
| "turn on fan" | `/api/relay4/on` |
| "turn off fan" | `/api/relay4/off` |

**Pro tip**: Use natural phrases like:
- "activate living room"
- "kitchen lights on"
- "start the fan"
- "bedroom off"

### Step 5: Test Voice Commands

1. Say: **"Hey Google, turn on living room light"**
2. Google Assistant responds: "Turning on living room light"
3. ESP32 receives command and activates relay
4. Light turns on! ✨

---

## Method 2: Shortcuts (iOS) / Routines (Android)

For faster response without IFTTT.

### iOS Shortcuts

1. Open **Shortcuts** app
2. Tap **+** to create new shortcut
3. Add action: **Get Contents of URL**
   - URL: `https://your-url.com/api/relay1/on`
   - Method: GET
4. Name shortcut: "Living Room On"
5. Add to Siri: "Turn on living room light"

### Android Google Assistant Routines

1. Open Google Assistant
2. Tap profile icon → **Settings** → **Routines**
3. Tap **+** to create routine
4. Add starter phrase: "turn on living room light"
5. Add action: **Adjust Home devices**
6. Link IFTTT applet or use custom command

---

## Method 3: Local Voice Recognition (Advanced)

Run voice recognition directly on ESP32 or Raspberry Pi.

### Option A: ESP32-S3 with I2S Microphone

- Requires ESP32-S3 (has AI capabilities)
- Add I2S microphone module
- Use ESP-SR library for speech recognition
- Works offline!

**Pros**: No internet needed, fast
**Cons**: Limited vocabulary, hardware required

### Option B: Raspberry Pi with Python

Set up a Raspberry Pi to listen for wake words and control ESP32.

**Pros**: More flexible, can use ChatGPT
**Cons**: Extra hardware, power consumption

---

## Method 4: Alexa Integration

Use Amazon Alexa instead of Google Assistant.

### Using IFTTT + Alexa

Same process as Google Assistant, but:
1. Connect **Amazon Alexa** service in IFTTT
2. Use trigger: "Alexa say a specific phrase"
3. Rest is identical

### Using Custom Alexa Skill (Advanced)

Create a custom Alexa skill that directly controls your ESP32:
- Requires AWS Lambda
- More complex setup
- More professional result

---

## Advanced: Natural Language Processing

Make your system understand complex commands.

### Example Setup

**"Turn on all lights"** → Activates relays 1, 2, 3

**Implementation**:
1. Add endpoint: `/api/all/on` in HomeControl.ino
2. Create function to control multiple relays:
```cpp
server.on("/api/all/on", HTTP_GET, []() {
  setRelay(0, true);
  setRelay(1, true);
  setRelay(2, true);
  server.send(200, "application/json", getRelayStatesJSON());
});
```
3. Create IFTTT applet linking voice command to this endpoint

### More Advanced Commands

- **"Goodnight mode"** → Turn off all lights, turn on bedroom
- **"Movie time"** → Dim living room, turn off kitchen
- **"I'm home"** → Turn on living room and kitchen

---

## Troubleshooting

### Voice Command Doesn't Work

1. **Check IFTTT applet status**: Go to IFTTT → My Applets → Check if enabled
2. **Test webhook directly**: Open webhook URL in browser
3. **Verify remote access**: Make sure public URL is accessible
4. **Check Assistant response**: If Google responds but relay doesn't activate, it's a network issue

### Delayed Response

- IFTTT can have 1-5 second delay (normal)
- Using Shortcuts/Routines is faster
- Local voice recognition is instant

### Wrong Relay Activates

- Double-check webhook URLs in IFTTT applets
- Verify relay numbering matches your wiring

---

## Security Considerations

> [!WARNING]
> Voice-controlled smart homes are convenient but have security implications:

1. **Authentication**: Add password to webhooks
   ```
   https://user:pass@your-url.com/api/relay1/on
   ```

2. **HTTPS Only**: Always use HTTPS for remote access

3. **Rate Limiting**: Prevent abuse by limiting API calls

4. **Guest Mode**: Create separate commands with limited access

---

## Sample Voice Commands Reference

Customize these to match your switches:

### Living Room Light
- "Turn on living room light"
- "Activate living room" 
- "Living room lights on"
- "Turn off living room"

### Bedroom
- "Turn on bedroom light"
- "Bedroom on"
- "Turn off bedroom"

### Kitchen
- "Turn on kitchen"
- "Kitchen light on"
- "Turn off kitchen light"

### Fan
- "Turn on the fan"
- "Start fan"
- "Turn off fan"
- "Stop fan"

---

## Next Level: AI Voice Assistant

Integrate with ChatGPT for natural conversations:

**You**: "It's getting hot in here"
**AI**: *Analyzes context, turns on fan*

This requires:
- Voice-to-text (Google Cloud Speech API)
- AI processing (OpenAI API)
- Text-to-speech (Google TTS)
- ESP32 API integration

Would you like a guide on building this? Let me know! 🚀

---

**Congratulations!** 🎉 You now have full voice control of your smart home!

Next: Build a mobile app → [User Manual](user_manual.md)
