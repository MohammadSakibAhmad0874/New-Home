# Hardware Setup Guide

## Required Components

### 1. ESP32 Development Board
- Any ESP32 board (DevKit, NodeMCU-32S, etc.)
- USB cable for programming
- Built-in WiFi

### 2. 4-Channel Relay Module
- **Voltage**: 5V DC
- **Type**: Active-LOW (most common)
- **Current Rating**: Minimum 10A per relay
- **Isolation**: Optocoupler isolation recommended

### 3. Power Supply
- **For ESP32**: USB power (5V 500mA) or VIN (7-12V)
- **For Relays**: External 5V 2A adapter (recommended)
- **Important**: Don't power 4 relays from ESP32's 5V pin

### 4. Additional Items
- Male-to-female jumper wires
- Breadboard (optional, for prototyping)
- Electrical enclosure
- Wire strippers, screwdrivers

## Wiring Diagram

### ESP32 to Relay Module Connections

| Component | ESP32 Pin | Notes |
|-----------|-----------|-------|
| Relay 1 IN | GPIO 23 | Switch 1 control |
| Relay 2 IN | GPIO 22 | Switch 2 control |
| Relay 3 IN | GPIO 21 | Switch 3 control |
| Relay 4 IN | GPIO 19 | Switch 4 control |
| Relay VCC | 5V External | **DO NOT use ESP32 5V** |
| Relay GND | GND | **MUST share common ground** |

### Visual Wiring

```
ESP32                    Relay Module
┌─────────┐             ┌──────────┐
│         │             │          │
│  GPIO23 ├────────────►│ IN1      │
│  GPIO22 ├────────────►│ IN2      │
│  GPIO21 ├────────────►│ IN3      │
│  GPIO19 ├────────────►│ IN4      │
│         │             │          │
│     GND ├────┬───────►│ GND      │
│         │    │        │          │
└─────────┘    │        │ VCC      │◄── 5V External Supply
               │        └──────────┘
               │
               └─────────► External 5V GND
```

## Critical Wiring Rules

> [!CAUTION]
> **Common Ground is MANDATORY**
> 
> ESP32 GND, Relay Module GND, and External Power Supply GND **MUST** be connected together. This is the #1 cause of relay malfunction.

> [!WARNING]
> **Power Supply Separation**
> 
> - **ESP32**: Powered via USB OR external 5V/VIN
> - **Relay Module VCC**: Powered from external 5V adapter
> - **NEVER** power 4 relays from ESP32's 3.3V or 5V pin
> - Under load, relays draw 60-80mA each = 320mA total

> [!CAUTION]
> **High Voltage Safety**
> 
> Relay outputs switch mains voltage (120V/240V):
> - Ensure proper wire gauge for load current
> - Use proper terminal blocks
> - Keep high voltage isolated from low voltage
> - Install in proper electrical enclosure
> - Add fuses for each load

## Relay Module Configuration

### Active-LOW vs Active-HIGH

Most relay modules are **active-LOW**:
- `digitalWrite(pin, LOW)` → Relay ON (LED lights up)
- `digitalWrite(pin, HIGH)` → Relay OFF (LED off)

To verify:
1. Power the relay module
2. Touch IN1 to GND briefly
3. If relay clicks ON → Active-LOW ✓
4. If nothing happens → Active-HIGH

Update `firmware/config.h` accordingly.

## Recommended GPIO Pins

| GPIO | Safe for Use | Notes |
|------|--------------|-------|
| 23 | ✅ Yes | Relay 1 (default) |
| 22 | ✅ Yes | Relay 2 (default) |
| 21 | ✅ Yes | Relay 3 (default) |
| 19 | ✅ Yes | Relay 4 (default) |
| 18 | ✅ Yes | Alternative |
| 5 | ✅ Yes | Alternative |
| 0 | ⚠️ Boot pin | Avoid if possible |
| 2 | ⚠️ Built-in LED | Avoid |
| 6-11 | ❌ No | Flash memory |
| 12 | ⚠️ Boot voltage | Pull down required |

## Testing Without Mains Power

**Before connecting any mains electricity:**

1. Connect only ESP32 and relay module (low voltage)
2. Upload firmware
3. Observe relay LEDs and listen for clicks
4. Use multimeter on relay outputs (COM/NO/NC)
5. Verify all 4 relays respond correctly
6. Test rapid toggling

## Final Installation Checklist

- [ ] All low voltage connections secure
- [ ] Common ground verified with multimeter
- [ ] Relay module clicks when commanded
- [ ] Web interface controls all relays correctly
- [ ] No loose wires
- [ ] System mounted in electrical enclosure
- [ ] High voltage wiring uses proper gauge wire
- [ ] Each load has appropriate fuse
- [ ] Manual override switches installed
- [ ] System tested without load
- [ ] System tested with load (low voltage first)
- [ ] All safety covers installed

## Troubleshooting

### Relays Don't Respond
- ✓ Check common ground connection
- ✓ Verify relay module has power (VCC LED on)
- ✓ Test relay manually (touch IN to GND)
- ✓ Check GPIO pin configuration in code

### Random Relay Behavior
- ✓ Add common ground
- ✓ Use external power supply for relays
- ✓ Check for loose connections
- ✓ Add pull-up resistors if needed

### ESP32 Reboots
- ✓ Relays drawing too much current
- ✓ Use external power for relays
- ✓ Add decoupling capacitors

---

> [!TIP]
> Start simple: Get one relay working perfectly before adding the rest!
