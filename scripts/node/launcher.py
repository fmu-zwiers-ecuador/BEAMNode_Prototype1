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

    print(f"[launcher] Starting {script_name}...")
    
    # We use subprocess.run for detect.py (waits for it to finish)
    # We also use it for scheduler.py because scheduler runs an infinite loop.
    # The launcher basically "becomes" the supervisor for the scheduler.
    try:
        # capture_output=True means output is hidden unless we write it to log
        # For the main scheduler loop, you might want to see output in systemd logs:
        # set capture_output=False if you want real-time logs in 'journalctl'
        capture = True 
        
        result = subprocess.run(
            ["python3", script_path], 
            capture_output=capture, 
            text=True
        )
        
        # If the script finishes (or crashes), we log the output
        log_file = os.path.join(LOG_DIR, f"{script_name}.log")
        with open(log_file, "a") as f:
            f.write(f"\n--- Run at {time.ctime()} ---\n")
            if result.stdout: f.write(result.stdout)
            if result.stderr: f.write(result.stderr)

        if result.returncode != 0:
            print(f"[launcher] ERROR: {script_name} exited with code {result.returncode}")
            return False
        
        print(f"[launcher] {script_name} finished successfully.")
        return True

    except Exception as e:
        print(f"[launcher] CRITICAL EXCEPTION running {script_name}: {e}")
        return False

# --- THIS IS THE MISSING PART ---
if __name__ == "__main__":
    print("[launcher] Service sequence initiating...")

    # 1. Run Detect (Runs once to update config.json, then exits)
    success = run_script("detect.py")
    
    if success:
        print("[launcher] Detection complete. Launching Scheduler...")
        
        # 2. Run Scheduler (This runs an infinite loop)
        # The service will stay 'Active' as long as this line is running
        run_script("scheduler.py")
    else:
        print("[launcher] Detection failed. Exiting.")
        sys.exit(1)
