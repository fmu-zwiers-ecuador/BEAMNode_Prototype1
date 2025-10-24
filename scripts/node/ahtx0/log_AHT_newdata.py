"""
AHTx0 (AHT10/AHT20) Environmental Data Logger
Reads temperature and humidity, logs to env_data.json.
Pressure is not supported by this sensor, so it's set to NA (null in JSON).
"""

import json
from datetime import datetime, timezone
import os
import board
import adafruit_ahtx0  # Official Adafruit AHTx0 library

# -----------------------------
# Initialize the AHTx0 sensor
# -----------------------------
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_ahtx0.AHTx0(i2c)

# -----------------------------
# Read sensor values
# -----------------------------
temperature = float(sensor.temperature)
humidity = float(sensor.relative_humidity)
pressure = None  # AHTx0 has no pressure sensor (will appear as null in JSON)

# -----------------------------
# Target file path
# -----------------------------
file_path = "env_data.json"  # Saves in the same directory as the script

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
    # Attempt to load existing data if it exists, otherwise create a new structure
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                data = json.load(json_file)
                if not isinstance(data, dict) or "records" not in data:
                    data = {
                        "node_id": "beam-node-01",
                        "sensor": "ahtx0",
                        "records": []
                    }
            except Exception:
                data = {
                    "node_id": "beam-node-01",
                    "sensor": "ahtx0",
                    "records": []
                }
    else:
        data = {
            "node_id": "beam-node-01",
            "sensor": "ahtx0",
            "records": []
        }

    # Append and write back
    data["records"].append(env_json_data)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Env data appended to {file_path}")
    print(f"Temperature: {temperature:.1f}°C | Humidity: {humidity:.1f}% | Pressure: {pressure}")
except Exception as e:
    print(f"Error saving env data: {e}")
