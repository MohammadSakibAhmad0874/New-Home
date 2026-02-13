/*
 * Smart Home Automation System v1.2
 * ESP32-based WiFi controlled relay switch
 * 
 * Features:
 * - WiFi Setup Wizard (Captive Portal)
 * - No-code WiFi configuration
 * - mDNS: Access via http://smarthome.local from any device
 * - 4 relay control
 * - State persistence
 * - Remote access ready
 * - REST API
 * - Modern web interface
 * - Settings page
 */

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include "config.h"
#include "relayControl.h"
#include "wifiManager.h"

#if ENABLE_MDNS
#include <ESPmDNS.h>
#endif

#include "firebaseSync.h"

WebServer server(WEB_SERVER_PORT);

// Track connection state
bool useAccessPoint = false;

// ==================== mDNS Setup ====================

/*
 * Start mDNS so the device is accessible via http://smarthome.local
 * from any device on the same WiFi network
 */
void startMDNS() {
  #if ENABLE_MDNS
  if (MDNS.begin(MDNS_HOSTNAME)) {
    // Advertise the HTTP service so devices can discover it
    MDNS.addService("http", "tcp", WEB_SERVER_PORT);
    
    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n✓ mDNS started!");
    Serial.print("  Access from ANY device: http://");
    Serial.print(MDNS_HOSTNAME);
    Serial.println(".local");
    #endif
  } else {
    #if ENABLE_SERIAL_DEBUG
    Serial.println("⚠ mDNS failed to start");
    #endif
  }
  #endif
}

/*
 * Setup Function - Runs once at startup
 */
void setup() {
  // Initialize serial communication
  #if ENABLE_SERIAL_DEBUG
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n========================================");
  Serial.println("  Smart Home Automation System v1.2");
  Serial.println("========================================\n");
  #endif
  
  // Initialize relay control
  initRelays();
  
  // WiFi Setup with captive portal
  #if ENABLE_CAPTIVE_PORTAL
  setupWiFiWithPortal();
  #else
  // Fallback: start AP directly
  startCaptivePortal();
  useAccessPoint = true;
  #endif
  
  // Start mDNS for device discovery (only when connected to WiFi)
  if (!portalActive && wifiConnected) {
    startMDNS();
    // Start Firebase cloud sync
    initFirebaseSync();
  }
  
  // Setup web server routes
  setupWebServer();
  
  // Start web server
  server.begin();
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("\n✓ Web server started!");
  Serial.println("========================================");
  if (portalActive) {
    Serial.println("📱 Setup Mode Active!");
    Serial.print("  Connect to WiFi: ");
    Serial.println(AP_SSID);
    Serial.print("  Then open: ");
    Serial.println(WiFi.softAPIP());
  } else {
    Serial.print("  WiFi IP: ");
    Serial.println(WiFi.localIP());
    #if ENABLE_MDNS
    Serial.print("  Dashboard URL: http://");
    Serial.print(MDNS_HOSTNAME);
    Serial.println(".local");
    #endif
    #if ENABLE_ALWAYS_ON_AP
    Serial.println("\n  📡 Always-On Hotspot:");
    Serial.print("  Connect to WiFi: ");
    Serial.println(HOTSPOT_SSID);
    Serial.print("  Then open: http://");
    Serial.println(WiFi.softAPIP());
    #endif
    Serial.println("  ↑ Open this on ANY phone/laptop/tablet!");
  }
  Serial.println("========================================\n");
  #endif
}

/*
 * Main Loop - Runs continuously
 */
void loop() {
  // Handle web server requests
  server.handleClient();
  
  // Handle DNS for captive portal
  handlePortalDNS();
  
  // Firebase cloud sync (poll for remote commands)
  cloudSyncLoop();
  
  // Check WiFi connection (reconnect if lost)
  if (!portalActive && wifiConnected && WiFi.status() != WL_CONNECTED) {
    #if ENABLE_SERIAL_DEBUG
    Serial.println("⚠ WiFi connection lost. Reconnecting...");
    #endif
    wifiConnected = false;
    if (!tryConnectSavedWiFi()) {
      #if ENABLE_SERIAL_DEBUG
      Serial.println("⚠ Reconnect failed. Starting setup portal...");
      #endif
      startCaptivePortal();
    }
  }
}

// ==================== WiFi Setup ====================

/*
 * Smart WiFi setup: check saved credentials → connect or start portal
 */
