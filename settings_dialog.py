import tkinter as tk


class SettingsDialog(tk.Toplevel):
    """Modal dialog for editing timer durations."""

    FIELDS = [
        ("Work duration (min):", "work_minutes"),
        ("Short break (min):", "short_break_minutes"),
        ("Long break (min):", "long_break_minutes"),
        ("Long break after N sessions:", "long_break_after"),
    ]

    def __init__(self, parent, settings):
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        self._vars = {}
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

    def _ok(self):
        try:
            self.result = {key: int(var.get()) for key, var in self._vars.items()}
        except ValueError:
            return
        self.destroy()
