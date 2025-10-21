## Script to move all information in DATA directory to shipping directory, and compress to ensure
# ease of transfer

import shutil
import os
import time
import json
from datetime import datetime, timezone

# load config_json for filenames

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Load config
config_path = os.path.join(project_root, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

global_cfg = config["global"]

# define data directory path

data_src = global_cfg.get("base_dir")

# find timestamp and determine zip name

timestamp = datetime.now(timezone.utc).isoformat()
zip_name = f'data_{timestamp}'

# define destination

zip_destination = global_cfg.get("ship_dir") 

# move and compress data directory
try:
    shutil.make_archive(zip_name, 'zip', root_dir=data_src, base_dir=zip_destination)
    print(f"Data successfully moved to Shipping as {zip_name}'")
except Exception as e:
    print(f"Error compressing directory: {e}")

