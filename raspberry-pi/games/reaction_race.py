import random
import time
from dataclasses import dataclass
from typing import Any, Callable

from event_bus import EventBus, GameEvent


StatePublisher = Callable[[dict[str, Any]], None]
CommandPublisher = Callable[[dict[str, Any]], None]
PlayerCountProvider = Callable[[], int]


@dataclass
class ReactionRaceGame:
    event_bus: EventBus
    publish_state: StatePublisher
    publish_command: CommandPublisher
    online_player_count: PlayerCountProvider
    min_players: int = 2
    min_delay_seconds: float = 0.0
    max_delay_seconds: float = 10.0
    restart_delay_seconds: float = 5.0
    blink_count: int = 3
    blink_interval_ms: int = 150
    blink_start_lead_seconds: float = 1.0
    off_repeat_seconds: float = 1.0
    off_repeat_interval_seconds: float = 0.15
    rng: random.Random | None = None
    clock: Callable[[], float] = time.monotonic
    wall_clock: Callable[[], float] = time.time

    def __post_init__(self) -> None:
        self.rng = self.rng or random.Random()
        self.status = "waiting_for_players"
        self.ready_at: float | None = None
        self.led_on_at: float | None = None
        self.finished_at: float | None = None
        self.winner: int | None = None
        self.false_start_player: int | None = None
        self.response_ms: int | None = None
        self.off_repeat_until: float | None = None
        self.next_off_repeat_at: float | None = None

    def start(self) -> None:
        self.event_bus.subscribe("button.press", self.on_button_press)
        self.turn_leds_off()
        self.broadcast_state()

    def tick(self) -> None:
        now = self.clock()
        self.repeat_leds_off_if_needed(now)

        if self.status == "waiting_for_players":
            if self.online_player_count() >= self.min_players:
                self.schedule_round(now)
            return

        if self.status == "ready" and self.ready_at is not None and now >= self.ready_at:
            self.start_reaction_window(now)
            return

        if self.status in {"finished", "false_start"} and self.finished_at is not None:
            if now - self.finished_at >= self.restart_delay_seconds:
                self.reset_round()

    def on_button_press(self, event: GameEvent) -> None:
        if event.player is None:
            return

        if self.status == "ready":
            self.false_start_player = event.player
            self.finish_round(status="false_start", now=self.clock())
            return

        if self.status != "active" or self.winner is not None:
            return

        now = self.clock()
        self.winner = event.player

        reaction_ms = event.payload.get("reaction_ms")

        if isinstance(reaction_ms, int):
            self.response_ms = reaction_ms
        elif self.led_on_at is not None:
            self.response_ms = int((now - self.led_on_at) * 1000)

        self.finish_round(status="finished", now=now)

    def schedule_round(self, now: float) -> None:
        delay = self.rng.uniform(self.min_delay_seconds, self.max_delay_seconds)
        blink_duration = (self.blink_count * 2 * self.blink_interval_ms) / 1000
        total_delay = self.blink_start_lead_seconds + blink_duration + delay
        self.ready_at = now + total_delay
        self.led_on_at = None
        self.finished_at = None
        self.winner = None
        self.false_start_player = None
        self.response_ms = None
        self.off_repeat_until = None
        self.next_off_repeat_at = None
        self.status = "ready"
        self.turn_leds_off()
        self.blink_round_start(self.blink_start_lead_seconds)
        self.arm_reaction_leds(total_delay)
        self.broadcast_state(delay_seconds=round(delay, 3))
        print(f"Reaction Race: round starts after blink + {delay:.2f}s")

    def start_reaction_window(self, now: float) -> None:
        self.status = "active"
        self.led_on_at = now
        self.broadcast_state()
        print("Reaction Race: LEDs on")

    def finish_round(self, status: str, now: float) -> None:
        self.status = status
        self.finished_at = now
        self.start_repeating_leds_off(now)
        self.broadcast_state()

        if status == "false_start":
            print(f"Reaction Race false start: Player {self.false_start_player}")
        else:
            print(f"Reaction Race winner: Player {self.winner} in {self.response_ms}ms")

    def reset_round(self) -> None:
        self.status = "waiting_for_players"
        self.ready_at = None
        self.led_on_at = None
        self.finished_at = None
        self.winner = None
        self.false_start_player = None
        self.response_ms = None
        self.off_repeat_until = None
        self.next_off_repeat_at = None
        self.turn_leds_off()
        self.broadcast_state()

    def turn_leds_on(self) -> None:
        self.publish_command(
            {
                "type": "command",
                "controller_id": "all",
                "command": "led.set",
                "value": 1,
            }
        )

    def turn_leds_off(self) -> None:
        self.publish_command(
            {
                "type": "command",
                "controller_id": "all",
                "command": "led.set",
                "value": 0,
            }
        )

    def start_repeating_leds_off(self, now: float) -> None:
        self.off_repeat_until = now + self.off_repeat_seconds
        self.next_off_repeat_at = now
        self.repeat_leds_off_if_needed(now)

    def repeat_leds_off_if_needed(self, now: float) -> None:
        if self.off_repeat_until is None or self.next_off_repeat_at is None:
            return

        if now > self.off_repeat_until:
            self.off_repeat_until = None
            self.next_off_repeat_at = None
            return

        if now < self.next_off_repeat_at:
            return

        self.turn_leds_off()
        self.next_off_repeat_at = now + self.off_repeat_interval_seconds

    def blink_round_start(self, delay_seconds: float) -> None:
        self.publish_command(
            {
                "type": "command",
                "controller_id": "all",
                "command": "led.blink",
                "count": self.blink_count,
                "interval_ms": self.blink_interval_ms,
                "start_epoch_ms": int((self.wall_clock() + delay_seconds) * 1000),
                "fallback_delay_ms": int(delay_seconds * 1000),
            }
        )

    def arm_reaction_leds(self, delay_seconds: float) -> None:
        self.publish_command(
            {
                "type": "command",
                "controller_id": "all",
                "command": "led.arm",
                "start_epoch_ms": int((self.wall_clock() + delay_seconds) * 1000),
                "fallback_delay_ms": int(delay_seconds * 1000),
            }
        )

    def snapshot(self, delay_seconds: float | None = None) -> dict[str, Any]:
        state = {
            "type": "game_state",
            "game": "reaction_race",
            "status": self.status,
            "min_players": self.min_players,
            "online_players": self.online_player_count(),
            "winner": self.winner,
            "false_start_player": self.false_start_player,
            "response_ms": self.response_ms,
        }

        if delay_seconds is not None:
            state["delay_seconds"] = delay_seconds

        return state

    def broadcast_state(self, delay_seconds: float | None = None) -> None:
        self.publish_state(self.snapshot(delay_seconds))
