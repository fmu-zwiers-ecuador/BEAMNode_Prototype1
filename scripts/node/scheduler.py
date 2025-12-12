############## SCHEDULER.PY - BEAM PROJECT - GABRIEL GONZALEZ - OCT 2025 ##################
## This script should schedule times for data collection from all sensors: AHT, Audio,   ##
## BME280, and TSL2591.                                                                  ##
###########################################################################################


import json
import os
import subprocess
import time
from datetime import datetime, timedelta

CONFIG_PATH = "./config.json"
NODE_DIR = "."

# create /home/pi/data if it doesn't exist
data_dir = "/home/pi/data"
os.makedirs(data_dir, exist_ok=True)

# create /home/pi/shipping if it doesn't exist
shipping_dir = "/home/pi/shipping"
os.makedirs(shipping_dir, exist_ok=True)

# Track last run times
last_run_times = {}

# current time
current_time = datetime.now()

#beginning of next hour
start_time = (current_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

def load_config():
    """Load frequency configuration for all sensors."""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def find_sensor_script(sensor):
    """Find the Python script inside each sensor’s directory."""
    sensor_dir = os.path.join(NODE_DIR, sensor)
    if not os.path.isdir(sensor_dir):
        print(f"[WARN] Directory not found for sensor '{sensor}'")
        return None

    for file in os.listdir(sensor_dir):
        if file.endswith(".py"):
            return os.path.join(sensor_dir, file)

    print(f"[WARN] No .py script found in '{sensor_dir}'")
    return None

def run_sensor_once(sensor):
    """Run the sensor’s Python script once."""
    script_path = find_sensor_script(sensor)
    if not script_path:
        return

    print(f"[INFO] Running {sensor} at {datetime.now().strftime('%H:%M:%S')}")
    result = subprocess.run(["python3", script_path], capture_output=True, text=True)

    # You can log result.stdout/result.stderr here if needed
    if result.returncode == 0:
        print(f"[INFO] {sensor} finished successfully.")
    else:
        print(f"[ERROR] {sensor} exited with code {result.returncode}")
        print(result.stderr)



def scheduler_loop():
    print("[INFO] Frequency-based Scheduler started")
    config = load_config()

    # Initialize last run times to "now" so they don't all start instantly
    now = datetime.now()
    for sensor in config.keys():
        last_run_times[sensor] = now

    while True:
        now = datetime.now()
        config = load_config()  # reload in case user updates config.json

        for sensor, params in config.items():
            freq_min = params.get("frequency")
            enabled = params.get("enabled", True)
            if freq_min is None or not enabled:
                continue  # skip if no frequency defined
            last_run = last_run_times.get(sensor)
            next_run = last_run + timedelta(minutes=freq_min)

            if now >= next_run:
                run_sensor_once(sensor)
                last_run_times[sensor] = datetime.now()
            time.sleep(1)  # brief sleep to avoid tight loop
    
                        
        time.sleep(5)  # check every 5 seconds

if __name__ == "__main__":
    try:
        # wait until start time
        print(f"[INFO] Scheduler will start at {start_time.strftime('%H:%M:%S')}")
        while datetime.now() < start_time:
            time.sleep(1)
        scheduler_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Scheduler shutting down gracefully.")