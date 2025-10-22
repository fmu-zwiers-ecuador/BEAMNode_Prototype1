import json
from datetime import datetime, timezone
import os
# Removed: import requests (no longer needed for config fetching)

try:
    import board
    import adafruit_ahtx0
    print("INFO: Using real hardware libraries (board, adafruit_ahtx0).")
except ImportError as e:
    # If this fails, the script will halt during sensor initialization (as designed in the non-mock version)
    print(f"ERROR: Failed to import hardware library: {e}. Ensure 'board' and 'adafruit_ahtx0' are installed.")


# -----------------------------
# Configuration File Path and Loading 
# -----------------------------
CONFIG_FILE = "config.json"


def get_config_data():
    """
    Loads configuration from the local CONFIG_FILE.
    Uses a robust default structure if the file is missing or parsing fails.
    """
    
    # Robust default structure for fallback
    default_config = {
        "node_id": "beam-node-01-default",
        "sensor_parameters": {
            "ahtx0": {
                "log_file": "env_data.json",
                "sensor_name": "ahtx0",
                "temperature_offset": 0.0,
                "humidity_offset": 0.0    
            }
        }
    }

    print(f"INFO: Attempting to load config from local file: {CONFIG_FILE}")
    
    try:
        # Open and load the JSON content from the local file
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print("INFO: Configuration loaded successfully from local file.")
        return config

    except FileNotFoundError:
        print(f"ERROR: Configuration file '{CONFIG_FILE}' not found. Using default settings.")
        return default_config
    except json.JSONDecodeError:
        print(f"ERROR: Configuration file '{CONFIG_FILE}' is not valid JSON. Using default settings.")
        return default_config
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during config loading: {e}. Using default settings.")
        return default_config


# Load Configuration and get AHTx0 specific parameters
full_config = get_config_data()
ahtx0_params = full_config.get("sensor_parameters", {}).get("ahtx0", {})


# Use config values, falling back to defaults if not found
NODE_ID = full_config.get("node_id", "beam-node-01-default")
SENSOR_NAME = ahtx0_params.get("sensor_name", "ahtx0-default")
file_path = ahtx0_params.get("log_file", "env_data.json")
temp_offset = ahtx0_params.get("temperature_offset", 0.0)
hum_offset = ahtx0_params.get("humidity_offset", 0.0)


# -----------------------------
# Initialize the AHTx0 sensor and read values
# -----------------------------
try:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    sensor = adafruit_ahtx0.AHTx0(i2c)

    # Read raw sensor values
    temperature = float(sensor.temperature)
    humidity = float(sensor.relative_humidity)
    pressure = None  # AHTx0 has no pressure sensor

    # Apply calibration offsets from the config file
    temperature += temp_offset
    humidity += hum_offset

except Exception as e:
    print(f"CRITICAL ERROR: Sensor initialization failed: {e}. Check wiring and I2C connection. Using zeroed data.")
    temperature = 0.0
    humidity = 0.0
    pressure = None


# -----------------------------
# New record
# -----------------------------
env_json_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "temperature_C": temperature,
    "humidity_percent": humidity,
    "pressure_hPa": pressure
}


# -----------------------------
# Save to JSON file
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
                data = {}
            except Exception as e:
                print(f"ERROR: Could not read existing data: {e}")
                data = {}

    # 2. Ensure the base structure is correct, using configured values
    if not isinstance(data, dict) or "records" not in data:
        data = {
            "node_id": NODE_ID,
            "sensor": SENSOR_NAME,
            "records": []
        }
    
    # 3. Append the new record
    data["records"].append(env_json_data)
    
    # 4. Write the updated data back to the file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("-" * 50)
    print(f"AHTx0 Environmental Data Logger (Config Node: {NODE_ID})")
    print(f"Timestamp: {env_json_data['timestamp']}")
    # Only show raw vs final if offsets were actually applied
    if temp_offset != 0.0 or hum_offset != 0.0:
        # Note: If sensor read failed, temp/hum are 0.0, so the difference calculation is accurate.
        print(f"Raw Temp: {(temperature - temp_offset):.2f}°C | Applied Offset: {temp_offset:.1f}°C")
        print(f"Final Temp: {temperature:.2f}°C")
        print(f"Raw Hum: {(humidity - hum_offset):.2f}% | Applied Offset: {hum_offset:.1f}%")
        print(f"Final Hum: {humidity:.2f}%")
    else:
        print(f"Temperature: {temperature:.2f}°C | Humidity: {humidity:.2f}% (No offset applied)")
        
    print(f"Pressure: {pressure if pressure is not None else 'N/A'}")
    print("-" * 50)
    print(f"SUCCESS: Data appended to configured file: {file_path}")

except Exception as e:
    print(f"FATAL ERROR: Failed to process and save environment data: {e}")
