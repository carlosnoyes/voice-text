import threading
import pystray
from PIL import Image, ImageDraw


# Icon colors for different states
COLOR_IDLE = "#4CAF50"       # Green — ready
COLOR_RECORDING = "#F44336"  # Red — recording
COLOR_DISABLED = "#9E9E9E"   # Grey — paused


def _create_icon_image(color):
    """Draw a simple filled circle icon."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, size - 4, size - 4], fill=color)
    # Small microphone-like detail in center
    cx, cy = size // 2, size // 2
    draw.rounded_rectangle(
        [cx - 6, cy - 12, cx + 6, cy + 4],
        radius=4,
        fill="white",
    )
    draw.arc([cx - 10, cy - 4, cx + 10, cy + 12], 0, 180, fill="white", width=2)
    draw.line([cx, cy + 12, cx, cy + 18], fill="white", width=2)
    return img


class TrayIcon:
    """System tray icon with enable/disable toggle and exit."""

    def __init__(self, on_exit, on_toggle):
        self._on_exit = on_exit
        self._on_toggle = on_toggle
        self._enabled = True
        self._icon = pystray.Icon(
            name="voice-text",
            icon=_create_icon_image(COLOR_IDLE),
            title="Voice-to-Text (Active)",
            menu=pystray.Menu(
                pystray.MenuItem(
                    text=lambda _: "Disable" if self._enabled else "Enable",
                    action=self._toggle,
                    default=True,  # double-click action
                ),
                pystray.MenuItem("Exit", self._exit),
            ),
        )

    def _toggle(self, icon, item):
        self._enabled = not self._enabled
        self._on_toggle(self._enabled)
        if self._enabled:
            icon.icon = _create_icon_image(COLOR_IDLE)
            icon.title = "Voice-to-Text (Active)"
        else:
            icon.icon = _create_icon_image(COLOR_DISABLED)
            icon.title = "Voice-to-Text (Paused)"

    def _exit(self, icon, item):
        icon.stop()
        self._on_exit()

    def set_recording(self, is_recording):
        """Change icon to red while recording, green when idle."""
        if not self._enabled:
            return
        if is_recording:
            self._icon.icon = _create_icon_image(COLOR_RECORDING)
            self._icon.title = "Voice-to-Text (Recording...)"
        else:
            self._icon.icon = _create_icon_image(COLOR_IDLE)
            self._icon.title = "Voice-to-Text (Active)"

    def run(self):
        """Blocks the calling thread — run in a background thread."""
        self._icon.run()

    def stop(self):
        self._icon.stop()
