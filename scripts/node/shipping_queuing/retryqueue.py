"""
retryqueue.py: A script that request and queues data from each node.

This script checks to see if all 5 nodes are dead or alive. It then uses 
rsync to check for new data and pull it from the shipping folder on the 
nodes to the supervisor using mDNS hostnames (pi@nodeX.local).

Path: /home/pi/shipping(on node) ==> /home/pi/data(on supervisor)

Author: Gabriel Gonzalez, Noel Challa, Alex Lance, Jackson Roberts, and Jaylen Small
Last Updated: 2-4-26 
"""
#!/usr/bin/env python3
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

# SSH options to prevent hanging on new hosts or password prompts
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5"]

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

def load_nodes():
    if not os.path.exists(JSON_FILEPATH):
        log(f"ERROR: node state file missing: {JSON_FILEPATH}")
        return {}
    with open(JSON_FILEPATH, "r") as f:
        return json.load(f)

def save_nodes(nodes):
    with open(JSON_FILEPATH, "w") as f:
        json.dump(nodes, f, indent=4)

def get_full_host(name, info):
    raw_host = info.get("hostname", name)
    return raw_host if raw_host.endswith(".local") else f"{raw_host}.local"

# ---------------------------------------------------
# NETWORK & DATA OPERATIONS
# ---------------------------------------------------
def ping_node(full_hostname):
    try:
        subprocess.run(["ping", "-c", str(PING_COUNT), "-W", "2", full_hostname],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except:
        return False

def has_remote_data(full_hostname):
    remote_path = f"pi@{full_hostname}:{REMOTE_SHIP_DIR}/"
    # Added SSH_OPTS to rsync via -e
    cmd = ["rsync", "-d", "-e", f"ssh {' '.join(SSH_OPTS)}", remote_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = [l for l in result.stdout.splitlines() if l.strip() and not l.strip().endswith('.')]
        return len(lines) > 0
    except:
        return False

def rsync_pull(full_hostname):
    os.makedirs(SUPERVISOR_DATA_ROOT, exist_ok=True)
    remote_source = f"pi@{full_hostname}:{REMOTE_SHIP_DIR}/"
    cmd = ["rsync", "-avz", "--partial", "--ignore-existing", "-e", f"ssh {' '.join(SSH_OPTS)}",
           remote_source, SUPERVISOR_DATA_ROOT]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        return True
    except:
        return False

def delete_shipping_data(full_hostname):
    # Added SSH_OPTS here
    cmd = ["ssh"] + SSH_OPTS + [f"pi@{full_hostname}", f"sudo rm -rf {REMOTE_SHIP_DIR}/*"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log(f"{full_hostname}: SUCCESS clearing remote data")
        return True
    except:
        log(f"{full_hostname}: ERROR — Could not clear remote data (Check NOPASSWD sudo).")
        return False

# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------
def main():
    log("=== STARTING PASSWORDLESS QUEUE ===")
    nodes = load_nodes()
    if not nodes: return

    # STEP 1: Health Check
    for name, info in nodes.items():
        full_host = get_full_host(name, info)
        nodes[name]["node_state"] = "alive" if ping_node(full_host) else "dead"
    save_nodes(nodes)

    # STEP 2: Transfer
    failed_nodes = []
    for name, info in nodes.items():
        full_host = get_full_host(name, info)
        if info["node_state"] == "dead":
            failed_nodes.append(name)
            continue
        
        if has_remote_data(full_host):
            if rsync_pull(full_host):
                delete_shipping_data(full_host)
                nodes[name]["transfer_fail"] = False
            else:
                nodes[name]["transfer_fail"] = True
                failed_nodes.append(name)
    save_nodes(nodes)

    # STEP 3: Retries
    for attempt in range(1, MAX_RETRIES + 1):
        if not failed_nodes: break
        still_failing = []
        for name in failed_nodes:
            full_host = get_full_host(name, nodes[name])
            if ping_node(full_host) and has_remote_data(full_host):
                if rsync_pull(full_host):
                    delete_shipping_data(full_host)
                    continue
            still_failing.append(name)
        failed_nodes = still_failing
    
    log("=== FINISHED ===")

if __name__ == "__main__":
    main()
