#**** BEAM PROJECT - FRANCIS MARION UNIVERSITY - DETECT . PY ****#
# This script is meant to use Python's subprocess module to run the
# 'i2cdetect' command to scan i2c ports for sensors. It should return
# text detailing which sensors are currently online.
#
# Collaborators:
#
#********************************************************************#

import spidev  # For interfacing with SPI devices from user space via the spidev linux kernel driver.
import RPi.GPIO as GPIO
import subprocess
import logging 
import re
import os, time, json, logging, spidev, RPi.GPIO as GPIO
import json   
import sys

CONFIG_PATH = "/home/pi/BEAMNode_Prototype1/scripts/node/config.json"


def set_config_flag(path, section, key, value):
    """Safely set a flag in config.json without touching anything else."""
    try:
        with open(path, "r") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}

    if section not in cfg or not isinstance(cfg[section], dict):
        cfg[section] = {}

    # Only update if it isn't already the desired value
    if cfg[section].get(key) != value:
        cfg[section][key] = value
        # Atomic-ish write to avoid partial files on power los
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp_path, path)


#*****************************************************#
# This section is for SPI detection (BME/BMP280)
#*****************************************************#

# These pin numbers correlate to each sensor
# CS_PIN = 5, 9, 10, 11 is BME
# CS_PIN = 2, 3 is TSL2591

import logging.handlers

PRIMARY_LOG_DIR = "/home/pi/BEAMNode_Prototype1/logs"
FALLBACK_LOG_DIR = "/tmp/beam_logs"


def get_log_dir():
    """Return a writable log directory, falling back to /tmp if needed."""
    try:
        os.makedirs(PRIMARY_LOG_DIR, exist_ok=True)
        test_file = os.path.join(PRIMARY_LOG_DIR, ".writetest")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return PRIMARY_LOG_DIR
    except Exception as e:
        print(f"[detect] Log directory not writable ({e}), using fallback /tmp", file=sys.stderr)
        os.makedirs(FALLBACK_LOG_DIR, exist_ok=True)
        return FALLBACK_LOG_DIR


LOG_DIR = get_log_dir()
LOG_PATH = os.path.join(LOG_DIR, "detect_bme280.log")

try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception as e:
    print(f"[detect] Warning: could not create log dir {LOG_DIR}: {e}")

spi_logger = logging.getLogger("detect_bme280")
spi_logger.setLevel(logging.INFO)

if not spi_logger.handlers:
    try:
        fh = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=262_144, backupCount=3)
        fh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        spi_logger.addHandler(fh)
    except Exception as e:
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
        spi_logger.addHandler(sh)
        print(f"[detect] Warning: file logging disabled ({e}). Using console handler.")

_spi_fh = logging.FileHandler("detect_bme280.log", mode="a")
_spi_fh.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
spi_logger.addHandler(_spi_fh)
spi_logger.propagate = False  # keep it out of root logger


