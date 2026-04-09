from __future__ import annotations

import threading
from typing import Any, Callable

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class TrayIcon:
    """System tray icon wrapper around pystray."""

    def __init__(
        self,
        on_show: Callable[[], None] | None = None,
        on_toggle: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
        *,
        on_skip: Callable[[], None] | None = None,
        on_reset: Callable[[], None] | None = None,
        on_add_minute: Callable[[], None] | None = None,
        on_settings: Callable[[], None] | None = None,
    ) -> None:
        self._icon: Any = None
        self._status_text = "Pomodoro Timer"
        self._on_show = self._wrap(on_show)
        self._on_toggle = self._wrap(on_toggle)
        self._on_skip = self._wrap(on_skip)
        self._on_reset = self._wrap(on_reset)
        self._on_add_minute = self._wrap(on_add_minute)
        self._on_settings = self._wrap(on_settings)
        self._on_quit = self._wrap(on_quit)

    def start(self, color: str, status_text: str | None = None) -> None:
        if not TRAY_AVAILABLE:
            return
        if status_text is not None:
            self._status_text = status_text
        icon = pystray.Icon(
            "pomodoro",
            self._make_image(color),
            self._status_text,
            pystray.Menu(
                pystray.MenuItem("Show Window", self._on_show, default=True),
                pystray.MenuItem("Start / Pause", self._on_toggle),
                pystray.MenuItem("Skip", self._on_skip),
                pystray.MenuItem("Reset", self._on_reset),
                pystray.MenuItem("+1 minute", self._on_add_minute),
                pystray.MenuItem("Settings", self._on_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self._on_quit),
            ),
        )
        self._icon = icon
        threading.Thread(target=icon.run, daemon=True).start()

    def update_color(self, color: str) -> None:
        if self._icon:
            self._icon.icon = self._make_image(color)

    def update_status_text(self, status_text: str) -> None:
        self._status_text = status_text
        if self._icon:
            self._icon.title = status_text

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
            self._icon = None

    @staticmethod
    def _wrap(callback: Callable[[], None] | None) -> Callable[..., None]:
        if callback is None:
            return lambda *_args, **_kwargs: None

        def wrapped(*_args: Any, **_kwargs: Any) -> None:
            callback()

        return wrapped

    @staticmethod
    def _make_image(color: str) -> Any:
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([4, 4, size - 4, size - 4], fill=color)
        return img
