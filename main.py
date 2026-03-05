"""Voice-to-text: hold F7, speak, release to transcribe and type."""

import sys
import os
import threading
import config
from hotkeys.listener import HotkeyListener
from tray.icon import TrayIcon


def main():
    if not config.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not found in .env")
        sys.exit(1)

    print("Voice-to-text active!")
    print("  Hold F7 -> speak -> release to transcribe")
    print()
    print("Running in system tray. Right-click tray icon to disable/exit.")
    print()

    listener = None

    def on_exit():
        print("\nExiting.")
        os._exit(0)

    def on_toggle(enabled):
        if listener:
            listener.set_enabled(enabled)
        state = "enabled" if enabled else "disabled"
        print(f"  Voice-to-text {state}")

    def on_hotkey_change(new_key):
        if listener:
            listener.set_hotkey(new_key)
        print(f"  Hotkey changed to: {new_key}")

    tray = TrayIcon(on_exit=on_exit, on_toggle=on_toggle, on_hotkey_change=on_hotkey_change)
    listener = HotkeyListener(tray=tray)

    hotkey_thread = threading.Thread(target=listener.run, daemon=True)
    hotkey_thread.start()

    tray.run()


if __name__ == "__main__":
    main()
