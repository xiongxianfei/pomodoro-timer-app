from __future__ import annotations

import threading
import time
from typing import Callable, cast

from .constants import (
    DEFAULT_SETTINGS,
    WORK,
    SHORT_BREAK,
    LONG_BREAK,
    AppSettings,
    TimerSettingsUpdate,
)


class PomodoroTimer:
    """
    Pure timer logic — no GUI dependencies.

    Callbacks (called from the countdown thread):
        on_tick()      — fired every second while running
        on_complete()  — fired when remaining reaches zero
    """

    def __init__(
        self,
        settings: AppSettings | None = None,
        on_tick: Callable[[], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        self.settings: AppSettings = cast(
            AppSettings,
            settings.copy() if settings is not None else DEFAULT_SETTINGS.copy(),
        )
        self.phase: str = WORK
        self.pomodoros_done: int = 0
        self.running: bool = False
        self.remaining: int = self._phase_seconds()
        self._stop_event: threading.Event = threading.Event()
        self._on_tick = on_tick
        self._on_complete = on_complete

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._stop_event = threading.Event()
        self.running = True
        threading.Thread(
            target=self._countdown, args=(self._stop_event,), daemon=True
        ).start()

    def stop(self) -> None:
        self._stop_event.set()
        self.running = False

    def skip(self) -> None:
        self.stop()
        self.advance_phase()

    def reset(self) -> None:
        self.stop()
        self.remaining = self._phase_seconds()

    def advance_phase(self) -> None:
        if self.phase == WORK:
            self.pomodoros_done += 1
            if self.pomodoros_done % self.settings["long_break_after"] == 0:
                self.phase = LONG_BREAK
            else:
                self.phase = SHORT_BREAK
        else:
            self.phase = WORK
        self.remaining = self._phase_seconds()

    def apply_settings(self, new_settings: TimerSettingsUpdate) -> None:
        old_settings = self.settings.copy()
        updated = self.settings.copy()
        updated.update(new_settings)
        duration_changed = self._duration_settings_changed(new_settings, old_settings)
        self.settings = cast(AppSettings, updated)
        if duration_changed:
            self.remaining = self._phase_seconds()

    @property
    def session_display(self) -> tuple[int, int]:
        """Returns (completed, total) for the current cycle."""
        n = self.settings["long_break_after"]
        done = self.pomodoros_done % n
        if done == 0:
            done = n if self.pomodoros_done > 0 else 0
        return done, n

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _phase_seconds(self) -> int:
        if self.phase == WORK:
            return self.settings["work_minutes"] * 60
        if self.phase == SHORT_BREAK:
            return self.settings["short_break_minutes"] * 60
        if self.phase == LONG_BREAK:
            return self.settings["long_break_minutes"] * 60
        raise ValueError(f"Unknown phase: {self.phase}")

    def _duration_settings_changed(
        self,
        new_settings: TimerSettingsUpdate,
        old_settings: AppSettings,
    ) -> bool:
        if "work_minutes" in new_settings and new_settings["work_minutes"] != old_settings["work_minutes"]:
            return True
        if "short_break_minutes" in new_settings and new_settings["short_break_minutes"] != old_settings["short_break_minutes"]:
            return True
        if "long_break_minutes" in new_settings and new_settings["long_break_minutes"] != old_settings["long_break_minutes"]:
            return True
        if "long_break_after" in new_settings and new_settings["long_break_after"] != old_settings["long_break_after"]:
            return True
        if "repeat_after_minutes" in new_settings and new_settings["repeat_after_minutes"] != old_settings["repeat_after_minutes"]:
            return True
        return False

    def _countdown(self, stop_event: threading.Event) -> None:
        while not stop_event.is_set() and self.remaining > 0:
            time.sleep(1)
            if not stop_event.is_set():
                self.remaining -= 1
                if self._on_tick:
                    self._on_tick()

        if not stop_event.is_set() and self.remaining == 0:
            if self._on_complete:
                self._on_complete()
