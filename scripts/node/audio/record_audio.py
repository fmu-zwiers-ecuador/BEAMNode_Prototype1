# record.py — Unified Audio Recorder for BEAM
# Author: Raiz Mohammed / Jaidyn Edwards
# Updated: 2025-10-20

import os
import json
import time
import wave
import pyaudio
from datetime import datetime, timezone

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Load config
config_path = os.path.join(project_root, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

audio_config = config["audio"]
global_config = config["global"]

# Check if recording is enabled

# Base directory: /home/pi/data/audio
base_dir = global_config.get("base_dir", os.path.join(project_root, "data"))
directory = os.path.join(base_dir, audio_config.get("directory", "audio"))
os.makedirs(directory, exist_ok=True)

# File path setup
timestamp = datetime.now(timezone.utc).isoformat()
file_prefix = audio_config.get("file_prefix", "recording_")
wav_filename = os.path.join(directory, f"{file_prefix}{timestamp}.wav")

# Recording parameters
DURATION = audio_config.get("duration_sec", 10)
RATE = audio_config.get("sample_rate", 48000)
CHANNELS = audio_config.get("channels", 1)
FORMAT = pyaudio.paInt16 if audio_config.get("format", "int16") == "int16" else pyaudio.paFloat32
CHUNK = audio_config.get("chunk", 1024)

# Initialize audio interface
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

if global_config.get("print_debug", True):
    print(f"[BEAM] Recording {DURATION}s of audio to {wav_filename}")

frames = []
for _ in range(0, int(RATE / CHUNK * DURATION)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)

stream.stop_stream()
stream.close()
audio.terminate()

# Save .wav file
with wave.open(wav_filename, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

if global_config.get("print_debug", True):
    print(f"[BEAM] Saved audio file: {wav_filename}")

# Create MASTER.json in same directory
master_json = os.path.join(directory, "MASTER.json")

# New record entry
record_entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "file": wav_filename,
    "duration_sec": DURATION,
    "sample_rate": RATE,
    "channels": CHANNELS,
    "format": "int16"
}

# Append to MASTER.json
if not os.path.exists(master_json):
    with open(master_json, "w") as f:
        json.dump({"node_id": global_config.get("node_id"), "sensor": "audio", "records": []}, f, indent=4)

with open(master_json, "r+") as f:
    log = json.load(f)
    if "records" not in log:
        log["records"] = []
    log["records"].append(record_entry)
    f.seek(0)
    json.dump(log, f, indent=4)
    f.truncate()

if global_config.get("print_debug", True):
    print(f"[BEAM] Logged record to {master_json}")