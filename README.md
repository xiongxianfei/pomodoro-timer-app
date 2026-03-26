# Pomodoro Timer

[![Tests](https://github.com/xiongxianfei/pomodoro-timer-app/actions/workflows/test.yml/badge.svg)](https://github.com/xiongxianfei/pomodoro-timer-app/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/xiongxianfei/pomodoro-timer-app/branch/main/graph/badge.svg)](https://codecov.io/gh/xiongxianfei/pomodoro-timer-app)

A lightweight desktop Pomodoro Timer for Windows 11, built with Python and tkinter. Stay focused with timed work sessions, automatic break reminders, sound alerts, and a system tray icon so it never gets in your way.

![Pomodoro Timer screenshot](docs/screenshot.png)

## Features

- **Pomodoro cycle** — 25-min work sessions alternate with short breaks; every 4th session triggers a long break
- **Auto-advance** — the next phase starts automatically when a session ends
- **Sound + toast alert** — plays a system sound and shows a Windows toast notification on session end
- **Auto-restore** — the window pops to the foreground when a session ends, even if minimized
- **System tray** — closing the window sends it to the tray; the timer keeps running in the background
- **Persistent settings** — durations are saved to disk and restored on next launch
- **Validated settings** — each value is range-checked; invalid input shows a descriptive error
- **Session counter** — tracks completed Pomodoros within the current cycle (e.g. `3 / 4`)
- **Statistics** — shows today's and all-time completed Pomodoro counts, persisted across restarts
- **Auto-update check** — notifies you in-app when a new version is available
- **Color-coded phases** — red for work, green for short break, blue for long break

## Download

**No Python required.** Grab the latest build from the [Releases](https://github.com/xiongxianfei/pomodoro-timer-app/releases/latest) page:

| Option | File | Notes |
|--------|------|-------|
| **Installer** (recommended) | `PomodoroTimer-Setup-x.y.z.exe` | Adds Start Menu shortcut, optional desktop icon and run-at-login |
| **Portable** | `PomodoroTimer.exe` | Single file, no installation needed |

> **Note:** Windows SmartScreen may show a warning on first launch since the exe is unsigned. Click **More info → Run anyway** to proceed.

## Requirements

- Windows 11

## Run from Source

If you prefer to run from source, Python 3.9+ is required:

```bash
git clone https://github.com/xiongxianfei/pomodoro-timer-app.git
cd pomodoro-timer-app
pip install .
python main.py
```

## Build Locally

### Portable exe (PyInstaller)

```bash
pip install pyinstaller
pip install .
pyinstaller --onefile --windowed --name "PomodoroTimer" --icon=icon.ico --add-data "icon.ico;." main.py
```

Output: `dist/PomodoroTimer.exe`

### Installer (Inno Setup)

1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php)
2. Build the exe first (step above)
3. Compile the installer:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DAppVersion=1.0.4 installer.iss
```

Output: `Output/PomodoroTimer-Setup-1.0.4.exe`

> Both steps run automatically on every tagged release via GitHub Actions.

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
├── pyproject.toml       # Build config, dependencies, mypy & pytest settings
├── src/
│   └── pomodoro/
│       ├── __init__.py
│       ├── constants.py         # Phase constants, colors, default settings, bounds
│       ├── timer.py             # PomodoroTimer — pure countdown logic, no GUI
│       ├── storage.py           # load_settings / save_settings — JSON persistence
│       ├── settings_dialog.py   # SettingsDialog — modal form with bounds validation
│       ├── tray.py              # TrayIcon — pystray wrapper
│       └── ui.py                # PomodoroApp — window and wiring
├── tests/
│   ├── test_constants.py
│   └── test_timer.py
└── .github/
    └── workflows/
        ├── test.yml     # CI: type check + tests on push, PR, and daily schedule
        └── release.yml  # Build exe and publish GitHub release on tag push
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
| [winotify](https://github.com/versa-synnc/winotify) | Windows toast notifications |

All other functionality uses the Python standard library (`tkinter`, `winsound`, `threading`, `time`, `json`, `pathlib`).

## Star History

[![Star History Chart](https://api.star-history.com/image?repos=xiongxianfei/pomodoro-timer-app&type=date&legend=top-left)](https://www.star-history.com/?repos=xiongxianfei%2Fpomodoro-timer-app&type=date&legend=top-left)

## License

MIT
