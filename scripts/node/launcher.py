#!/usr/bin/env python3
"""
Launcher for BEAMNode:
1. Run detect.py once at startup
2. Launch scheduler.py (continuous)
3. Run shipping.py at scheduled time
"""

import subprocess
import sys
import time
import os
from datetime import datetime, timedelta

# ----------------- CONFIG -----------------
PYTHON_EXEC = "/usr/bin/env"
PYTHON_ARGS = ["python3"]

DETECT_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/sensor_detection/detect.py"
SCHEDULER_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/scheduler.py"
SHIPPING_SCRIPT = "/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing/shipping.py"

# Scheduler and shipping times
SCHEDULER_HOUR = 12
SHIPPING_HOUR = 13

# ----------------- FUNCTIONS -----------------
def run_script(script_path):
    """Run a Python script synchronously. Exit on failure."""
    print(f"[Launcher] Running: {script_path}")
    try:
        result = subprocess.run([PYTHON_EXEC] + PYTHON_ARGS + [script_path],
                                stdout=sys.stdout,
                                stderr=sys.stderr,
                                check=True)
        print(f"[Launcher] {os.path.basename(script_path)} finished with code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"[Launcher] ERROR: {os.path.basename(script_path)} failed (code {e.returncode})")
        sys.exit(1)
    except Exception as e:
        print(f"[Launcher] CRITICAL ERROR running {script_path}: {e}")
        sys.exit(1)


def wait_until(hour):
    """Pause execution until the next occurrence of the given hour."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if now >= target:
        # if the hour has passed today, schedule for tomorrow
        target += timedelta(days=1)
    wait_seconds = (target - now).total_seconds()
    print(f"[Launcher] Waiting {wait_seconds:.0f}s until {hour:02d}:00")
    time.sleep(wait_seconds)


def main():
    print("[Launcher] --- BEAMNode Launcher Starting ---")

    # 1️⃣ Run detect.py once
    run_script(DETECT_SCRIPT)

    # 2️⃣ Wait until scheduler hour and start scheduler.py in background
    wait_until(SCHEDULER_HOUR)
    print("[Launcher] Launching scheduler.py...")
    try:
        scheduler_proc = subprocess.Popen([PYTHON_EXEC] + PYTHON_ARGS + [SCHEDULER_SCRIPT],
                                          stdout=sys.stdout,
                                          stderr=sys.stderr)
        print(f"[Launcher] scheduler.py running with PID {scheduler_proc.pid}")
    except Exception as e:
        print(f"[Launcher] ERROR launching scheduler.py: {e}")
        sys.exit(1)

    # 3️⃣ Wait until shipping hour and run shipping.py once
    wait_until(SHIPPING_HOUR)
    run_script(SHIPPING_SCRIPT)

    # 4️⃣ Keep launcher alive to monitor scheduler
    try:
        print("[Launcher] Monitoring scheduler.py process...")
        scheduler_proc.wait()
        print(f"[Launcher] scheduler.py exited with code {scheduler_proc.returncode}")
    except KeyboardInterrupt:
        print("[Launcher] KeyboardInterrupt received. Terminating scheduler...")
        scheduler_proc.terminate()
        scheduler_proc.wait()

    print("[Launcher] Launcher exiting.")


if __name__ == "__main__":
    main()
