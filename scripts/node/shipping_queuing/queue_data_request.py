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

SUPERVISOR_DATA_DIR = "/home/pi/supervisor_data"
REMOTE_DATA_PATH = "/home/pi/data"
LOG_FILE = "/home/pi/queue_data_request.log"

# -----------------------------
# UTILITIES
# -----------------------------
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                # Example line: rtt min/avg/max/mdev = 0.242/0.256/0.262/0.010 ms
                avg_str = line.split("/")[4]
                return float(avg_str)
    except subprocess.CalledProcessError:
        return None
    
def rsync_data(ip, hostname):
    """Sync remote data folder from node to supervisor."""
    dest_dir = os.path.join(SUPERVISOR_DATA_DIR, hostname)
    os.makedirs(dest_dir, exist_ok=True)

    #Example sudo rsync -avz pi@node{number}.local/home/pi/ /home/pi/data
    rsync_cmd = [
        "rsync", "-avz",
        f"pi@{ip}:{REMOTE_DATA_PATH}/",  # remote source
        dest_dir                         # local destination
    ]

    try:
        subprocess.run(rsync_cmd, check=True)
        log(f"Successfully synced data from {hostname} ({ip})")
    except subprocess.CalledProcessError:
        log(f"Failed to sync data from {hostname} ({ip})")

# -----------------------------
# MAIN LOGIC
# -----------------------------   
def main():
    log("=== Starting daily data queue ===")

    # Measure latency for all nodes
    latencies = {}
    for name, ip in NODES.items():
        latency = ping_latency(ip)
        latencies[name] = latency
        log(f"{name} ({ip}) -> {latency if latency else 'unreachable'} ms")

     # Sort nodes by latency (ignore unreachable)
    reachable = {n: l for n, l in latencies.items() if l is not None}
    sorted_nodes = sorted(reachable.items(), key=lambda x: x[1])

    if not sorted_nodes:
        log("No reachable nodes. Exiting.")
        return

    log(f"Best connection: {sorted_nodes[0][0]} ({sorted_nodes[0][1]} ms)")

    # Request data from best node first
    for name, latency in sorted_nodes:
        log(f"Requesting data from {name} ({latency} ms)...")
        rsync_data(NODES[name], name)
        time.sleep(2)  # small delay between transfers

    log("=== Data queue complete ===\n")

if __name__ == "__main__":
    main()


