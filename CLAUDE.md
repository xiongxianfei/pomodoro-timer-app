# CLAUDE.md

Project conventions for Claude Code when working in this repository.

## Project

A Windows 11 desktop Pomodoro Timer built with Python + tkinter.
GitHub: https://github.com/xiongxianfei/pomodoro-timer-app

## Common commands

```bash
# Run the app
python main.py

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=pomodoro --cov-report=term-missing

# Type check
mypy src/pomodoro/

# Build standalone exe
pyinstaller --onefile --windowed --name "PomodoroTimer" --icon=icon.ico --add-data "icon.ico;." main.py
```

## Project structure

```
src/pomodoro/    — all application modules (src layout)
tests/           — unit tests
main.py          — entry point only (3 lines)
installer.iss    — Inno Setup script for Windows installer
pyproject.toml   — build config, dependencies, mypy, pytest, coverage settings
```

## Key conventions

- **src layout**: all modules live under `src/pomodoro/`. Use relative imports inside the package (`from .constants import ...`). `main.py` uses an absolute import (`from pomodoro.ui import PomodoroApp`).
- **Version string**: single source of truth is `APP_VERSION` in `src/pomodoro/constants.py`. Update this before tagging a release.
- **Pure logic modules**: `constants`, `timer`, `storage`, `stats`, `updater` — no GUI imports, fully testable.
- **GUI modules**: `ui`, `tray`, `settings_dialog` — Windows-only, excluded from mypy and coverage (see `pyproject.toml`).

## Branch protection

`main` is protected — all changes must go through a pull request. Never push directly to `main`.

When implementing a change:
1. Create a feature branch
2. Commit and push
3. Open a PR with `gh pr create`
4. CI must pass before merging

## Releasing

Releases are triggered two ways:
- **GitHub UI**: Actions → Release → Run workflow → enter `v1.x.y`
- **Terminal**: `git tag v1.x.y && git push origin v1.x.y`

Both produce `PomodoroTimer.exe` (portable) and `PomodoroTimer-Setup-x.y.z.exe` (installer).

## CI

- **test.yml**: runs mypy + pytest on Python 3.9–3.12, triggered on push/PR/daily
- **release.yml**: builds exe + installer, creates GitHub release, triggered on tag push or workflow_dispatch
- `ui.py` is excluded from mypy (`[[tool.mypy.overrides]]`) — Windows-only imports fail on Linux
- GUI modules are excluded from coverage (`[tool.coverage.run] omit`) — can't run headlessly
