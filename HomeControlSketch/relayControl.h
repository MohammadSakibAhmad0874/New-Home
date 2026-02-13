/*
 * Relay Control Module
 * Handles all relay operations, state management, and persistence
 */

#ifndef RELAY_CONTROL_H
#define RELAY_CONTROL_H

#include <Preferences.h>
#include "config.h"

// Relay state storage
bool relayStates[4] = {false, false, false, false};
const int relayPins[4] = {RELAY_PIN_1, RELAY_PIN_2, RELAY_PIN_3, RELAY_PIN_4};

// Preferences for state persistence
Preferences preferences;

/*
 * Initialize all relay pins and load saved states
 */
void initRelays() {
  // Initialize preferences if persistence is enabled
  #if ENABLE_STATE_PERSISTENCE
  preferences.begin("relay-states", false);
  #endif
  
  // Setup GPIO pins
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    
    #if ENABLE_STATE_PERSISTENCE
    // Load saved state from flash memory
    relayStates[i] = preferences.getBool(String("relay" + String(i)).c_str(), false);
    #else
    relayStates[i] = false;
    #endif
    
    // Set initial state
    digitalWrite(relayPins[i], relayStates[i] ? RELAY_ON : RELAY_OFF);
    
    #if ENABLE_SERIAL_DEBUG
    Serial.print("Relay ");
    Serial.print(i + 1);
    Serial.print(" initialized: ");
    Serial.println(relayStates[i] ? "ON" : "OFF");
    #endif
  }
}

/*
 * Set relay state
 * @param relayIndex: 0-3 for relays 1-4
 * @param state: true = ON, false = OFF
 */
void setRelay(int relayIndex, bool state) {
  if (relayIndex < 0 || relayIndex > 3) return;
  
  relayStates[relayIndex] = state;
  digitalWrite(relayPins[relayIndex], state ? RELAY_ON : RELAY_OFF);
  
  // Save state to flash memory
  #if ENABLE_STATE_PERSISTENCE
  preferences.putBool(String("relay" + String(relayIndex)).c_str(), state);
  #endif
  
  #if ENABLE_SERIAL_DEBUG
  Serial.print("Relay ");
  Serial.print(relayIndex + 1);
  Serial.print(" set to: ");
  Serial.println(state ? "ON" : "OFF");
  #endif
}

/*
 * Toggle relay state
 * @param relayIndex: 0-3 for relays 1-4
 */
void toggleRelay(int relayIndex) {
  if (relayIndex < 0 || relayIndex > 3) return;
  setRelay(relayIndex, !relayStates[relayIndex]);
}

/*
 * Get relay state
 * @param relayIndex: 0-3 for relays 1-4
 * @return: true = ON, false = OFF
 */
bool getRelayState(int relayIndex) {
  if (relayIndex < 0 || relayIndex > 3) return false;
  return relayStates[relayIndex];
}

/*
 * Turn all relays OFF (safety function)
 */
void allRelaysOff() {
  for (int i = 0; i < 4; i++) {
    setRelay(i, false);
  }
  #if ENABLE_SERIAL_DEBUG
  Serial.println("All relays turned OFF");
  #endif
}

/*
 * Get all relay states as JSON string
 */
String getRelayStatesJSON() {
  String json = "{";
  for (int i = 0; i < 4; i++) {
    json += "\"relay" + String(i + 1) + "\":" + (relayStates[i] ? "true" : "false");
    if (i < 3) json += ",";
  }
  json += "}";
  return json;
}

#endif
