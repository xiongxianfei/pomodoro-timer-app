from __future__ import annotations

import os
import sys
import tkinter as tk
import winsound
import webbrowser

from .constants import APP_VERSION, PHASE_LABELS, PHASE_COLORS, WORK
from .completion_policy import (
    CompletionDecision,
    ReminderState,
    build_completion_decision,
    format_tray_status,
    should_schedule_repeat,
)
from .storage import load_settings, save_settings
from .timer import PomodoroTimer
from .tray import TrayIcon, TRAY_AVAILABLE
from .settings_dialog import SettingsDialog
from .stats import Stats, load_stats, record_pomodoro
from .updater import check_for_update

try:
    from winotify import Notification as WinNotification
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False


def _resource_path(filename: str) -> str:
    """Resolve path to a bundled resource (works for both dev and PyInstaller exe)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base, filename)


class PomodoroApp:
    """Main application window. Wires together the timer, tray, and settings dialog."""

    TRAY_TITLE = "Pomodoro Timer"

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        try:
            self.root.iconbitmap(_resource_path("icon.ico"))
        except Exception:
            pass

        settings = load_settings()
        self.timer = PomodoroTimer(
            settings=settings,
            on_tick=lambda: self.root.after(0, self._refresh_ui),  # type: ignore[arg-type]
            on_complete=lambda: self.root.after(0, self._on_session_complete),  # type: ignore[arg-type]
        )

        self._stats: Stats = load_stats()
        self._repeat_reminder = ReminderState()
        self._build_ui()

        self.tray = TrayIcon(
            on_show=lambda: self.root.after(0, self._show_window_from_interaction),
            on_toggle=lambda: self.root.after(0, self.toggle),
            on_skip=lambda: self.root.after(0, self.skip),
            on_reset=lambda: self.root.after(0, self.reset),
            on_add_minute=lambda: self.root.after(0, self.add_minute),
            on_settings=lambda: self.root.after(0, self.open_settings),
            on_quit=lambda: self.root.after(0, self.quit_app),
        )
        if TRAY_AVAILABLE:
            self.tray.start(PHASE_COLORS[self.timer.phase], self._tray_status_text())

        self._refresh_ui()
        check_for_update(APP_VERSION, self._on_update_available)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = self.root
        root.configure(bg="#2c2c2c")
        pad = {"padx": 20, "pady": 6}

        self._phase_var = tk.StringVar()
        self._time_var = tk.StringVar()
        self._counter_var = tk.StringVar()
        self._stats_var = tk.StringVar()
        self._update_var = tk.StringVar()

        tk.Label(
            root, textvariable=self._phase_var,
            font=("Segoe UI", 14), bg="#2c2c2c", fg="#ecf0f1",
        ).pack(**pad)

        self._time_label = tk.Label(
            root, textvariable=self._time_var,
            font=("Segoe UI", 56, "bold"), bg="#2c2c2c", fg="#e74c3c",
        )
        self._time_label.pack(padx=20, pady=4)

        btn_row = tk.Frame(root, bg="#2c2c2c")
        btn_row.pack(**pad)

        self._start_btn = tk.Button(
            btn_row, text="Start", width=10, command=self.toggle,
            bg="#e74c3c", fg="white", relief="flat", font=("Segoe UI", 11), cursor="hand2",
        )
        self._start_btn.pack(side="left", padx=6)

        tk.Button(
            btn_row, text="Skip", width=8, command=self.skip,
            bg="#7f8c8d", fg="white", relief="flat", font=("Segoe UI", 11), cursor="hand2",
        ).pack(side="left", padx=6)

        tk.Button(
            root, text="Reset", width=10, command=self.reset,
            bg="#7f8c8d", fg="white", relief="flat", font=("Segoe UI", 11), cursor="hand2",
        ).pack(pady=2)

        tk.Label(
            root, textvariable=self._counter_var,
            font=("Segoe UI", 12), bg="#2c2c2c", fg="#bdc3c7",
        ).pack(**pad)

        tk.Button(
            root, text="Settings", width=10, command=self.open_settings,
            bg="#34495e", fg="white", relief="flat", font=("Segoe UI", 11), cursor="hand2",
        ).pack(pady=(2, 8))

        tk.Label(
            root, textvariable=self._stats_var,
            font=("Segoe UI", 9), bg="#2c2c2c", fg="#7f8c8d",
        ).pack(pady=(0, 4))

        self._update_label = tk.Label(
            root, textvariable=self._update_var,
            font=("Segoe UI", 9), bg="#2c2c2c", fg="#f39c12",
            cursor="hand2",
        )
        self._update_label.pack(pady=(0, 12))
        self._update_label.bind("<Button-1>", self._open_releases_page)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def toggle(self) -> None:
        self._cancel_pending_repeat_reminder()
        if self.timer.running:
            self.timer.stop()
        else:
            self.timer.start()
        self._refresh_ui()

    def skip(self) -> None:
        self._cancel_pending_repeat_reminder()
        self.timer.skip()
        self._refresh_ui()

    def reset(self) -> None:
        self._cancel_pending_repeat_reminder()
        self.timer.reset()
        self._refresh_ui()

    def add_minute(self) -> None:
        self._cancel_pending_repeat_reminder()
        self.timer.add_minutes(1)
        self._refresh_ui()

    def open_settings(self) -> None:
        self._cancel_pending_repeat_reminder()
        was_running = self.timer.running
        if was_running:
            self.timer.stop()

        dlg = SettingsDialog(self.root, self.timer.settings)
        if dlg.result:
            self.timer.apply_settings(dlg.result)
            save_settings(self.timer.settings)

        if was_running:
            self.timer.start()

        self._refresh_ui()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_session_complete(self) -> None:
        was_work = self.timer.phase == WORK
        decision = build_completion_decision(self.timer.settings)
        self._cancel_pending_repeat_reminder()
        self.timer.running = False
        self._notify_completion(decision)
        if was_work:
            self._stats = record_pomodoro()
        self.timer.advance_phase()
        if decision.show_toast:
            self._show_toast()
        if decision.restore_window:
            self.show_window()
        self._schedule_repeat_reminder(decision)
        if decision.auto_start_next_phase:
            self.timer.start()
        self._refresh_ui()

    def _on_update_available(self, version: str) -> None:
        self.root.after(0, lambda: self._update_var.set(f"Update available: {version} — click to download"))

    def _open_releases_page(self, _event: object) -> None:
        if self._update_var.get():
            webbrowser.open("https://github.com/xiongxianfei/pomodoro-timer-app/releases/latest")

    def _play_sound(self) -> None:
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except RuntimeError:
            pass

    def _show_toast(self) -> None:
        if not TOAST_AVAILABLE:
            return
        try:
            toast = WinNotification(
                app_id="Pomodoro Timer",
                title="Session Complete",
                msg=f"Next: {PHASE_LABELS[self.timer.phase]}",
                duration="short",
                icon=_resource_path("icon.ico"),
            )
            toast.show()
        except Exception:
            pass

    def _on_close(self) -> None:
        self._cancel_pending_repeat_reminder()
        if TRAY_AVAILABLE and self.timer.settings["minimize_to_tray_on_close"]:
            self.root.withdraw()
        else:
            self.quit_app()

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def show_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _show_window_from_interaction(self) -> None:
        self._cancel_pending_repeat_reminder()
        self.show_window()

    def quit_app(self) -> None:
        self._cancel_pending_repeat_reminder()
        self.timer.stop()
        self.tray.stop()
        self.root.destroy()

    # ------------------------------------------------------------------
    # UI refresh
    # ------------------------------------------------------------------

    def _refresh_ui(self) -> None:
        mins, secs = divmod(self.timer.remaining, 60)
        self._time_var.set(f"{mins:02d}:{secs:02d}")
        self._phase_var.set(PHASE_LABELS[self.timer.phase])

        done, total = self.timer.session_display
        self._counter_var.set(f"Pomodoros: {done} / {total}")
        self._stats_var.set(
            f"Today: {self._stats['today']}  |  All-time: {self._stats['total']}"
        )

        color = PHASE_COLORS[self.timer.phase]
        self._time_label.configure(fg=color)
        self._start_btn.configure(text="Pause" if self.timer.running else "Start", bg=color)
        self.tray.update_color(color)
        self.tray.update_status_text(self._tray_status_text())

    def _notify_completion(self, decision: CompletionDecision) -> None:
        if decision.play_sound:
            self._play_sound()

    def _schedule_repeat_reminder(self, decision: CompletionDecision) -> None:
        if not should_schedule_repeat(decision):
            return

        def fire_repeat_reminder() -> None:
            self._repeat_reminder.clear()
            self._notify_completion(decision)
            if decision.show_toast:
                self._show_toast()

        reminder_handle = self.root.after(
            decision.repeat_after_seconds * 1000,
            fire_repeat_reminder,
        )
        self._repeat_reminder.arm(reminder_handle)

    def _cancel_pending_repeat_reminder(self) -> None:
        self._repeat_reminder.cancel(self.root.after_cancel)

    def _tray_status_text(self) -> str:
        if not self.timer.settings["show_countdown_in_tray"]:
            return self.TRAY_TITLE
        return format_tray_status(
            PHASE_LABELS[self.timer.phase],
            self.timer.remaining,
            self.timer.running,
        )

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()
