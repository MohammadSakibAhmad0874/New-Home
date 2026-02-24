/*
 * WiFi Manager Module
 * Handles WiFi provisioning with captive portal, credential storage,
 * and network scanning for no-code setup.
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <WiFi.h>
#include <DNSServer.h>
#include <Preferences.h>
#include "config.h"

// DNS server for captive portal
DNSServer dnsServer;
const byte DNS_PORT = 53;

// WiFi Manager Preferences (separate namespace from relay states)
Preferences wifiPrefs;

// State flags
bool portalActive = false;
bool wifiConnected = false;
String savedSSID = "";
String savedPassword = "";

// ==================== Forward Declarations ====================
void startAlwaysOnAP();
void startCaptivePortal();
void stopCaptivePortal();

// ==================== Credential Storage ====================

/*
 * Load saved WiFi credentials from flash memory
 * Returns true if credentials were found
 */
bool loadSavedWiFi() {
  wifiPrefs.begin("wifi-creds", true);  // read-only
  savedSSID = wifiPrefs.getString("ssid", "");
  savedPassword = wifiPrefs.getString("password", "");
  wifiPrefs.end();
  
  #if ENABLE_SERIAL_DEBUG
  if (savedSSID.length() > 0) {
    Serial.print("📶 Found saved WiFi: ");
    Serial.println(savedSSID);
  } else {
    Serial.println("📶 No saved WiFi credentials found");
  }
  #endif
  
  return savedSSID.length() > 0;
}

/*
 * Save WiFi credentials to flash memory
 */
void saveWiFiCredentials(String ssid, String password) {
  wifiPrefs.begin("wifi-creds", false);  // read-write
  wifiPrefs.putString("ssid", ssid);
  wifiPrefs.putString("password", password);
  wifiPrefs.end();
  
  savedSSID = ssid;
  savedPassword = password;
  
  #if ENABLE_SERIAL_DEBUG
  Serial.print("💾 WiFi credentials saved for: ");
  Serial.println(ssid);
  #endif
}

/*
 * Clear saved WiFi credentials (factory reset)
 */
void clearWiFiCredentials() {
  wifiPrefs.begin("wifi-creds", false);
  wifiPrefs.clear();
  wifiPrefs.end();
  
  savedSSID = "";
  savedPassword = "";
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("🗑️ WiFi credentials cleared");
  #endif
}

/*
 * Check if stored credentials exist
 */
bool hasStoredCredentials() {
  return savedSSID.length() > 0;
}

// ==================== WiFi Connection ====================

/*
 * Try connecting with saved credentials
 * Returns true if successfully connected
 */
bool tryConnectSavedWiFi() {
  if (!hasStoredCredentials()) return false;
  
  #if ENABLE_SERIAL_DEBUG
  Serial.print("📶 Connecting to: ");
  Serial.println(savedSSID);
  #endif
  
  // Use AP+STA dual mode: connect to WiFi AND create hotspot
  #if ENABLE_ALWAYS_ON_AP
  WiFi.mode(WIFI_AP_STA);
  #else
  WiFi.mode(WIFI_STA);
  #endif
  WiFi.begin(savedSSID.c_str(), savedPassword.c_str());
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startTime) < WIFI_TIMEOUT) {
    delay(500);
    #if ENABLE_SERIAL_DEBUG
    Serial.print(".");
    #endif
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    
    // Start the always-on hotspot
    #if ENABLE_ALWAYS_ON_AP
    startAlwaysOnAP();
    #endif
    
    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n✓ WiFi connected!");
    Serial.print("  WiFi IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("  Signal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    #if ENABLE_ALWAYS_ON_AP
    Serial.println("\n✓ Hotspot active!");
    Serial.print("  Hotspot WiFi: ");
    Serial.println(HOTSPOT_SSID);
    Serial.print("  Hotspot IP: ");
    Serial.println(WiFi.softAPIP());
    #endif
    #endif
    return true;
  }
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("\n✗ Connection failed");
  #endif
  return false;
}

// ==================== Captive Portal ====================

/*
 * Start captive portal (AP mode + DNS redirect)
 */
