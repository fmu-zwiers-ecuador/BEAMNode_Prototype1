import subprocess
import os
import time
import json
from datetime import datetime

# -----------------------------
# CONFIGURATION
# -----------------------------

# node class with IP addresses, states, and failed transfer, read from node_states.json
class Node:
    def __init__(self, name, ip, transfer, state):
        self.name = name
        self.ip = ip
        self.transfer_fail = transfer
        self.state = state


json_filepath = "./node_states.json"


# read nodes from json file

def load_nodes(json_filepath):
    nodes = {}
    if os.path.exists(json_filepath):
        with open(json_filepath, "r") as f:
            data = json.load(f)
            for name, info in data.items():
                node = Node(name, info["ip"], )
                nodes[name] = node
    return nodes

nodes = load_nodes(json_filepath)



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
        return True
    except subprocess.CalledProcessError:
        log(f"Failed to rsync shipped data from {hostname} ({ip})")
        return False
    
def ping_nodes():
    for node in nodes.values():
        latency = ping_latency(node.ip)
        node
        if latency is not None:
            log(f"Node {node.name} ({node.ip}) latency: {latency} ms")
            # set node to alive
            node.alive = True
        else:
            log(f"Node {node.name} ({node.ip}) is unreachable")
            node.alive = False

def ping_dead_nodes():
    for node in nodes.values():
        if not node.alive:
            latency = ping_latency(node.ip)
            if latency is not None:
                log(f"Node {node.name} ({node.ip}) is back online with latency: {latency} ms")
                node.alive = True

# ------------------------------
# MAIN LOGIC
# ------------------------------

def main():
    log("=== Starting shipped data queue ===")

    # Load nodes from JSON
    # Measure latency for all nodes
    nodes = load_nodes(json_filepath)

    # find alive and dead nodes
    ping_nodes()

    # request data from non failed nodes first
    for node in nodes.values():
        if node.alive and not node.transfer_fail:
            success = rsync_shipped_data(node.ip, node.name)
            if not success:
                node.transfer_fail = True

    # periodically retry failed nodes
    RETRY_INTERVAL = 300  # seconds
    while True:
        time.sleep(RETRY_INTERVAL)
        # re-ping failed nodes
        ping_dead_nodes()
        # retry failed transfers
        log("=== Retrying failed data transfers ===")
        for node in nodes.values():
            if node.alive and node.transfer_fail:
                success = rsync_shipped_data(node.ip, node.name)
                if success:
                    node.transfer_fail = False
  
