import json
from datetime import datetime, timezone
import os
import time

# --- Hardware Library Imports ---
try:
    # Attempt to import hardware libraries (required for running on RPi/sensor)
    import board
    import adafruit_ahtx0
except ImportError as e:
    # This block ensures the script can run locally even if hardware libraries aren't installed,
    # though it will halt later during sensor initialization.
    print(f"ERROR: Failed to import hardware library: {e}. Ensure 'board' and 'adafruit_ahtx0' are installed if running on device.")


# -----------------------------
# Configuration File Path and Loading
# -----------------------------
# Updated path to pull from the '/BEAMNode_Prototype1/scripts/node/' directory.
CONFIG_FILE = "/home/pi/BEAMNode_Prototype1/scripts/node/config.json"


def get_config_data():
    """
    Loads configuration from the local CONFIG_FILE.
    If the file is missing or invalid, it returns an empty dictionary.
    """

    try:
        # Open and load the JSON content from the local file
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config

    except FileNotFoundError:
        # Configuration file not found. Returns empty dict to use hardcoded fallbacks.
        print(f"ERROR: Configuration file '{CONFIG_FILE}' not found. Cannot load configuration.")
        return {}
    except json.JSONDecodeError:
        # File is found but corrupted/invalid JSON.
        print(f"ERROR: Configuration file '{CONFIG_FILE}' is not valid JSON. Cannot load configuration.")
        return {}
    except Exception as e:
        # Catch any other unexpected error during config loading.
        print(f"ERROR: An unexpected error occurred during config loading: {e}. Cannot load configuration.")
        return {}


# Load Configuration and get AHTx0 specific parameters
full_config = get_config_data()
ahtx0_params = full_config.get("sensor_parameters", {}).get("ahtx0", {})


# Use config values, falling back to hardcoded defaults if not found
NODE_ID = full_config.get("node_id", "beam-node-01-default")
SENSOR_NAME = ahtx0_params.get("sensor_name", "ahtx0-default")
file_path = ahtx0_params.get("log_file", "env_data.json")


# -----------------------------
# Initialize the AHTx0 sensor and read values
# -----------------------------
try:
    # board.I2C will only work if running on a device with i2c enabled
    i2c = board.I2C() 
    sensor = adafruit_ahtx0.AHTx0(i2c)

    # Read sensor values (no offsets applied as per request)
    temperature = float(sensor.temperature)
    humidity = float(sensor.relative_humidity)
    pressure = None  # AHTx0 has no pressure sensor

except NameError:
    # This handles the case where board/adafruit_ahtx0 failed to import
    print("CRITICAL ERROR: Hardware libraries not found. Using zeroed data.")
    temperature = 0.0
    humidity = 0.0
    pressure = None
except Exception as e:
    # This handles I2C connection/initialization errors
    print(f"CRITICAL ERROR: Sensor initialization failed: {e}. Check wiring and I2C connection. Using zeroed data.")
    temperature = 0.0
    humidity = 0.0
    pressure = None


# -----------------------------
# New record structure
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
    data = {}

    # 1. Check if file exists and load it
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                print(f"WARNING: '{file_path}' is corrupted or empty. Starting new JSON structure.")
                # 'data' remains {} for re-initialization logic below
            except Exception as e:
                print(f"ERROR: Could not read existing data: {e}. Starting new JSON structure.")
                # 'data' remains {}

    # 2. Ensure base structure and update metadata fields (Node ID and Sensor name)
    # This ensures the latest config/defaults are always written to the file.
    if not isinstance(data, dict):
        data = {}

    # Update metadata fields
    data["node_id"] = NODE_ID
    data["sensor"] = SENSOR_NAME

    # Ensure 'records' key exists and is a list
    if "records" not in data or not isinstance(data["records"], list):
        # Initialize or fix the records list
        data["records"] = []
        print("WARNING: 'records' array was missing or invalid. Initializing new records list.")

    # 3. Append the new record
    data["records"].append(env_json_data)

    # 4. Write the updated data back to the file
    with open(file_path, "w") as json_file:
        # Use indent=4 for human readability
        json.dump(data, json_file, indent=4)

except Exception as e:
    # This is the essential 'except' block that resolves the SyntaxError
    print(f"CRITICAL ERROR: Failed to save data to file '{file_path}': {e}")
