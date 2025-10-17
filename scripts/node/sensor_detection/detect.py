
#**** BEAM PROJECT - FRANCIS MARION UNIVERSITY - DETECT . PY ****#
# This script is meant to use Python's subprocess module to run the #
# 'i2cdetect' command to scan i2c ports for sensors. It should return #
# text detailing which sensors are currently online. #

# Collaborators:

#********************************************************************#

import spidev # For interfacing with SPI devices from user space via the spidev linux kernel driver.
import RPi.GPIO as GPIO
import subprocess
import logging
import re
import os, time, json, logging, spidev, RPi.GPIO as GPIO
import json
CONFIG_PATH = "/home/pi/BEAMNode_Prototype1/config.json"
def set_config_flag(path, section, key, value):
    """Safely set a boolean flag in config.json without touching anything else."""
    try:
        with open(path, "r") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}

    if section not in cfg or not isinstance(cfg[section], dict):
        cfg[section] = {}

    # Only update if it isn't already the desired value
    if cfg[section].get(key) is not value:
        cfg[section][key] = value
        # Atomic-ish write to avoid partial files on power loss
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp_path, path)

#*****************************************************#
#This section is for SPI detection
#*****************************************************#

# These pin numbers corrolate to each sensor
# CS_PIN = 5, 9, 10, 11 is BME
# CS_PIN = 2, 3 is TSL2591

# ---------------------------
# SPI LOGGER (BME/BMP280)
# ---------------------------
spi_logger = logging.getLogger("detect_bme280")
spi_logger.setLevel(logging.INFO)
_spi_fh = logging.FileHandler("detect_bme280.log", mode="a")
_spi_fh.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
spi_logger.addHandler(_spi_fh)
spi_logger.propagate = False  # keep it out of root logger


def spi_init(cs_pin):
	GPIO.setmode(GPIO.BCM) #Sets the numbering system for the GPIO
	GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH) #Sets up GPIO an initializes it to inactive
	spi = spidev.SpiDev()
	spi.open(0, 0)  # Open SPI bus 0, device 0
	spi.max_speed_hz = 1000000
	spi.mode = 0
	try:
		spi.no_cs = True  # prevents CE0/CE1 from being driven by spidev
	except AttributeError:
		spi_logger.warning("spidev.no_cs not available; consider updating python-spidev")
	return spi  

def read_chip_ID(spi, reg, cs_pin):
	"""
	This method returns the memory address of the specified pin

	Args: 
		spi: The
		reg: Address of the register to be read.
		CS_PIN: The GPIO pin to check the address of.

	Returns:
		The memory address from the CS_PIN
	"""
	
	GPIO.output(cs_pin, 0)
	response = spi.xfer2([reg | 0x80, 0x00]) [1]
	GPIO.output(cs_pin, 1)
	return response

def read_BME():

	CS_PIN = 5
	spi = spi_init(CS_PIN)
	try:
		spi_logger.info("Starting BME/BMP280 chip-ID read (SPI mode=0, 1MHz, CS=GPIO5)")
		chip1 = read_chip_ID(spi, 0xD0, CS_PIN)
		import time  # ADDED: tiny delay between reads
		time.sleep(0.002)  # ADDED
		chip2 = read_chip_ID(spi, 0xD0, CS_PIN)  # ADDED
		chip = chip1 if chip1 == chip2 else 0x00  # ADDED: require stable ID
		if chip in (0x60, 0x58):
			which = "BME280" if chip == 0x60 else "BMP280"

			msg = f"Chip ID: 0x{chip:02X} ({which})"
			print(f"Chip ID: 0x{chip:02x} ({'BME280' if chip==0x60 else 'BMP280'})")
			spi_logger.info(msg)
			# flip bme280.enabled in config when detected
			set_config_flag(CONFIG_PATH, "bme280", "enabled", True)
			# end of new config detection

		else:
			msg = f"Chip ID: 0x{chip:02X} (unexpected; check CS/wiring/mode)"
			print(f"Chip ID: 0x{chip:02x} (unexpected; check wiring)")
			spi_logger.warning(msg)

				
	except Exception as e:
		spi_logger.exception(f"SPI detection failed: {e}")
		raise
	finally:
		spi.close()
		GPIO.cleanup()
		spi_logger.info("SPI closed and GPIO cleaned up.")

read_BME()

#*****************************************************#
# This section is for Camera detection
# Detect IMX219 using Picamera2
#*****************************************************#
from picamera2 import Picamera2

def detect_imx219_picamera2():
    try:
        cams = Picamera2.global_camera_info()  # list of dicts
        # Look for a camera model string containing "imx219"
        for c in cams:
            model = (c.get("Model") or c.get("model") or "").lower()
            if "imx219" in model:
                return True, f"Found camera: {c}"
            
        return False, f"No IMX219 found. Cameras: {cams}"
    except Exception as e:
        return False, f"Picamera2 unavailable or failed: {e}"

ok, info = detect_imx219_picamera2()
print(ok, info)

#*****************************************************#
#This section is for I2C detection
#*****************************************************#

# Hardcoded address dictionary for sensors
addr_table = {	# THESE ARE PLACEHOLDERS - REPLACE WITH CORRECT ADDRESSES
	"TSL2591": 0x29,
	#"BME280": 00,
	#"PIR" : 00
}

#Basic logging configurations for the TSL2591
logging.basicConfig(
    filename='detect_tsl2591.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

# Function1 - scan_i2c(busnum) - Run i2c detect on selected bus and return
# string with i2c output
def scan_i2c(busnum):
    try:
        result = subprocess.run(
            ["sudo", "i2cdetect", "-y", str(busnum)],
            capture_output=True,
            text=True,  # ensures stdout is a string
            check=True  # raises CalledProcessError on failure
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        print("Error during i2cdetect:")
        print(e.stderr)
        return -1

    except FileNotFoundError:
        print("i2cdetect command not found.")
        return -1

# Function2 - get_devices(adds) - Take in output from i2c detect, parse,
# return which sensors are currently online
def get_devices(adds):

	# check adds for -1, if so, return error #
	if adds == -1:
		return "There are no avalible sensors"

	detected_sensors = []

	address_matches = re.findall(r"\b[0-9a-f]{2}\b", adds, re.IGNORECASE)
	found_addrs = [int(addr, 16) for addr in address_matches]

	for sensor_name, sensor_addr in addr_table.items():
		if sensor_addr in found_addrs:
			detected_sensors.append(sensor_name)
			logging.info(f'{sensor_name} detected.')
	
	return detected_sensors

i2coutput = scan_i2c(1) # i2c output for bus 1
devices = get_devices(i2coutput)

print(f"The following sensors are online: {devices}")
if isinstance(devices, list) and "TSL2591" in devices:
    set_config_flag(CONFIG_PATH, "tsl2591", "enabled", True)
