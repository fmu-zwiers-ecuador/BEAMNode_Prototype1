"""
retryqueue.py: A script that request and queues data from each node.

This script checks to see if all 5 nodes are dead or alive. It then uses 
rsync to check for new data and pull it from the shipping folder on the 
nodes to the supervisor using mDNS hostnames (pi@nodeX.local).

Path: /home/pi/shipping(on node) ==> /home/pi/data(on supervisor)

Author: Gabriel Gonzalez, Noel Challa, Alex Lance, Jackson Roberts, and Jaylen Small
Last Updated: 2-4-26 
"""
import sys
from pathlib import Path

# Adjusting path for vendor libraries
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
def ping_node(full_hostname):
    """Return True if node responds via .local address, else False."""
    try:
        subprocess.check_output(
            ["ping", "-c", str(PING_COUNT), "-W", "2", full_hostname],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def has_remote_data(full_hostname):
    """Checks remote directory using the rsync list method."""
    remote_path = f"pi@{full_hostname}:{REMOTE_SHIP_DIR}/"
    cmd = ["rsync", "-d", remote_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Filter output: ignore the directory itself ('.') and empty lines
        lines = [l for l in result.stdout.strip().split('\n') if l.strip() and not l.strip().endswith('.')]
        log(f"{full_hostname}: SUCCESS checking remote directory.")
        return len(lines) > 0
    except subprocess.CalledProcessError:
        log(f"{full_hostname}: ERROR checking remote directory.")
        return False

def rsync_pull(full_hostname):
    """Pulls data from node to supervisor."""
    os.makedirs(SUPERVISOR_DATA_ROOT, exist_ok=True)
    remote_source = f"pi@{full_hostname}:{REMOTE_SHIP_DIR}/"
    cmd = [
        "rsync", "-avz", "--partial", "--ignore-existing",
        remote_source, SUPERVISOR_DATA_ROOT
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def delete_shipping_data(full_hostname):
    """Clears remote shipping data after successful transfer."""
    log(f"{full_hostname}: Wiping remote shipping folder...")
    cmd = ["ssh", f"pi@{full_hostname}", f"sudo rm -rf {REMOTE_SHIP_DIR}/*"]
    try:
        subprocess.run(cmd, check=True)
        log(f"{full_hostname}: SUCCESS clearing remote data")
        return True
    except subprocess.CalledProcessError:
        log(f"{full_hostname}: ERROR — Could not clear remote data.")
        return False

# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------
def main():
    log("=== STARTING DAILY SHIPPING QUEUE (mDNS Mode) ===")
    nodes = load_nodes()
    if not nodes:
        return

    # STEP 1 — Ping & State Check
    log("=== PINGING ALL NODES ===")
    for name, info in nodes.items():
        # Ensure the hostname ends in .local
        raw_host = info.get("hostname", name)
        full_host = raw_host if raw_host.endswith(".local") else f"{raw_host}.local"
        
        was_alive = info.get("node_state") == "alive"
        
        if ping_node(full_host):
            nodes[name]["node_state"] = "alive"
            if not was_alive: log(f"{full_host}: RECOVERED")
        else:
            nodes[name]["node_state"] = "dead"
            if was_alive: log(f"{full_host}: LOST CONNECTION")
    save_nodes(nodes)

    # STEP 2 — Initial Transfer Attempt
    log("=== INITIAL DATA TRANSFER ATTEMPT ===")
    failed_nodes = []

    for name, info in nodes.items():
        raw_host = info.get("hostname", name)
        full_host = raw_host if raw_host.endswith(".local") else f"{raw_host}.local"

        if info["node_state"] == "dead":
            log(f"{full_host}: SKIPPED (DEAD)")
            failed_nodes.append(name)
            continue

        if not has_remote_data(full_host):
            nodes[name]["transfer_fail"] = False
            continue

        log(f"{full_host}: Pulling data...")
        if rsync_pull(full_host):
            log(f"{full_host}: SUCCESS — transferred")
            nodes[name]["transfer_fail"] = False
            delete_shipping_data(full_host)
        else:
            log(f"{full_host}: FAILURE — transfer failed")
            nodes[name]["transfer_fail"] = True
            failed_nodes.append(name)

    save_nodes(nodes)

    # STEP 3 — Retries
    if failed_nodes:
        log(f"=== RETRYING FAILED NODES ===")
        for attempt in range(1, MAX_RETRIES + 1):
            if not failed_nodes: break
            log(f"--- RETRY ROUND {attempt} ---")
            
            still_failing = []
            for name in failed_nodes:
                raw_host = nodes[name].get("hostname", name)
                full_host = raw_host if raw_host.endswith(".local") else f"{raw_host}.local"
                
                if not ping_node(full_host) or not has_remote_data(full_host):
                    still_failing.append(name)
                    continue

                if rsync_pull(full_host):
                    log(f"{full_host}: SUCCESS on retry")
                    nodes[name]["transfer_fail"] = False
                    delete_shipping_data(full_host)
                else:
                    still_failing.append(name)
            
            failed_nodes = still_failing
            save_nodes(nodes)

    # STEP 4 — Finalize
    if not failed_nodes:
        log("=== FINAL STATUS: ALL NODES SUCCEEDED ===")
    else:
        log("=== FINAL STATUS: SOME NODES FAILED ===")

if __name__ == "__main__":
    main()
