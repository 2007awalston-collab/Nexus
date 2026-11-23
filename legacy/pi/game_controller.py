import json
import time
from dataclasses import dataclass, field
from typing import Any

import paho.mqtt.client as mqtt


MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
BASE_TOPIC = "boardgame"


@dataclass
class NodeInfo:
    node_id: str
    role: str = "unknown"
    name: str = ""
    firmware: str = ""
    capabilities: list[dict[str, Any]] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)


class GameController:
    def __init__(self) -> None:
        self.nodes: dict[str, NodeInfo] = {}
        self.motor_state = "stop"
        self.client = mqtt.Client(client_id="PiGameController")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self) -> None:
        print(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
        self.client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
        self.client.loop_forever()

    def on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        print(f"MQTT connected: rc={rc}")
        client.subscribe(f"{BASE_TOPIC}/nodes/+/register")
        client.subscribe(f"{BASE_TOPIC}/nodes/+/heartbeat")
        client.subscribe(f"{BASE_TOPIC}/nodes/+/event")
        print("Listening for node registration, heartbeat, and events.")

    def on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        topic = msg.topic

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            print(f"Ignoring invalid JSON on {topic}: {msg.payload!r}")
            return

        parts = topic.split("/")
        if len(parts) < 4:
            return

        node_id = parts[2]
        message_kind = parts[3]

        if message_kind == "register":
            self.handle_register(node_id, payload)
        elif message_kind == "heartbeat":
            self.handle_heartbeat(node_id, payload)
        elif message_kind == "event":
            self.handle_event(node_id, payload)

    def handle_register(self, node_id: str, payload: dict[str, Any]) -> None:
        info = NodeInfo(
            node_id=node_id,
            role=payload.get("role", "unknown"),
            name=payload.get("name", node_id),
            firmware=payload.get("firmware", ""),
            capabilities=payload.get("capabilities", []),
            last_seen=time.time(),
        )
        self.nodes[node_id] = info
        print(f"Registered {node_id}: role={info.role}, name={info.name}, capabilities={len(info.capabilities)}")

    def handle_heartbeat(self, node_id: str, payload: dict[str, Any]) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].last_seen = time.time()
        else:
            print(f"Heartbeat from unregistered node {node_id}")

    def handle_event(self, node_id: str, payload: dict[str, Any]) -> None:
        event = payload.get("event", "")
        print(f"Event from {node_id}: {event} {payload}")

        if event == "button.press":
            self.toggle_motor()

    def toggle_motor(self) -> None:
        if self.motor_state == "stop":
            self.motor_state = "forward"
        elif self.motor_state == "forward":
            self.motor_state = "reverse"
        else:
            self.motor_state = "stop"

        self.send_motor_command("motor_1", self.motor_state, speed=220)

    def send_motor_command(self, node_id: str, value: str, speed: int = 220) -> None:
        topic = f"{BASE_TOPIC}/nodes/{node_id}/cmd"
        payload = {
            "type": "command",
            "command": "motor.set",
            "value": value,
            "speed": speed,
        }
        self.client.publish(topic, json.dumps(payload))
        print(f"Sent {value} to {node_id}")


if __name__ == "__main__":
    GameController().start()
