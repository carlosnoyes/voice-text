import time
import pyperclip
import pynput.keyboard

_controller = pynput.keyboard.Controller()


def type_text(text: str):
    """Copy text to clipboard and paste it with Ctrl+V."""
    pyperclip.copy(text)
    time.sleep(0.05)  # brief pause so the clipboard is ready
    with _controller.pressed(pynput.keyboard.Key.ctrl):
        _controller.tap(pynput.keyboard.KeyCode.from_char('v'))
