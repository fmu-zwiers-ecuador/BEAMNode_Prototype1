# record2.py
# Audio recording with AudioMoth USB mic + JSON metadata logging
# Author: Jaidyn Edwards / Raiz Mohammed
# Date: 2025-09-26 (updated 2025-10-01)

import os
import json
import time
import datetime
import wave
import pyaudio

# Config
OUTPUT_DIR = "/home/pi/beam_project/recordings"
MASTER_JSON = "/home/pi/beam_project/MASTER.json"
DURATION = 10            # seconds
RATE = 48000             # 48kHz sample rate
CHANNELS = 1             # mono
FORMAT = pyaudio.paInt16 # 16-bit audio
CHUNK = 1024             # buffer size

# Ensure folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Filename + timestamp
timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
wav_filename = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.wav")

# Init PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print(f"[BEAM] Recording {DURATION}s of audio to {wav_filename}")

frames = []
for _ in range(0, int(RATE / CHUNK * DURATION)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)

stream.stop_stream()
stream.close()
audio.terminate()

# Save .wav
with wave.open(wav_filename, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"[BEAM] Saved audio: {wav_filename}")

# Metadata for log
record = {
    "time": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "file": wav_filename,
    "duration_sec": DURATION,
    "sample_rate": RATE,
    "channels": CHANNELS,
    "format": "int16"
}

# Update MASTER.json
if not os.path.exists(MASTER_JSON):
    with open(MASTER_JSON, "w") as f:
        json.dump({"records": []}, f, indent=4)

with open(MASTER_JSON, "r+") as f:
    log = json.load(f)
    log["records"].append(record)
    f.seek(0)
    json.dump(log, f, indent=4)
    f.truncate()

print(f"[BEAM] Logged record to {MASTER_JSON}")
