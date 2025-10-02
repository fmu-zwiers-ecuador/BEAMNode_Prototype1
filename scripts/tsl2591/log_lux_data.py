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
    
lux_json_data = {
    "Date": datetime.now().isoformat(),
    "Lux value": lux
}

file_name = f"lux_data.json"
file_path = os.path.join(directory, file_name)

try:
    with open(file_path, 'w') as json_file:
        json.dump(lux_json_data, json_file, indent=4)
    print(f"Lux data saved to {file_name} at {datetime.now()}")
except Exception as e:
     print(f"Error saving lux data: {e}")