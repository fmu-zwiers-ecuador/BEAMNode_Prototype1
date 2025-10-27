############## SCHEDULER.PY - BEAM PROJECT - GABRIEL GONZALEZ - OCT 2025 ##################
## This script should schedule times for data collection from all sensors: AHT, Audio,   ##
## BME280, and TSL2591.                                                                  ##
###########################################################################################


import json
import os
import subprocess
import time
from datetime import datetime

CONFIG_PATH = "../config.json"
NODE_DIR = ".."

# Track running processes per sensor
running_processes = {}

def load_config():
    """Load sensor scheduling configuration."""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

# change this to see if current time matches sensor time
def audio_interval_check(now, start_str, end_str):
    """Check if current time (local) is within a recurring daily time window."""
    start = datetime.strptime(start_str, "%H:%M").time()
    end = datetime.strptime(end_str, "%H:%M").time()

    # Handle case where interval crosses midnight
    if start < end:
        return start <= now.time() <= end
    else:
        return now.time() >= start or now.time() <= end
    
# function to run bme, aht, and tsl, should only run once if time matches
def sensor_run(now, sensor_start):
    """Check if current time matches sensor start time"""
    start = datetime.strptime(sensor_start, "%H:%M").time()
    return now.time() == start

def find_sensor_script(sensor):                                 # keep
    """Find the control script inside the sensor’s folder."""
    sensor_dir = os.path.join(NODE_DIR, sensor)
    if not os.path.isdir(sensor_dir):
        print(f"[WARN] Directory not found for sensor '{sensor}'")
        return None

    for file in os.listdir(sensor_dir):
        if file.endswith(".py"):
            return os.path.join(sensor_dir, file)

    print(f"[WARN] No .py script found in '{sensor_dir}'")
    return None

def launch_sensor(sensor):
    """Launch the sensor’s control script."""
    script_path = find_sensor_script(sensor)
    if not script_path:
        return None

    print(f"[INFO] Starting sensor '{sensor}' using {script_path}")
    return subprocess.Popen(["python3", script_path])

def stop_sensor(sensor):
    """Stop a running sensor process."""
    proc = running_processes.get(sensor)
    if proc and proc.poll() is None:
        print(f"[INFO] Stopping sensor '{sensor}'")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    running_processes.pop(sensor, None)

def scheduler_loop():
    """Main loop that activates and deactivates sensors on schedule."""
    print("[INFO] Scheduler started")
    while True:
        now = datetime.now()  # local time
        config = load_config()

        for sensor, intervals in config.items():
            # Determie if sensor is audio
            if sensor == "audio":
                active = any(
                    audio_interval_check(now, interval["start"], interval["end"])
                    for interval in intervals
                )
                if active and sensor not in running_processes:
                    running_processes[sensor] = launch_sensor(sensor)
                elif not active and sensor in running_processes:
                    stop_sensor(sensor)
            else:
                active = any(
                    sensor_run(now, interval["start"])
                    for interval in intervals
                )


        time.sleep(10)  # poll every 10 seconds

if __name__ == "__main__":
    try:
        scheduler_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Scheduler shutting down...")
        for sensor in list(running_processes.keys()):
            stop_sensor(sensor)
        print("[INFO] All sensors stopped.")
