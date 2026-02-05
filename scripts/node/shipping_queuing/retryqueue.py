#!/usr/bin/env python3
"""
retryqueue.py: A script that requests and queues data from each node.
Path: /home/pi/shipping(on node) ==> /home/pi/data(on supervisor)

Author: Gabriel Gonzalez, Noel Challa, Alex Lance, Jackson Roberts, and Jaylen Small
Last Updated: 2-5-26 
"""

import sys
import subprocess
import os
import json
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
JSON_FILEPATH = "/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing/node_states.json"
SUPERVISOR_DATA_ROOT = "/home/pi/data"
REMOTE_SHIP_DIR = "/home/pi/shipping"
LOG_FILE = "/home/pi/logs/queue.log"

MAX_RETRIES = 5
PING_COUNT = 1

# SSH options to force non-interactive mode (prevents hanging)
SSH_OPTS = [
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=5",
    "-o", "StrictHostKeyChecking=accept-new"
]

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
    try:
        with open(JSON_FILEPATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR: Could not read JSON: {e}")
        return {}

def save_nodes(nodes):
    try:
        with open(JSON_FILEPATH, "w") as f:
            json.dump(nodes, f, indent=4)
    except Exception as e:
        log(f"ERROR: Could not save JSON: {e}")

# ---------------------------------------------------
# NETWORK & DATA OPERATIONS
# ---------------------------------------------------
def get_full_host(name, info):
    raw_host = info.get("hostname", name)
    return raw_host if raw_host.endswith(".local") else f"{raw_host}.local"

def ping_node(full_hostname):
    """Checks if node is reachable on the network."""
    try:
        subprocess.run(
            ["ping", "-c", str(PING_COUNT), "-W", "2", full_hostname],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except:
        return False

def has_remote_data(full_hostname):
    """Lists remote files to verify if there is actually data to ship."""
    remote_path = f"pi@{full_hostname}:{REMOTE_SHIP_DIR}/"
    # Uses rsync --list-only to see what is in the folder
    cmd = ["rsync", "--list-only", "-e", f"ssh {' '.join(SSH_OPTS)}", remote_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = [l for l in result.stdout.splitlines() if l.strip() and not l.strip().endswith('.')]
        log(f"{full_hostname}: SUCCESS checking remote data")
        return len(lines) > 0
    except:
        log(f"{full_hostname}: ERROR — Data check failed (Check SSH Keys)")
        return False

def rsync_pull(full_hostname):
    """Executes the actual transfer from node to supervisor."""
    os.makedirs(SUPERVISOR_DATA_ROOT, exist_ok=True)
    remote_source = f"pi@{full_hostname}:{REMOTE_SHIP_DIR}/"
    cmd = [
        "rsync", "-avz", "--partial", "--ignore-existing",
        "-e", f"ssh {' '.join(SSH_OPTS)}",
        remote_source, SUPERVISOR_DATA_ROOT
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def delete_shipping_data(full_hostname):
    """Wipes the node's shipping folder after a successful transfer."""
    # Requires NOPASSWD: /usr/bin/rm in node's /etc/sudoers
    cmd = ["ssh"] + SSH_OPTS + [f"pi@{full_hostname}", f"sudo rm -rf {REMOTE_SHIP_DIR}/*"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log(f"{full_hostname}: Remote folder cleared.")
        return True
    except:
        log(f"{full_hostname}: WARNING - Failed to clear remote data.")
        return False

# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------
def main():
    log("=== STARTING PASSWORDLESS SHIPPING QUEUE ===")
    nodes = load_nodes()
    if not nodes:
        return

    # STEP 1 — Health Check
    log("=== PINGING NODES ===")
    for name, info in nodes.items():
        full_host = get_full_host(name, info)
        if ping_node(full_host):
            nodes[name]["node_state"] = "alive"
        else:
            nodes[name]["node_state"] = "dead"
            log(f"{full_host}: OFFLINE")
    save_nodes(nodes)

    # STEP 2 — Initial Transfer Attempt
    log("=== INITIAL TRANSFER ATTEMPT ===")
    failed_nodes = []

    for name, info in nodes.items():
        full_host = get_full_host(name, info)

        if info["node_state"] == "dead":
            failed_nodes.append(name)
            continue

        if not has_remote_data(full_host):
            log(f"{full_host}: No files found to ship.")
            nodes[name]["transfer_fail"] = False
            continue

        log(f"{full_host}: Pulling data...")
        if rsync_pull(full_host):
            log(f"{full_host}: TRANSFER SUCCESS")
            nodes[name]["transfer_fail"] = False
            delete_shipping_data(full_host)
        else:
            log(f"{full_host}: TRANSFER FAILURE")
            nodes[name]["transfer_fail"] = True
            failed_nodes.append(name)

    save_nodes(nodes)

    # STEP 3 — Retries
    if failed_nodes:
        log(f"=== RETRYING FAILED NODES (Max {MAX_RETRIES}) ===")
        for attempt in range(1, MAX_RETRIES + 1):
            if not failed_nodes: break
            log(f"--- Retry Round {attempt} ---")
            
            still_failing = []
            for name in failed_nodes:
                full_host = get_full_host(name, nodes[name])
                
                # Check if node is back online and has data
                if ping_node(full_host) and has_remote_data(full_host):
                    if rsync_pull(full_host):
                        log(f"{full_host}: SUCCESS on retry")
                        nodes[name]["transfer_fail"] = False
                        delete_shipping_data(full_host)
                        continue
                
                still_failing.append(name)
            
            failed_nodes = still_failing
            save_nodes(nodes)

    # STEP 4 — Final Status
    if not failed_nodes:
        log("=== FINAL STATUS: ALL NODES COMPLETED ===")
    else:
        log(f"=== FINAL STATUS: {len(failed_nodes)} NODES REMAIN FAILED ===")

if __name__ == "__main__":
    main()
