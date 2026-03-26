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

DEFAULT_SETTINGS: dict[str, int] = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "long_break_after": 4,
}

# Inclusive (min, max) bounds for each setting
SETTINGS_BOUNDS: dict[str, tuple[int, int]] = {
    "work_minutes":        (1, 120),
    "short_break_minutes": (1, 60),
    "long_break_minutes":  (1, 120),
    "long_break_after":    (1, 10),
}
