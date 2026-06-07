import json
import time
from typing import Any

import paho.mqtt.client as mqtt

from controller_manager import ControllerManager
from controller_config import FIXED_PLAYER_ASSIGNMENTS


MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883

REGISTER_TOPIC = "controller/register"
ASSIGN_TOPIC = "controller/assign"
HEARTBEAT_TOPIC = "controller/heartbeat"
ONLINE_TIMEOUT_SECONDS = 15


class NexusGameServer:
    def __init__(self) -> None:
        self.controller_manager = ControllerManager(FIXED_PLAYER_ASSIGNMENTS)
        self.client = mqtt.Client(client_id="NexusGameServer")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self) -> None:
        print(f"Nexus Connect game server starting on MQTT {MQTT_HOST}:{MQTT_PORT}")
        self.client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
        self.client.loop_start()

        try:
            while True:
                self.check_controller_timeouts()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping Nexus Connect game server.")
            self.client.loop_stop()
            self.client.disconnect()

    def on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        print(f"MQTT connected: rc={rc}")
        client.subscribe(REGISTER_TOPIC)
        client.subscribe(HEARTBEAT_TOPIC)
        print(f"Listening for controller registrations on: {REGISTER_TOPIC}")
        print(f"Listening for controller heartbeats on: {HEARTBEAT_TOPIC}")

    def on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            print(f"Ignoring invalid JSON: {msg.payload!r}")
            return

        if msg.topic == REGISTER_TOPIC:
            self.handle_registration(payload)
        elif msg.topic == HEARTBEAT_TOPIC:
            self.handle_heartbeat(payload)

    def handle_registration(self, payload: dict[str, Any]) -> None:
        if payload.get("type") != "register":
            print(f"Ignoring non-registration message: {payload}")
            return

        controller_id = payload.get("controller_id")
        if not controller_id:
            print(f"Ignoring registration without controller_id: {payload}")
            return

        self.register_controller(controller_id)

    def handle_heartbeat(self, payload: dict[str, Any]) -> None:
        if payload.get("type") != "heartbeat":
            print(f"Ignoring non-heartbeat message: {payload}")
            return

        controller_id = payload.get("controller_id")
        if not controller_id:
            print(f"Ignoring heartbeat without controller_id: {payload}")
            return

        controller = self.controller_manager.mark_seen(controller_id)

        if controller is None:
            print(f"Heartbeat from unregistered controller: {controller_id}")

    def register_controller(self, controller_id: str) -> None:
        controller, is_new = self.controller_manager.register(controller_id)

        if is_new:
            print()
            print("Controller Registered:")
            print(controller_id)
            print()
            print("Assigned:")
            print(f"Player {controller.player}")
        else:
            print(f"Controller reconnected: {controller_id} -> Player {controller.player}")

        self.publish_player_assignment(controller_id, controller.player)

    def publish_player_assignment(self, controller_id: str, player_number: int) -> None:
        payload = {
            "type": "assign_player",
            "controller_id": controller_id,
            "player": player_number,
        }
        self.client.publish(ASSIGN_TOPIC, json.dumps(payload, separators=(",", ":")))

    def check_controller_timeouts(self) -> None:
        offline_controllers = self.controller_manager.mark_inactive_controllers_offline(
            ONLINE_TIMEOUT_SECONDS
        )

        for controller in offline_controllers:
            print(f"Controller offline: Player {controller.player} ({controller.controller_id})")


if __name__ == "__main__":
    NexusGameServer().start()
