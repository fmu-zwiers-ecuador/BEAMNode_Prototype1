#**** BEAM PROJECT - FRANCIS MARION UNIVERSITY - DETECT . PY ****#
# Streamlined human-readable detection printouts
#********************************************************************#

import spidev
import RPi.GPIO as GPIO
import subprocess
import logging
import re
import os, time, json, sys
from picamera2 import Picamera2

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
    if cfg[section].get(key) != value:
        cfg[section][key] = value
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w") as f:
            json.dump(cfg, f, indent=2)
        os.replace(tmp_path, path)

# ---------------- SPI (BME/BMP280) ---------------- #

CS_PIN_BME = 5

def spi_init(cs_pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH)
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1_000_000
    spi.mode = 0
    try:
        spi.no_cs = True
    except AttributeError:
        pass
    return spi

def read_chip_ID(spi, reg, cs_pin):
    GPIO.output(cs_pin, 0)
    response = spi.xfer2([reg | 0x80, 0x00])[1]
    GPIO.output(cs_pin, 1)
    return response

def detect_spi_sensor():
    set_config_flag(CONFIG_PATH, "bme280", "enabled", False)
    spi = spi_init(CS_PIN_BME)
    try:
        chip1 = read_chip_ID(spi, 0xD0, CS_PIN_BME)
        time.sleep(0.002)
        chip2 = read_chip_ID(spi, 0xD0, CS_PIN_BME)
        chip = chip1 if chip1 == chip2 else 0x00
        if chip in (0x60, 0x58):
            sensor_name = "BME280" if chip == 0x60 else "BMP280"
            print(f"SPI Sensor Found: {sensor_name} (ID 0x{chip:02X})")
            set_config_flag(CONFIG_PATH, "bme280", "enabled", True)
            return sensor_name
        else:
            print(f"SPI Sensor: Unknown or not found (ID 0x{chip:02X})")
            return None
    except Exception:
        print("SPI Sensor detection failed")
        return None
    finally:
        spi.close()
        GPIO.cleanup()

# ---------------- Camera (IMX219) ---------------- #

def detect_camera():
    try:
        cams = Picamera2.global_camera_info()
        for c in cams:
            model = (c.get("Model") or c.get("model") or "").lower()
            if "imx219" in model:
                print("Camera Found: IMX219")
                set_config_flag(CONFIG_PATH, "camera", "enabled", True)
                set_config_flag(CONFIG_PATH, "camera", "model", "imx219")
                return True
    except Exception:
        pass
    print("Camera Not Found")
    set_config_flag(CONFIG_PATH, "camera", "enabled", False)
    set_config_flag(CONFIG_PATH, "camera", "model", None)
    return False

# ---------------- I2C Sensors ---------------- #

I2C_ADDR_TABLE = {
    "tsl2591": [0x29],
    "aht": [0x38],
}

CANDIDATE_I2C_BUSES = (1,)

def scan_i2c(busnum):
    try:
        result = subprocess.run(
            ["sudo", "i2cdetect", "-y", str(busnum)],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except Exception:
        return ""

def detect_i2c_sensors():
    detected = []
    for bus in CANDIDATE_I2C_BUSES:
        if not os.path.exists(f"/dev/i2c-{bus}"):
            continue
        output = scan_i2c(bus)
        found_addrs = set(int(m, 16) for m in re.findall(r"\b[0-9a-f]{2}\b", output, re.IGNORECASE))
        for name, addrs in I2C_ADDR_TABLE.items():
            for addr in addrs:
                if addr in found_addrs:
                    print(f"I2C Sensor Found: {name} (Bus {bus}, Addr 0x{addr:02X})")
                    set_config_flag(CONFIG_PATH, name, "enabled", True)
                    set_config_flag(CONFIG_PATH, name, "i2c_bus", bus)
                    set_config_flag(CONFIG_PATH, name, "address_hex", f"0x{addr:02X}")
                    detected.append(name)
                else:
                    set_config_flag(CONFIG_PATH, name, "enabled", False)
    if not detected:
        print("No I2C sensors detected")
    return detected

# ---------------- AudioMoth USB ---------------- #

def detect_audiomoth():
    try:
        result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "audiomoth" in line.lower():
                print(f"AudioMoth USB Found: {line.strip()}")
                set_config_flag(CONFIG_PATH, "audio", "enabled", True)
                set_config_flag(CONFIG_PATH, "audio", "mount_path", None)
                return True
    except Exception:
        pass
    print("AudioMoth USB Not Found")
    set_config_flag(CONFIG_PATH, "audio", "enabled", False)
    set_config_flag(CONFIG_PATH, "audio", "mount_path", None)
    return False

# ---------------- Main ---------------- #

print("=== Sensor Detection Summary ===")
detect_spi_sensor()
detect_camera()
detect_i2c_sensors()
detect_audiomoth()
print("=== Detection Complete ===")