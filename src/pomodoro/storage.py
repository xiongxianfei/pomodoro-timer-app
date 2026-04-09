from __future__ import annotations

import json
import os
from pathlib import Path

from .constants import (
    DEFAULT_SETTINGS,
    NOTIFICATION_MODES,
    SETTINGS_BOUNDS,
    AppSettings,
)

BOOL_SETTINGS = (
    "restore_window_on_complete",
    "auto_start_next_phase",
    "minimize_to_tray_on_close",
    "show_countdown_in_tray",
)


def _config_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    return base / "pomodoro" / "settings.json"


def load_settings() -> AppSettings:
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

    result: AppSettings = dict(DEFAULT_SETTINGS)
    for key, (lo, hi) in SETTINGS_BOUNDS.items():
        value = data.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            result[key] = max(lo, min(hi, value))
    for key in BOOL_SETTINGS:
        value = data.get(key)
        if isinstance(value, bool):
            result[key] = value
    value = data.get("notification_mode")
    if isinstance(value, str) and value in NOTIFICATION_MODES:
        result["notification_mode"] = value
    return result


def save_settings(settings: AppSettings) -> None:
    """Persist settings to disk. Silently ignores write errors."""
    path = _config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
