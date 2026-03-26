from __future__ import annotations

import threading
import time
from typing import Callable

from .constants import DEFAULT_SETTINGS, WORK, SHORT_BREAK, LONG_BREAK


class PomodoroTimer:
    """
    Pure timer logic — no GUI dependencies.

    Callbacks (called from the countdown thread):
        on_tick()      — fired every second while running
        on_complete()  — fired when remaining reaches zero
    """

    def __init__(
        self,
        settings: dict[str, int] | None = None,
        on_tick: Callable[[], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        self.settings: dict[str, int] = settings if settings is not None else dict(DEFAULT_SETTINGS)
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

    def apply_settings(self, new_settings: dict[str, int]) -> None:
        self.settings.update(new_settings)
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
        key_map: dict[str, str] = {
            WORK: "work_minutes",
            SHORT_BREAK: "short_break_minutes",
            LONG_BREAK: "long_break_minutes",
        }
        return self.settings[key_map[self.phase]] * 60

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
