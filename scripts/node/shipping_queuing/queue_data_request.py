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

# Supervisor-side: root where all node data accumulates
SUPERVISOR_DATA_ROOT = "/home/pi/data"

# Node-side shipping directory (must match node config global.ship_dir)
REMOTE_SHIP_DIR = "/home/pi/shipping"

LOG_FILE = "/home/pi/queue_data_request.log"

# -----------------------------
# UTILITIES
# -----------------------------
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def ping_latency(ip, count=3):
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
# RSYNC OF SHIPPED ZIPS
# -----------------------------
def rsync_shipped_zips(ip, hostname):
    """
    Pull *.zip from node shipping dir into:
    /home/pi/data/<hostname>/<pullTimestamp>/
    """
    pull_ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest_dir = os.path.join(SUPERVISOR_DATA_ROOT, hostname, pull_ts)
    os.makedirs(dest_dir, exist_ok=True)

    rsync_cmd = [
        "rsync",
        "-avz",
        "--partial",
        "--prune-empty-dirs",
        "--ignore-existing",      # do not overwrite if rerun
        "--include", "*.zip",
        "--exclude", "*",
        f"pi@{ip}:{REMOTE_SHIP_DIR}/",
        dest_dir
    ]

    try:
        subprocess.run(rsync_cmd, check=True)
        log(f"Pulled shipped zips from {hostname} ({ip}) -> {dest_dir}")
    except subprocess.CalledProcessError:
        log(f"Failed to rsync shipped zips from {hostname} ({ip})")

# -----------------------------
# MAIN LOGIC
# -----------------------------
def main():
    log("=== Starting shipped data queue ===")

    # Measure latency for all nodes
    latencies = {}
    for name, ip in NODES.items():
        latency = ping_latency(ip)
        latencies[name] = latency
        log(f"{name} ({ip}) -> {latency if latency is not None else 'unreachable'} ms")

        
    # Sort nodes by best latency
    reachable = {n: l for n, l in latencies.items() if l is not None}
    sorted_nodes = sorted(reachable.items(), key=lambda x: x[1])

    if not sorted_nodes:
        log("No reachable nodes. Exiting.")
        return

    log(f"Best connection: {sorted_nodes[0][0]} ({sorted_nodes[0][1]} ms)")

    # Pull from best-first; each pull goes to its own <timestamp> folder (append behavior)
    for name, latency in sorted_nodes:
        log(f"Requesting shipped data from {name} ({latency} ms)...")
        rsync_shipped_zips(NODES[name], name)
        time.sleep(1)

    log("=== Shipped data queue complete ===\n")

if __name__ == "__main__":
    main()
