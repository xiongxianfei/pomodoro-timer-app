from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


from pomodoro.stats import load_stats, record_pomodoro


class TestLoadStats(unittest.TestCase):
    def test_returns_zeros_when_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no" / "stats.json"
            with patch("pomodoro.stats._stats_path", return_value=missing):
                stats = load_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["today"], 0)

    def test_returns_zeros_on_corrupt_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text("{{bad}}")
            with patch("pomodoro.stats._stats_path", return_value=path):
                stats = load_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["today"], 0)

    def test_loads_existing_counts(self) -> None:
        data = {"total": 42, "today": 3, "last_date": "2099-01-01"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text(json.dumps(data))
            with patch("pomodoro.stats._stats_path", return_value=path):
                with patch("pomodoro.stats._today", return_value="2099-01-01"):
                    stats = load_stats()
        self.assertEqual(stats["total"], 42)
        self.assertEqual(stats["today"], 3)

    def test_resets_today_on_new_day(self) -> None:
        data = {"total": 10, "today": 5, "last_date": "2020-01-01"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text(json.dumps(data))
            with patch("pomodoro.stats._stats_path", return_value=path):
                with patch("pomodoro.stats._today", return_value="2020-01-02"):
                    stats = load_stats()
        self.assertEqual(stats["total"], 10)
        self.assertEqual(stats["today"], 0)

    def test_negative_values_clamped_to_zero(self) -> None:
        data = {"total": -5, "today": -1, "last_date": "2099-01-01"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text(json.dumps(data))
            with patch("pomodoro.stats._stats_path", return_value=path):
                with patch("pomodoro.stats._today", return_value="2099-01-01"):
                    stats = load_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["today"], 0)


class TestRecordPomodoro(unittest.TestCase):
    def test_increments_total_and_today(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            with patch("pomodoro.stats._stats_path", return_value=path):
                stats = record_pomodoro()
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["today"], 1)

    def test_accumulates_across_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            with patch("pomodoro.stats._stats_path", return_value=path):
                record_pomodoro()
                record_pomodoro()
                stats = record_pomodoro()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["today"], 3)

    def test_today_resets_but_total_persists(self) -> None:
        data = {"total": 5, "today": 3, "last_date": "2020-06-01"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text(json.dumps(data))
            with patch("pomodoro.stats._stats_path", return_value=path):
                with patch("pomodoro.stats._today", return_value="2020-06-02"):
                    stats = record_pomodoro()
        self.assertEqual(stats["total"], 6)
        self.assertEqual(stats["today"], 1)


if __name__ == "__main__":
    unittest.main()
