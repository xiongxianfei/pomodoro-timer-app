from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from .constants import AppSettings


@dataclass(frozen=True, slots=True)
class CompletionDecision:
    play_sound: bool
    show_toast: bool
    restore_window: bool
    auto_start_next_phase: bool
    repeat_after_seconds: Optional[int]


@dataclass(slots=True)
class ReminderState:
    pending_handle: object | None = None

    def arm(self, handle: object) -> None:
        self.pending_handle = handle

    def clear(self) -> object | None:
        handle = self.pending_handle
        self.pending_handle = None
        return handle

    def cancel(self, cancel_callback: Callable[[object], None]) -> bool:
        handle = self.clear()
        if handle is None:
            return False
        cancel_callback(handle)
        return True


def build_completion_decision(settings: AppSettings) -> CompletionDecision:
    notification_mode = settings["notification_mode"]
    play_sound = notification_mode in {"toast_sound", "toast_sound_repeat"}
    repeat_after_seconds = (
        settings["repeat_after_minutes"] * 60
        if notification_mode == "toast_sound_repeat"
        else None
    )
    return CompletionDecision(
        play_sound=play_sound,
        show_toast=True,
        restore_window=settings["restore_window_on_complete"],
        auto_start_next_phase=settings["auto_start_next_phase"],
        repeat_after_seconds=repeat_after_seconds,
    )


def should_schedule_repeat(decision: CompletionDecision) -> bool:
    return decision.repeat_after_seconds is not None


def format_tray_status(phase_label: str, remaining: int, running: bool) -> str:
    minutes, seconds = divmod(remaining, 60)
    status = f"{phase_label} - {minutes:02d}:{seconds:02d} left"
    if running:
        return status
    return f"Paused - {status}"
