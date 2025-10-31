## Script to move all information in DATA directory to shipping directory, and compress to ensure
# ease of transfer

import shutil
import os
import time
import json
from datetime import datetime, timezone


# Load config.json for directory paths

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load config
config_path = os.path.join(project_root, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

global_cfg = config["global"]


# Define paths

data_src = global_cfg.get("base_dir")
zip_destination = global_cfg.get("ship_dir")
os.makedirs(zip_destination, exist_ok=True)  # Ensure folder exists


# Create ZIP name and output path

timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
zip_name = f"data_{timestamp}"
zip_output = os.path.join(zip_destination, zip_name)

# Measure time and compress data

start_time = time.time()

try:
    shutil.make_archive(zip_output, 'zip', root_dir=data_src)
    end_time = time.time()
    total_time = end_time - start_time

    # Get ZIP file size (in MB)
    zip_file_path = f"{zip_output}.zip"
    zip_size = os.path.getsize(zip_file_path) / (1024 * 1024)

    print(f"Data successfully moved to Shipping as {zip_file_path}")
    print(f"ZIP file size: {zip_size:.2f} MB")
    print(f"Total shipping time: {total_time:.2f} seconds")

except Exception as e:
    print(f"Error compressing directory: {e}")
