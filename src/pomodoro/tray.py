import threading

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


class TrayIcon:
    """System tray icon wrapper around pystray."""

    def __init__(self, on_show, on_toggle, on_quit):
        self._icon = None
        self._on_show = on_show
        self._on_toggle = on_toggle
        self._on_quit = on_quit

    def start(self, color):
        if not TRAY_AVAILABLE:
            return
        self._icon = pystray.Icon(
            "pomodoro",
            self._make_image(color),
            "Pomodoro Timer",
            pystray.Menu(
                pystray.MenuItem("Show Window", lambda: self._on_show(), default=True),
                pystray.MenuItem("Start / Pause", lambda: self._on_toggle()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", lambda: self._on_quit()),
            ),
        )
        threading.Thread(target=self._icon.run, daemon=True).start()

    def update_color(self, color):
        if self._icon:
            self._icon.icon = self._make_image(color)

    def stop(self):
        if self._icon:
            self._icon.stop()
            self._icon = None

    @staticmethod
    def _make_image(color):
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([4, 4, size - 4, size - 4], fill=color)
        return img
