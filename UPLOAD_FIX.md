# Arduino Upload Error - FIXED! ✅

## The Problem

You got this error:
```
fatal error: config.h: No such file or directory
#include "config.h"
```

## The Cause

Arduino IDE has a strict rule: **The `.ino` file must be in a folder with the exact same name**.

❌ **Wrong**: `firmware/HomeControl.ino` (folder name doesn't match)
✅ **Correct**: `HomeControlSketch/HomeControlSketch.ino` (folder and file match)

## ✅ The Fix (Already Applied!)

I've created a properly structured folder for you:

**New Location**: `C:\Users\Ghosty\Desktop\HomeControl\HomeControlSketch\`

This folder now contains:
- `HomeControlSketch.ino` (main file - renamed from HomeControl.ino)
- `config.h`
- `relayControl.h`

## 🚀 How to Upload Now

### Step 1: Close Current Arduino IDE Window

### Step 2: Open the Sketch Correctly

**Method A - Double-click (Easiest)**:
1. Navigate to: `C:\Users\Ghosty\Desktop\HomeControl\HomeControlSketch\`
2. Double-click on `HomeControlSketch.ino`
3. Arduino IDE will open with all 3 files in tabs

**Method B - From Arduino IDE**:
1. Open Arduino IDE
2. File → Open
3. Navigate to `C:\Users\Ghosty\Desktop\HomeControl\HomeControlSketch\`
4. Select `HomeControlSketch.ino`
5. Click Open

### Step 3: Verify All Files Are Loaded

You should see **3 tabs** at the top:
- `HomeControlSketch` (main)
- `config.h`
- `relayControl.h`

### Step 4: Configure WiFi (IMPORTANT!)

Click on the `config.h` tab and edit:
```cpp
const char* WIFI_SSID = "YOUR_WIFI_NAME";      // ← Put your WiFi name here
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // ← Put your WiFi password here
```

**Save** the file (Ctrl+S)

### Step 5: Select Board & Port

- Tools → Board → ESP32 Arduino → **ESP32 Dev Module**
- Tools → Port → Select your ESP32's COM port (e.g., COM3, COM4)

### Step 6: Upload!

1. Click the **Upload** button (→ arrow)
2. If it says "Connecting....", **hold the BOOT button** on your ESP32
3. Wait for upload to complete
4. You should see "Hard resetting via RTS pin..."

## ✅ Success!

If upload completes without errors, you're done!

### Next Steps After Upload

1. Open Serial Monitor (Tools → Serial Monitor)
2. Set baud rate to **115200**
3. Press RESET button on ESP32
4. Copy the IP address shown
5. Open browser and navigate to that IP
6. Control your switches! 🎉

## Troubleshooting

### Still Getting Errors?

**"Sketch not found in correct directory"**:
- Make sure the folder is named `HomeControlSketch`
- Make sure the .ino file is also named `HomeControlSketch.ino`

**"config.h not found"**:
- Verify all 3 files are in the same `HomeControlSketch/` folder
- Close and reopen Arduino IDE

**Upload fails**:
- Hold BOOT button while uploading
- Check USB cable (use data cable, not charge-only)
- Try different USB port

### Original Files

Your original files are still safe in `firmware/` folder if you need them.

---

**You're all set!** Open `HomeControlSketch.ino` and upload! 🚀
