import spidev
import json
from datetime import datetime, timezone
import os

from adafruit_bme280 import basic
import board, busio
from digitalio import DigitalInOut

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Load config
config_path = os.path.join(project_root, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

bme_config = config["bme280"]
global_config = config["global"]

# Check if sensor is enabled
if not bme_config.get("enabled", True):
    exit(0)

node_id = global_config.get("node_id", "unknown-node")

# SPI Pins
spi_config = bme_config.get("spi", {})
CS_PIN = getattr(board, spi_config.get("cs_pin", "D5"))
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs  = DigitalInOut(CS_PIN)

# Initialize BME280
baudrate = spi_config.get("baudrate", 100000)
sensor = basic.Adafruit_BME280_SPI(spi, cs, baudrate=baudrate)

# Read values
temperature = float(sensor.temperature)
humidity = float(sensor.humidity)
pressure = float(sensor.pressure)

# Directory and file for logs
directory = os.path.join(global_config.get("base_dir", os.path.join(project_root, "data")), bme_config.get("directory", "bme280"))
os.makedirs(directory, exist_ok=True)
file_name = bme_config.get("file_name", "env_data.json")
file_path = os.path.join(directory, file_name)

# New record
env_json_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "temperature_C": temperature,
    "humidity_percent": humidity,
    "pressure_hPa": pressure
}

# Append to JSON
try:
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict) or "records" not in data:
                    data = {"node_id": node_id, "sensor": "bme280", "records": []}
            except Exception:
                data = {"node_id": node_id, "sensor": "bme280", "records": []}
    else:
        data = {"node_id": node_id, "sensor": "bme280", "records": []}

    data["records"].append(env_json_data)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    if global_config.get("print_debug", True):
        print(f"Env data appended to {file_name} at {datetime.now(timezone.utc)}")
except Exception as e:
    print(f"Error saving env data: {e}")
