from pathlib import Path
import sys
import importlib
from types import ModuleType
import unittest
from unittest.mock import patch

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


class TestTrayIconContract(unittest.TestCase):
    def test_tray_uses_status_text_and_exposes_all_menu_items(self):
        fake_pystray = ModuleType("pystray")
        fake_pil = ModuleType("PIL")

        created_icons = []

        class FakeImageObj:
            pass

        class FakeDrawer:
            def ellipse(self, *args, **kwargs):
                return None

        class FakeImageModule:
            @staticmethod
            def new(mode, size, color):
                return FakeImageObj()

        class FakeImageDrawModule:
            @staticmethod
            def Draw(img):
                return FakeDrawer()

        class FakeMenuItem:
            def __init__(self, text, action, default=False):
                self.text = text
                self.action = action
                self.default = default

        class FakeMenu:
            SEPARATOR = object()

            def __init__(self, *items):
                self.items = items

        class FakeIcon:
            def __init__(self, name, icon, title, menu):
                self.name = name
                self.icon = icon
                self.title = title
                self.menu = menu
                self.stopped = False
                created_icons.append(self)

            def run(self):
                return None

            def stop(self):
                self.stopped = True

        fake_pystray.Icon = FakeIcon
        fake_pystray.Menu = FakeMenu
        fake_pystray.MenuItem = FakeMenuItem
        fake_pil.Image = FakeImageModule
        fake_pil.ImageDraw = FakeImageDrawModule

        with patch.dict(
            sys.modules,
            {
                "pystray": fake_pystray,
                "PIL": fake_pil,
            },
        ):
            tray = importlib.import_module("pomodoro.tray")
            tray = importlib.reload(tray)

            updates = []
            icon = tray.TrayIcon(
                on_show=lambda: updates.append("show"),
                on_toggle=lambda: updates.append("toggle"),
                on_skip=lambda: updates.append("skip"),
                on_reset=lambda: updates.append("reset"),
                on_add_minute=lambda: updates.append("add"),
                on_settings=lambda: updates.append("settings"),
                on_quit=lambda: updates.append("quit"),
            )

            icon.start("#ff0000", "Paused - Work Session - 25:00 left")
            self.assertEqual(len(created_icons), 1)
            tray_icon = created_icons[0]
            self.assertEqual(tray_icon.title, "Paused - Work Session - 25:00 left")

            labels = [
                item.text
                for item in tray_icon.menu.items
                if item is not FakeMenu.SEPARATOR
            ]
            self.assertEqual(
                labels,
                [
                    "Show Window",
                    "Start / Pause",
                    "Skip",
                    "Reset",
                    "+1 minute",
                    "Settings",
                    "Quit",
                ],
            )

            actionable_items = [
                item for item in tray_icon.menu.items
                if item is not FakeMenu.SEPARATOR
            ]
            for item in actionable_items:
                item.action()
            self.assertEqual(
                updates,
                ["show", "toggle", "skip", "reset", "add", "settings", "quit"],
            )

            icon.update_status_text("Work Session - 24:59 left")
            self.assertEqual(tray_icon.title, "Work Session - 24:59 left")

        sys.modules.pop("pomodoro.tray", None)

    def test_tray_methods_are_noops_when_unavailable(self):
        tray = importlib.import_module("pomodoro.tray")

        with patch.object(tray, "TRAY_AVAILABLE", False):
            icon = tray.TrayIcon()
            icon.start("#00ff00", "Work Session - 25:00 left")
            icon.update_color("#ff0000")
            icon.update_status_text("Paused - Work Session - 24:59 left")
            icon.stop()

            self.assertIsNone(icon._icon)


if __name__ == "__main__":
    unittest.main()
