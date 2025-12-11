############## SCHEDULER.PY - BEAM PROJECT - GABRIEL GONZALEZ and Jackson Roberts - DEC 2025 ##################
## This script schedules times for data collection from all sensors.                         ##
###########################################################################################


import json
import os
import subprocess
import time
from datetime import datetime, timedelta

# --- Absolute Path Configuration ---
# 💡 FIX 1: Use absolute paths relative to the script's location for reliable access
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..')) # /home/pi/BEAMNode_Prototype1/

# Configuration and Script Paths
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")
NODE_DIR = BASE_DIR # This points to /home/pi/BEAMNode_Prototype1/scripts/node

# Data and Shipping Directories
# 💡 FIX 2: Ensure data directories are created relative to /home/pi for reliability
data_dir = "/home/pi/data"
os.makedirs(data_dir, exist_ok=True)

shipping_dir = "/home/pi/shipping"
os.makedirs(shipping_dir, exist_ok=True)


# Track last run times
last_run_times = {}

# --- Utility Functions ---

def load_config():
    """Load frequency configuration for all sensors."""
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[CRITICAL ERROR] Config file not found at: {CONFIG_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"[CRITICAL ERROR] Failed to parse JSON in: {CONFIG_PATH}")
        return {}


def find_sensor_script(sensor):
    """Find the Python script inside each sensor’s directory."""
    # Assuming sensor folders are within NODE_DIR (e.g., /scripts/node/AHT)
    sensor_dir = os.path.join(NODE_DIR, sensor)
    
    # 💡 FIX 3: Corrected path search logic - it seems the sensor folders are *siblings* # to the scheduler.py file, which is usually correct in BEAM-like projects.
    
    sensor_parent_dir = os.path.abspath(os.path.join(NODE_DIR, '..')) # scripts/
    sensor_path = os.path.join(sensor_parent_dir, sensor) # scripts/AHT
    
    if not os.path.isdir(sensor_path):
        print(f"[WARN] Directory not found for sensor '{sensor}' at {sensor_path}")
        return None

    for file in os.listdir(sensor_path):
        if file.endswith(".py"):
            return os.path.join(sensor_path, file)

    print(f"[WARN] No .py script found in '{sensor_path}'")
    return None


def run_sensor_once(sensor):
    """Run the sensor’s Python script once."""
    script_path = find_sensor_script(sensor)
    if not script_path:
        return

    print(f"[INFO] Running {sensor} at {datetime.now().strftime('%H:%M:%S')}")
    
    # 💡 Improvement: Added a timeout for robustness
    try:
        result = subprocess.run(
            ["python3", script_path], 
            capture_output=True, 
            text=True,
            timeout=30 # 30 second timeout for the sensor script
        )
        
        # Log result output if not successful for debugging
        if result.returncode == 0:
            print(f"[INFO] {sensor} finished successfully.")
        else:
            print(f"[ERROR] {sensor} exited with code {result.returncode}")
            print(f"[ERROR] STDOUT: {result.stdout.strip()}")
            print(f"[ERROR] STDERR: {result.stderr.strip()}")
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {sensor} script timed out after 30 seconds.")
    except FileNotFoundError:
        print(f"[CRITICAL ERROR] python3 executable not found.")


def scheduler_loop():
    print("[INFO] Frequency-based Scheduler started")
    
    # Check that data directory is writable (simple test)
    if not os.access(data_dir, os.W_OK):
        print(f"[CRITICAL ERROR] Cannot write to data directory: {data_dir}. Check permissions!")
        return

    config = load_config()

    # Initialize last run times to ensure first run happens almost immediately
    now = datetime.now()
    for sensor in config.keys():
        # Set last run time far in the past to trigger immediate run on startup
        last_run_times[sensor] = now - timedelta(hours=10)

    while True:
        now = datetime.now()
        config = load_config()  # reload config during loop

        for sensor, params in config.items():
            freq_min = params.get("frequency")
            enabled = params.get("enabled", True)
            
            if freq_min is None or not enabled:
                continue
                
            last_run = last_run_times.get(sensor, now) # Use 'now' if key is missing
            next_run = last_run + timedelta(minutes=freq_min)

            if now >= next_run:
                run_
