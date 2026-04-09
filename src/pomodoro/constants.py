from __future__ import annotations

from typing import Literal, TypedDict

APP_VERSION: str = "1.0.4"

WORK: str = "work"
SHORT_BREAK: str = "short_break"
LONG_BREAK: str = "long_break"

PHASE_LABELS: dict[str, str] = {
    WORK: "Work Session",
    SHORT_BREAK: "Short Break",
    LONG_BREAK: "Long Break",
}

PHASE_COLORS: dict[str, str] = {
    WORK: "#c0392b",
    SHORT_BREAK: "#27ae60",
    LONG_BREAK: "#2980b9",
}

NotificationMode = Literal["toast", "toast_sound", "toast_sound_repeat"]


class AppSettings(TypedDict):
    work_minutes: int
    short_break_minutes: int
    long_break_minutes: int
    long_break_after: int
    restore_window_on_complete: bool
    notification_mode: NotificationMode
    repeat_after_minutes: int
    auto_start_next_phase: bool
    minimize_to_tray_on_close: bool
    show_countdown_in_tray: bool


INT_SETTINGS: tuple[str, ...] = (
    "work_minutes",
    "short_break_minutes",
    "long_break_minutes",
    "long_break_after",
    "repeat_after_minutes",
)

BOOL_SETTINGS: tuple[str, ...] = (
    "restore_window_on_complete",
    "auto_start_next_phase",
    "minimize_to_tray_on_close",
    "show_countdown_in_tray",
)


DEFAULT_SETTINGS: AppSettings = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "long_break_after": 4,
    "restore_window_on_complete": False,
    "notification_mode": "toast",
    "repeat_after_minutes": 2,
    "auto_start_next_phase": True,
    "minimize_to_tray_on_close": True,
    "show_countdown_in_tray": True,
}

# Inclusive (min, max) bounds for each setting
SETTINGS_BOUNDS: dict[str, tuple[int, int]] = {
    "work_minutes":        (1, 120),
    "short_break_minutes": (1, 60),
    "long_break_minutes":  (1, 120),
    "long_break_after":    (1, 10),
    "repeat_after_minutes": (1, 10),
}

NOTIFICATION_MODES: tuple[NotificationMode, ...] = (
    "toast",
    "toast_sound",
    "toast_sound_repeat",
)
