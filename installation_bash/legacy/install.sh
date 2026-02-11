#!/bin/bash
set -euo pipefail

sudo apt update
sudo apt install -y \
  python3-pip python3-venv \
  libportaudio2 libjack0 \
  python3-pyaudio \
  batctl

# Create required data + log roots for the node runtime
sudo mkdir -p /home/pi/data /home/pi/shipping /home/pi/logs /home/pi/BEAMNode_Prototype1/logs
sudo chown -R pi:pi /home/pi/data /home/pi/shipping /home/pi/logs /home/pi/BEAMNode_Prototype1/logs

# Upgrade pip tooling (system-wide). --break-system-packages is for Debian/RPi OS policy.
sudo python3 -m pip install --upgrade pip setuptools wheel --break-system-packages

# Adafruit + sensors
sudo python3 -m pip install --break-system-packages \
  adafruit-blinka==8.69.0 \
  adafruit-circuitpython-bme280==2.6.30 \
  adafruit-circuitpython-tsl2591==1.4.6 \
  adafruit-circuitpython-ahtx0==1.0.28

# NOTE:
# Do NOT apt install portaudio19-dev here (it can force exact-matching -dev deps and break on some Pi repos).
# If you ever *must* use pip's PyAudio instead, the typical requirement is:
#   sudo apt install libportaudio2 libjack0
#   pip3 install pyaudio
# (ideally inside a venv).  [oai_citation:1‡piwheels.org](https://www.piwheels.org/project/pyaudio/?utm_source=chatgpt.com)

sudo apt upgrade -y
