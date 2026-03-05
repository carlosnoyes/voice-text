import threading
import tkinter as tk
import pystray
from PIL import Image, ImageDraw
from pynput.keyboard import Key


# Icon colors for different states
COLOR_IDLE = "#4CAF50"       # Green — ready
COLOR_RECORDING = "#F44336"  # Red — recording
COLOR_PROCESSING = "#2196F3" # Blue — transcribing/pasting
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


def _capture_hotkey_dialog(current_key_name: str):
    """Show a dialog that waits for a key press and returns the pynput Key or KeyCode.
    Must be called from a dedicated thread (not the pystray callback thread).
    """
    from pynput.keyboard import KeyCode
    result = [None]
    done = threading.Event()

    def run():
        root = tk.Tk()
        root.title("Change Hotkey")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        w, h = 320, 150
        root.update_idletasks()
        x = (root.winfo_screenwidth() - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(root, text=f"Current hotkey: {current_key_name}", fg="gray").pack(pady=(12, 0))
        tk.Label(root, text="Press a new key to change it.", wraplength=300, pady=8).pack()
        status = tk.Label(root, text="", fg="#1a7a1a", font=("", 10, "bold"))
        status.pack()
        tk.Button(root, text="Cancel", command=root.destroy, width=10).pack(pady=8)

        root.protocol("WM_DELETE_WINDOW", root.destroy)

        _SPECIAL = {k.name: k for k in Key}

        def on_key(event):
            keysym = event.keysym
            # ignore bare modifier presses
            if keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R",
                          "Alt_L", "Alt_R", "Super_L", "Super_R", "Caps_Lock"):
                return
            lower = keysym.lower()
            if lower in _SPECIAL:
                result[0] = _SPECIAL[lower]
            elif len(keysym) == 1:
                result[0] = KeyCode.from_char(keysym.lower())
            else:
                if keysym in _SPECIAL:
                    result[0] = _SPECIAL[keysym]
                else:
                    result[0] = KeyCode.from_char(keysym)

            status.config(text=f"Hotkey set to: {keysym}")
            root.after(800, root.destroy)

        root.bind("<KeyPress>", on_key)
        root.focus_force()
        root.mainloop()
        done.set()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    done.wait()
    return result[0]


class TrayIcon:
    """System tray icon with enable/disable toggle and exit."""

    def __init__(self, on_exit, on_toggle, on_hotkey_change=None, current_hotkey_name="f8"):
        self._on_exit = on_exit
        self._on_toggle = on_toggle
        self._on_hotkey_change = on_hotkey_change
        self._enabled = True
        self._hotkey_name = current_hotkey_name
        self._icon = pystray.Icon(
            name="voice-text",
            icon=_create_icon_image(COLOR_IDLE),
            title=f"Voice-to-Text (Active) — hotkey: {current_hotkey_name}",
            menu=pystray.Menu(
                pystray.MenuItem(
                    text=lambda _: "Disable" if self._enabled else "Enable",
                    action=self._toggle,
                    default=True,  # double-click action
                ),
                pystray.MenuItem(
                    text=lambda _: f"Change Hotkey ({self._hotkey_name})",
                    action=self._change_hotkey,
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

    def _change_hotkey(self, icon, item):
        new_key = _capture_hotkey_dialog(self._hotkey_name)
        if new_key is not None and self._on_hotkey_change:
            self._on_hotkey_change(new_key)
            self._hotkey_name = new_key.name if isinstance(new_key, Key) else str(new_key)
            icon.title = f"Voice-to-Text (Active) — hotkey: {self._hotkey_name}"

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
            self._icon.title = f"Voice-to-Text (Active) — hotkey: {self._hotkey_name}"

    def set_processing(self, is_processing):
        """Change icon to blue while transcribing/pasting."""
        if not self._enabled:
            return
        if is_processing:
            self._icon.icon = _create_icon_image(COLOR_PROCESSING)
            self._icon.title = "Voice-to-Text (Processing...)"
        else:
            self._icon.icon = _create_icon_image(COLOR_IDLE)
            self._icon.title = f"Voice-to-Text (Active) — hotkey: {self._hotkey_name}"

    def run(self):
        """Blocks the calling thread — run in a background thread."""
        self._icon.run()

    def stop(self):
        self._icon.stop()
