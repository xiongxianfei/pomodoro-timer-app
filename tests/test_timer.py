from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pomodoro.timer import PomodoroTimer
from pomodoro.constants import WORK, SHORT_BREAK, LONG_BREAK


class TestInitialState(unittest.TestCase):
    def setUp(self):
        self.t = PomodoroTimer()

    def test_starts_in_work_phase(self):
        self.assertEqual(self.t.phase, WORK)

    def test_initial_remaining_matches_work_setting(self):
        self.assertEqual(self.t.remaining, self.t.settings["work_minutes"] * 60)

    def test_not_running(self):
        self.assertFalse(self.t.running)

    def test_no_pomodoros_done(self):
        self.assertEqual(self.t.pomodoros_done, 0)


class TestPhaseTransitions(unittest.TestCase):
    def setUp(self):
        self.t = PomodoroTimer()

    def test_work_advances_to_short_break(self):
        self.t.advance_phase()
        self.assertEqual(self.t.phase, SHORT_BREAK)

    def test_short_break_returns_to_work(self):
        self.t.advance_phase()  # WORK -> SHORT_BREAK
        self.t.advance_phase()  # SHORT_BREAK -> WORK
        self.assertEqual(self.t.phase, WORK)

    def test_fourth_pomodoro_triggers_long_break(self):
        for _ in range(3):
            self.t.advance_phase()  # WORK -> SHORT_BREAK
            self.t.advance_phase()  # SHORT_BREAK -> WORK
        self.t.advance_phase()      # 4th WORK -> LONG_BREAK
        self.assertEqual(self.t.phase, LONG_BREAK)

    def test_long_break_returns_to_work(self):
        for _ in range(4):
            self.t.advance_phase()
            if self.t.phase != WORK:
                self.t.advance_phase()
        self.assertEqual(self.t.phase, WORK)

    def test_pomodoros_done_increments_on_work_complete(self):
        self.t.advance_phase()
        self.assertEqual(self.t.pomodoros_done, 1)

    def test_pomodoros_done_does_not_increment_on_break_complete(self):
        self.t.advance_phase()  # WORK -> SHORT_BREAK (pomodoros_done = 1)
        self.t.advance_phase()  # SHORT_BREAK -> WORK (pomodoros_done still 1)
        self.assertEqual(self.t.pomodoros_done, 1)

    def test_remaining_resets_after_phase_change(self):
        self.t.advance_phase()
        self.assertEqual(self.t.remaining, self.t.settings["short_break_minutes"] * 60)


class TestSessionDisplay(unittest.TestCase):
    def setUp(self):
        self.t = PomodoroTimer()

    def test_initial_display(self):
        done, total = self.t.session_display
        self.assertEqual(done, 0)
        self.assertEqual(total, 4)

    def test_display_after_one_pomodoro(self):
        self.t.advance_phase()
        done, total = self.t.session_display
        self.assertEqual(done, 1)

    def test_display_shows_full_at_end_of_cycle(self):
        # After 4 pomodoros the counter shows 4/4 (full cycle just completed)
        for _ in range(4):
            self.t.advance_phase()  # WORK -> break
            self.t.advance_phase()  # break -> WORK
        done, total = self.t.session_display
        self.assertEqual(done, total)

    def test_display_shows_full_at_long_break_threshold(self):
        for _ in range(4):
            self.t.advance_phase()
            if self.t.phase != WORK:
                self.t.advance_phase()
        # After completing 4 pomodoros, at long break boundary
        # Advance to long break
        self.t2 = PomodoroTimer()
        for _ in range(3):
            self.t2.advance_phase()
            self.t2.advance_phase()
        self.t2.advance_phase()  # -> LONG_BREAK, pomodoros_done = 4
        done, total = self.t2.session_display
        self.assertEqual(done, total)


class TestApplySettings(unittest.TestCase):
    def setUp(self):
        self.t = PomodoroTimer()

    def test_apply_settings_updates_values(self):
        self.t.apply_settings({"work_minutes": 50})
        self.assertEqual(self.t.settings["work_minutes"], 50)

    def test_apply_settings_resets_remaining(self):
        self.t.apply_settings({"work_minutes": 50})
        self.assertEqual(self.t.remaining, 50 * 60)

    def test_partial_update_preserves_other_settings(self):
        original_short = self.t.settings["short_break_minutes"]
        self.t.apply_settings({"work_minutes": 50})
        self.assertEqual(self.t.settings["short_break_minutes"], original_short)

    def test_apply_settings_accepts_partial_bool_update(self):
        self.t.remaining = 123
        self.t.apply_settings({"auto_start_next_phase": False})
        self.assertEqual(self.t.remaining, 123)
        self.assertFalse(self.t.settings["auto_start_next_phase"])


class TestInvalidPhaseHandling(unittest.TestCase):
    def test_phase_seconds_raises_on_unknown_phase(self):
        t = PomodoroTimer()
        t.phase = "invalid_phase"
        with self.assertRaises(ValueError):
            t._phase_seconds()


class TestSkipAndReset(unittest.TestCase):
    def setUp(self):
        self.t = PomodoroTimer()

    def test_skip_advances_phase(self):
        self.t.skip()
        self.assertEqual(self.t.phase, SHORT_BREAK)

    def test_reset_restores_remaining(self):
        self.t.remaining = 10
        self.t.reset()
        self.assertEqual(self.t.remaining, self.t.settings["work_minutes"] * 60)

    def test_reset_stays_in_same_phase(self):
        self.t.reset()
        self.assertEqual(self.t.phase, WORK)


class TestCallbacks(unittest.TestCase):
    def test_on_tick_is_called(self):
        ticks = []
        t = PomodoroTimer(on_tick=lambda: ticks.append(1))
        t._on_tick()
        self.assertEqual(len(ticks), 1)

    def test_on_complete_is_called(self):
        completed = []
        t = PomodoroTimer(on_complete=lambda: completed.append(1))
        t._on_complete()
        self.assertEqual(len(completed), 1)

    def test_no_error_without_callbacks(self):
        # Countdown internally guards with `if self._on_tick`, so None is safe
        t = PomodoroTimer()
        self.assertIsNone(t._on_tick)
        self.assertIsNone(t._on_complete)


if __name__ == "__main__":
    unittest.main()
