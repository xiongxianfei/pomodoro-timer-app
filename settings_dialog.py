from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from constants import SETTINGS_BOUNDS


class SettingsDialog(tk.Toplevel):
    """Modal dialog for editing timer durations."""

    FIELDS: list[tuple[str, str]] = [
        ("Work duration (min):", "work_minutes"),
        ("Short break (min):", "short_break_minutes"),
        ("Long break (min):", "long_break_minutes"),
        ("Long break after N sessions:", "long_break_after"),
    ]

    def __init__(self, parent: tk.Tk, settings: dict[str, int]) -> None:
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.grab_set()
        self.result: dict[str, int] | None = None

        self._vars: dict[str, tk.StringVar] = {}
        for row, (label, key) in enumerate(self.FIELDS):
            tk.Label(self, text=label, anchor="w").grid(
                row=row, column=0, padx=12, pady=6, sticky="w"
            )
            var = tk.StringVar(value=str(settings[key]))
            tk.Entry(self, textvariable=var, width=6, justify="center").grid(
                row=row, column=1, padx=12, pady=6
            )
            self._vars[key] = var

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(self.FIELDS), column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="OK", width=8, command=self._ok).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancel", width=8, command=self.destroy).pack(side="left", padx=6)

        self.transient(parent)
        self.wait_window(self)

    def _ok(self) -> None:
        parsed: dict[str, int] = {}
        errors: list[str] = []

        for _, key in self.FIELDS:
            raw = self._vars[key].get().strip()
            try:
                value = int(raw)
            except ValueError:
                errors.append(f"'{raw}' is not a valid integer.")
                continue

            lo, hi = SETTINGS_BOUNDS[key]
            if not (lo <= value <= hi):
                label = next(lbl for lbl, k in self.FIELDS if k == key)
                errors.append(f"{label.rstrip(':')} must be between {lo} and {hi}.")
                continue

            parsed[key] = value

        if errors:
            messagebox.showerror("Invalid Settings", "\n".join(errors), parent=self)
            return

        self.result = parsed
        self.destroy()
