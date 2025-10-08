import board
import adafruit_tsl2591
import json
from datetime import datetime, timezone
import os

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()

# Initialize the sensor.
sensor = adafruit_tsl2591.TSL2591(i2c)

# Read and calculate the light level in lux.
lux = sensor.lux

# Initializes directory where data will be stored
directory = "/home/pi/data/tsl2591/"

# Create directory if it does not exist
os.makedirs(directory, exist_ok=True)

# Set the file name and path
file_name = f"lux_data.json"
file_path = os.path.join(directory, file_name)

# New collected data
new_lux_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "lux": lux
}

try:
    # Attempt to load existing data if it exist, create a new dict if not
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            if not isinstance(data, dict) or "records" not in data:
                data = {
                    "node_id": "beam-node-01",
                    "sensor": "tsl2591",
                    "records": []
                }
    else:
        data = {
            "node_id": "beam-node-01",
            "sensor": "tsl2591",
            "records": []
        }

    # Append the new data
    data["records"].append(new_lux_data)

    # Save back to the file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Lux data appended to {file_name} at {datetime.now()}")
except Exception as e:
     print(f"Error saving lux data: {e}")