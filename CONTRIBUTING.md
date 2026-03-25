# Contributing

Thank you for your interest in contributing to Pomodoro Timer!

## Getting Started

```bash
git clone https://github.com/xiongxianfei/pomodoro-timer-app.git
cd pomodoro-timer-app
pip install -r requirements.txt
pip install pytest mypy
```

## Project Structure

| File | Responsibility |
|------|----------------|
| `constants.py` | Phase constants, colors, settings bounds |
| `timer.py` | Pure countdown logic — no GUI |
| `storage.py` | JSON settings persistence |
| `settings_dialog.py` | Modal settings form |
| `tray.py` | System tray icon |
| `ui.py` | Main window and wiring |

## Development Workflow

1. **Fork** the repository and create a branch from `main`
2. **Make your changes** — keep PRs focused on a single concern
3. **Run tests** before pushing:
   ```bash
   pytest tests/ -v
   mypy constants.py timer.py storage.py settings_dialog.py
   ```
4. **Open a Pull Request** using the provided template

## Guidelines

- `timer.py` and `storage.py` must remain GUI-free (no `tkinter` imports)
- New logic should come with tests in `tests/`
- Type hints are required on all new functions
- Keep commits focused and use clear messages

## Reporting Bugs / Requesting Features

Use the [issue templates](https://github.com/xiongxianfei/pomodoro-timer-app/issues/new/choose).

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities privately.
