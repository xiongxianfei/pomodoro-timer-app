from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pomodoro.constants import DEFAULT_SETTINGS
from pomodoro.completion_policy import (
    build_completion_decision,
    format_tray_status,
    should_schedule_repeat,
)


class TestBuildCompletionDecision(unittest.TestCase):
    def test_toast_mode_uses_toast_without_sound_or_repeat(self):
        settings = dict(DEFAULT_SETTINGS)
        settings["notification_mode"] = "toast"
        settings["restore_window_on_complete"] = True
        settings["auto_start_next_phase"] = False

        decision = build_completion_decision(settings)

        self.assertFalse(decision.play_sound)
        self.assertTrue(decision.show_toast)
        self.assertTrue(decision.restore_window)
        self.assertFalse(decision.auto_start_next_phase)
        self.assertIsNone(decision.repeat_after_seconds)

    def test_repeat_mode_sets_delay_in_seconds(self):
        settings = dict(DEFAULT_SETTINGS)
        settings["notification_mode"] = "toast_sound_repeat"
        settings["repeat_after_minutes"] = 3

        decision = build_completion_decision(settings)

        self.assertTrue(decision.play_sound)
        self.assertTrue(decision.show_toast)
        self.assertEqual(decision.repeat_after_seconds, 180)
        self.assertTrue(should_schedule_repeat(decision))


class TestFormatTrayStatus(unittest.TestCase):
    def test_paused_prefix_is_included_when_not_running(self):
        text = format_tray_status("Short Break", 4 * 60 + 10, running=False)
        self.assertEqual(text, "Paused - Short Break - 04:10 left")

    def test_running_work_session_omits_paused_prefix(self):
        text = format_tray_status("Work Session", 12 * 60 + 34, running=True)
        self.assertEqual(text, "Work Session - 12:34 left")


if __name__ == "__main__":
    unittest.main()
