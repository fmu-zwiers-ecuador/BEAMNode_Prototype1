#!/usr/bin/env python3
# launcher.py - BEAMNode service launcher
# Runs detection and scheduler at startup

import subprocess
import os
import sys
import time

NODE_DIR = "/home/pi/BEAMNode_Prototype1/scripts/node"
LOG_DIR = "/home/pi/BEAMNode_Prototype1/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def run_script(script_name):
    script_path = os.path.join(NODE_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"[launcher] ERROR: {script_path} does not exist")
        return False

    print(f"[launcher] Running {script_name}...")
    
    # Check if we are running the scheduler, which runs forever
    # We still use subprocess.run, so this script acts as a supervisor
    # that waits for scheduler to finish (or crash).
    try:
        result = subprocess.run(["python3", script_path], capture_output=True, text=True)
        
        # If we get here, the script has finished or crashed
        log_file = os.path.join(LOG_DIR, f"{script_name}.log")
        with open(log_file, "a") as f:
            f.write(f"\n--- Run at {time.ctime()} ---\n")
            f.write(result.stdout)
            f.write(result.stderr)

        if result.returncode != 0:
            print(f"[launcher] ERROR: {script_name} exited with {result.returncode}")
            return False
        
        print(f"[launcher] {script_name} finished successfully.")
        return True

    except Exception as e:
        print(f"[launcher] CRITICAL ERROR running {script_name}: {e}")
        return False

if __name__ == "__main__":
    print("[launcher] Service started.")

    # 1. Run Detection (Runs once, then finishes)
    # This ensures config.json is updated before the scheduler looks at it.
    success = run_script("detect.py")
    
    if success:
        print("[launcher] Detection complete. Starting Scheduler...")
        
        # 2. Run Scheduler (Runs forever)
        # The launcher will pause here and stay alive as long as scheduler.py runs.
        # If scheduler.py crashes, run_script returns, and the service exits (triggering a restart).
        run_script("scheduler.py")
    else:
        print("[launcher] Detection failed. Exiting to trigger restart.")
        sys.exit(1)
