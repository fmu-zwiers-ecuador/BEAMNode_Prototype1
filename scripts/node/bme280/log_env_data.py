import json
from datetime import datetime, timezone
import os
import sys

import board
import busio
from digitalio import DigitalInOut
from adafruit_bme280 import basic

# Determine project root dynamically
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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

# SPI configuration from config.json (unchanged)
spi_config = bme_config.get("spi", {})
sck_pin  = spi_config.get("sck_pin", "SCK")
mosi_pin = spi_config.get("mosi_pin", "MOSI")
miso_pin = spi_config.get("miso_pin", "MISO")
cs_pin   = spi_config.get("cs_pin", "D5")
baudrate = spi_config.get("baudrate")  # Read but don't apply on Pi

# Create SPI bus (Raspberry Pi / Blinka)
spi = busio.SPI(
    getattr(board, sck_pin),
    MOSI=getattr(board, mosi_pin),
    MISO=getattr(board, miso_pin),
)

# Chip select pin
cs = DigitalInOut(getattr(board, cs_pin))

# Apply baudrate ONLY if running on CircuitPython
if sys.implementation.name == "circuitpython" and baudrate is not None:
    while not spi.try_lock():
        pass
    spi.configure(baudrate=baudrate)
    spi.unlock()

# Initialize BME280 (NO baudrate argument)
sensor = basic.Adafruit_BME280_SPI(spi, cs)

# Read values
temperature = float(sensor.temperature)
humidity = float(sensor.humidity)
pressure = float(sensor.pressure)

# Directory and file for logs
directory = os.path.join(
    global_config.get("base_dir", os.path.join(project_root, "data")),
    bme_config.get("directory", "bme280"),
)
os.makedirs(directory, exist_ok=True)

file_name = bme_config.get("file_name", "env_data.json")
file_path = os.path.join(directory, file_name)

# New record
env_json_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "temperature_C": temperature,
    "humidity_percent": humidity,
    "pressure_hPa": pressure,
}

# Append to JSON
try:
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict) or "records" not in data:
                    data = {
                        "node_id": node_id,
                        "sensor": "bme280",
                        "records": [],
                    }
            except Exception:
                data = {
                    "node_id": node_id,
                    "sensor": "bme280",
                    "records": [],
                }
    else:
        data = {
            "node_id": node_id,
            "sensor": "bme280",
            "records": [],
        }

    data["records"].append(env_json_data)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    if global_config.get("print_debug", True):
        print(f"Env data appended to {file_name} at {datetime.now(timezone.utc)}")

except Exception as e:
    print(f"Error saving env data: {e}")
