# --- Stage 1: Builder ---
FROM archlinux:latest AS builder

RUN pacman -Sy --noconfirm \
    python python-pip python-virtualenv \
    git portaudio ffmpeg xclip xdotool libnotify unzip wget \
    && pacman -Scc --noconfirm

WORKDIR /build

# Create virtualenv and install python packages inside it
RUN python -m virtualenv /build/venv && \
    /build/venv/bin/pip install --upgrade pip && \
    /build/venv/bin/pip install vosk sounddevice pyperclip

# Download and extract Vosk model
RUN wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip && \
    unzip vosk-model-en-us-0.22-lgraph.zip && \
    rm vosk-model-en-us-0.22-lgraph.zip

# Write dictation_service.py script inline
RUN cat <<'EOF' > /build/dictation_service.py
import vosk
import sys
import sounddevice as sd
import queue
import json
import pyperclip
import subprocess
import time
from pathlib import Path

# --- Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_NAME = "vosk-model-en-us-0.22-lgraph"
MODEL_PATH = SCRIPT_DIR / MODEL_NAME
TRIGGER_FILE = Path("/tmp/vosk_trigger")

NOTIFY_SEND_PATH = "/usr/bin/notify-send"
XDOTOOL_PATH = "/usr/bin/xdotool"
SAMPLE_RATE = 44100

def notify(summary, body=""):
    try:
        subprocess.run([NOTIFY_SEND_PATH, summary, body, "-t", "2000"], check=True)
    except Exception:
        print(f"NOTIFY: {summary} - {body}")

print("Available audio devices:")
for i, dev in enumerate(sd.query_devices()):
    print(f"{i}: {dev['name']} - Input Channels: {dev['max_input_channels']}")

# Find first device with input channels > 0
device_index = None
for i, dev in enumerate(sd.query_devices()):
    if dev['max_input_channels'] > 0:
        device_index = i
        break

if device_index is None:
    print("ERROR: No input audio device found!")
    sys.exit(1)

print(f"Using audio input device #{device_index}: {sd.query_devices(device_index)['name']}")

def transcribe_audio():
    import numpy as np
    q = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"PortAudio Status: {status}", file=sys.stderr)
        q.put(indata.copy())

    try:
        with sd.InputStream(samplerate=44100,
                            channels=1,
                            dtype='int16',
                            device=device_index,
                            blocksize=2048,
                            callback=audio_callback):
            print("Stream started. Listening...")

            # Warm-up
            warmup_end = time.time() + 1.5
            while time.time() < warmup_end:
                try:
                    q.get(timeout=0.5)
                except queue.Empty:
                    pass

            print("Now capturing voice...")

            start_time = time.time()
            while time.time() - start_time < 5:
                try:
                    data = q.get(timeout=1)
                    if recognizer.AcceptWaveform(data.tobytes()):
                        break
                except queue.Empty:
                    continue

            result = json.loads(recognizer.Result())
            return result.get("text", "")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

print("--- Vosk Dictation Service ---")
if not MODEL_PATH.exists():
    print(f"FATAL ERROR: Model not found at {MODEL_PATH}")
    sys.exit(1)

print(f"Loading model '{MODEL_NAME}'... This may take a few seconds.")
try:
    model = vosk.Model(str(MODEL_PATH))
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    print("Model loaded successfully. Service is waiting for a trigger.")
    notify("Vosk Service Ready", "Hotkey is now active.")
except Exception as e:
    print(f"FATAL ERROR: Could not load model. {e}")
    sys.exit(1)

while True:
    try:
        if TRIGGER_FILE.exists():
            print("Trigger detected! Starting transcription.")
            notify("Vosk is Listening...", "Speak now.")
            TRIGGER_FILE.unlink()

            recognized_text = transcribe_audio()

            if recognized_text:
                print(f"Transcribed: '{recognized_text}'")
                subprocess.run([XDOTOOL_PATH, "type", "--clearmodifiers", recognized_text])
                pyperclip.copy(recognized_text)
            else:
                notify("Vosk Dictation", "No text was recognized.")

        time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nService stopped by user.")
        break
    except Exception as e:
        print(f"An error occurred in the main loop: {e}")
        notify("Vosk Service Error", str(e))

EOF
# --- Stage 2: Runtime ---
FROM archlinux:latest

RUN pacman -Sy --noconfirm \
    python portaudio ffmpeg xclip xdotool libnotify \
    && pacman -Scc --noconfirm

COPY --from=builder /build/venv /venv
COPY --from=builder /build/dictation_service.py /app/dictation_service.py
COPY --from=builder /build/vosk-model-en-us-0.22-lgraph /app/vosk-model-en-us-0.22-lgraph

WORKDIR /app

ENV PATH="/venv/bin:$PATH"

CMD ["python", "dictation_service.py"]
