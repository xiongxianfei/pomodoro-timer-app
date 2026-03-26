from __future__ import annotations

import json
import threading
import urllib.request
from typing import Callable

RELEASES_API = (
    "https://api.github.com/repos/xiongxianfei/pomodoro-timer-app/releases/latest"
)


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convert 'v1.2.3' or '1.2.3' to (1, 2, 3)."""
    return tuple(int(x) for x in tag.lstrip("v").split("."))


def check_for_update(current_version: str, callback: Callable[[str], None]) -> None:
    """Check GitHub for a newer release in a background thread.

    Calls callback(latest_tag) if a newer version is available.
    Silently ignores all network / parse errors.
    """

    def _check() -> None:
        try:
            req = urllib.request.Request(
                RELEASES_API,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "pomodoro-timer-app",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            latest: str = data.get("tag_name", "")
            if latest and _parse_version(latest) > _parse_version(current_version):
                callback(latest)
        except Exception:
            pass

    threading.Thread(target=_check, daemon=True).start()
