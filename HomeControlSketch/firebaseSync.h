/*
 * Firebase Cloud Sync Module
 * 
 * Syncs relay states with Firebase Realtime Database
 * so the ESP32 can be controlled from anywhere via the web dashboard.
 * 
 * Uses HTTP REST API — no additional libraries needed!
 */

#ifndef FIREBASE_SYNC_H
#define FIREBASE_SYNC_H

#include <HTTPClient.h>
#include <ArduinoJson.h>

// ==================== Firebase Configuration ====================
// Get these from your Firebase project settings

// Your Firebase Realtime Database URL (no trailing slash)
#define FIREBASE_HOST "apnaghar-3f865-default-rtdb.firebaseio.com"

// Firebase Database Secret (or Web API Key)
// Go to: Firebase Console → Project Settings → Service Accounts → Database Secrets
#define FIREBASE_AUTH "YOUR_DATABASE_SECRET_HERE"

// Unique Device ID — must match what you registered on the web app
#define DEVICE_ID "SH-001"

// ==================== Sync Settings ====================
unsigned long lastSyncTime = 0;
unsigned long lastHeartbeatTime = 0;
const unsigned long SYNC_INTERVAL = 2000;     // Check for commands every 2 seconds
const unsigned long HEARTBEAT_INTERVAL = 30000; // Send heartbeat every 30 seconds

bool firebaseEnabled = false;

// Forward declarations
void pushStatesToCloud();

// ==================== Firebase HTTP Helpers ====================

String firebaseGet(String path) {
    if (WiFi.status() != WL_CONNECTED) return "";
    
    HTTPClient http;
    String url = "https://" + String(FIREBASE_HOST) + "/" + path + ".json?auth=" + String(FIREBASE_AUTH);
    
    http.begin(url);
    http.setTimeout(5000);
    int httpCode = http.GET();
    
    String payload = "";
    if (httpCode == 200) {
        payload = http.getString();
    } else {
        #if ENABLE_SERIAL_DEBUG
        Serial.print("Firebase GET error: ");
        Serial.println(httpCode);
        #endif
    }
    http.end();
    return payload;
}

bool firebasePut(String path, String jsonData) {
    if (WiFi.status() != WL_CONNECTED) return false;
    
    HTTPClient http;
    String url = "https://" + String(FIREBASE_HOST) + "/" + path + ".json?auth=" + String(FIREBASE_AUTH);
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(5000);
    int httpCode = http.PUT(jsonData);
    
    http.end();
    return (httpCode == 200);
}

bool firebasePatch(String path, String jsonData) {
    if (WiFi.status() != WL_CONNECTED) return false;
    
    HTTPClient http;
    String url = "https://" + String(FIREBASE_HOST) + "/" + path + ".json?auth=" + String(FIREBASE_AUTH);
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(5000);
    int httpCode = http.sendRequest("PATCH", jsonData);
    
    http.end();
    return (httpCode == 200);
}

// ==================== Cloud Sync Functions ====================

/*
 * Initialize Firebase connection
 * Call this after WiFi connects
 */
void initFirebaseSync() {
    if (String(FIREBASE_HOST) == "YOUR_PROJECT_ID-default-rtdb.firebaseio.com") {
        #if ENABLE_SERIAL_DEBUG
        Serial.println("⚠ Firebase not configured — cloud sync disabled");
        Serial.println("  Edit firebaseSync.h with your Firebase credentials");
        #endif
        firebaseEnabled = false;
        return;
    }
    
    firebaseEnabled = true;
    
    #if ENABLE_SERIAL_DEBUG
    Serial.println("\n☁ Firebase Cloud Sync starting...");
    Serial.print("  Device ID: ");
    Serial.println(DEVICE_ID);
    #endif
    
    // Set device as online
    firebasePatch("devices/" + String(DEVICE_ID), 
        "{\"online\":true,\"lastSeen\":" + String(millis()) + ",\"ip\":\"" + WiFi.localIP().toString() + "\"}");
    
    // Push current relay states to cloud
    pushStatesToCloud();
    
    #if ENABLE_SERIAL_DEBUG
    Serial.println("☁ Firebase Cloud Sync active!");
    #endif
}

