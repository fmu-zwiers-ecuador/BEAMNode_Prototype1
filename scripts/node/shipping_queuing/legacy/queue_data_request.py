"""
queue_data_request.py: A script that request and queues data from each node.

This script checks the ping latency for all the nodes and sorts them in a queue from best connection to worst connection.
Then the rsync command is ran on all of of the nodes to request the data from the shipping folder in the nodes to transfer them onto the shipping folder on the supervisor. 
It should go like this: /home/pi/shipping(on node) ==> /home/pi/data(on supervisor)

Author: Noel Challa and Jaylen Small
Last Updated: 1-26-26 
"""
import subprocess
import os
import time
import json
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------
NODES = {
    "node1": "192.168.1.1",
    "node2": "192.168.1.2",
    "node3": "192.168.1.3",
    "node4": "192.168.1.4",
    "node5": "192.168.1.5"
}

# Supervisor-side: root where all shipped data accumulates
SUPERVISOR_DATA_ROOT = "/home/pi/data"

# Node-side shipping directory (must match node config global.ship_dir)
REMOTE_SHIP_DIR = "/home/pi/shipping"

LOG_FILE = "/home/pi/queue_data_request.log"

# -----------------------------
# UTILITIES
# -----------------------------
def log(message: str) -> None:
    """Append a timestamped message to the log file and print it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def ping_latency(ip: str, count: int = 3):
    """Ping a host and return average latency in ms (None if unreachable)."""
    try:
        output = subprocess.check_output(
            ["ping", "-c", str(count), "-W", "1", ip],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        for line in output.splitlines():
            if "avg" in line:
                # Example: rtt min/avg/max/mdev = 0.242/0.256/0.262/0.010 ms
                avg_str = line.split("/")[4]
                return float(avg_str)
    except subprocess.CalledProcessError:
        return None

# -----------------------------
# RSYNC OF SHIPPED DATA (NO ZIPS)
# -----------------------------
def rsync_shipped_data(ip: str, hostname: str) -> None:
    """
    Pull everything from the node's shipping dir directly into:
        /home/pi/data/

    Nodes ship folders like:
        data-<hostname>-<timestamp>/

    These get copied straight into /home/pi/data, and because
    names include timestamps, new pulls append instead of overwrite.
    """
    dest_dir = SUPERVISOR_DATA_ROOT  # /home/pi/data
    os.makedirs(dest_dir, exist_ok=True)

    rsync_cmd = [
        "rsync",
        "-avz",
        "--partial",
        "--ignore-existing",                # do not overwrite files that already exist
        f"pi@{ip}:{REMOTE_SHIP_DIR}/",      # /home/pi/shipping/ on node
        dest_dir                            # /home/pi/data/ on supervisor
    ]

    try:
        subprocess.run(rsync_cmd, check=True)
        log(f"Pulled shipped data from {hostname} ({ip}) -> {dest_dir}")
    except subprocess.CalledProcessError:
        log(f"Failed to rsync shipped data from {hostname} ({ip})")

# ------------------------------
# MAIN LOGIC
# ------------------------------
def main() -> None:
    log("=== Starting shipped data queue ===")

    # Measure latency for all nodes
    latencies = {}
    for name, ip in NODES.items():
        latency = ping_latency(ip)
        latencies[name] = latency
        log(f"{name} ({ip}) -> {latency if latency is not None else 'unreachable'} ms")

    # Sort nodes by best latency (lowest ms first), ignore unreachable
    reachable = {n: l for n, l in latencies.items() if l is not None}
    sorted_nodes = sorted(reachable.items(), key=lambda x: x[1])

    if not sorted_nodes:
        log("No reachable nodes. Exiting.")
        return

    log(f"Best connection: {sorted_nodes[0][0]} ({sorted_nodes[0][1]} ms)")

    # Pull from best-first; each pull appends into /home/pi/data/
    for name, latency in sorted_nodes:
        log(f"Requesting shipped data from {name} ({latency} ms)...")
        rsync_shipped_data(NODES[name], name)
        time.sleep(1)

    log("=== Shipped data queue complete ===\n")

if __name__ == "__main__":
    main()
