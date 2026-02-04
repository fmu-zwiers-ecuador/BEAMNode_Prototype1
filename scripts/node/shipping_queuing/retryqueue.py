"""
retryqueue.py: A script that request and queues data from each node.

This script checks to see if all 5 nodes are dead or alive, and then checks the 
ping status. It then uses rsync to check for new data and pull it from the 
shipping folder on the nodes to the supervisor.

Path: /home/pi/shipping(on node) ==> /home/pi/data(on supervisor)

Author: Gabriel Gonzalez, Noel Challa, Alex Lance, Jackson Roberts, Jaylen Small
Last Updated: 2-4-26 
"""
import sys
from pathlib import Path

# Adjusting path for vendor libraries if necessary
VENDOR_DIR = Path(__file__).resolve().parents[1] / "vendor"
sys.path.insert(0, str(VENDOR_DIR))

import subprocess
import os
import json
from datetime import datetime

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
JSON_FILEPATH = "/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing/node_states.json"
SUPERVISOR_DATA_ROOT = "/home/pi/data"
REMOTE_SHIP_DIR = "/home/pi/shipping"
LOG_FILE = "/home/pi/logs/queue.log"

MAX_RETRIES = 5
PING_COUNT = 1

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

# ---------------------------------------------------
# LOAD/SAVE NODE STATE
# ---------------------------------------------------
def load_nodes():
    if not os.path.exists(JSON_FILEPATH):
        log(f"ERROR: node state file missing: {JSON_FILEPATH}")
        return {}
    with open(JSON_FILEPATH, "r") as f:
        return json.load(f)

def save_nodes(nodes):
    with open(JSON_FILEPATH, "w") as f:
        json.dump(nodes, f, indent=4)

# ---------------------------------------------------
# NETWORK & DATA OPERATIONS
# ---------------------------------------------------
def ping_node(ip):
    """Return True if node responds, else False."""
    try:
        subprocess.check_output(
            ["ping", "-c", str(PING_COUNT), "-W", "1", ip],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def has_remote_data(ip, name):
    """Checks if remote directory has files using rsync list mode."""
    # Listing via rsync is faster than SSH + LS
    cmd = ["rsync", f"pi@{ip}:{REMOTE_SHIP_DIR}/"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # rsync output for an empty dir shows only '.'
        # If output lines > 1, files are present
        files_present = len(result.stdout.strip().split('\n')) > 1
        if not files_present:
            log(f"{name}: No data found in shipping directory.")
        return files_present
    except subprocess.CalledProcessError:
        log(f"{name}: Error checking remote directory.")
        return False

def rsync_pull(ip):
    """Pulls data from node to supervisor."""
    os.makedirs(SUPERVISOR_DATA_ROOT, exist_ok=True)
    cmd = [
        "rsync", "-avz", "--partial", "--ignore-existing",
        f"pi@{ip}:{REMOTE_SHIP_DIR}/", SUPERVISOR_DATA_ROOT
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def delete_shipping_data(ip, name):
    """Clears remote shipping data via single SSH command."""
    log(f"{name}: Wiping remote shipping folder...")
    # Standard SSH command execution
    cmd = ["ssh", f"pi@{ip}", f"sudo rm -rf {REMOTE_SHIP_DIR}/*"]
    try:
        subprocess.run(cmd, check=True)
        log(f"{name}: SUCCESS — Remote folder cleared.")
        return True
    except subprocess.CalledProcessError:
        log(f"{name}: ERROR — Could not clear remote data.")
        return False

# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------
def main():
    log("=== STARTING DAILY SHIPPING QUEUE ===")
    nodes = load_nodes()
    if not nodes:
        return

    # STEP 1 — Ping & State Check
    log("=== PINGING ALL NODES ===")
    for name, info in nodes.items():
        ip = info["ip"]
        was_alive = info.get("node_state") == "alive"
        
        if ping_node(ip):
            nodes[name]["node_state"] = "alive"
            if not was_alive: log(f"{name}: RECOVERED")
        else:
            nodes[name]["node_state"] = "dead"
            if was_alive: log(f"{name}: LOST CONNECTION")
    save_nodes(nodes)

    # STEP 2 — Initial Transfer Attempt
    log("=== INITIAL DATA TRANSFER ATTEMPT ===")
    failed_nodes = []

    for name, info in nodes.items():
        ip = info["ip"]

        if info["node_state"] == "dead":
            log(f"{name}: SKIPPED (DEAD)")
            failed_nodes.append(name)
            continue

        # Check for data before pulling
        if not has_remote_data(ip, name):
            nodes[name]["transfer_fail"] = False
            continue

        log(f"{name}: Pulling data...")
        if rsync_pull(ip):
            log(f"{name}: SUCCESS — transferred")
            nodes[name]["transfer_fail"] = False
            delete_shipping_data(ip, name) # Fixed typo
        else:
            log(f"{name}: FAILURE — transfer failed")
            nodes[name]["transfer_fail"] = True
            failed_nodes.append(name)

    save_nodes(nodes)

    # STEP 3 — Retries for Failed/Offline Nodes
    if failed_nodes:
        log(f"=== RETRYING FAILED NODES (UP TO {MAX_RETRIES}) ===")
        for attempt in range(1, MAX_RETRIES + 1):
            if not failed_nodes: break
            log(f"--- RETRY ROUND {attempt} ---")
            
            still_failing = []
            for name in failed_nodes:
                ip = nodes[name]["ip"]
                
                # Re-ping to see if node came back online
                if not ping_node(ip):
                    still_failing.append(name)
                    continue

                if not has_remote_data(ip, name):
                    nodes[name]["transfer_fail"] = False
                    continue

                if rsync_pull(ip):
                    log(f"{name}: SUCCESS on retry #{attempt}")
                    nodes[name]["transfer_fail"] = False
                    delete_shipping_data(ip, name)
                else:
                    still_failing.append(name)
            
            failed_nodes = still_failing
            save_nodes(nodes)

    # STEP 4 — Finalize
    if not failed_nodes:
        log("=== FINAL STATUS: ALL NODES SUCCEEDED ===")
    else:
        log("=== FINAL STATUS: SOME NODES FAILED ===")

    log("=== END OF DAILY SHIPPING QUEUE ===")

if __name__ == "__main__":
    main()
