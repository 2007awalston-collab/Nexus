# Legacy code

Earlier versions of Nexus Connect, kept for reference. The current system lives in `raspberry-pi/` and `esp32_controller/`.

- `pi/game_controller.py`: the first Raspberry Pi controller service. It tracked registered nodes and routed simple game commands.
- `esp32/BoardGameNode/`: a generic ESP32 node template for buttons, LEDs, OLEDs and motors.
- `esp32/examples/ButtonNode/`: a minimal button controller.
- `esp32/examples/MotorNode/`: a TB6612FNG motor controller on pins D2 to D5.

These sketches use the earlier `boardgame/nodes/...` MQTT topics. Set `ssid`, `password` and `mqttServer` at the top of each sketch before uploading.
