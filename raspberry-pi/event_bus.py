from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class GameEvent:
    name: str
    controller_id: str
    player: int | None = None
    control: str = ""
    value: Any = None
    payload: dict[str, Any] = field(default_factory=dict)


EventHandler = Callable[[GameEvent], None]


class EventBus:
    def __init__(self) -> None:
        self.handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self.handlers[event_name].append(handler)

    def publish(self, event: GameEvent) -> None:
        for handler in self.handlers.get(event.name, []):
            handler(event)

        for handler in self.handlers.get("*", []):
            handler(event)
