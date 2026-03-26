from __future__ import annotations

import json
import time
import unittest
from unittest.mock import MagicMock, patch

from pomodoro.updater import _parse_version, check_for_update


class TestParseVersion(unittest.TestCase):
    def test_parses_with_v_prefix(self) -> None:
        self.assertEqual(_parse_version("v1.2.3"), (1, 2, 3))

    def test_parses_without_prefix(self) -> None:
        self.assertEqual(_parse_version("1.2.3"), (1, 2, 3))

    def test_single_digit_parts(self) -> None:
        self.assertEqual(_parse_version("v0.0.1"), (0, 0, 1))

    def test_version_comparison_newer(self) -> None:
        self.assertGreater(_parse_version("v1.1.0"), _parse_version("v1.0.9"))

    def test_version_comparison_older(self) -> None:
        self.assertLess(_parse_version("v1.0.0"), _parse_version("v2.0.0"))

    def test_same_version(self) -> None:
        self.assertEqual(_parse_version("v1.0.3"), _parse_version("1.0.3"))


class TestCheckForUpdate(unittest.TestCase):
    def _fake_response(self, tag: str) -> MagicMock:
        body = json.dumps({"tag_name": tag}).encode()
        resp = MagicMock()
        resp.read.return_value = body
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        return resp

    def test_calls_callback_when_newer_version_available(self) -> None:
        received: list[str] = []
        with patch("pomodoro.updater.urllib.request.urlopen", return_value=self._fake_response("v9.9.9")):
            check_for_update("v1.0.0", received.append)
            time.sleep(0.2)
        self.assertEqual(received, ["v9.9.9"])

    def test_no_callback_when_already_up_to_date(self) -> None:
        received: list[str] = []
        with patch("pomodoro.updater.urllib.request.urlopen", return_value=self._fake_response("v1.0.0")):
            check_for_update("v1.0.0", received.append)
            time.sleep(0.2)
        self.assertEqual(received, [])

    def test_no_callback_when_current_is_newer(self) -> None:
        received: list[str] = []
        with patch("pomodoro.updater.urllib.request.urlopen", return_value=self._fake_response("v0.9.0")):
            check_for_update("v1.0.0", received.append)
            time.sleep(0.2)
        self.assertEqual(received, [])

    def test_silently_ignores_network_error(self) -> None:
        received: list[str] = []
        with patch("pomodoro.updater.urllib.request.urlopen", side_effect=OSError("no network")):
            check_for_update("v1.0.0", received.append)
            time.sleep(0.2)
        self.assertEqual(received, [])

    def test_silently_ignores_missing_tag_field(self) -> None:
        received: list[str] = []
        resp = MagicMock()
        resp.read.return_value = json.dumps({}).encode()
        resp.__enter__ = lambda s: s
        resp.__exit__ = MagicMock(return_value=False)
        with patch("pomodoro.updater.urllib.request.urlopen", return_value=resp):
            check_for_update("v1.0.0", received.append)
            time.sleep(0.2)
        self.assertEqual(received, [])


if __name__ == "__main__":
    unittest.main()
