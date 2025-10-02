import board
import adafruit_tsl2591
import json
from datetime import datetime
import os

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()

# Initialize the sensor.
sensor = adafruit_tsl2591.TSL2591(i2c)

# Read and calculate the light level in lux.
lux = sensor.lux

directory = "data/tsl2591/"

# Create directory if it does not exist
os.makedirs(directory, exist_ok=True)

file_name = f"lux_data.json"
file_path = os.path.join(directory, file_name)

lux_json_data = {
    "Date": datetime.now().isoformat(),
    "Lux value": lux
}

try:
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            if not isinstance(data, list):
                data = []  # Reset if data is not a list
    else:
        data = []

    # Append the new data
    data.append(lux_json_data)

    # Save back to the file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Lux data appended to {file_name} at {datetime.now()}")
except Exception as e:
     print(f"Error saving lux data: {e}")