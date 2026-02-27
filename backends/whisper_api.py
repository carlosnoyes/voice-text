import io
import openai
from audio.recorder import AudioRecorder
import config


class WhisperAPIBackend:
    def __init__(self):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.recorder = AudioRecorder(sample_rate=config.SAMPLE_RATE)

    def transcribe(self, audio_data) -> str:
        wav_bytes = self.recorder.get_wav_bytes(audio_data)
        audio_file = io.BytesIO(wav_bytes)
        audio_file.name = "audio.wav"

        response = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
        )
        return response.text
