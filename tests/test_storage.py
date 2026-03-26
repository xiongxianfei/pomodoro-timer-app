from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pomodoro.constants import DEFAULT_SETTINGS, SETTINGS_BOUNDS
from pomodoro.storage import load_settings, save_settings


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


class TestSaveSettings(unittest.TestCase):
    def test_creates_file_and_persists_settings(self) -> None:
        settings = dict(DEFAULT_SETTINGS)
        settings["work_minutes"] = 35
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "subdir" / "settings.json"
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(settings)
            saved = json.loads(path.read_text())
        self.assertEqual(saved["work_minutes"], 35)

    def test_roundtrip_load_after_save(self) -> None:
        settings = dict(DEFAULT_SETTINGS)
        settings["long_break_minutes"] = 20
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(settings)
                result = load_settings()
        self.assertEqual(result["long_break_minutes"], 20)

    def test_silently_ignores_write_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # point path at an existing directory — can't write a directory as a file
            path = Path(tmp)
            with patch("pomodoro.storage._config_path", return_value=path):
                save_settings(dict(DEFAULT_SETTINGS))  # must not raise


if __name__ == "__main__":
    unittest.main()
