from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pomodoro.constants import AppSettings, DEFAULT_SETTINGS, SETTINGS_BOUNDS
from pomodoro.storage import load_settings, save_settings


def _default_settings() -> AppSettings:
    return DEFAULT_SETTINGS.copy()


class TestLoadSettings(unittest.TestCase):
    def test_returns_defaults_when_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no" / "settings.json"
            with patch("pomodoro.storage._config_path", return_value=missing):
                result = load_settings()
        self.assertEqual(result, dict(DEFAULT_SETTINGS))

    def test_returns_defaults_on_corrupt_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text("not valid json {{")
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result, dict(DEFAULT_SETTINGS))

    def test_returns_defaults_when_json_is_not_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text("[1, 2, 3]")
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result, dict(DEFAULT_SETTINGS))

    def test_loads_valid_settings(self) -> None:
        data = {
            "work_minutes": 30,
            "short_break_minutes": 10,
            "long_break_minutes": 20,
            "long_break_after": 3,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps(data))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["work_minutes"], 30)
        self.assertEqual(result["long_break_after"], 3)

    def test_clamps_value_above_max(self) -> None:
        _lo, hi = SETTINGS_BOUNDS["work_minutes"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"work_minutes": hi + 999}))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["work_minutes"], hi)

    def test_clamps_value_below_min(self) -> None:
        lo, _hi = SETTINGS_BOUNDS["work_minutes"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"work_minutes": lo - 1}))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["work_minutes"], lo)

    def test_ignores_non_integer_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"work_minutes": "not_an_int"}))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["work_minutes"], DEFAULT_SETTINGS["work_minutes"])

    def test_invalid_bool_values_fall_back_to_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"auto_start_next_phase": 1}))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(
            result["auto_start_next_phase"],
            DEFAULT_SETTINGS["auto_start_next_phase"],
        )

    def test_invalid_notification_mode_falls_back_to_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"notification_mode": "loud"}))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["notification_mode"], DEFAULT_SETTINGS["notification_mode"])

    def test_partial_settings_use_defaults_for_missing_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps({"work_minutes": 45}))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["work_minutes"], 45)
        self.assertEqual(
            result["short_break_minutes"], DEFAULT_SETTINGS["short_break_minutes"]
        )

    def test_loads_new_setting_fields(self) -> None:
        data = {
            "work_minutes": 30,
            "short_break_minutes": 10,
            "long_break_minutes": 20,
            "long_break_after": 3,
            "restore_window_on_complete": True,
            "notification_mode": "toast_sound",
            "repeat_after_minutes": 4,
            "auto_start_next_phase": False,
            "minimize_to_tray_on_close": False,
            "show_countdown_in_tray": False,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps(data))
            with patch("pomodoro.storage._config_path", return_value=path):
                result = load_settings()
        self.assertEqual(result["restore_window_on_complete"], True)
        self.assertEqual(result["notification_mode"], "toast_sound")
        self.assertEqual(result["repeat_after_minutes"], 4)
        self.assertEqual(result["auto_start_next_phase"], False)
        self.assertEqual(result["minimize_to_tray_on_close"], False)
        self.assertEqual(result["show_countdown_in_tray"], False)


class TestSaveSettings(unittest.TestCase):
    def test_creates_file_and_persists_settings(self) -> None:
        settings = _default_settings()
        settings["work_minutes"] = 35
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subdir" / "settings.json"
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(settings)
            saved = json.loads(path.read_text())
        self.assertEqual(saved["work_minutes"], 35)

    def test_roundtrip_load_after_save(self) -> None:
        settings = _default_settings()
        settings["long_break_minutes"] = 20
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(settings)
                result = load_settings()
        self.assertEqual(result["long_break_minutes"], 20)

    def test_roundtrip_persists_new_setting_fields(self) -> None:
        settings = _default_settings()
        settings.update(
            {
                "restore_window_on_complete": True,
                "notification_mode": "toast_sound_repeat",
                "repeat_after_minutes": 6,
                "auto_start_next_phase": False,
                "minimize_to_tray_on_close": False,
                "show_countdown_in_tray": False,
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(settings)
                result = load_settings()
        self.assertEqual(result["restore_window_on_complete"], True)
        self.assertEqual(result["notification_mode"], "toast_sound_repeat")
        self.assertEqual(result["repeat_after_minutes"], 6)
        self.assertEqual(result["auto_start_next_phase"], False)
        self.assertEqual(result["minimize_to_tray_on_close"], False)
        self.assertEqual(result["show_countdown_in_tray"], False)

    def test_silently_ignores_write_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # point path at an existing directory — can't write a directory as a file
            path = Path(tmp)
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(_default_settings())  # must not raise


if __name__ == "__main__":
    unittest.main()
