import os
from dotenv import load_dotenv
from pynput.keyboard import Key

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Hotkey (hold to record)
HOTKEY = Key.f8

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
