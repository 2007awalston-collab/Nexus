import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from event_bus import EventBus, GameEvent
from games.reaction_race import ReactionRaceGame


class ManualClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class ReactionRaceGameTest(unittest.TestCase):
    def make_game(self, online_players: int = 2) -> tuple[ReactionRaceGame, EventBus, list, list, ManualClock]:
        states = []
        commands = []
        bus = EventBus()
        clock = ManualClock()
        game = ReactionRaceGame(
            bus,
            states.append,
            commands.append,
            lambda: online_players,
            lambda: ["A", "B"] if online_players >= 2 else ["A"],
            {},
            min_delay_seconds=1.0,
            max_delay_seconds=1.0,
            restart_delay_seconds=5.0,
            rng=random.Random(1),
            clock=clock,
        )
        game.start()
        return game, bus, states, commands, clock

    def test_leds_turn_on_after_random_wait_and_first_press_wins(self) -> None:
        game, bus, states, commands, clock = self.make_game()

        game.tick()
        self.assertEqual(game.status, "ready")
        blink_commands = [command for command in commands if command.get("command") == "led.blink"]
        arm_commands = [command for command in commands if command.get("command") == "led.arm"]

        self.assertEqual(len(blink_commands), 2)
        self.assertEqual(len(arm_commands), 2)
        self.assertEqual(blink_commands[0]["count"], 3)
        self.assertEqual(blink_commands[0]["fallback_delay_ms"], 1000)

        clock.advance(2.9)
        game.tick()
        self.assertEqual(game.status, "active")
        self.assertEqual(commands[-1]["command"], "led.arm")

        clock.advance(0.250)
        bus.publish(GameEvent(name="button.press", controller_id="A", player=1))

        self.assertEqual(game.status, "finished")
        self.assertEqual(game.winner, 1)
        self.assertEqual(game.response_ms, 250)
        self.assertEqual(commands[-1]["value"], 0)
        self.assertEqual(states[-1]["winner"], 1)

        off_command_count = len(
            [command for command in commands if command.get("command") == "led.set" and command.get("value") == 0]
        )
        clock.advance(0.15)
        game.tick()
        self.assertGreater(
            len(
                [command for command in commands if command.get("command") == "led.set" and command.get("value") == 0]
            ),
            off_command_count,
        )

    def test_press_before_led_turns_on_is_false_start(self) -> None:
        game, bus, states, commands, _clock = self.make_game()

        game.tick()
        bus.publish(GameEvent(name="button.press", controller_id="A", player=2))

        self.assertEqual(game.status, "false_start")
        self.assertEqual(game.false_start_player, 2)
        self.assertIsNone(game.winner)
        self.assertEqual(commands[-1]["value"], 0)
        self.assertEqual(states[-1]["false_start_player"], 2)

    def test_waits_for_two_online_players(self) -> None:
        game, _bus, _states, commands, _clock = self.make_game(online_players=1)

        game.tick()

        self.assertEqual(game.status, "waiting_for_players")
        self.assertEqual(commands[-1]["value"], 0)

    def test_applies_per_controller_led_timing_offsets(self) -> None:
        states = []
        commands = []
        bus = EventBus()
        clock = ManualClock()
        game = ReactionRaceGame(
            bus,
            states.append,
            commands.append,
            lambda: 2,
            lambda: ["A", "B"],
            {"B": -120},
            min_delay_seconds=1.0,
            max_delay_seconds=1.0,
            rng=random.Random(1),
            clock=clock,
            wall_clock=lambda: 100.0,
        )
        game.start()

        game.tick()
        arm_commands = [command for command in commands if command.get("command") == "led.arm"]

        self.assertEqual(arm_commands[0]["controller_id"], "A")
        self.assertEqual(arm_commands[0]["fallback_delay_ms"], 2900)
        self.assertEqual(arm_commands[1]["controller_id"], "B")
        self.assertEqual(arm_commands[1]["fallback_delay_ms"], 2780)


if __name__ == "__main__":
    unittest.main()
