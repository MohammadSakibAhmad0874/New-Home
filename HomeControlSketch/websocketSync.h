/*
 * WebSocket Sync Module
 * Replaces Firebase with custom BaaS WebSocket connection.
 */

#ifndef WEBSOCKET_SYNC_H
#define WEBSOCKET_SYNC_H

#include <ArduinoWebsockets.h> // Library: ArduinoWebsockets by Gil Maimon
#include <ArduinoJson.h>

using namespace websockets;

// ==================== Backend Configuration ====================
// IP address of your computer running the backend
// CHANGE THIS TO YOUR PC's IP ADDRESS!
#define BACKEND_HOST "192.168.1.100" 
#define BACKEND_PORT 8000

// Device ID (must match backend registration)
#define DEVICE_ID "SH-001"

// ==================== Globals ====================
WebsocketsClient client;
bool isConnected = false;
unsigned long lastPingTime = 0;
const unsigned long PING_INTERVAL = 30000; // 30s heartbeat

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
        #if ENABLE_SERIAL_DEBUG
        Serial.println("✅ WS Connected!");
        #endif
        // Send initial state
        sendStateUpdate();
    } else if (event == WebsocketsEvent::ConnectionClosed) {
        isConnected = false;
        #if ENABLE_SERIAL_DEBUG
        Serial.println("❌ WS Disconnected");
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
    
    // Connect
    String url = "ws://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + "/api/v1/ws/" + String(DEVICE_ID);
    
    #if ENABLE_SERIAL_DEBUG
    Serial.print("Connecting to: ");
    Serial.println(url);
    #endif
    
    client.connect(url);
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
    if(WiFi.status() == WL_CONNECTED) {
        client.poll(); // Keep connection alive
        sendHeartbeat();
    }
}

// Helper to replace the one in firebaseSync.h
void notifyCloudStateChange(int relayIndex, bool newState) {
    // Update global array first (already done in main loop usually, but ensure consistency)
    relayStates[relayIndex] = newState;
    sendStateUpdate();
}

#endif