def spi_init(cs_pin):
    GPIO.setmode(GPIO.BCM)  # Sets the numbering system for the GPIO
    GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH)  # Sets up GPIO and initializes it to inactive
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
        spi: The spi device
        reg: Address of the register to be read.
        cs_pin: The GPIO pin used for chip select.

    Returns:
        The value read from the given register.
    """

    GPIO.output(cs_pin, 0)
    response = spi.xfer2([reg | 0x80, 0x00])[1]
    GPIO.output(cs_pin, 1)
    return response


def read_BME():
    # pessimistically disable bme280; we'll only enable it on good detection
    set_config_flag(CONFIG_PATH, "bme280", "enabled", False)

    CS_PIN = 5
    spi = spi_init(CS_PIN)
    try:
        spi_logger.info("Starting BME/BMP280 chip-ID read (SPI mode=0, 1MHz, CS=GPIO5)")
        chip1 = read_chip_ID(spi, 0xD0, CS_PIN)
        time.sleep(0.002)
        chip2 = read_chip_ID(spi, 0xD0, CS_PIN)
        chip = chip1 if chip1 == chip2 else 0x00  # require stable ID

        if chip in (0x60, 0x58):
            which = "BME280" if chip == 0x60 else "BMP280"
            msg = f"Chip ID: 0x{chip:02X} ({which})"
            print(msg)
            spi_logger.info(msg)
            # flip bme280.enabled in config when detected
            set_config_flag(CONFIG_PATH, "bme280", "enabled", True)
        else:
            msg = f"Chip ID: 0x{chip:02X} (unexpected; check CS/wiring/mode)"
            print(f"Chip ID: 0x{chip:02x} (unexpected; check wiring)")
            spi_logger.warning(msg)
            # keep enabled = False on unexpected chip
            set_config_flag(CONFIG_PATH, "bme280", "enabled", False)

    except Exception as e:
        spi_logger.exception(f"SPI detection failed: {e}")
        # if detection fails, ensure bme280 is disabled
        set_config_flag(CONFIG_PATH, "bme280", "enabled", False)
        raise
    finally:
        spi.close()
        GPIO.cleanup()
        spi_logger.info("SPI closed and GPIO cleaned up.")


read_BME()

#*****************************************************#
# This section is for Camera detection (IMX219 via Picamera2)
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

try:
    if ok:
        set_config_flag(CONFIG_PATH, "camera", "enabled", True)
        set_config_flag(CONFIG_PATH, "camera", "model", "imx219")
        set_config_flag(CONFIG_PATH, "camera", "last_detect_info", info)
    else:
        # explicitly disable when not found / failure
        set_config_flag(CONFIG_PATH, "camera", "enabled", False)
        set_config_flag(CONFIG_PATH, "camera", "model", None)
        set_config_flag(CONFIG_PATH, "camera", "last_detect_info", info)
except Exception as e:
    print(f"[detect] Failed to update camera flags: {e}")

#*****************************************************#
# I2C detection (TSL2591 + AHT)
#*****************************************************#

# TSL2591 may appear at 0x29 or 0x3A depending on board.
# AHT20/21 uses 0x38.
addr_table = {
    "tsl2591": [0x29],
    "aht": [0x38],
}

# Try both buses; some nodes use i2c-1, others i2c-2.
CANDIDATE_I2C_BUSES = (1)

logging.basicConfig(
    filename='detect_tsl2591.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

def scan_i2c(busnum):
    """Run i2cdetect on a bus and return output text."""
    try:
        result = subprocess.run(
            ["sudo", "i2cdetect", "-y", str(busnum)],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except Exception:
        return -1

def scan_all_i2c_buses(bus):
    """Scan all available I2C buses and collect found addresses."""
    all_found_addrs = set()
    addr_to_buses = {}

    if not os.path.exists(f"/dev/i2c-{bus}"):
        return -1

    adds = scan_i2c(bus)
    if adds == -1:
        return adds

    matches = re.findall(r"\b[0-9a-f]{2}\b", adds, re.IGNORECASE)
    for m in matches:
        addr = int(m, 16)
        all_found_addrs.add(addr)
        addr_to_buses.setdefault(addr, set()).add(bus)
    
    # buses=CANDIDATE_I2C_BUSES
    # for bus in buses:
    #     if not os.path.exists(f"/dev/i2c-{bus}"):
    #         continue

    #     adds = scan_i2c(bus)
    #     if adds == -1:
    #         continue

    #     matches = re.findall(r"\b[0-9a-f]{2}\b", adds, re.IGNORECASE)
    #     for m in matches:
    #         addr = int(m, 16)
    #         all_found_addrs.add(addr)
    #         addr_to_buses.setdefault(addr, set()).add(bus)

    return all_found_addrs, addr_to_buses

def detect_i2c_sensors():
    """Detect sensors on all I2C buses and update config."""
    found_addrs, addr_to_buses = scan_all_i2c_buses()
    detected = []

    for sensor_name, possible_addrs in addr_table.items():
        found_addr = None
        found_bus = None

        # Pick first matching address
        for addr in possible_addrs:
            if addr in found_addrs:
                found_addr = addr
                found_bus = min(addr_to_buses[addr])
                break

        if found_addr is not None:
            detected.append(sensor_name)
            set_config_flag(CONFIG_PATH, sensor_name, "enabled", True)
            set_config_flag(CONFIG_PATH, sensor_name, "i2c_bus", found_bus)
            set_config_flag(CONFIG_PATH, sensor_name, "address_hex", f"0x{found_addr:02X}")
        else:
            set_config_flag(CONFIG_PATH, sensor_name, "enabled", False)
            set_config_flag(CONFIG_PATH, sensor_name, "i2c_bus", None)

    return detected

devices = detect_i2c_sensors()

#*****************************************************#
# AudioMoth (USB) - detection
# Looks for the first mounted USB storage under common roots
#*****************************************************#


def detect_audiomoth_simple():
    """Detect AudioMoth by lsusb only."""
    try:
        result = subprocess.run(
            ["lsusb"],
            capture_output=True,
            text=True,
            check=True
        )

        for line in result.stdout.splitlines():
            if "audiomoth" in line.lower():
                # AudioMoth detected
                set_config_flag(CONFIG_PATH, "audio", "enabled", True)
                set_config_flag(CONFIG_PATH, "audio", "mount_path", None)
                return True, f"AudioMoth detected: {line.strip()}"

    except Exception as e:
        print(f"[detect] lsusb failed: {e}")

    # Nothing found
    set_config_flag(CONFIG_PATH, "audio", "enabled", False)
    set_config_flag(CONFIG_PATH, "audio", "mount_path", None)
    return False, "No AudioMoth USB device found."


ok_am, info_am = detect_audiomoth_simple()
print("AudioMoth:", ok_am, "-", info_am)

print(f"The following sensors are online: {devices}")
if isinstance(devices, list):
    print("The following sensors are online:", ", ".join(devices) if devices else "None")
else:
    print(devices)
