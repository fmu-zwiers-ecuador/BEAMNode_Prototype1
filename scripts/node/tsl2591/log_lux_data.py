"""
log_lux_data.py: A simple script to log lux data to json.

This script logs the lux value along with the current timestamp into a json file, stored on the home/pi/data directory.

Author: Jaylen Small
Last Updated: 1-26-26 
"""
import sys
from pathlib import Path

VENDOR_DIR = Path(__file__).resolve().parents[1] / "vendor"
sys.path.insert(0, str(VENDOR_DIR))

import board
import adafruit_tsl2591
import json
from datetime import datetime, timezone
import os

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load config
config_path = os.path.join(project_root, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

tsl_config = config["tsl2591"]
global_config = config["global"]

node_id = global_config.get("node_id", "unknown-node")

# Directory and file for logs
directory = os.path.join(global_config.get("base_dir", os.path.join(project_root, "data")), tsl_config.get("directory", "tsl2591"))
os.makedirs(directory, exist_ok=True)
file_name = tsl_config.get("file_name", "lux_data.json")
file_path = os.path.join(directory, file_name)

# Initialize sensor
i2c = board.I2C()
sensor = adafruit_tsl2591.TSL2591(i2c)

# Read lux
lux = sensor.lux

# New record
new_lux_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "lux": lux
}

# Append to JSON
try:
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "records" not in data:
                data = {"node_id": node_id, "sensor": "tsl2591", "records": []}
    else:
        data = {"node_id": node_id, "sensor": "tsl2591", "records": []}

    data["records"].append(new_lux_data)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    if global_config.get("print_debug", True):
        print(f"Lux data appended to {file_name} at {datetime.now(timezone.utc)}")
except Exception as e:
    print(f"Error saving lux data: {e}")
