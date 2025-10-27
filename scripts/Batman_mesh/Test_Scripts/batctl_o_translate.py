#!/usr/bin/env python3
import subprocess
import re

# Updated MAC-to-name mapping
mac_map = {
    "b8:27:eb:38:b3:8c": "supervisor1",
    "b8:27:eb:d2:d3:99": "node1",
    "b8:27:eb:f5:7a:f9": "node2",
    "b8:27:eb:8c:30:bc": "node3",
    "b8:27:eb:f0:28:aa": "node4",
    "b8:27:eb:a5:39:90": "node5",
}

# Run batctl o
try:
    output = subprocess.check_output(["sudo", "batctl", "o"], text=True)
except subprocess.CalledProcessError as e:
    print("Error running batctl:", e)
    exit(1)

# Clean lines and parse
lines = output.strip().splitlines()

for line in lines:
    # Find MAC addresses and quality value (#/255)
    match = re.search(r"([0-9a-f:]{17}).*\((\d+)\).*?([0-9a-f:]{17})", line, re.IGNORECASE)
    if match:
        originator_mac = match.group(1).lower()
        quality = match.group(2)
        nexthop_mac = match.group(3).lower()

        originator_name = mac_map.get(originator_mac, originator_mac)
        nexthop_name = mac_map.get(nexthop_mac, nexthop_mac)

        print(f"{originator_name} to {nexthop_name} = {quality}")
