"""
queue_data_request.py: A script that request and queues data from each node.

This script checks to see if all 5 nodes are dead or alive, and then checks the ping latency for all the alive nodes and sorts them in a queue from best connection to worst connection.
Then the rsync command is ran on all of the alive nodes to request the data from the shipping folder in the nodes to be transfered onto the shipping folder on the supervisor. 
It should go like this: /home/pi/shipping(on node) ==> /home/pi/data(on supervisor)

If there are any dead nodes, the script attemps to retry a connection 10 times before giving up.

Author: Gabriel Gonzalez, Noel Challa and Jaylen Small
Last Updated: 1-30-26 
"""
import sys
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parents[1] / "vendor"
sys.path.insert(0, str(VENDOR_DIR))

import subprocess
import os
import time
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
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


# ---------------------------------------------------
# LOAD NODE STATE
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
# PING
# ---------------------------------------------------
def ping_node(ip):
    """Return True if node responds, else False."""
    try:
        output = subprocess.check_output(
            ["ping", "-c", str(PING_COUNT), "-W", "1", ip],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


# ---------------------------------------------------
# RSYNC
# ---------------------------------------------------
def rsync_pull(ip, hostname):
    dest = SUPERVISOR_DATA_ROOT
    os.makedirs(dest, exist_ok=True)

    cmd = [
        "rsync", "-avz", "--partial", "--ignore-existing",
        f"pi@{ip}:{REMOTE_SHIP_DIR}/", dest
    ]

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
def main():
    log("=== STARTING DAILY SHIPPING QUEUE ===")

    nodes = load_nodes()

    # STEP 1 — Ping all nodes
    log("=== PINGING ALL NODES ===")
    for name, info in nodes.items():
        ip = info["ip"]
        alive_before = info["node_state"]

        if ping_node(ip):
            nodes[name]["node_state"] = "alive"

            if alive_before == "dead":
                log(f"{name}: RECOVERED — node back online")

        else:
            nodes[name]["node_state"] = "dead"

            if alive_before == "alive":
                log(f"{name}: LOST CONNECTION — now dead")

    save_nodes(nodes)

    # STEP 2 — Attempt data transfer for ALIVE nodes
    log("=== INITIAL DATA TRANSFER ATTEMPT ===")
    failed_nodes = []

    for name, info in nodes.items():
        ip = info["ip"]

        if info["node_state"] == "dead":
            log(f"{name}: SKIPPED — node is DEAD")
            failed_nodes.append(name)
            continue

        log(f"{name}: Attempting data pull...")
        success = rsync_pull(ip, name)

        if success:
            log(f"{name}: SUCCESS — data transferred")
            nodes[name]["transfer_fail"] = False
        else:
            log(f"{name}: FAILURE — data transfer failed")
            nodes[name]["transfer_fail"] = True
            failed_nodes.append(name)

    save_nodes(nodes)

    # STEP 3 — Retry failed nodes up to MAX_RETRIES
    if failed_nodes:
        log(f"=== RETRYING FAILED NODES (UP TO {MAX_RETRIES} TIMES) ===")

    for attempt in range(1, MAX_RETRIES + 1):
        if not failed_nodes:
            break  # all succeeded

        log(f"--- RETRY ROUND {attempt}/{MAX_RETRIES} ---")

        retry_success = []
        retry_fail = []

        for name in failed_nodes:
            ip = nodes[name]["ip"]

            # Check if node came online
            if not ping_node(ip):
                log(f"{name}: STILL DEAD — retry skipped")
                retry_fail.append(name)
                continue

            log(f"{name}: Retrying data pull...")
            success = rsync_pull(ip, name)

            if success:
                log(f"{name}: SUCCESS on retry #{attempt}")
                nodes[name]["transfer_fail"] = False
                retry_success.append(name)
            else:
                log(f"{name}: FAILURE on retry #{attempt}")
                retry_fail.append(name)

        # update node list
        failed_nodes = retry_fail
        save_nodes(nodes)

        if not retry_fail:
            break  # everything succeeded

    # STEP 4 — Final result
    if failed_nodes:
        log("=== FINAL STATUS: SOME NODES FAILED ===")
        for name in failed_nodes:
            log(f"{name}: FINAL FAIL — data NOT pulled (node may be offline)")
    else:
        log("=== FINAL STATUS: ALL NODES SUCCEEDED ===")

    log("=== END OF DAILY SHIPPING QUEUE ===")


if __name__ == "__main__":
    main()
