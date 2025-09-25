
#**** BEAM PROJECT - FRANCIS MARION UNIVERSITY - DETECT . PY ****#
# This script is meant to use Python's subprocess module to run the #
# 'i2cdetect' command to scan i2c ports for sensors. It should return #
# text detailing which sensors are currently online. #

# Collaborators:

#********************************************************************#

import spidev # For interfacing with SPI devices from user space via the spidev linux kernel driver.
import RPi.GPIO as GPIO
import subprocess

#*****************************************************#
#This section is for SPI detection
#*****************************************************#

# These pin numbers corrolate to each sensor
# CS_PIN = 5, 9, 10, 11 is BME
# CS_PIN = 2, 3 is TSL2591

def spi_init(cs_pin):
	GPIO.setmode(GPIO.BCM) #Sets the numbering system for the GPIO
	GPIO.setup(cs_pin, GPIO.OUT, initial=GPIO.HIGH) #Sets up GPIO an initializes it to inactive
	spi = spidev.SpiDev()
	spi.open(0, 0)  # Open SPI bus 0, device 0
	spi.max_speed_hz = 1000000
	spi.mode = 0
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
		chip = read_chip_ID(spi, 0xD0, 5)
		if chip in (0x60, 0x58):
			print(f"Chip ID: 0x{chip:02x} ({'BME280' if chip==0x60 else 'BMP280'})")
		else:
			print(f"Chip ID: 0x{chip:02x} (unexpected; check wiring)")
	finally:
		spi.close()
		GPIO.cleanup()

read_BME()

#*****************************************************#
#This section is for I2C detection
#*****************************************************#

# Hardcoded address dictionary for sensors
addr_table = {	# THESE ARE PLACEHOLDERS - REPLACE WITH CORRECT ADDRESSES
	"TSL2591": 29,
	"BME280": 00,
	"PIR" : 00
}

# Function1 - scan_i2c(busnum) - Run i2c detect on selected bus and return
# string with i2c output
def scan_i2c(busnum):
	# Set up subprocess call
	try:
		result_text = subprocess.run(f"sudo i2cdetect -y {busnum}", shell=True) # this will be i2cdetect output
		return result_text

	except subprocess.CalledProcessError as e:
		# handle errors: display error message, return -1
		print(e.stderr)
		return -1

	except FileNotFoundError:
		# handle errors: dissplay error message, return -1
		print("The specified file could not be found")
		return -1

# Function2 - get_devices(adds) - Take in output from i2c detect, parse,
# return which sensors are currently online
def get_devices(adds):

	# check adds for -1, if so, return error #
	if adds == -1:
		return "There are no avalible sensors"

	detected_sensors = []

	# parse through i2cdetect output, match aadresses to dictionary, add found addresses to detected_sensors #

	########################################################################################################
	tsl2591 = addr_table["TSL2591"]
	
	for num in adds:
		if num == tsl2591:
			detected_sensors.append("TSL2591")
	
	return detected_sensors

i2coutput = scan_i2c(1) # i2c output for bus 1
devices = get_devices(i2coutput)

print(f"The following sensors are online: {devices}")
