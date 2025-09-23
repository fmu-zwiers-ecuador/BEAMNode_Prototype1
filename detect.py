
#**** BEAM PROJECT - FRANCIS MARION UNIVERSITY - DETECT . PY ****#
# This script is meant to use Python's subprocess module to run the #
# 'i2cdetect' command to scan i2c ports for sensors. It should return #
# text detailing which sensors are currently online. #

# Collaborators:

#********************************************************************#

import subprocess


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