void startCaptivePortal() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  
  // Start DNS server — redirect ALL domains to our IP
  dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());
  portalActive = true;
  wifiConnected = false;
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("\n🌐 Captive Portal Started!");
  Serial.println("========================================");
  Serial.print("  Connect to WiFi: ");
  Serial.println(AP_SSID);
  Serial.print("  Password: ");
  Serial.println(AP_PASSWORD);
  Serial.print("  Open browser → ");
  Serial.println(WiFi.softAPIP());
  Serial.println("========================================\n");
  #endif
}

/*
 * Stop captive portal
 */
void stopCaptivePortal() {
  dnsServer.stop();
  portalActive = false;
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("🌐 Captive portal stopped");
  #endif
}

/*
 * Start always-on hotspot (AP+STA dual mode)
 * Creates a WiFi network that any device can connect to
 * Access dashboard at 192.168.4.1
 */
void startAlwaysOnAP() {
  #if ENABLE_ALWAYS_ON_AP
  WiFi.softAP(HOTSPOT_SSID, HOTSPOT_PASSWORD);
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("\n📡 Always-On Hotspot Started!");
  Serial.println("========================================");
  Serial.print("  Hotspot WiFi: ");
  Serial.println(HOTSPOT_SSID);
  Serial.print("  Password: ");
  Serial.println(HOTSPOT_PASSWORD);
  Serial.print("  Open browser → http://");
  Serial.println(WiFi.softAPIP());
  Serial.println("  ↑ Works from ANY phone/laptop/tablet!");
  Serial.println("========================================");
  #endif
  #endif
}

/*
 * Process DNS requests (call in loop)
 */
void handlePortalDNS() {
  if (portalActive) {
    dnsServer.processNextRequest();
  }
}

// ==================== Network Scanning ====================

/*
 * Scan for nearby WiFi networks
 * Returns JSON array of networks
 */
String scanNetworksJSON() {
  #if ENABLE_SERIAL_DEBUG
  Serial.println("📡 Scanning for WiFi networks...");
  #endif
  
  int n = WiFi.scanNetworks();
  
  String json = "[";
  for (int i = 0; i < n; i++) {
    if (i > 0) json += ",";
    json += "{\"ssid\":\"" + WiFi.SSID(i) + "\",";
    json += "\"rssi\":" + String(WiFi.RSSI(i)) + ",";
    json += "\"secure\":" + String(WiFi.encryptionType(i) != WIFI_AUTH_OPEN ? "true" : "false") + "}";
  }
  json += "]";
  
  WiFi.scanDelete();
  
  #if ENABLE_SERIAL_DEBUG
  Serial.print("📡 Found ");
  Serial.print(n);
  Serial.println(" networks");
  #endif
  
  return json;
}

// ==================== Setup Wizard HTML ====================

/*
 * Returns the captive portal setup wizard HTML
 */
