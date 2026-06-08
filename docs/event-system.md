# Nexus Connect Event System

The event system turns raw controller input into game actions.

## Flow

1. ESP32 controller registers with the Pi.
2. Pi assigns the controller a player number.
3. ESP32 publishes input messages to `controller/event`.
4. Pi converts the MQTT message into a `GameEvent`.
5. The active game handles the event and publishes game state.

## Controller Event Topic

```text
controller/event
```

## Button Press Event

```json
{
  "type": "event",
  "controller_id": "94:A9:90:68:A1:90",
  "event": "button.press",
  "control": "main_button",
  "value": 1
}
```

## Game State Topic

```text
game/state
```

Game state messages are retained by MQTT so a display or debug client can see the latest state after connecting.

## Reaction Race

Reaction Race is the first Nexus Connect game.

- The Pi waits for two online controllers.
- The Pi blinks all controller LEDs 3 times to show the round is starting.
- The Pi turns all controller LEDs off.
- The Pi waits a random 0-10 seconds.
- The Pi turns all controller LEDs on at the same time.
- The first `button.press` after the LEDs turn on wins.
- A `button.press` before the LEDs turn on is a false start.
- Events from unregistered controllers are ignored.
- Events without a player assignment are ignored.

Example state:

```json
{
  "type": "game_state",
  "game": "reaction_race",
  "status": "finished",
  "min_players": 2,
  "online_players": 2,
  "winner": 1,
  "false_start_player": null,
  "response_ms": 247
}
```

## Controller Command Topic

The Pi sends LED commands to all controllers on:

```text
controller/command
```

Turn all controller LEDs on:

```json
{
  "type": "command",
  "controller_id": "all",
  "command": "led.set",
  "value": 1
}
```

Turn all controller LEDs off:

```json
{
  "type": "command",
  "controller_id": "all",
  "command": "led.set",
  "value": 0
}
```

Blink all controller LEDs 3 times:

```json
{
  "type": "command",
  "controller_id": "all",
  "command": "led.blink",
  "count": 3,
  "interval_ms": 150
}
```

## Local Test Event

After the Pi game server is running, simulate a button press:

```bash
mosquitto_pub -h 127.0.0.1 -t controller/event -m '{"type":"event","controller_id":"94:A9:90:68:A1:90","event":"button.press","control":"main_button","value":1}'
```

Replace the controller ID with one that has already registered.
