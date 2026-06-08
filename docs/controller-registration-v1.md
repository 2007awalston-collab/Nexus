# Nexus Connect Controller Registration, Version 1

Version 1 handles controller identity, player assignment, heartbeats, button events, and LED commands.

It does not implement OLED menus, vibration motors, or advanced game-specific controller hardware yet.

## Flow

1. ESP32 boots.
2. ESP32 connects to WiFi.
3. ESP32 connects to MQTT on the Raspberry Pi.
4. ESP32 reads its WiFi MAC address.
5. ESP32 publishes a registration message.
6. Raspberry Pi stores the controller.
7. Raspberry Pi assigns the next player number.
8. ESP32 receives the player assignment.
9. ESP32 publishes button events.
10. Raspberry Pi sends LED commands for the active game.

## MQTT Topics

ESP32 publishes registration:

```text
controller/register
```

Raspberry Pi publishes assignment:

```text
controller/assign
```

ESP32 publishes input events:

```text
controller/event
```

Raspberry Pi publishes controller commands:

```text
controller/command
```

## Registration Message

```json
{
  "type": "register",
  "controller_id": "94:A9:90:68:A1:90"
}
```

## Assignment Message

```json
{
  "type": "assign_player",
  "controller_id": "94:A9:90:68:A1:90",
  "player": 1
}
```

## Raspberry Pi Setup

Install the Python MQTT library:

```bash
python3 -m pip install paho-mqtt
```

Run the game server:

```bash
cd raspberry-pi
python3 game_server.py
```

Expected output when the first controller connects:

```text
Controller Registered:
94:A9:90:68:A1:90

Assigned:
Player 1
```

## ESP32 Setup

Open this sketch in Arduino IDE:

```text
esp32_controller/esp32_controller.ino
```

Change:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
```

The MQTT server is already set to:

```cpp
const char* mqttServer = "192.168.68.74";
```

Upload the same sketch to each controller ESP32. Each board will use its own MAC address as its permanent controller ID.
