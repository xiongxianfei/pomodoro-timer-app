import tkinter as tk
import winsound

from constants import PHASE_LABELS, PHASE_COLORS
from timer import PomodoroTimer
from tray import TrayIcon, TRAY_AVAILABLE
from settings_dialog import SettingsDialog


class PomodoroApp:
    """Main application window. Wires together the timer, tray, and settings dialog."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.timer = PomodoroTimer(
            on_tick=lambda: self.root.after(0, self._refresh_ui),
            on_complete=lambda: self.root.after(0, self._on_session_complete),
        )

        self._build_ui()

        self.tray = TrayIcon(
            on_show=lambda: self.root.after(0, self.show_window),
            on_toggle=lambda: self.root.after(0, self.toggle),
            on_quit=lambda: self.root.after(0, self.quit_app),
        )
        if TRAY_AVAILABLE:
            self.tray.start(PHASE_COLORS[self.timer.phase])

        self._refresh_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        root = self.root
        root.configure(bg="#2c2c2c")
        pad = {"padx": 20, "pady": 6}

        self._phase_var = tk.StringVar()
        self._time_var = tk.StringVar()
        self._counter_var = tk.StringVar()

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
        ).pack(pady=(2, 16))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def toggle(self):
        if self.timer.running:
            self.timer.stop()
        else:
            self.timer.start()
        self._refresh_ui()

    def skip(self):
        self.timer.skip()
        self._refresh_ui()

    def reset(self):
        self.timer.reset()
        self._refresh_ui()

    def open_settings(self):
        was_running = self.timer.running
        if was_running:
            self.timer.stop()

        dlg = SettingsDialog(self.root, self.timer.settings)
        if dlg.result:
            self.timer.apply_settings(dlg.result)

        if was_running:
            self.timer.start()

        self._refresh_ui()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_session_complete(self):
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        self.show_window()
        self.timer.advance_phase()
        self.timer.start()
        self._refresh_ui()

    def _on_close(self):
        if TRAY_AVAILABLE:
            self.root.withdraw()
        else:
            self.quit_app()

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        self.timer.stop()
        self.tray.stop()
        self.root.destroy()

    # ------------------------------------------------------------------
    # UI refresh
    # ------------------------------------------------------------------

    def _refresh_ui(self):
        mins, secs = divmod(self.timer.remaining, 60)
        self._time_var.set(f"{mins:02d}:{secs:02d}")
        self._phase_var.set(PHASE_LABELS[self.timer.phase])

        done, total = self.timer.session_display
        self._counter_var.set(f"Pomodoros: {done} / {total}")

        color = PHASE_COLORS[self.timer.phase]
        self._time_label.configure(fg=color)
        self._start_btn.configure(text="Pause" if self.timer.running else "Start", bg=color)
        self.tray.update_color(color)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        self.root.mainloop()
