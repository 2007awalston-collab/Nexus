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
        self.assertEqual(commands[-1]["command"], "led.blink")
        self.assertEqual(commands[-1]["count"], 3)

        clock.advance(1.0)
        game.tick()
        self.assertEqual(game.status, "active")
        self.assertEqual(commands[-1]["value"], 1)

        clock.advance(0.250)
        bus.publish(GameEvent(name="button.press", controller_id="A", player=1))

        self.assertEqual(game.status, "finished")
        self.assertEqual(game.winner, 1)
        self.assertEqual(game.response_ms, 250)
        self.assertEqual(commands[-1]["value"], 0)
        self.assertEqual(states[-1]["winner"], 1)

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


if __name__ == "__main__":
    unittest.main()
