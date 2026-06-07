# Communication Protocol

## Design Goals

- Each ESP32 has a stable `node_id`.
- Each ESP32 tells the Pi what hardware capabilities it has.
- The Pi can add/remove nodes without rewriting the whole game.
- Inputs and outputs use predictable MQTT topics.
- Messages are JSON so they are easy to inspect from the Pi terminal.

## MQTT Topic Layout

Base namespace:

```text
boardgame
```

Node registration:

```text
boardgame/nodes/<node_id>/register
```

Node heartbeat:

```text
boardgame/nodes/<node_id>/heartbeat
```

Input events from ESP32 to Pi:

```text
boardgame/nodes/<node_id>/event
```

Commands from Pi to ESP32:

```text
boardgame/nodes/<node_id>/cmd
```

Broadcast game-state messages from Pi to all ESP32s:

```text
boardgame/game/state
```

## Registration Message

Published by each ESP32 when it boots and whenever it reconnects.

```json
{
  "type": "register",
  "node_id": "motor_1",
  "role": "motor",
  "name": "Motor Node 1",
  "firmware": "0.1.0",
  "capabilities": [
    {
      "id": "drive_motor",
      "type": "motor",
      "commands": ["motor.set"],
      "values": ["forward", "reverse", "stop"],
      "speed_range": [0, 255]
    }
  ]
}
```

## Heartbeat Message

Published every few seconds so the Pi can detect offline nodes.

```json
{
  "type": "heartbeat",
  "node_id": "motor_1",
  "uptime_ms": 123456
}
```

## Button Event

Published from button node to Pi.

```json
{
  "type": "event",
  "node_id": "button_1",
  "event": "button.press",
  "control": "main_button",
  "value": 1
}
```

## Motor Command

Published from Pi to motor node.

```json
{
  "type": "command",
  "command": "motor.set",
  "value": "forward",
  "speed": 220
}
```

Valid values:

```text
forward
reverse
stop
```

## Future Device Types

Suggested command/event names:

```text
button.press
button.release
encoder.turn
encoder.press
led.set
led.rgb
oled.text
oled.clear
motor.set
haptic.pulse
```

