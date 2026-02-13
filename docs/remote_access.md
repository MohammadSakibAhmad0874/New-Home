# Remote Access Guide

This guide explains how to control your smart home from **anywhere in the world** using remote access.

> [!WARNING]
> Remote access involves exposing your ESP32 to the internet. Follow security best practices and understand the risks before proceeding.

## Overview

By default, your system only works on your local WiFi network. To control it from outside your home, you have **3 options**:

| Method | Difficulty | Cost | Security | Best For |
|--------|-----------|------|----------|----------|
| **Option 1**: Port Forwarding | Medium | Free | ⚠️ Manual | Tech-savvy users |
| **Option 2**: Ngrok/Cloudflare Tunnel | Easy | Free | ✅ Good | Beginners |
| **Option 3**: Cloud Service (Firebase/AWS) | Hard | Paid | ✅ Best | Production systems |

**Recommended**: **Option 2 (Ngrok)** for ease and security.

---

## Option 1: Port Forwarding + DDNS (Free, Medium Difficulty)

This method exposes your home WiFi router to the internet.

### Requirements
- Access to your WiFi router settings
- Dynamic DNS service (free)
- Understanding of network security

### Step 1: Set Static IP for ESP32

**Using Router DHCP Reservation:**

1. Find ESP32's MAC address from Serial Monitor or router admin page
2. Log into your router (usually 192.168.1.1 or 192.168.0.1)
3. Go to DHCP settings → DHCP Reservation
4. Add reservation: MAC address → IP (e.g., 192.168.1.100)
5. Reboot ESP32 to get static IP

### Step 2: Setup Port Forwarding

