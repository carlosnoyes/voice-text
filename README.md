# Voice-to-Text

System-wide voice-to-text for Windows. Hold F7, speak, release — text is typed into whatever app has focus. Runs in the system tray.

Uses the OpenAI Whisper API (~1-2s latency after release, $0.006/min).

Voice commands are converted automatically: say "hello world period how are you question mark" and get `Hello world. How are you?`

Supported commands: `period`, `comma`, `exclamation point`, `question mark`, `colon`, `semicolon`, `hyphen`, `dash`, `ellipsis`, `open/close parenthesis`, `open/close quote`.

## Install

### 1. Prerequisites

- Python 3.11+
- An OpenAI API key (get one at https://platform.openai.com/api-keys)

### 2. Clone and set up

```bash
git clone https://github.com/carlosnoyes/voice-text.git
cd voice-text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API key

```bash
copy .env.example .env
```

Edit `.env` and paste your OpenAI API key.

### 4. Run

```bash
python main.py
```

A green microphone icon appears in your system tray (bottom-right, near the clock).

- **Hold F7** to record, release to transcribe and type
- **Double-click** the tray icon to enable/disable
- **Right-click** → Exit to quit
- Icon turns **red** while recording, **grey** when disabled

## Auto-Start on Login

1. Press `Win + R`, type `shell:startup`, hit Enter
2. Right-click in the folder → **New → Shortcut**
3. Paste any path (e.g. `pythonw.exe`) and click Next, name it "Voice Text", click Finish
4. Right-click the new shortcut → **Properties**, then edit these fields:
   - **Target:**
     ```
     C:\Users\YOUR_USERNAME\path\to\voice-text\.venv\Scripts\pythonw.exe C:\Users\YOUR_USERNAME\path\to\voice-text\main.py
     ```
   - **Start in:**
     ```
     C:\Users\YOUR_USERNAME\path\to\voice-text
     ```
5. Click OK

> Use `pythonw.exe` (not `python.exe`) so no console window appears. The **Start in** field is important — `.env` is loaded from the working directory.

## Project Structure

```
voice-text/
├── main.py              # Entry point
├── config.py            # Hotkey, API key, audio settings
├── audio/
│   └── recorder.py      # Mic capture (buffer-based)
├── backends/
│   └── whisper_api.py   # OpenAI Whisper file upload
├── hotkeys/
│   └── listener.py      # Hold-to-record orchestrator
├── output/
│   └── typer.py         # Keyboard simulation
├── postprocess/
│   └── commands.py      # Voice command → punctuation
└── tray/
    └── icon.py          # System tray icon
```
