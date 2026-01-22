#!/usr/bin/env python3
# launcher.py - Master controller for BEAMNode Prototype 1
# Responsibilities: Startup Detection, Scheduler Maintenance, and 13:00 Shipping.

import subprocess
import os
import time
import sys
from datetime import datetime

# --- CONFIGURATION ---
NODE_DIR = "/home/pi/BEAMNode_Prototype1/scripts/node"
DETECT_PATH = os.path.join(NODE_DIR, "sensor_detection/detect.py")
SCHEDULER_PATH = os.path.join(NODE_DIR, "scheduler.py")
SHIPPING_PATH = os.path.join(NODE_DIR, "shipping_queuing/shipping.py")
LOG_PATH = "/home/pi/BEAMNode_Prototype1/logs/launcher.log"

def log(msg):
    """Internal launcher logging."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [launcher] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except:
        pass

def run_script_sync(path):
    """Runs a script and waits for it to finish (Synchronous)."""
    if os.path.exists(path):
        log(f"Executing: {path}")
        subprocess.run(["python3", path])
    else:
        log(f"ERROR: File not found at {path}")

def start_scheduler_async():
    """Starts the original scheduler.py in the background (Asynchronous)."""
    if os.path.exists(SCHEDULER_PATH):
        log(f"Starting Background Scheduler: {SCHEDULER_PATH}")
        return subprocess.Popen(["python3", SCHEDULER_PATH])
    else:
        log(f"CRITICAL ERROR: Scheduler script missing.")
        return None

if __name__ == "__main__":
    log("=== BEAMNode System Startup ===")

    # 1. REQUIREMENT: Run detect.py once on startup
    run_script_sync(DETECT_PATH)

    # 2. REQUIREMENT: Start original scheduler and keep it going
    sched_proc = start_scheduler_async()

    if sched_proc is None:
        log("Failed to initialize scheduler. System exiting.")
        sys.exit(1)

    # 3. MONITORING LOOP
    log("Entering master monitoring loop...")
    while True:
        try:
            now = datetime.now()

            # A. Check Scheduler Health (Restart if Pi went down or process crashed)
            if sched_proc.poll() is not None:
                log("ALERT: Scheduler process stopped. Restarting...")
                time.sleep(5)
                sched_proc = start_scheduler_async()

            # B. REQUIREMENT: Run Shipping.py at 13:00
            # We use a 30-second window to ensure the trigger catches
            if now.hour == 13 and now.minute == 0 and 0 <= now.second <= 30:
                log("13:00 Target reached. Running Shipping.py...")
                run_script_sync(SHIPPING_PATH)
                log("Shipping complete. Resuming monitor.")
                time.sleep(31) # Avoid double-triggering within the same minute

            # Sleep to keep CPU usage minimal
            time.sleep(10)

        except KeyboardInterrupt:
            log("Manual shutdown detected. Terminating scheduler...")
            sched_proc.terminate()
            break
        except Exception as e:
            log(f"Unexpected monitor error: {e}")
            time.sleep(10)