1. Log into router admin panel
2. Find **Port Forwarding** or **Virtual Server** section
3. Create new rule:
   - **Service Name**: SmartHome
   - **External Port**: 8080 (or any port > 1024)
   - **Internal IP**: 192.168.1.100 (ESP32's static IP)
   - **Internal Port**: 80
   - **Protocol**: TCP
4. Save and enable the rule

### Step 3: Setup Dynamic DNS (DDNS)

Your home IP address changes periodically. DDNS gives you a permanent domain name.

**Using No-IP (Free):**

1. Create account at: https://www.noip.com/
2. Create a hostname (e.g., `myhome.ddns.net`)
3. Install No-IP DUC (Dynamic Update Client) on your computer OR configure DDNS in router
4. Enter your No-IP credentials

**Using Router Built-in DDNS:**
- Many routers support DynDNS, No-IP, or custom DDNS
- Check router's DDNS settings and follow instructions

### Step 4: Access Remotely

From anywhere in the world, open browser and go to:
```
http://myhome.ddns.net:8080
```

### Security Improvements

> [!CAUTION]
> Port forwarding exposes your system to the internet. Add security:

**1. Add Basic Authentication** (recommended):

Edit `HomeControl.ino`, add at the top of `handleRoot()`:

```cpp
void handleRoot() {
  if (!server.authenticate("admin", "yourpassword123")) {
    return server.requestAuthentication();
  }
  // ... rest of function
}
```

**2. Change Default Port**: Use non-standard port (e.g., 8443 instead of 8080)

**3. Enable HTTPS**: Requires SSL certificate (advanced)

**4. Use VPN**: Instead of port forwarding, use VPN to access home network

---

## Option 2: Ngrok Tunnel (Easy, Recommended)

Ngrok creates a secure tunnel without port forwarding.

### Advantages
✅ No router configuration needed
✅ Built-in HTTPS
✅ Works behind corporate firewalls
✅ Free tier available

### Step 1: Install Ngrok on Your Computer

**Windows:**
1. Download from: https://ngrok.com/download
2. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok`)
3. Open Command Prompt in that folder

**Mac/Linux:**
```bash
brew install ngrok  # Mac with Homebrew
# or
sudo snap install ngrok  # Linux
```

### Step 2: Create Ngrok Account (Free)

1. Sign up at: https://dashboard.ngrok.com/signup
2. Copy your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure ngrok:
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
   ```

### Step 3: Find ESP32's Local IP

Check Serial Monitor or router admin page (e.g., `192.168.1.150`)

### Step 4: Start Ngrok Tunnel

In terminal/command prompt:
```bash
ngrok http 192.168.1.150:80
```

You'll see output like:
```
Forwarding   https://abc123.ngrok-free.app -> http://192.168.1.150:80
```

### Step 5: Access Remotely

Copy the `https://abc123.ngrok-free.app` URL and access from **anywhere**!

> [!TIP]
> **Keep Ngrok Running**: The tunnel only works while ngrok is running on your computer. If you close it, the URL becomes invalid.

### Run Ngrok Automatically (Windows)

Create a batch file `start_ngrok.bat`:
```batch
@echo off
cd C:\ngrok
ngrok http 192.168.1.150:80
```

Add to Windows Startup folder to run automatically.

### Permanent Ngrok URL (Paid)

Free tier gives random URLs that change. Paid plans ($8/month) provide custom domains:
```
https://myhome.ngrok.app
```

---

## Option 3: Cloudflare Tunnel (Free Alternative to Ngrok)

Similar to Ngrok but completely free with permanent URLs.

### Step 1: Install Cloudflared

**Windows:**
Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

**Mac/Linux:**
```bash
brew install cloudflare/cloudflare/cloudflared  # Mac
# or
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64  # Linux
```

### Step 2: Authenticate

```bash
cloudflared tunnel login
```

### Step 3: Create Tunnel

```bash
cloudflared tunnel create smarthome
```

### Step 4: Route Traffic

Find your ESP32's IP (e.g., 192.168.1.150):

```bash
cloudflared tunnel route dns smarthome myhome.yourdomain.com
```

### Step 5: Run Tunnel

```bash
cloudflared tunnel run --url http://192.168.1.150:80 smarthome
```

Access via: `https://myhome.yourdomain.com`

---

## Option 4: Cloud Backend (Production-Grade)

For serious **commercial/production** use, integrate with cloud services:

### Firebase Real-time Database

1. ESP32 sends relay states to Firebase
2. Mobile app reads/writes to Firebase
3. ESP32 listens for changes

**Pros**: Scalable, secure, mobile-friendly
**Cons**: Complex setup, requires coding

### AWS IoT Core

Enterprise-grade IoT platform with:
- MQTT messaging
- Device shadows
- Security certificates

**Pros**: Enterprise security, unlimited scaling
**Cons**: More expensive, steep learning curve

### Blynk (Commercial Platform)

- Pre-built dashboard
- Mobile app included
- Cloud hosting

**Pros**: Easy integration
**Cons**: Subscription required ($5-15/month)

---

## Security Best Practices

> [!IMPORTANT]
> Regardless of which method you choose:

1. **Add Authentication**: Use username/password
2. **Use HTTPS**: Encrypt communication (Ngrok/Cloudflare provide this)
3. **Change Default Passwords**: Update AP_PASSWORD in config.h
4. **Regular Updates**: Keep ESP32 firmware updated
5. **Monitor Access Logs**: Check who's accessing your system
6. **Use Strong WiFi Password**: Secure your home network
7. **Firewall Rules**: Limit access to specific IPs if possible

---

## Which Method Should You Use?

**Choose Ngrok if:**
- ✅ You want quick setup
- ✅ You don't want to configure router
- ✅ You're okay with running software on your computer
- ✅ You need HTTPS

**Choose Port Forwarding if:**
- ✅ You want complete control
- ✅ You have tech experience
- ✅ You can secure it properly
- ✅ You want no external dependencies

**Choose Cloudflare Tunnel if:**
- ✅ You want free permanent URLs
- ✅ You need HTTPS
- ✅ You want better performance than Ngrok free tier

**Choose Cloud Backend if:**
- ✅ Building a commercial product
- ✅ Need enterprise security
- ✅ Want mobile app integration
- ✅ Have budget and technical skills

---

## Testing Remote Access

1. **Disconnect from home WiFi**: Use mobile data
2. **Access your URL**: Test the control panel
3. **Toggle switches**: Verify relay responds
4. **Check latency**: Should be under 2 seconds

---

## Troubleshooting

### Port Forwarding Not Working

- Verify router port forwarding rule is enabled
- Check firewall isn't blocking the port
- Test locally first: `http://router-public-ip:8080`
- Some ISPs block port forwarding (use Ngrok instead)

### Ngrok Tunnel Disconnects

- Free tier has session limits
- Upgrade to paid plan for stability
- Use Cloudflare Tunnel as free alternative

### Slow Response Times

- Check internet upload speed
- ESP32 WiFi signal strength
- Choose geographically closer tunnel server

---

Next: [Voice Control Integration](voice_integration.md) 🎤
