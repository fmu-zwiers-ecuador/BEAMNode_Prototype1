import json
from datetime import datetime, timezone
import os
import time

# --- Hardware Library Imports ---
try:
    import board
    import adafruit_ahtx0
except ImportError as e:
    print(f"ERROR: Failed to import hardware library: {e}. Ensure 'board' and 'adafruit_ahtx0' are installed if running on device.")

# -----------------------------
# Configuration File Path and Loading
# -----------------------------
CONFIG_FILE = "/home/pi/BEAMNode_Prototype1/scripts/node/config.json"


def get_config_data():
    """Load configuration from CONFIG_FILE, returning {} on error."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{CONFIG_FILE}' not found. Cannot load configuration.")
    except json.JSONDecodeError:
        print(f"ERROR: Configuration file '{CONFIG_FILE}' is not valid JSON. Cannot load configuration.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during config loading: {e}. Cannot load configuration.")
    return {}


# Load Configuration and get AHT specific parameters
full_config = get_config_data()
global_cfg = full_config.get("global", {})
aht_cfg = full_config.get("aht", {})

# Skip if disabled in config
if not aht_cfg.get("enabled", False):
    print("AHT sensor disabled in config; exiting.")
    raise SystemExit(0)

NODE_ID = global_cfg.get("node_id", "beam-node-01")
SENSOR_NAME = "aht"

# Determine output path using config
base_dir = global_cfg.get("base_dir", "/home/pi/data")
sensor_dir = aht_cfg.get("directory", "aht")
file_name = aht_cfg.get("file_name", "aht_env.json")
file_path = os.path.join(base_dir, sensor_dir, file_name)

# --- Initialize variables to None (indicating unread/failed state) ---
temperature = None
humidity = None
pressure = None

# -----------------------------
# Initialize the AHTx0 sensor and read values
# -----------------------------
try:
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)

    temperature = float(sensor.temperature)
    humidity = float(sensor.relative_humidity)
    pressure = None  # AHTx0 has no pressure sensor
except NameError as e:
    print(f"CRITICAL ERROR: Hardware libraries not found. Cannot read sensor: {e}.")
except Exception as e:
    print(f"CRITICAL ERROR: Sensor initialization failed: {e}. Check wiring and I2C connection.")

# -----------------------------
# CHECK IF DATA IS VALID BEFORE PROCEEDING
# -----------------------------
if temperature is None or humidity is None:
    print("WARNING: Skipping data save because sensor read failed. Check previous logs for errors.")
    raise SystemExit(0)

# -----------------------------
# New record structure (Only executes if data is NOT None)
# -----------------------------
env_json_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "temperature_C": temperature,
    "humidity_percent": humidity,
    "pressure_hPa": pressure
}

# -----------------------------
# Save to JSON file (Improved robustness)
# -----------------------------
try:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    data = {}

    # 1. Check if file exists and load it
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                print(f"WARNING: '{file_path}' is corrupted or empty. Starting new JSON structure.")
            except Exception as e:
                print(f"ERROR: Could not read existing data: {e}. Starting new JSON structure.")

    # 2. Ensure base structure and update metadata fields
    if not isinstance(data, dict):
        data = {}

    data["node_id"] = NODE_ID
    data["sensor"] = SENSOR_NAME

    if "records" not in data or not isinstance(data["records"], list):
        data["records"] = []
        print("WARNING: 'records' array was missing or invalid. Initializing new records list.")

    # 3. Append the new record
    data["records"].append(env_json_data)

    # 4. Write back to disk
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    if global_cfg.get("print_debug", True):
        print(f"AHT data appended to {file_path}")

except Exception as e:
    print(f"ERROR: Failed to write AHT data: {e}")
