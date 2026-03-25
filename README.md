# Pomodoro Timer

A lightweight desktop Pomodoro Timer for Windows 11, built with Python and tkinter. Stay focused with timed work sessions, automatic break reminders, sound alerts, and a system tray icon so it never gets in your way.

## Features

- **Pomodoro cycle** — 25-min work sessions alternate with short breaks; every 4th session triggers a long break
- **Auto-advance** — the next phase starts automatically when a session ends
- **Sound alert** — plays a system sound at the end of each session
- **Auto-restore** — the window pops to the foreground when a session ends, even if minimized
- **System tray** — closing the window sends it to the tray; the timer keeps running in the background
- **Persistent settings** — durations are saved to disk and restored on next launch
- **Validated settings** — each value is range-checked; invalid input shows a descriptive error
- **Session counter** — tracks completed Pomodoros within the current cycle (e.g. `3 / 4`)
- **Color-coded phases** — red for work, green for short break, blue for long break

## Requirements

- Windows 11 (uses `winsound` for audio alerts)
- Python 3.9+

## Installation

```bash
git clone https://github.com/xiongxianfei/pomodoro-timer-app.git
cd pomodoro-timer-app
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Controls

| Button | Action |
|--------|--------|
| **Start / Pause** | Start or pause the current countdown |
| **Skip** | End the current phase early and move to the next |
| **Reset** | Restart the current phase's countdown |
| **Settings** | Open the settings dialog |

### System Tray

- **Close (X)** — hides the window; the timer continues running in the background
- **Tray icon double-click** — restores the window
- **Tray icon right-click** → Show Window / Start-Pause / Quit

## Configuration

Click **Settings** to adjust:

| Setting | Default | Range |
|---------|---------|-------|
| Work duration | 25 min | 1 – 120 |
| Short break | 5 min | 1 – 60 |
| Long break | 15 min | 1 – 120 |
| Long break after N sessions | 4 | 1 – 10 |

Settings are validated on save and persisted to `%APPDATA%\pomodoro\settings.json`. They take effect immediately and reset the current phase to the new duration.

## Project Structure

```
pomodoro-timer-app/
├── main.py              # Entry point
├── constants.py         # Phase constants, colors, default settings, bounds
├── timer.py             # PomodoroTimer — pure countdown logic, no GUI
├── storage.py           # load_settings / save_settings — JSON persistence
├── settings_dialog.py   # SettingsDialog — modal form with bounds validation
├── tray.py              # TrayIcon — pystray wrapper
├── ui.py                # PomodoroApp — window and wiring
├── mypy.ini             # Static type-checking configuration
├── requirements.txt     # Runtime dependencies
├── tests/
│   ├── test_constants.py
│   └── test_timer.py
└── .github/
    └── workflows/
        └── test.yml     # CI: type check + tests on push, PR, and daily schedule
```

## Architecture

- **`PomodoroTimer`** (`timer.py`) — pure logic with no GUI dependency. Manages phase transitions, countdown thread, and settings. Communicates with the UI via `on_tick` / `on_complete` callbacks. Fully type-annotated.
- **`PomodoroApp`** (`ui.py`) — tkinter window that wires together the timer, tray, and settings dialog. All cross-thread GUI updates go through `root.after()`. Loads settings on startup, saves on change.
- **`SettingsDialog`** (`settings_dialog.py`) — modal `Toplevel` dialog. Validates all fields against `SETTINGS_BOUNDS` before accepting; lists every violation in an error dialog.
- **`TrayIcon`** (`tray.py`) — wraps `pystray`. Icon color mirrors the current phase. Runs in its own daemon thread as required by `pystray`.
- **`storage`** (`storage.py`) — reads and writes `settings.json` using the standard library `json` module. Clamps all loaded values to their valid ranges so a corrupted file cannot inject bad state.

## CI / Quality

The GitHub Actions workflow (`.github/workflows/test.yml`) runs on every push, pull request, and daily at 02:00 UTC:

1. **Type check** — `mypy` across all pure-logic modules (`constants`, `timer`, `storage`, `settings_dialog`)
2. **Tests** — `pytest` across Python 3.9, 3.10, 3.11, and 3.12

## Dependencies

| Package | Purpose |
|---------|---------|
| [pystray](https://github.com/moses-palmer/pystray) | System tray icon |
| [Pillow](https://python-pillow.org/) | Generate tray icon image programmatically |

All other functionality uses the Python standard library (`tkinter`, `winsound`, `threading`, `time`, `json`, `pathlib`).

## License

MIT
