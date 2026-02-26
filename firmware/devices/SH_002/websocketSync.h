/*
 * WebSocket Sync Module
 * Replaces Firebase with custom BaaS WebSocket connection.
 */

#ifndef WEBSOCKET_SYNC_H
#define WEBSOCKET_SYNC_H

#include <ArduinoWebsockets.h> // Library: ArduinoWebsockets by Gil Maimon
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>  // Required for wss:// with setInsecure()

using namespace websockets;

// ============= Backend Configuration =============
// Configuration is now in config.h
// Uses: BACKEND_HOST, BACKEND_PORT, DEVICE_ID, DEVICE_API_KEY

// ==================== Globals ====================
WebsocketsClient client;
bool isConnected = false;
unsigned long lastPingTime = 0;
unsigned long lastReconnectAttempt = 0;
unsigned long reconnectInterval = 5000;          // starts at 5s, backs off slowly
int reconnectAttempts = 0;                       // track consecutive failures
const unsigned long PING_INTERVAL    = 25000;    // 25s heartbeat
const unsigned long MIN_RECONNECT    = 5000;     // minimum 5s between retries
const unsigned long MAX_RECONNECT    = 60000;    // cap at 60s (Render cold start)
const int BACKOFF_AFTER_ATTEMPTS     = 3;        // only start backing off after N failures

// Forward declarations
void sendStateUpdate();

// ==================== Message Handling ====================

void onMessageCallback(WebsocketsMessage message) {
    String data = message.data();
    
    #if ENABLE_SERIAL_DEBUG
    Serial.print("📩 WS Recv: ");
    Serial.println(data);
    #endif

    // Parse JSON
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, data);
    
    if (error) {
        #if ENABLE_SERIAL_DEBUG
        Serial.print("JSON Error: ");
        Serial.println(error.c_str());
        #endif
        return;
    }

    String type = doc["type"] | "";
    
    if (type == "command" || type == "update") {
        JsonObject state = doc["data"];
        bool changed = false;
        
        for (int i = 0; i < 4; i++) {
            String key = "relay" + String(i + 1);
            if (state.containsKey(key)) {
                bool newState = state[key]["state"];
                if (newState != relayStates[i]) {
                    relayStates[i] = newState;
                    digitalWrite(relayPins[i], newState ? RELAY_ON : RELAY_OFF);
                    changed = true;
                    
                    #if ENABLE_SERIAL_DEBUG
                    Serial.print("⚡ Relay ");
                    Serial.print(i + 1);
                    Serial.println(newState ? " ON" : " OFF");
                    #endif
                }
            }
        }
        
        // Save if needed
        if (changed) {
            for (int i = 0; i < 4; i++) {
                #if ENABLE_STATE_PERSISTENCE
                preferences.putBool(String("relay" + String(i)).c_str(), relayStates[i]);
                #endif
            }
            // Acknowledge update back to server? 
            // Usually not needed for broadcast, but good for confirmation.
            // sendStateUpdate(); // Optional, prevents loops if careful
        }
    }
}

void onEventsCallback(WebsocketsEvent event, String data) {
    if (event == WebsocketsEvent::ConnectionOpened) {
        isConnected = true;
        reconnectInterval = MIN_RECONNECT; // reset backoff on success
        reconnectAttempts = 0;             // reset attempt counter
        #if ENABLE_SERIAL_DEBUG
        Serial.println("✅ WS Connected!");
        #endif
        // Send initial state
        sendStateUpdate();
    } else if (event == WebsocketsEvent::ConnectionClosed) {
        isConnected = false;
        #if ENABLE_SERIAL_DEBUG
        Serial.println("❌ WS Disconnected. Will retry...");
        #endif
    } else if (event == WebsocketsEvent::GotPing) {
        client.pong();
    }
}

// ==================== Core Functions ====================

void initWebSocket() {
    // Setup callbacks
    client.onMessage(onMessageCallback);
    client.onEvent(onEventsCallback);
    
    // CRITICAL: Skip SSL cert verification for wss:// connections.
    // Without this, TLS handshake fails silently on ESP32 (no root CA loaded).
    // Use a proper root CA cert in production for security.
    if (BACKEND_SECURE) {
        client.setInsecure();
    }

    // Construct URL with Auth
    String protocol = BACKEND_SECURE ? "wss://" : "ws://";
    String portStr = (BACKEND_PORT == 80 || BACKEND_PORT == 443) ? "" : ":" + String(BACKEND_PORT);
    String url = protocol + String(BACKEND_HOST) + portStr + "/api/v1/ws/" + String(DEVICE_ID) + "?api_key=" + String(DEVICE_API_KEY);
    
    #if ENABLE_SERIAL_DEBUG
    Serial.print("🔌 WS Connecting to: ");
    Serial.println(url);
    #endif
    
    bool ok = client.connect(url);
    
    #if ENABLE_SERIAL_DEBUG
    if (!ok) {
        Serial.println("⚠️  WS connect() returned false — server may be sleeping (Render cold start), retrying...");
    }
    #endif
}

void sendHeartbeat() {
    if (!isConnected) return;
    if (millis() - lastPingTime < PING_INTERVAL) return;
    lastPingTime = millis();
    
    // Simple heartbeat/ping
    client.send("{\"type\":\"heartbeat\"}");
}

void sendStateUpdate() {
    if (!isConnected) return;
    
    StaticJsonDocument<512> doc;
    doc["type"] = "state_update";
    
    JsonObject data = doc.createNestedObject("data");
    for (int i = 0; i < 4; i++) {
        String key = "relay" + String(i + 1);
        JsonObject relay = data.createNestedObject(key);
        relay["state"] = (relayStates[i] == true); // explicitly bool
    }
    
    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);
}



// Call this in loop()
void cloudSyncLoop() {
    if (WiFi.status() != WL_CONNECTED) return;

    client.poll(); // Must always poll even if reconnecting

    if (!isConnected) {
        // Auto-reconnect with Render.com cold-start friendly backoff.
        // We retry quickly at first (5s x3) to catch the server waking up,
        // then slowly back off up to 60s to avoid hammering a sleeping server.
        if (millis() - lastReconnectAttempt > reconnectInterval) {
            lastReconnectAttempt = millis(); // reset BEFORE connect so timing is clean
            reconnectAttempts++;

            // Calculate NEXT interval before connecting
            unsigned long nextInterval;
            if (reconnectAttempts < BACKOFF_AFTER_ATTEMPTS) {
                nextInterval = MIN_RECONNECT; // stay at 5s during wake-up window
            } else {
                nextInterval = min(reconnectInterval * 2, MAX_RECONNECT);
            }

            #if ENABLE_SERIAL_DEBUG
            Serial.print("🔄 WS reconnecting (attempt ");
            Serial.print(reconnectAttempts);
            Serial.print(", next retry in ");
            Serial.print(nextInterval / 1000);
            Serial.println("s)...");
            #endif

            initWebSocket();
            reconnectInterval = nextInterval;
        }
        return;
    }

    sendHeartbeat();
}

// Helper to replace the one in firebaseSync.h
void notifyCloudStateChange(int relayIndex, bool newState) {
    // Update global array first (already done in main loop usually, but ensure consistency)
    relayStates[relayIndex] = newState;
    sendStateUpdate();
}

#endif
