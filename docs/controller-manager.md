# Controller Manager

The controller manager is the Raspberry Pi layer that owns controller state.

Game code should not directly manage raw controller dictionaries. Instead, game code should ask the controller manager which controllers exist, which player they belong to, and whether they are online.

## Tracked Data

Each controller is tracked by MAC address:

```python
controllers = {
    "AA:BB:CC:11:22:33": {
        "player": 1,
        "online": True,
        "last_seen": 1749300000.0
    }
}
```

## Current Responsibilities

- Register new controllers.
- Assign the next available player number.
- Assign fixed player numbers for known controller IDs.
- Preserve a controller's player number when it reconnects.
- Track the last time each controller was seen.
- Mark controllers offline when heartbeats stop.

## Fixed Player Assignments

Known ESP32 controllers can be locked to specific player numbers in:

```text
raspberry-pi/controller_config.py
```

Example:

```python
FIXED_PLAYER_ASSIGNMENTS = {
    "94:A9:90:68:A1:90": 1,
    "AA:BB:CC:11:22:33": 2,
    "DD:EE:FF:44:55:66": 3,
}
```

If a controller ID is listed there, it always receives that player number.

If a controller ID is not listed, it receives the next available non-reserved player number.

## MQTT Topics

Registration:

```text
controller/register
```

Heartbeat:

```text
controller/heartbeat
```

Player assignment:

```text
controller/assign
```

## Timeout Rule

The Pi marks a controller offline if it does not receive a heartbeat for 15 seconds.

The ESP32 sends a heartbeat every 5 seconds after it receives a player assignment.

## Future Upgrades

- Controller names, colors, and roles.
- Battery reporting.
- Input capability reporting.
- Output capability reporting.
- Commands by player number instead of raw controller ID.
