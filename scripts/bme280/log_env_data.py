
import spidev   
import json
from datetime import datetime, timezone
import os

from adafruit_bme280 import basic  # <-- import for initialization over SPI to work
import board, busio
from digitalio import DigitalInOut

# SPI Setup GPIO5 = physical pin 29 for Chip Select
CS_PIN = board.D5
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs  = DigitalInOut(CS_PIN)

# Initialize the BME280 sensor over SPI 
sensor = basic.Adafruit_BME280_SPI(spi, cs, baudrate=100000)

# Read sensor values
temperature = float(sensor.temperature)
humidity    = float(sensor.humidity)
pressure    = float(sensor.pressure)

# Directory for saving logs
directory = "/home/pi/data/bme280/"
os.makedirs(directory, exist_ok=True)

# Target file (single JSON with a "records" array)
file_name = "env_data.json"
file_path = os.path.join(directory, file_name)

# New record
env_json_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "temperature_C": temperature,
    "humidity_percent": humidity,
    "pressure_hPa": pressure
}

try:
    # Attempt to load existing data if it exist, create a new dict if not
    if os.path.exists(file_path):
        with open(file_path, "r") as json_file:
            try:
                data = json.load(json_file)
                if not isinstance(data, dict) or "records" not in data:
                    data = {
                        "node_id": "beam-node-01",
                        "sensor": "bme280",
                        "records": []
                    }
            except Exception:
                data = {
                    "node_id": "beam-node-01",
                    "sensor": "bme280",
                    "records": []
                }
    else:
        data = {
            "node_id": "beam-node-01",
            "sensor": "bme280",
            "records": []
        }

    # Append and write back
    data["records"].append(env_json_data)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Env data appended to {file_name} at {datetime.now()}")
except Exception as e:
    print(f"Error saving env data: {e}")
