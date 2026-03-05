import os
import re
from pathlib import Path
from dotenv import load_dotenv
from pynput.keyboard import Key, KeyCode

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Hotkey (hold to record) — loaded from .env HOTKEY= or defaults to f8
def _parse_hotkey(value: str):
    """Parse a hotkey string like 'f8' or 'a' into a pynput Key or KeyCode."""
    if not value:
        return Key.f8
    try:
        return Key[value.lower()]
    except KeyError:
        return KeyCode.from_char(value.lower())

HOTKEY = _parse_hotkey(os.getenv("HOTKEY", "f8"))

_ENV_PATH = Path(__file__).parent / ".env"

def save_hotkey(key) -> None:
    """Persist the hotkey to .env so it survives restarts."""
    # Determine the string representation
    if isinstance(key, Key):
        key_str = key.name
    elif isinstance(key, KeyCode) and key.char:
        key_str = key.char
    else:
        key_str = str(key)

    text = _ENV_PATH.read_text(encoding="utf-8") if _ENV_PATH.exists() else ""
    if re.search(r"^HOTKEY=", text, re.MULTILINE):
        text = re.sub(r"^HOTKEY=.*$", f"HOTKEY={key_str}", text, flags=re.MULTILINE)
    else:
        text = text.rstrip("\n") + f"\nHOTKEY={key_str}\n"
    _ENV_PATH.write_text(text, encoding="utf-8")

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
