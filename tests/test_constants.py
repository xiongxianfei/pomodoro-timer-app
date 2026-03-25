import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from constants import (
    WORK, SHORT_BREAK, LONG_BREAK,
    PHASE_LABELS, PHASE_COLORS, DEFAULT_SETTINGS,
)


class TestPhaseConstants(unittest.TestCase):
    def test_all_phases_have_labels(self):
        for phase in (WORK, SHORT_BREAK, LONG_BREAK):
            self.assertIn(phase, PHASE_LABELS)

    def test_all_phases_have_colors(self):
        for phase in (WORK, SHORT_BREAK, LONG_BREAK):
            self.assertIn(phase, PHASE_COLORS)

    def test_colors_are_valid_hex(self):
        for phase, color in PHASE_COLORS.items():
            self.assertRegex(color, r"^#[0-9a-fA-F]{6}$", f"Invalid color for {phase}")

    def test_labels_are_non_empty_strings(self):
        for phase, label in PHASE_LABELS.items():
            self.assertIsInstance(label, str)
            self.assertTrue(len(label) > 0)


class TestDefaultSettings(unittest.TestCase):
    REQUIRED_KEYS = ["work_minutes", "short_break_minutes", "long_break_minutes", "long_break_after"]

    def test_all_required_keys_present(self):
        for key in self.REQUIRED_KEYS:
            self.assertIn(key, DEFAULT_SETTINGS)

    def test_all_values_are_positive_integers(self):
        for key, value in DEFAULT_SETTINGS.items():
            self.assertIsInstance(value, int, f"{key} should be int")
            self.assertGreater(value, 0, f"{key} should be positive")

    def test_work_duration_is_standard(self):
        self.assertEqual(DEFAULT_SETTINGS["work_minutes"], 25)

    def test_long_break_is_longer_than_short_break(self):
        self.assertGreater(
            DEFAULT_SETTINGS["long_break_minutes"],
            DEFAULT_SETTINGS["short_break_minutes"],
        )


if __name__ == "__main__":
    unittest.main()
