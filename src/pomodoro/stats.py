from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import TypedDict


class Stats(TypedDict):
    total: int
    today: int
    last_date: str


def _stats_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"
    return base / "pomodoro" / "stats.json"


def _today() -> str:
    return date.today().isoformat()


def _empty() -> Stats:
    return Stats(total=0, today=0, last_date=_today())


def load_stats() -> Stats:
    """Load stats from disk. Always returns a valid Stats dict."""
    path = _stats_path()
    if not path.exists():
        return _empty()
    try:
        with open(path) as f:
            data: object = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _empty()
    if not isinstance(data, dict):
        return _empty()

    stats = _empty()
    if isinstance(data.get("total"), int):
        stats["total"] = max(0, data["total"])
    if isinstance(data.get("today"), int):
        stats["today"] = max(0, data["today"])
    if isinstance(data.get("last_date"), str):
        stats["last_date"] = data["last_date"]

    # Reset today counter on a new calendar day
    if stats["last_date"] != _today():
        stats["today"] = 0
        stats["last_date"] = _today()
    return stats


def record_pomodoro() -> Stats:
    """Increment completed-pomodoro counts and persist. Returns updated stats."""
    stats = load_stats()
    stats["today"] += 1
    stats["total"] += 1
    stats["last_date"] = _today()
    _save_stats(stats)
    return stats


def _save_stats(stats: Stats) -> None:
    path = _stats_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(stats, f, indent=2)
    except OSError:
        pass
