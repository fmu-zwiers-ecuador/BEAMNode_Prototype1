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
    result = subprocess.run(["python3", script_path], capture_output=True, text=True)
    
    log_file = os.path.join(LOG_DIR, f"{script_name}.log")
    with open(log_file, "a") as f:
        f.write(result.stdout)
        f.write(result.stderr)

    if result.returncode != 0:
        print(f"[launcher] ERROR: {script_name} exited with {result.returncode}")