void setupWiFiWithPortal() {
  // Try to load saved WiFi credentials from flash
  if (loadSavedWiFi()) {
    // Credentials found — try connecting
    if (tryConnectSavedWiFi()) {
      // Success! Dashboard mode
      useAccessPoint = false;
      return;
    }
    #if ENABLE_SERIAL_DEBUG
    Serial.println("⚠ Saved WiFi failed. Starting setup wizard...");
    #endif
  }
  
  // No credentials or connection failed — start captive portal
  startCaptivePortal();
  useAccessPoint = true;
}

/*
 * Setup Web Server Routes
 */
void setupWebServer() {
  // Main page - dashboard or setup wizard depending on state
  server.on("/", HTTP_GET, handleRoot);
  
  // Setup wizard page
  server.on("/setup", HTTP_GET, handleSetupPage);
  
  // Settings page
  server.on("/settings", HTTP_GET, handleSettingsPage);
  
  // WiFi API endpoints
  server.on("/api/scan", HTTP_GET, handleScanNetworks);
  server.on("/api/wifi/save", HTTP_POST, handleSaveWiFi);
  server.on("/api/wifi/reset", HTTP_POST, handleResetWiFi);
  server.on("/api/system", HTTP_GET, handleSystemInfo);
  
  // Relay control endpoints (toggle + cloud notify)
  server.on("/r1", HTTP_GET, []() { toggleRelay(0); notifyCloudStateChange(0, relayStates[0]); handleRoot(); });
  server.on("/r2", HTTP_GET, []() { toggleRelay(1); notifyCloudStateChange(1, relayStates[1]); handleRoot(); });
  server.on("/r3", HTTP_GET, []() { toggleRelay(2); notifyCloudStateChange(2, relayStates[2]); handleRoot(); });
  server.on("/r4", HTTP_GET, []() { toggleRelay(3); notifyCloudStateChange(3, relayStates[3]); handleRoot(); });
  
  // API endpoints for programmatic access
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/relay1/on", HTTP_GET, []() { setRelay(0, true); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay1/off", HTTP_GET, []() { setRelay(0, false); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay2/on", HTTP_GET, []() { setRelay(1, true); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay2/off", HTTP_GET, []() { setRelay(1, false); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay3/on", HTTP_GET, []() { setRelay(2, true); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay3/off", HTTP_GET, []() { setRelay(2, false); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay4/on", HTTP_GET, []() { setRelay(3, true); server.send(200, "application/json", getRelayStatesJSON()); });
  server.on("/api/relay4/off", HTTP_GET, []() { setRelay(3, false); server.send(200, "application/json", getRelayStatesJSON()); });
  
  // All OFF safety endpoint
  server.on("/api/alloff", HTTP_GET, []() { 
    allRelaysOff(); 
    server.send(200, "application/json", getRelayStatesJSON()); 
  });
  
  // Captive portal catch-all (redirect all requests to setup page)
  server.onNotFound(handleCaptiveOrNotFound);
}

// ==================== Route Handlers ====================

/*
 * Root page: show setup wizard if in portal mode, dashboard otherwise
 */
void handleRoot() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  
  if (portalActive) {
    // In setup mode — show the setup wizard
    server.send(200, "text/html", getSetupPageHTML());
  } else {
    // Normal mode — show the dashboard
    String html = getWebInterface();
    server.send(200, "text/html", html);
  }
}

/*
 * Setup wizard page (accessible anytime via /setup)
 */
void handleSetupPage() {
  server.send(200, "text/html", getSetupPageHTML());
}

/*
 * Settings page
 */
void handleSettingsPage() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  server.send(200, "text/html", getSettingsPageHTML());
}

/*
 * Scan for WiFi networks
 */
void handleScanNetworks() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  server.send(200, "application/json", scanNetworksJSON());
}

/*
 * Save WiFi credentials and attempt connection
 */
