import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ControllerRecord:
    controller_id: str
    player: int
    online: bool
    last_seen: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "player": self.player,
            "online": self.online,
            "last_seen": self.last_seen,
        }


class ControllerManager:
    def __init__(self, fixed_player_assignments: dict[str, int] | None = None) -> None:
        self.controllers: dict[str, ControllerRecord] = {}
        self.fixed_player_assignments = fixed_player_assignments or {}

    def register(self, controller_id: str) -> tuple[ControllerRecord, bool]:
        now = time.time()

        if controller_id in self.controllers:
            controller = self.controllers[controller_id]
            controller.online = True
            controller.last_seen = now
            return controller, False

        controller = ControllerRecord(
            controller_id=controller_id,
            player=self.player_number_for_controller(controller_id),
            online=True,
            last_seen=now,
        )
        self.controllers[controller_id] = controller
        return controller, True

    def player_number_for_controller(self, controller_id: str) -> int:
        fixed_player = self.fixed_player_assignments.get(controller_id)

        if fixed_player is not None:
            return fixed_player

        return self.next_player_number()

    def mark_seen(self, controller_id: str) -> ControllerRecord | None:
        controller = self.controllers.get(controller_id)

        if controller is None:
            return None

        controller.online = True
        controller.last_seen = time.time()
        return controller

    def mark_inactive_controllers_offline(self, timeout_seconds: float) -> list[ControllerRecord]:
        now = time.time()
        changed: list[ControllerRecord] = []

        for controller in self.controllers.values():
            if controller.online and now - controller.last_seen > timeout_seconds:
                controller.online = False
                changed.append(controller)

        return changed

    def next_player_number(self) -> int:
        used_players = {controller.player for controller in self.controllers.values()}
        used_players.update(self.fixed_player_assignments.values())
        player = 1

        while player in used_players:
            player += 1

        return player

    def get_controller_by_player(self, player: int) -> ControllerRecord | None:
        for controller in self.controllers.values():
            if controller.player == player:
                return controller

        return None

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {
            controller_id: controller.to_dict()
            for controller_id, controller in self.controllers.items()
        }
