import time
import pynput.keyboard

_controller = pynput.keyboard.Controller()


def type_text(text: str):
    """Type text into the focused application using keyboard simulation."""
    for char in text:
        if char == "\n":
            _controller.press(pynput.keyboard.Key.enter)
            _controller.release(pynput.keyboard.Key.enter)
        else:
            _controller.type(char)
        time.sleep(0.005)
