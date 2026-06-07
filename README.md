# Physical Video Board Game System

This project is a scalable starting point for a tabletop game system built from:

- Raspberry Pi 5 as the central game controller
- ESP32 modules as wireless input/output nodes
- MQTT as the communication layer

The current architecture is:

```text
ESP32 nodes <-> WiFi <-> Raspberry Pi 5 MQTT broker <-> Python game controller
```

## Why MQTT

MQTT fits this project well because each controller can publish events and subscribe to commands without needing to know about every other controller.

The Raspberry Pi runs:

- Mosquitto MQTT broker
- Python game controller service

Each ESP32:

- connects to WiFi
- connects to the Pi MQTT broker
- publishes a registration message
- publishes input events
- listens for output commands
- sends heartbeat messages so the Pi knows it is still online

## Folder Layout

```text
docs/protocol.md
  Topic names, JSON message formats, and registration rules.

pi/game_controller.py
  Raspberry Pi controller service. Tracks registered nodes and routes simple game commands.

esp32/BoardGameNode/BoardGameNode.ino
  Reusable ESP32 template for buttons, LEDs, OLEDs, motors, and other hardware.

esp32/examples/ButtonNode/ButtonNode.ino
  Minimal button controller that publishes button events.

esp32/examples/MotorNode/MotorNode.ino
  Motor controller for TB6612FNG using D2/D3/D4/D5 pins.
```

## First Milestone

1. Run Mosquitto on the Raspberry Pi.
2. Run `pi/game_controller.py` on the Raspberry Pi.
3. Upload `MotorNode.ino` to the motor ESP32.
4. Upload `ButtonNode.ino` to the button ESP32.
5. Watch the Pi log registrations and events.

## Install Python Dependency On Pi

```bash
sudo apt update
sudo apt install python3-pip
python3 -m pip install paho-mqtt
```

## Run The Pi Controller

```bash
cd video-board-game-system/pi
python3 game_controller.py
```

## MQTT Test Commands

Send a command to the motor node:

```bash
mosquitto_pub -h 127.0.0.1 -t boardgame/nodes/motor_1/cmd -m '{"type":"command","command":"motor.set","value":"forward","speed":220}'
```

Stop it:

```bash
mosquitto_pub -h 127.0.0.1 -t boardgame/nodes/motor_1/cmd -m '{"type":"command","command":"motor.set","value":"stop"}'
```

