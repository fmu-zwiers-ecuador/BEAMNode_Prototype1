#!/usr/bin/env python3
import subprocess
import re

# MAC-to-node mapping
mac_map = {
    "b8:27:eb:38:b3:8c": "supervisor1",
    "b8:27:eb:d2:d3:99": "node1",
    "b8:27:eb:f5:7a:f9": "node2",
    "b8:27:eb:8c:30:bc": "node3",
    "b8:27:eb:f0:28:aa": "node4",
    "b8:27:eb:a5:39:90": "node5",
}

def run_batctl(cmd):
    """Run a batctl command and return its output as text."""
    try:
        return subprocess.check_output(["sudo", "batctl", cmd], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running batctl {cmd}: {e}")
        return ""

# --------------------------------------------------------
# Parse "batctl o" (originator table)
# --------------------------------------------------------
originator_output = run_batctl("o")
originator_data = {}

# Example line: "* b8:27:eb:d2:d3:99  0.120s (255) b8:27:eb:d2:d3:99"
for line in originator_output.splitlines():
    match = re.search(r"([0-9a-f:]{17})\s+([\d\.]+s)\s+\((\d+)\)\s+([0-9a-f:]{17})", line, re.IGNORECASE)
    if match:
        originator_mac = match.group(1).lower()
        last_seen = match.group(2)
        quality = match.group(3)
        nexthop_mac = match.group(4).lower()

        originator_name = mac_map.get(originator_mac, originator_mac)
        nexthop_name = mac_map.get(nexthop_mac, nexthop_mac)

        originator_data[originator_mac] = {
            "originator_name": originator_name,
            "nexthop_name": nexthop_name,
            "quality": quality,
            "last_seen": last_seen,
        }

# --------------------------------------------------------
# Parse "batctl n" (neighbor table)
# --------------------------------------------------------
neighbor_output = run_batctl("n")
neighbor_data = {}

# Example line: "wlan0   b8:27:eb:f5:7a:f9     0.280s (240)"
for line in neighbor_output.splitlines():
    match = re.search(r"([0-9a-f:]{17})\s+([\d\.]+s)\s+\((\d+)\)", line, re.IGNORECASE)
    if match:
        mac = match.group(1).lower()
        last_seen = match.group(2)
        quality = match.group(3)
        name = mac_map.get(mac, mac)

        neighbor_data[mac] = {
            "name": name,
            "quality": quality,
            "last_seen": last_seen,
        }

# --------------------------------------------------------
# Combine and display results
# --------------------------------------------------------
print("\nCombined Mesh Link Summary:")
print("-----------------------------------------------------------")

all_macs = set(originator_data.keys()) | set(neighbor_data.keys())

for mac in all_macs:
    name = mac_map.get(mac, mac)
    o_quality = originator_data.get(mac, {}).get("quality", "—")
    o_last_seen = originator_data.get(mac, {}).get("last_seen", "—")
    n_quality = neighbor_data.get(mac, {}).get("quality", "—")
    n_last_seen = neighbor_data.get(mac, {}).get("last_seen", "—")

    # Prefer neighbor "last-seen" if available (more direct)
    last_seen = n_last_seen if n_last_seen != "—" else o_last_seen
    quality = n_quality if n_quality != "—" else o_quality

    nexthop = originator_data.get(mac, {}).get("nexthop_name", "—")

    print(f"{name} to {nexthop} = {quality} | Last-seen = {last_seen}")