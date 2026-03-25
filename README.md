# Pomodoro Timer

A lightweight desktop Pomodoro Timer for Windows 11, built with Python and tkinter. Stay focused with timed work sessions, automatic break reminders, sound alerts, and a system tray icon so it never gets in your way.

## Features

- **Pomodoro cycle** — 25-min work sessions alternate with short breaks; every 4th session triggers a long break
- **Auto-advance** — the next phase starts automatically when a session ends
- **Sound alert** — plays a system sound at the end of each session
- **Auto-restore** — the window pops to the foreground when a session ends, even if minimized
- **System tray** — closing the window sends it to the tray; the timer keeps running in the background
- **Configurable durations** — work, short break, long break, and long-break interval are all adjustable in Settings
- **Session counter** — tracks completed Pomodoros within the current cycle (e.g. `3 / 4`)
- **Color-coded phases** — red for work, green for short break, blue for long break

## Requirements

- Windows 11 (uses `winsound` for audio alerts)
- Python 3.8+

## Installation

```bash
git clone https://github.com/<your-username>/pomodoro-timer.git
cd pomodoro-timer
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

| Setting | Default |
|---------|---------|
| Work duration | 25 min |
| Short break | 5 min |
| Long break | 15 min |
| Long break after N sessions | 4 |

Settings take effect immediately and reset the current phase to the new duration.

## Project Structure

```
pomodoro-timer/
├── main.py              # Entry point
├── constants.py         # Phase constants, colors, default settings
├── timer.py             # PomodoroTimer — pure countdown logic, no GUI
├── settings_dialog.py   # SettingsDialog — modal settings form
├── tray.py              # TrayIcon — pystray wrapper
├── ui.py                # PomodoroApp — window and wiring
├── requirements.txt     # Third-party dependencies
└── README.md
```

### Architecture

- **`PomodoroTimer`** (`timer.py`) — pure logic with no GUI dependency. Manages phase transitions, countdown thread, and settings. Communicates with the UI via `on_tick` / `on_complete` callbacks.
- **`PomodoroApp`** (`ui.py`) — tkinter window that wires together the timer, tray, and settings dialog. All cross-thread GUI updates go through `root.after()`.
- **`SettingsDialog`** (`settings_dialog.py`) — modal `Toplevel` dialog for editing the four configurable values.
- **`TrayIcon`** (`tray.py`) — wraps `pystray`. Icon color mirrors the current phase. Runs in its own daemon thread as required by `pystray`.

## Dependencies

| Package | Purpose |
|---------|---------|
| [pystray](https://github.com/moses-palmer/pystray) | System tray icon |
| [Pillow](https://python-pillow.org/) | Generate tray icon image programmatically |

All other functionality uses the Python standard library (`tkinter`, `winsound`, `threading`, `time`).

## License

MIT
