#!/usr/bin/env python3
import subprocess
import os
import json
from datetime import datetime

JSON_FILEPATH = "/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing/node_states.json"
LOG_FILE = "/home/pi/logs/ping.log"

def log(message: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def ping_latency(ip: str, count: int = 1):
    try:
        output = subprocess.check_output(
            ["ping", "-c", str(count), "-W", "1", ip],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        for line in output.splitlines():
            if "avg" in line or "min/avg/max" in line:
                avg_str = line.split("/")[4]
                return float(avg_str)
    except subprocess.CalledProcessError:
        return None

def main():
    if not os.path.exists(JSON_FILEPATH):
        log(f"Node status file not found: {JSON_FILEPATH}")
        return

    with open(JSON_FILEPATH, "r") as f:
        nodes = json.load(f)

    log("=== 10-MINUTE PING CHECK START ===")

    changed = False

    for name, info in nodes.items():
        ip = info["ip"]
        current_state = info.get("node_state", "unknown")

        latency = ping_latency(ip)

        if latency is not None:
            log(f"Node {name} ({ip}) alive, latency {latency:.2f} ms")
            if current_state != "alive":
                log(f"Node {name} transitioned to ALIVE at this time.")
                nodes[name]["node_state"] = "alive"
                changed = True
        else:
            log(f"Node {name} ({ip}) is DEAD (no ping response).")
            if current_state != "dead":
                log(f"Node {name} transitioned to DEAD at this time.")
                nodes[name]["node_state"] = "dead"
                changed = True

    if changed:
        with open(JSON_FILEPATH, "w") as f:
            json.dump(nodes, f, indent=4)

    log("=== 10-MINUTE PING CHECK END ===")

if __name__ == "__main__":
    main()
