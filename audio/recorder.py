import sounddevice as sd
import threading
import io
import wave


class AudioRecorder:
    """Hold-to-record audio capture. Thread-safe start/stop."""

    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._stream = None
        self._frames = []
        self._recording = False
        self._lock = threading.Lock()

    def start(self):
        """Called on key press. Opens mic stream, begins collecting frames."""
        with self._lock:
            self._frames = []
            self._recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.chunk_size,
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            if self._recording:
                self._frames.append(indata.copy().tobytes())

    def stop(self) -> bytes:
        """Called on key release. Returns raw PCM bytes."""
        with self._lock:
            self._recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            return b"".join(self._frames)

    def get_wav_bytes(self, pcm_data: bytes) -> bytes:
        """Wraps raw PCM in a WAV container for file-based APIs."""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm_data)
        return buf.getvalue()
