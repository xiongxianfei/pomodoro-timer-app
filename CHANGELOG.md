# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.4] - 2026-03-26

### Added
- Clickable update banner — clicking the "Update available" label opens the releases page in the browser (#10)
- Unit tests for `updater.py` — 11 cases covering version parsing and HTTP callback behaviour (#10)
- `CHANGELOG.md` (#11)

## [1.0.3] - 2026-03-26

### Added
- Session statistics — tracks daily and all-time completed Pomodoro counts, persisted to `%APPDATA%\pomodoro\stats.json` and displayed in the UI (#7)
- Auto-update check — background thread queries GitHub releases on startup and shows a clickable banner when a newer version is available (#7, #10)
- Windows installer (`PomodoroTimer-Setup-x.y.z.exe`) — adds Start Menu shortcut, optional desktop icon, and optional run-at-login; released alongside the portable exe (#7)
- `workflow_dispatch` trigger on the release workflow — releases can now be triggered from the GitHub Actions UI without local git commands (#9)
- App screenshot in README (#8)

### Changed
- Migrated all modules to src layout (`src/pomodoro/`) for standard Python packaging (#6)
- Replaced `requirements.txt` + `mypy.ini` with `pyproject.toml` for unified project config

### Fixed
- Type annotations added to `tray.py` and `ui.py`; `ui.py` excluded from mypy on Linux CI (Windows-only imports)

## [1.0.2] - 2026-03-25

### Fixed
- Release workflow: replaced `softprops/action-gh-release` with `gh` CLI to resolve Node.js 20 deprecation warnings
- Added `permissions: contents: write` to release job (default `GITHUB_TOKEN` is read-only)
- `pyproject.toml`: fixed SPDX license string and empty packages for app layout

## [1.0.1] - 2026-03-25

### Fixed
- Release workflow: granted `contents: write` permission to `GITHUB_TOKEN`

## [1.0.0] - 2026-03-25

### Added
- Pomodoro timer with 25-min work / 5-min short break / 15-min long break cycle
- Auto-advance to next phase on session complete
- Sound alert (`winsound`) and Windows toast notification (`winotify`) on session end
- Auto-restore window to foreground when session ends
- System tray icon (`pystray` + `Pillow`) — closing minimises to tray, timer keeps running
- Persistent settings saved to `%APPDATA%\pomodoro\settings.json`
- Input validation with per-field range bounds (`SETTINGS_BOUNDS`)
- Session counter showing completed Pomodoros in the current cycle
- Color-coded phases — red for work, green for short break, blue for long break
- Custom app icon (`icon.ico`)
- GitHub Actions CI — mypy type checking + pytest across Python 3.9–3.12, daily schedule
- PyInstaller standalone Windows exe, released via GitHub Actions on tag push
- GitHub community files: issue templates, PR template, `SECURITY.md`, `CONTRIBUTING.md`, `dependabot.yml`

[Unreleased]: https://github.com/xiongxianfei/pomodoro-timer-app/compare/v1.0.4...HEAD
[1.0.4]: https://github.com/xiongxianfei/pomodoro-timer-app/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/xiongxianfei/pomodoro-timer-app/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/xiongxianfei/pomodoro-timer-app/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/xiongxianfei/pomodoro-timer-app/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/xiongxianfei/pomodoro-timer-app/releases/tag/v1.0.0