void handleSaveWiFi() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  
  String ssid = server.arg("ssid");
  String password = server.arg("password");
  
  if (ssid.length() == 0) {
    server.send(400, "application/json", "{\"success\":false,\"error\":\"SSID required\"}");
    return;
  }
  
  #if ENABLE_SERIAL_DEBUG
  Serial.print("📶 Attempting connection to: ");
  Serial.println(ssid);
  #endif
  
  // Save the credentials
  saveWiFiCredentials(ssid, password);
  
  // Stop captive portal and try connecting
  stopCaptivePortal();
  #if ENABLE_ALWAYS_ON_AP
  WiFi.mode(WIFI_AP_STA);
  #else
  WiFi.mode(WIFI_STA);
  #endif
  WiFi.begin(ssid.c_str(), password.c_str());
  
  // Wait for connection
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startTime) < WIFI_TIMEOUT) {
    delay(500);
    #if ENABLE_SERIAL_DEBUG
    Serial.print(".");
    #endif
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    useAccessPoint = false;
    String ip = WiFi.localIP().toString();
    String hostname = String(MDNS_HOSTNAME) + ".local";
    
    // Start the always-on hotspot
    #if ENABLE_ALWAYS_ON_AP
    startAlwaysOnAP();
    String hotspotIP = WiFi.softAPIP().toString();
    #endif
    
    // Start mDNS for device discovery
    startMDNS();
    
    // Start Firebase cloud sync
    initFirebaseSync();
    
    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n✓ Connected! WiFi IP: " + ip);
    Serial.println("  URL: http://" + hostname);
    #if ENABLE_ALWAYS_ON_AP
    Serial.println("  Hotspot WiFi: " + String(HOTSPOT_SSID));
    Serial.println("  Hotspot IP: " + hotspotIP);
    #endif
    #endif
    
    // Send success response with IP, hostname, and hotspot info
    String response = "{\"success\":true,\"ip\":\"" + ip + "\",\"hostname\":\"" + hostname + "\"";
    #if ENABLE_ALWAYS_ON_AP
    response += ",\"hotspot\":\"" + String(HOTSPOT_SSID) + "\",\"hotspotIP\":\"" + hotspotIP + "\"";
    #endif
    response += "}";
    server.send(200, "application/json", response);
    
    // Restart the web server on the new network
    delay(1000);
    server.begin();
  } else {
    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n✗ Connection failed");
    #endif
    
    // Connection failed — clear bad credentials and restart portal
    clearWiFiCredentials();
    startCaptivePortal();
    server.begin();
    
    server.send(200, "application/json", "{\"success\":false,\"error\":\"Connection failed\"}");
  }
}

/*
 * Factory reset WiFi credentials
 */
void handleResetWiFi() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  
  clearWiFiCredentials();
  server.send(200, "application/json", "{\"success\":true,\"message\":\"Credentials cleared. Restarting...\"}");
  
  #if ENABLE_SERIAL_DEBUG
  Serial.println("🔄 Factory reset! Restarting...");
  #endif
  
  delay(1000);
  ESP.restart();
}

/*
 * System info endpoint
 */
void handleSystemInfo() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  
  String json = "{";
  json += "\"freeHeap\":" + String(ESP.getFreeHeap()) + ",";
  json += "\"uptime\":" + String(millis()) + ",";
  json += "\"wifiConnected\":" + String(wifiConnected ? "true" : "false") + ",";
  json += "\"ssid\":\"" + savedSSID + "\",";
  json += "\"ip\":\"" + (wifiConnected ? WiFi.localIP().toString() : WiFi.softAPIP().toString()) + "\",";
  #if ENABLE_MDNS
  json += "\"hostname\":\"" + String(MDNS_HOSTNAME) + ".local\",";
  #endif
  #if ENABLE_ALWAYS_ON_AP
  json += "\"hotspot\":\"" + String(HOTSPOT_SSID) + "\",";
  json += "\"hotspotIP\":\"" + WiFi.softAPIP().toString() + "\",";
  #endif
  json += "\"rssi\":" + String(WiFi.RSSI());
  json += "}";
  
  server.send(200, "application/json", json);
}

/*
 * Handle status API endpoint
 */
void handleStatus() {
  #if ENABLE_CORS
  server.sendHeader("Access-Control-Allow-Origin", "*");
  #endif
  
  server.send(200, "application/json", getRelayStatesJSON());
}

/*
 * Captive portal catch-all: redirect unknown requests to setup/dashboard
 * Also handles the Android/iOS captive portal detection endpoints
 */
void handleCaptiveOrNotFound() {
  if (portalActive) {
    // Redirect all requests to the setup page (captive portal behavior)
    server.sendHeader("Location", "http://" + WiFi.softAPIP().toString(), true);
    server.send(302, "text/plain", "");
  } else {
    server.send(404, "text/plain", "404: Not Found");
  }
}

/*
 * Generate web interface HTML (Dashboard)
 */
