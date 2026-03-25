from __future__ import annotations

import json
import os
from pathlib import Path

from constants import DEFAULT_SETTINGS, SETTINGS_BOUNDS


def _config_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    return base / "pomodoro" / "settings.json"


def load_settings() -> dict[str, int]:
    """Load settings from disk, falling back to defaults on any error."""
    path = _config_path()
    if not path.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        with open(path) as f:
            data: object = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)

    if not isinstance(data, dict):
        return dict(DEFAULT_SETTINGS)

    result = dict(DEFAULT_SETTINGS)
    for key, (lo, hi) in SETTINGS_BOUNDS.items():
        value = data.get(key)
        if isinstance(value, int):
            result[key] = max(lo, min(hi, value))
    return result


def save_settings(settings: dict[str, int]) -> None:
    """Persist settings to disk. Silently ignores write errors."""
    path = _config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
