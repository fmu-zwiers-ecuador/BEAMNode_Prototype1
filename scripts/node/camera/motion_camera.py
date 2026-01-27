"""
Motion-Triggered Camera Logger for BEAM
Author: Gabriel Gonzales, Raiz Mohammed
Date: 2025-10-20

Detects motion on GPIO pin (default: 4) and captures images using PiCamera2.
All parameters are loaded from config.json. Images and JSON metadata are saved
under /home/pi/data/camera/.
"""


import os
import json
import time
from datetime import datetime, timezone
from gpiozero import MotionSensor
from picamera2 import Picamera2

# -----------------------------
# Load configuration
# -----------------------------
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
config_path = os.path.join(project_root, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

global_config = config.get("global", {})
cam_config = config.get("camera", {})



node_id = global_config.get("node_id", "unknown-node")
base_dir = global_config.get("base_dir", os.path.join(project_root, "data"))

# -----------------------------
# Directory setup
# -----------------------------
directory = os.path.join(base_dir, cam_config.get("directory", "camera"))
os.makedirs(directory, exist_ok=True)
log_path = os.path.join(directory, "images_log.json")

# -----------------------------
# Motion sensor and camera setup
# -----------------------------
gpio_pin = cam_config.get("gpio_pin", 4)
pir = MotionSensor(gpio_pin)

picam = Picamera2()
main_res = tuple(cam_config.get("resolution", [1920, 1080]))
lores_res = tuple(cam_config.get("lores_resolution", [640, 480]))
camera_config = picam.create_still_configuration(
    main={"size": main_res}, lores={"size": lores_res}, display="lores"
)
picam.configure(camera_config)
picam.start()
time.sleep(1)  # allow sensor to warm up

if global_config.get("print_debug", True):
    print(f"[BEAM] Motion camera armed on GPIO {gpio_pin}, waiting for movement...")

i = 0
cooldown = cam_config.get("cooldown_sec", 1)

# -----------------------------
# Motion detection loop
# -----------------------------
while True:
    pir.wait_for_motion()
    timestamp = datetime.now(timezone.utc).isoformat()

    filename = f"{cam_config.get('file_prefix', 'motionpic_')}{timestamp}.jpg"
    file_path = os.path.join(directory, filename)

    if global_config.get("print_debug", True):
        print(f"[BEAM] Motion detected — capturing {filename}")

    # Capture image
    picam.capture_file(file_path)

    # Log metadata
    record = {
        "timestamp": timestamp,
        "file": file_path
    }

    # Append to log JSON
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict) or "records" not in data:
                        data = {"node_id": node_id, "sensor": "camera", "records": []}
                except Exception:
                    data = {"node_id": node_id, "sensor": "camera", "records": []}
        else:
            data = {"node_id": node_id, "sensor": "camera", "records": []}

        data["records"].append(record)
        with open(log_path, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"[ERROR] Failed to save image log: {e}")

    i += 1
    time.sleep(cooldown)