String getSetupPageHTML() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartHome Setup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            color: #f1f5f9;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .setup-container {
            max-width: 420px;
            width: 100%;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.5);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo .icon {
            font-size: 3.5em;
            margin-bottom: 10px;
        }
        
        .logo h1 {
            font-size: 1.8em;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .logo p {
            color: #94a3b8;
            margin-top: 8px;
            font-size: 0.95em;
        }
        
        .step-indicator {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 30px;
        }
        
        .step-dot {
            width: 10px; height: 10px;
            border-radius: 50%;
            background: rgba(255,255,255,0.15);
            transition: all 0.3s;
        }
        
        .step-dot.active {
            background: #3b82f6;
            box-shadow: 0 0 10px rgba(59,130,246,0.5);
        }
        
        .step-dot.done {
            background: #22c55e;
        }
        
        .step { display: none; }
        .step.active { display: block; animation: fadeIn 0.4s ease; }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .network-list {
            max-height: 280px;
            overflow-y: auto;
            margin: 15px 0;
            border-radius: 12px;
        }
        
        .network-list::-webkit-scrollbar { width: 4px; }
        .network-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
        
        .network-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .network-item:hover {
            background: rgba(59,130,246,0.15);
            border-color: rgba(59,130,246,0.3);
            transform: translateX(4px);
        }
        
        .network-item.selected {
            background: rgba(59,130,246,0.2);
            border-color: #3b82f6;
        }
        
        .network-name {
            font-weight: 600;
            font-size: 1em;
        }
        
        .network-signal {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #94a3b8;
            font-size: 0.85em;
        }
        
        .signal-bars {
            display: flex;
            align-items: flex-end;
            gap: 2px;
            height: 14px;
        }
        
        .signal-bar {
            width: 3px;
            background: rgba(255,255,255,0.2);
            border-radius: 2px;
        }
        
        .signal-bar.active { background: #22c55e; }
        
        input[type="password"], input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 12px;
            color: #f1f5f9;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s;
            margin: 8px 0;
        }
        
        input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 1.05em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 15px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: white;
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59,130,246,0.4);
        }
        
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.08);
            color: #94a3b8;
            margin-top: 10px;
        }
        
        .btn-secondary:hover { background: rgba(255,255,255,0.12); }
        
        .show-password {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #94a3b8;
            font-size: 0.9em;
            margin: 8px 0;
            cursor: pointer;
        }
        
        .show-password input { width: auto; margin: 0; }
        
        .connecting {
            text-align: center;
            padding: 30px 0;
        }
        
        .spinner {
            width: 50px; height: 50px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .success-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        
        .scan-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border: 1px dashed rgba(255,255,255,0.15);
            border-radius: 12px;
            color: #94a3b8;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 10px;
        }
        
        .scan-btn:hover { background: rgba(255,255,255,0.08); color: #f1f5f9; }
        
        .label { color: #94a3b8; font-size: 0.9em; margin-bottom: 4px; margin-top: 15px; }
        
        .error-msg {
            background: rgba(239,68,68,0.15);
            border: 1px solid rgba(239,68,68,0.3);
            color: #fca5a5;
            padding: 12px;
            border-radius: 10px;
            font-size: 0.9em;
            margin: 10px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="setup-container">
        <div class="logo">
            <div class="icon">🏠</div>
            <h1>SmartHome Setup</h1>
            <p>Let's connect your smart home to WiFi</p>
        </div>
        
        <div class="step-indicator">
            <div class="step-dot active" id="dot1"></div>
            <div class="step-dot" id="dot2"></div>
            <div class="step-dot" id="dot3"></div>
        </div>
        
        <!-- Step 1: Select Network -->
        <div class="step active" id="step1">
            <div class="scan-btn" onclick="scanNetworks()">
                🔄 Scan for Networks
            </div>
            <div class="network-list" id="networkList">
                <div style="text-align:center;color:#64748b;padding:30px;">
                    Tap "Scan" to find WiFi networks...
                </div>
            </div>
            <button class="btn btn-primary" id="nextBtn" onclick="goToStep(2)" disabled>
                Next →
            </button>
        </div>
        
        <!-- Step 2: Enter Password -->
        <div class="step" id="step2">
            <p class="label">Selected Network</p>
            <div style="padding:12px;background:rgba(59,130,246,0.1);border-radius:10px;margin-bottom:5px;">
                <strong id="selectedName">—</strong>
            </div>
            
            <p class="label">WiFi Password</p>
            <input type="password" id="wifiPass" placeholder="Enter WiFi password" autocomplete="off">
            <label class="show-password">
                <input type="checkbox" onchange="togglePasswordVisibility()">
                Show password
            </label>
            
            <div class="error-msg" id="errorMsg"></div>
            
            <button class="btn btn-primary" onclick="connectWiFi()">
                🔗 Connect
            </button>
            <button class="btn btn-secondary" onclick="goToStep(1)">
                ← Back
            </button>
        </div>
        
        <!-- Step 3: Connecting / Success -->
        <div class="step" id="step3">
            <div class="connecting" id="connectingView">
                <div class="spinner"></div>
                <h3>Connecting...</h3>
                <p style="color:#94a3b8;margin-top:8px;">Please wait while we connect to your WiFi</p>
            </div>
            <div class="connecting" id="successView" style="display:none;">
                <div class="success-icon">✅</div>
                <h3 style="color:#22c55e;">Connected!</h3>
                <p style="color:#94a3b8;margin-top:8px;">Access your dashboard from <strong>any device</strong>:</p>
                <p style="font-size:1.2em;font-weight:700;color:#60a5fa;margin:10px 0;" id="hostnameInfo"></p>
                <p style="color:#64748b;font-size:0.85em;" id="newIP"></p>
                <button class="btn btn-primary" id="openDashboard" style="display:none;" onclick="goToDashboard()">
                    Open Dashboard →
                </button>
            </div>
            <div class="connecting" id="failView" style="display:none;">
                <div class="success-icon">❌</div>
                <h3 style="color:#ef4444;">Connection Failed</h3>
                <p style="color:#94a3b8;margin-top:8px;">Wrong password or network unavailable</p>
                <button class="btn btn-primary" onclick="goToStep(2)">
                    Try Again
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let selectedSSID = '';
        let dashboardIP = '';
        let dashboardHostname = '';
        
        function scanNetworks() {
            document.getElementById('networkList').innerHTML = 
                '<div style="text-align:center;color:#94a3b8;padding:30px;"><div class="spinner" style="width:30px;height:30px;margin-bottom:10px;"></div>Scanning...</div>';
            
            fetch('/api/scan')
                .then(r => r.json())
                .then(networks => {
                    let html = '';
                    if (networks.length === 0) {
                        html = '<div style="text-align:center;color:#64748b;padding:20px;">No networks found. Try again.</div>';
                    }
                    // Remove duplicates and sort by signal strength
                    let seen = {};
                    networks.sort((a,b) => b.rssi - a.rssi);
                    networks.forEach(net => {
                        if (seen[net.ssid] || net.ssid === '') return;
                        seen[net.ssid] = true;
                        let bars = getSignalBars(net.rssi);
                        html += '<div class="network-item" onclick="selectNetwork(this, \'' + escapeHTML(net.ssid) + '\')">' +
                            '<span class="network-name">' + (net.secure ? '🔒 ' : '🔓 ') + escapeHTML(net.ssid) + '</span>' +
                            '<span class="network-signal">' + bars + '</span></div>';
                    });
                    document.getElementById('networkList').innerHTML = html;
                })
                .catch(() => {
                    document.getElementById('networkList').innerHTML = 
                        '<div style="text-align:center;color:#fca5a5;padding:20px;">Scan failed. Please try again.</div>';
                });
        }
        
        function getSignalBars(rssi) {
            let strength = rssi > -50 ? 4 : rssi > -60 ? 3 : rssi > -70 ? 2 : 1;
            let html = '<div class="signal-bars">';
            for (let i = 1; i <= 4; i++) {
                html += '<div class="signal-bar' + (i <= strength ? ' active' : '') + '" style="height:' + (i*3+2) + 'px"></div>';
            }
            return html + '</div>';
        }
        
        function escapeHTML(str) {
            return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
        }
        
        function selectNetwork(el, ssid) {
            document.querySelectorAll('.network-item').forEach(i => i.classList.remove('selected'));
            el.classList.add('selected');
            selectedSSID = ssid;
            document.getElementById('nextBtn').disabled = false;
        }
        
        function goToStep(step) {
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            document.getElementById('step' + step).classList.add('active');
            
            for (let i = 1; i <= 3; i++) {
                let dot = document.getElementById('dot' + i);
                dot.classList.remove('active', 'done');
                if (i < step) dot.classList.add('done');
                if (i === step) dot.classList.add('active');
            }
            
            if (step === 2) {
                document.getElementById('selectedName').textContent = selectedSSID;
                document.getElementById('wifiPass').value = '';
                document.getElementById('errorMsg').style.display = 'none';
            }
        }
        
        function togglePasswordVisibility() {
            let input = document.getElementById('wifiPass');
            input.type = input.type === 'password' ? 'text' : 'password';
        }
        
        function connectWiFi() {
            let password = document.getElementById('wifiPass').value;
            
            goToStep(3);
            document.getElementById('connectingView').style.display = 'block';
            document.getElementById('successView').style.display = 'none';
            document.getElementById('failView').style.display = 'none';
            
            fetch('/api/wifi/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'ssid=' + encodeURIComponent(selectedSSID) + '&password=' + encodeURIComponent(password)
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('connectingView').style.display = 'none';
                if (data.success) {
                    document.getElementById('successView').style.display = 'block';
                    dashboardIP = data.ip;
                    dashboardHostname = data.hostname || '';
                    if (dashboardHostname) {
                        document.getElementById('hostnameInfo').textContent = dashboardHostname;
                        document.getElementById('newIP').textContent = 'or use IP: ' + data.ip;
                    } else {
                        document.getElementById('hostnameInfo').textContent = data.ip;
                        document.getElementById('newIP').textContent = '';
                    }
                    document.getElementById('openDashboard').style.display = 'block';
                    // Auto-redirect after 5 seconds
                    setTimeout(() => { goToDashboard(); }, 5000);
                } else {
                    document.getElementById('failView').style.display = 'block';
                }
            })
            .catch(() => {
                document.getElementById('connectingView').style.display = 'none';
                document.getElementById('failView').style.display = 'block';
            });
        }
        
        function goToDashboard() {
            if (dashboardHostname) {
                window.location.href = 'http://' + dashboardHostname;
            } else if (dashboardIP) {
                window.location.href = 'http://' + dashboardIP;
            }
        }
        
        // Auto-scan on page load
        window.addEventListener('load', () => {
            setTimeout(scanNetworks, 500);
        });
    </script>
</body>
</html>
)rawliteral";
  return html;
}

