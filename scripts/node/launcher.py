#!/usr/bin/env python3
# launcher.py - BEAMNode service launcher
# 1. Runs detection on startup (sensor_detection/detect.py)
# 2. Launches Scheduler in background (scheduler.py)
# 3. Triggers Shipping daily at 13:00 (shipping_queuing/shipping.py)

import subprocess
import os
import sys
import time
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = "/home/pi/BEAMNode_Prototype1/scripts/node"
LOG_DIR = "/home/pi/BEAMNode_Prototype1/logs"

# Full paths to your scripts
DETECT_SCRIPT = os.path.join(BASE_DIR, "sensor_detection/detect.py")
SCHEDULER_SCRIPT = os.path.join(BASE_DIR, "scheduler.py")
SHIPPING_SCRIPT = os.path.join(BASE_DIR, "shipping_queuing/shipping.py")

os.makedirs(LOG_DIR, exist_ok=True)

def run_script_wait(script_full_path):
    """Runs a script and waits for it to finish (Blocking)."""
    if not os.path.exists(script_full_path):
        print(f"[launcher] ERROR: Script not found: {script_full_path}")
        return False

    script_name = os.path.basename(script_full_path)
    print(f"[launcher] Running {script_name}...")
    
    try:
        # Run script. Capture output for logging.
        result = subprocess.run(["python3", script_full_path], capture_output=True, text=True)
        
        # Write to log file
        log_file = os.path.join(LOG_DIR, f"{script_name}.log")
        with open(log_file, "a") as f:
            f.write(f"\n--- Run at {datetime.now()} ---\n")
            f.write(result.stdout)
            f.write(result.stderr)
        
        if result.returncode != 0:
            print(f"[launcher] ERROR: {script_name} failed with code {result.returncode}")
            # Print stderr to systemd logs so you can see it in status
            print(result.stderr)
            return False
        
        print(f"[launcher] {script_name} completed successfully.")
        return True
    except Exception as e:
        print(f"[launcher] Exception running {script_name}: {e}")
        return False

def start_scheduler_background():
    """Starts the scheduler as a background process (Non-blocking)."""
    if not os.path.exists(SCHEDULER_SCRIPT):
        print(f"[launcher] CRITICAL ERROR: Scheduler not found at {SCHEDULER_SCRIPT}")
        return None

    print("[launcher] Starting scheduler.py in background...")
    
    # Open a log file for the scheduler's stdout/stderr
    log_file = open(os.path.join(LOG_DIR, "scheduler_process.log"), "a")
    
    # We set cwd to BASE_DIR so scheduler can find config.json easily if needed
    proc = subprocess.Popen(
        ["python3", SCHEDULER_SCRIPT],
        stdout=log_file,
        stderr=log_file,
        cwd=BASE_DIR 
    )
    return proc

def main_loop():
    # 1. Run Detection (Wait for it to finish)
    # This detects sensors and updates config.json
    success = run_script_wait(DETECT_SCRIPT)
    if not success:
        print("[launcher] WARNING: Detection reported errors, but proceeding to scheduler...")

    # 2. Start Scheduler (Background)
    scheduler_process = start_scheduler_background()
    if scheduler_process is None:
        print("[launcher] Scheduler could not start. Exiting.")
        sys.exit(1)
    
    # State tracking for daily shipping
    last_ship_date = None

    print("[launcher] Entering Supervisor Loop (Monitoring Scheduler + 13:00 Shipping)")

    while True:
        current_time = datetime.now()
        
        # --- A. Monitor Scheduler Health ---
        # poll() returns None if running, or the exit code if stopped
        if scheduler_process.poll() is not None:
            print(f"[launcher] ALERT: Scheduler crashed (code {scheduler_process.returncode}). Restarting...")
            scheduler_process = start_scheduler_background()

        # --- B. Check for 13:00 Shipping (1:00 PM) ---
        # Run if hour is 13 AND we haven't shipped yet today
        today_str = current_time.strftime("%Y-%m-%d")
        
        if current_time.hour == 13 and last_ship_date != today_str:
            print("[launcher] It is 13:00. Starting Daily Shipping...")
            run_script_wait(SHIPPING_SCRIPT)
            last_ship_date = today_str # Mark as done for today
            print("[launcher] Shipping finished. Waiting for next schedule.")

        # Sleep to prevent high CPU usage (check every 10 seconds)
        time.sleep(10)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[launcher] Stopping service...")
