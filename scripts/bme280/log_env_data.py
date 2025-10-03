import spidev   # SPI low-level handling (required when using SPI)
import board
import busio
import digitalio
import adafruit_bme280
import json
from datetime import datetime
import os
from adafruit_bme280 import Adafruit_BME280_SPI #forced import
import board, busio, digitalio

# SPI Setup
# GPIO5 = physical pin 29 for Chip Select
CS_PIN = board.D5
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(CS_PIN)

# Initialize the BME280 sensor over SPI
sensor = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

# Read sensor values
temperature = sensor.temperature
humidity = sensor.humidity
pressure = sensor.pressure

# Directory for saving logs
directory = "data/bme280/"
os.makedirs(directory, exist_ok=True)

# Data object for JSON
env_json_data = {
    "Date": datetime.now().isoformat(),
    "Temperature_C": temperature,
    "Humidity_percent": humidity,
    "Pressure_hPa": pressure
}

# Writing to the same file
file_name = "env_data.jsonl"   # JSON Lines format
file_path = os.path.join(directory, file_name)

try:
    with open(file_path, "a") as json_file:   # < append
        json.dump(env_json_data, json_file)
        json_file.write("\n")                 # newline after each JSON object
    print(f"Env data appended to {file_name} at {datetime.now()}")
except Exception as e:
    print(f"Error saving env data: {e}")
