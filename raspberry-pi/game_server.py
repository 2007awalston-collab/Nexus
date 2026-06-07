import json
from typing import Any

import paho.mqtt.client as mqtt


MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883

REGISTER_TOPIC = "controller/register"
ASSIGN_TOPIC = "controller/assign"


class NexusGameServer:
    def __init__(self) -> None:
        self.controllers: dict[str, dict[str, Any]] = {}
        self.client = mqtt.Client(client_id="NexusGameServer")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self) -> None:
        print(f"Nexus Connect game server starting on MQTT {MQTT_HOST}:{MQTT_PORT}")
        self.client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
        self.client.loop_forever()

    def on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        print(f"MQTT connected: rc={rc}")
        client.subscribe(REGISTER_TOPIC)
        print(f"Listening for controller registrations on: {REGISTER_TOPIC}")

    def on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        if msg.topic != REGISTER_TOPIC:
            return

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            print(f"Ignoring invalid JSON: {msg.payload!r}")
            return

        if payload.get("type") != "register":
            print(f"Ignoring non-registration message: {payload}")
            return

        controller_id = payload.get("controller_id")
        if not controller_id:
            print(f"Ignoring registration without controller_id: {payload}")
            return

        self.register_controller(controller_id)

    def register_controller(self, controller_id: str) -> None:
        if controller_id not in self.controllers:
            player_number = len(self.controllers) + 1
            self.controllers[controller_id] = {
                "player": player_number,
                "status": "connected",
            }

            print()
            print("Controller Registered:")
            print(controller_id)
            print()
            print("Assigned:")
            print(f"Player {player_number}")
        else:
            player_number = self.controllers[controller_id]["player"]
            self.controllers[controller_id]["status"] = "connected"
            print(f"Controller reconnected: {controller_id} -> Player {player_number}")

        self.publish_player_assignment(controller_id, player_number)

    def publish_player_assignment(self, controller_id: str, player_number: int) -> None:
        payload = {
            "type": "assign_player",
            "controller_id": controller_id,
            "player": player_number,
        }
        self.client.publish(ASSIGN_TOPIC, json.dumps(payload))


if __name__ == "__main__":
    NexusGameServer().start()

