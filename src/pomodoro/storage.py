from __future__ import annotations

import json
import os
from pathlib import Path
from typing import cast

from .constants import (
    BOOL_SETTINGS,
    DEFAULT_SETTINGS,
    NOTIFICATION_MODES,
    SETTINGS_BOUNDS,
    AppSettings,
)


def _copy_default_settings() -> AppSettings:
    return cast(AppSettings, dict(DEFAULT_SETTINGS))


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
        return _copy_default_settings()
    try:
        with open(path) as f:
            data: object = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _copy_default_settings()

    if not isinstance(data, dict):
        return _copy_default_settings()

    result: dict[str, object] = dict(DEFAULT_SETTINGS)
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
    return cast(AppSettings, result)


def save_settings(settings: AppSettings) -> None:
    """Persist settings to disk. Silently ignores write errors."""
    path = _config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
