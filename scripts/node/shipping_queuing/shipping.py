import sys
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parents[1] / "vendor"
sys.path.insert(0, str(VENDOR_DIR))

## Script to move all information in DATA directory to shipping directory,
## renaming the folder with hostname and timestamp (no zipping)

import shutil
import os
import time
import json
from datetime import datetime, timezone

# Determine project root dynamically (one level up from this script)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load config
config_path = "/home/pi/BEAMNode_Prototype1/scripts/node/config.json"
with open(config_path, "r") as f:
    config = json.load(f)

global_cfg = config["global"]

# Paths from config (with safe defaults)
data_src = global_cfg.get("base_dir", "/home/pi/data")
ship_dir = global_cfg.get("ship_dir", "/home/pi/shipping")
os.makedirs(ship_dir, exist_ok=True)  # Ensure shipping folder exists

# Determine hostname (what the node is)
try:
    hostname = os.uname().nodename
except Exception:
    hostname = global_cfg.get("node_id", "unknown-node")

# UTC timestamp like 20251113T194522Z
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# New folder name in shipping: data-{hostname}-{timestamp}
dest_dir_name = f"data-{hostname}-{timestamp}"
dest_dir_path = os.path.join(ship_dir, dest_dir_name)

start_time = time.time()

try:
    if not os.path.exists(data_src):
        raise FileNotFoundError(f"Source data directory not found: {data_src}")

    # Move the entire data folder into shipping under the new name
    shutil.move(data_src, dest_dir_path)

    # Recreate an empty data folder so the node can keep writing new data
    os.makedirs(data_src, exist_ok=True)

    total_time = time.time() - start_time
    print(f"Data folder moved to Shipping as {dest_dir_path}")
    print(f"Total shipping time: {total_time:.2f} seconds")

except Exception as e:
    print(f"Error moving directory: {e}")