// ==================== Settings Page HTML ====================

/*
 * Returns the settings page HTML
 */
String getSettingsPageHTML() {
  String currentNetwork = wifiConnected ? savedSSID : "Not connected";
  String currentIP = wifiConnected ? WiFi.localIP().toString() : "—";
  String signalStr = wifiConnected ? String(WiFi.RSSI()) + " dBm" : "—";
  
  String html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartHome Settings</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        
        .container { max-width: 500px; width: 100%; }
        
        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 0.95em;
            margin-bottom: 20px;
            transition: color 0.2s;
        }
        
        .back-link:hover { color: #f1f5f9; }
        
        h1 {
            font-size: 2em;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        
        .info-row:last-child { border-bottom: none; }
        
        .info-label { color: #94a3b8; font-size: 0.9em; }
        .info-value { font-weight: 600; font-size: 0.95em; }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .status-badge.connected {
            background: rgba(34,197,94,0.15);
            color: #22c55e;
        }
        
        .status-badge.disconnected {
            background: rgba(239,68,68,0.15);
            color: #ef4444;
        }
        
        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        .btn-change {
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: white;
            box-shadow: 0 4px 15px rgba(59,130,246,0.3);
        }
        
        .btn-change:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59,130,246,0.4);
        }
        
        .btn-danger {
            background: rgba(239,68,68,0.15);
            color: #ef4444;
            border: 1px solid rgba(239,68,68,0.3);
        }
        
        .btn-danger:hover {
            background: rgba(239,68,68,0.25);
        }
        
        .confirm-dialog {
            display: none;
            background: rgba(0,0,0,0.5);
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: 100;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .confirm-box {
            background: #1e293b;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 30px;
            max-width: 360px;
            width: 100%;
            text-align: center;
        }
        
        .confirm-box h3 { margin-bottom: 10px; }
        .confirm-box p { color: #94a3b8; margin-bottom: 20px; font-size: 0.95em; }
        
        .confirm-actions { display: flex; gap: 10px; }
        .confirm-actions .btn { margin-top: 0; }
        
        .btn-cancel {
            background: rgba(255,255,255,0.08);
            color: #94a3b8;
        }
        
        .device-info { color: #64748b; font-size: 0.85em; text-align: center; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Dashboard</a>
        <h1>⚙️ Settings</h1>
        
        <div class="card">
            <div class="card-title">📶 WiFi Connection</div>
            <div class="info-row">
                <span class="info-label">Status</span>
                <span class="status-badge )rawliteral" + String(wifiConnected ? "connected" : "disconnected") + R"rawliteral(">
                    )rawliteral" + String(wifiConnected ? "● Connected" : "● Disconnected") + R"rawliteral(
                </span>
            </div>
            <div class="info-row">
                <span class="info-label">Network</span>
                <span class="info-value">)rawliteral" + currentNetwork + R"rawliteral(</span>
            </div>
            <div class="info-row">
                <span class="info-label">IP Address</span>
                <span class="info-value">)rawliteral" + currentIP + R"rawliteral(</span>
            </div>
            <div class="info-row">
                <span class="info-label">Hostname</span>
                <span class="info-value">)rawliteral" + String(MDNS_HOSTNAME) + R"rawliteral(.local</span>
            </div>
            <div class="info-row">
                <span class="info-label">Signal Strength</span>
                <span class="info-value">)rawliteral" + signalStr + R"rawliteral(</span>
            </div>
        </div>
        
        <div class="card" style="background:rgba(59,130,246,0.08);border-color:rgba(59,130,246,0.25);">
            <div class="card-title">� Access from Any Device</div>
            <p style="color:#94a3b8;font-size:0.9em;margin-bottom:12px;">Any phone, laptop, or tablet on the same WiFi can control your smart home:</p>
            <div style="text-align:center;padding:15px;background:rgba(0,0,0,0.2);border-radius:12px;margin-bottom:10px;">
                <p style="font-size:1.3em;font-weight:700;color:#60a5fa;">http://)rawliteral" + String(MDNS_HOSTNAME) + R"rawliteral(.local</p>
                <p style="color:#64748b;font-size:0.85em;margin-top:6px;">or use IP: )rawliteral" + currentIP + R"rawliteral(</p>
            </div>
            <p style="color:#64748b;font-size:0.8em;">💡 Just type this URL in any browser on a device connected to the same WiFi network.</p>
        </div>
        
        <div class="card">
            <div class="card-title">�🔧 WiFi Management</div>
            <button class="btn btn-change" onclick="window.location.href='/setup'">
                📡 Change WiFi Network
            </button>
            <button class="btn btn-danger" onclick="showResetConfirm()">
                🗑️ Factory Reset WiFi
            </button>
        </div>
        
        <div class="card">
            <div class="card-title">📱 Device Info</div>
            <div class="info-row">
                <span class="info-label">Device Name</span>
                <span class="info-value">)rawliteral" + String(DEVICE_NAME) + R"rawliteral(</span>
            </div>
            <div class="info-row">
                <span class="info-label">Firmware</span>
                <span class="info-value">v1.2</span>
            </div>
            <div class="info-row">
                <span class="info-label">Free Memory</span>
                <span class="info-value" id="freeHeap">—</span>
            </div>
            <div class="info-row">
                <span class="info-label">Uptime</span>
                <span class="info-value" id="uptime">—</span>
            </div>
        </div>
        
        <div class="device-info">
            Smart Home Automation System v1.2
        </div>
    </div>
    
    <!-- Reset Confirmation Dialog -->
    <div class="confirm-dialog" id="resetDialog">
        <div class="confirm-box">
            <h3>⚠️ Factory Reset</h3>
            <p>This will erase saved WiFi credentials. The device will restart in setup mode. Are you sure?</p>
            <div class="confirm-actions">
                <button class="btn btn-cancel" onclick="hideResetConfirm()">Cancel</button>
                <button class="btn btn-danger" onclick="doReset()">Reset</button>
            </div>
        </div>
    </div>
    
    <script>
        function showResetConfirm() {
            document.getElementById('resetDialog').style.display = 'flex';
        }
        
        function hideResetConfirm() {
            document.getElementById('resetDialog').style.display = 'none';
        }
        
        function doReset() {
            fetch('/api/wifi/reset', { method: 'POST' })
                .then(() => {
                    alert('WiFi credentials cleared! Device is restarting in setup mode...');
                    setTimeout(() => { window.close(); }, 2000);
                });
        }
        
        // Load system info
        function loadSystemInfo() {
            fetch('/api/system')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('freeHeap').textContent = Math.round(data.freeHeap / 1024) + ' KB';
                    let secs = Math.floor(data.uptime / 1000);
                    let hrs = Math.floor(secs / 3600);
                    let mins = Math.floor((secs % 3600) / 60);
                    document.getElementById('uptime').textContent = hrs + 'h ' + mins + 'm';
                })
                .catch(() => {});
        }
        
        loadSystemInfo();
        setInterval(loadSystemInfo, 10000);
    </script>
</body>
</html>
)rawliteral";
  return html;
}

#endif
