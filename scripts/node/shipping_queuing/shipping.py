## Script to move all information in DATA directory to shipping directory, and compress to ensure
# ease of transfer

import shutil
import os
import time
import json
from datetime import datetime, timezone

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load config
config_path = os.path.join(project_root, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

global_cfg = config["global"]

# Paths
data_src = global_cfg.get("base_dir")
ship_dir = global_cfg.get("ship_dir")
os.makedirs(ship_dir, exist_ok=True)  # Ensure folder exists

# ---- Name ZIP with node + UTC send date (e.g., beam-node-01_20251110T145122Z.zip)
node_id = global_cfg.get("node_id")
if not node_id:
    try:
        node_id = os.uname().nodename
    except Exception:
        node_id = "unknown-node"

timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
zip_name = f"{node_id}_{timestamp}"
zip_output = os.path.join(ship_dir, zip_name)

# Compress
start_time = time.time()
try:
    shutil.make_archive(zip_output, 'zip', root_dir=data_src)
    total_time = time.time() - start_time

    zip_file_path = f"{zip_output}.zip"
    zip_size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)

    print(f"Data successfully moved to Shipping as {zip_file_path}")
    print(f"ZIP file size: {zip_size_mb:.2f} MB")
    print(f"Total shipping time: {total_time:.2f} seconds")

except Exception as e:
    print(f"Error compressing directory: {e}")
