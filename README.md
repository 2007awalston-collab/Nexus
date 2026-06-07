# Nexus Connect

Nexus Connect is a scalable physical tabletop gaming system built from:

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
docs/controller-registration-v1.md
  Version 1 controller registration and player assignment protocol.

docs/controller-manager.md
  Raspberry Pi controller manager design and heartbeat behavior.

docs/protocol.md
  Earlier scalable node protocol notes.

raspberry-pi/game_server.py
  Version 1 Raspberry Pi game server. Registers controllers and assigns players.

raspberry-pi/controller_manager.py
  Tracks controller player numbers, online status, and last_seen timestamps.

esp32_controller/esp32_controller.ino
  Version 1 ESP32 controller registration sketch.

pi/game_controller.py
  Earlier Raspberry Pi controller service. Tracks registered nodes and routes simple game commands.

esp32/BoardGameNode/BoardGameNode.ino
  Reusable ESP32 template for buttons, LEDs, OLEDs, motors, and other hardware.

esp32/examples/ButtonNode/ButtonNode.ino
  Minimal button controller that publishes button events.

esp32/examples/MotorNode/MotorNode.ino
  Motor controller for TB6612FNG using D2/D3/D4/D5 pins.
```

## First Milestone

1. Run Mosquitto on the Raspberry Pi.
2. Run `raspberry-pi/game_server.py` on the Raspberry Pi.
3. Upload `esp32_controller/esp32_controller.ino` to each ESP32 controller.
4. Watch the Pi register each controller by MAC address.
5. Confirm the first connected controller is assigned Player 1.

## Install Python Dependency On Pi

```bash
sudo apt update
sudo apt install python3-pip
python3 -m pip install paho-mqtt
```

## Run The Pi Controller

```bash
cd PhysicalVideoBoardGame_System/raspberry-pi
python3 game_server.py
```

## Controller Registration V1

Version 1 uses these MQTT topics:

```text
controller/register
controller/assign
```

See [docs/controller-registration-v1.md](docs/controller-registration-v1.md) for the exact message format and test steps.

## MQTT Test Commands

Send a command to the motor node:

```bash
mosquitto_pub -h 127.0.0.1 -t boardgame/nodes/motor_1/cmd -m '{"type":"command","command":"motor.set","value":"forward","speed":220}'
```

Stop it:

```bash
mosquitto_pub -h 127.0.0.1 -t boardgame/nodes/motor_1/cmd -m '{"type":"command","command":"motor.set","value":"stop"}'
```