String getWebInterface() {
  String settingsLink = wifiConnected ? savedSSID : String(AP_SSID);
  String currentIP = wifiConnected ? WiFi.localIP().toString() : WiFi.softAPIP().toString();
  String hostnameUrl = String(MDNS_HOSTNAME) + ".local";
  String hotspotName = String(HOTSPOT_SSID);
  String hotspotIP = WiFi.softAPIP().toString();
  
  String html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>)rawliteral" + String(DEVICE_NAME) + R"rawliteral( Control</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            width: 100%;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 1.1em;
        }
        
        .controls {
            display: grid;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .switch-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 25px;
            transition: all 0.3s ease;
            cursor: pointer;
            text-decoration: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .switch-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        .switch-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .switch-icon {
            font-size: 2em;
        }
        
        .switch-name {
            font-size: 1.3em;
            font-weight: 600;
            color: #f1f5f9;
        }
        
        .toggle-btn {
            padding: 12px 30px;
            font-size: 1.1em;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 80px;
        }
        
        .toggle-btn.on {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: white;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
        }
        
        .toggle-btn.off {
            background: linear-gradient(135deg, #64748b, #475569);
            color: #cbd5e1;
        }
        
        .footer {
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding: 20px;
        }
        
        .settings-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #64748b;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
            transition: all 0.2s;
            margin-top: 15px;
            font-size: 0.9em;
        }
        
        .settings-link:hover {
            color: #f1f5f9;
            border-color: rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.05);
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.online {
            background: #22c55e;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @media (max-width: 600px) {
            h1 {
                font-size: 2em;
            }
            
            .switch-card {
                padding: 20px;
            }
            
            .switch-name {
                font-size: 1.1em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏠 )rawliteral" + String(DEVICE_NAME) + R"rawliteral(</h1>
            <p class="subtitle">
                <span class="status-indicator online"></span>
                System Online
            </p>
        </header>
        
        <div class="controls">
            <a href="/r1" class="switch-card">
                <div class="switch-info">
                    <span class="switch-icon">💡</span>
                    <span class="switch-name">)rawliteral" + String(SWITCH_1_NAME) + R"rawliteral(</span>
                </div>
                <button class="toggle-btn %STATE1%">%TEXT1%</button>
            </a>
            
            <a href="/r2" class="switch-card">
                <div class="switch-info">
                    <span class="switch-icon">🌙</span>
                    <span class="switch-name">)rawliteral" + String(SWITCH_2_NAME) + R"rawliteral(</span>
                </div>
                <button class="toggle-btn %STATE2%">%TEXT2%</button>
            </a>
            
            <a href="/r3" class="switch-card">
                <div class="switch-info">
                    <span class="switch-icon">🔆</span>
                    <span class="switch-name">)rawliteral" + String(SWITCH_3_NAME) + R"rawliteral(</span>
                </div>
                <button class="toggle-btn %STATE3%">%TEXT3%</button>
            </a>
            
            <a href="/r4" class="switch-card">
                <div class="switch-info">
                    <span class="switch-icon">🌀</span>
                    <span class="switch-name">)rawliteral" + String(SWITCH_4_NAME) + R"rawliteral(</span>
                </div>
                <button class="toggle-btn %STATE4%">%TEXT4%</button>
            </a>
        </div>
        
        <div class="access-card" style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);border-radius:16px;padding:20px;margin-bottom:20px;text-align:center;">
            <p style="color:#22c55e;font-size:1em;font-weight:600;margin-bottom:12px;">� Control from ANY Device</p>
            <div style="background:rgba(0,0,0,0.2);border-radius:12px;padding:15px;margin-bottom:10px;">
                <p style="color:#94a3b8;font-size:0.85em;margin-bottom:6px;">Step 1: Connect to WiFi</p>
                <p style="font-size:1.2em;font-weight:700;color:#60a5fa;">)rawliteral" + hotspotName + R"rawliteral(</p>
                <p style="color:#64748b;font-size:0.8em;margin-top:2px;">Password: )rawliteral" + String(HOTSPOT_PASSWORD) + R"rawliteral(</p>
            </div>
            <div style="background:rgba(0,0,0,0.2);border-radius:12px;padding:15px;">
                <p style="color:#94a3b8;font-size:0.85em;margin-bottom:6px;">Step 2: Open in browser</p>
                <p style="font-size:1.2em;font-weight:700;color:#22c55e;">http://)rawliteral" + hotspotIP + R"rawliteral(</p>
            </div>
            <p style="color:#475569;font-size:0.75em;margin-top:8px;">Also available at: )rawliteral" + currentIP + R"rawliteral( | )rawliteral" + hostnameUrl + R"rawliteral(</p>
        </div>
        
        <div class="footer">
            <p>Connected to: )rawliteral" + settingsLink + R"rawliteral(</p>
            <a href="/settings" class="settings-link">⚙️ Settings</a>
            <p style="margin-top: 10px; color: #475569;">Smart Home v1.2</p>
        </div>
    </div>
</body>
</html>
)rawliteral";

  // Replace state placeholders
  for (int i = 0; i < 4; i++) {
    bool state = getRelayState(i);
    html.replace("%STATE" + String(i+1) + "%", state ? "on" : "off");
    html.replace("%TEXT" + String(i+1) + "%", state ? "ON" : "OFF");
  }
  
  return html;
}
