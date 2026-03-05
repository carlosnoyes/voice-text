import threading
from pynput import keyboard

from backends.whisper_api import WhisperAPIBackend
from audio.recorder import AudioRecorder
from postprocess.commands import process_voice_commands
from output.typer import type_text
import config


class HotkeyListener:
    def __init__(self, tray=None):
        self.recorder = AudioRecorder(sample_rate=config.SAMPLE_RATE)
        self.backend = WhisperAPIBackend()
        self._tray = tray
        self._enabled = True
        self._recording = False
        self.__hotkey = config.HOTKEY

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_hotkey(self, key):
        self._hotkey = key

    @property
    def _hotkey(self):
        return self.__hotkey

    @_hotkey.setter
    def _hotkey(self, value):
        self.__hotkey = value

    def on_press(self, key):
        if not self._enabled:
            return
        if self._recording:
            return
        if key != self._hotkey:
            return

        self._recording = True
        print("  Recording...")
        if self._tray:
            self._tray.set_recording(True)
        self.recorder.start()

    def on_release(self, key):
        if key != self._hotkey or not self._recording:
            return

        self._recording = False
        print("  Processing...")
        audio_data = self.recorder.stop()

        if len(audio_data) < 1000:
            print("  (too short, skipped)")
            if self._tray:
                self._tray.set_recording(False)
            return

        # Transcribe in a background thread to keep hotkey listener responsive
        threading.Thread(
            target=self._transcribe_and_type,
            args=(audio_data,),
            daemon=True,
        ).start()

    def _transcribe_and_type(self, audio_data):
        try:
            raw_text = self.backend.transcribe(audio_data)
            print(f"  Raw: {raw_text}")
            processed = process_voice_commands(raw_text)
            print(f"  Processed: {processed}")
            type_text(processed)
        except Exception as e:
            print(f"  Error: {e}")
        finally:
            if self._tray:
                self._tray.set_recording(False)

    def run(self):
        with keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        ) as listener:
            listener.join()