/*
 * Push current relay states to Firebase
 */
void pushStatesToCloud() {
    if (!firebaseEnabled) return;
    
    String json = "{";
    json += "\"relay1\":{\"state\":" + String(relayStates[0] ? "true" : "false") + ",\"name\":\"" + String(SWITCH_1_NAME) + "\"},";
    json += "\"relay2\":{\"state\":" + String(relayStates[1] ? "true" : "false") + ",\"name\":\"" + String(SWITCH_2_NAME) + "\"},";
    json += "\"relay3\":{\"state\":" + String(relayStates[2] ? "true" : "false") + ",\"name\":\"" + String(SWITCH_3_NAME) + "\"},";
    json += "\"relay4\":{\"state\":" + String(relayStates[3] ? "true" : "false") + ",\"name\":\"" + String(SWITCH_4_NAME) + "\"}";
    json += "}";
    
    firebasePut("devices/" + String(DEVICE_ID) + "/relays", json);
}

/*
 * Check Firebase for remote commands (state changes from web dashboard)
 * If a state changed in the cloud, update the local relay
 */
void syncFromCloud() {
    if (!firebaseEnabled) return;
    if (millis() - lastSyncTime < SYNC_INTERVAL) return;
    lastSyncTime = millis();
    
    String response = firebaseGet("devices/" + String(DEVICE_ID) + "/relays");
    if (response.length() == 0 || response == "null") return;
    
    // Parse JSON response
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    if (error) {
        #if ENABLE_SERIAL_DEBUG
        Serial.print("JSON parse error: ");
        Serial.println(error.c_str());
        #endif
        return;
    }
    
    // Check each relay
    bool stateChanged = false;
    
    for (int i = 0; i < 4; i++) {
        String key = "relay" + String(i + 1);
        if (doc.containsKey(key)) {
            bool cloudState = doc[key]["state"] | false;
            if (cloudState != relayStates[i]) {
                relayStates[i] = cloudState;
                digitalWrite(relayPins[i], cloudState ? RELAY_ON : RELAY_OFF);
                stateChanged = true;
                
                #if ENABLE_SERIAL_DEBUG
                Serial.print("☁ Cloud command: Relay ");
                Serial.print(i + 1);
                Serial.println(cloudState ? " → ON" : " → OFF");
                #endif
            }
        }
    }
    
    // Save states if changed — use setRelay to handle persistence
    if (stateChanged) {
        for (int i = 0; i < 4; i++) {
            #if ENABLE_STATE_PERSISTENCE
            preferences.putBool(String("relay" + String(i)).c_str(), relayStates[i]);
            #endif
        }
    }
}

/*
 * Send heartbeat to Firebase (online status + timestamp)
 */
void sendHeartbeat() {
    if (!firebaseEnabled) return;
    if (millis() - lastHeartbeatTime < HEARTBEAT_INTERVAL) return;
    lastHeartbeatTime = millis();
    
    firebasePatch("devices/" + String(DEVICE_ID),
        "{\"online\":true,\"lastSeen\":" + String(millis()) + "}");
}

/*
 * Notify cloud when a relay is toggled locally (from the local web page)
 */
void notifyCloudStateChange(int relayIndex, bool newState) {
    if (!firebaseEnabled) return;
    
    String key = "relay" + String(relayIndex + 1);
    firebasePut("devices/" + String(DEVICE_ID) + "/relays/" + key + "/state",
        newState ? "true" : "false");
}

/*
 * Main cloud sync loop — call this in loop()
 */
void cloudSyncLoop() {
    if (!firebaseEnabled) return;
    
    syncFromCloud();
    sendHeartbeat();
}

#endif
