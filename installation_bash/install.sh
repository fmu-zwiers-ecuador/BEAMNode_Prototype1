#!/bin/bash
set -euo pipefail

sudo apt update
sudo apt install -y \
  python3-pip python3-venv \
  libportaudio2 libjack0 \
  python3-pyaudio \
  batctl

# Upgrade pip tooling (system-wide). --break-system-packages is for Debian/RPi OS policy.
sudo python3 -m pip install --upgrade pip setuptools wheel --break-system-packages

# Adafruit + sensors
sudo python3 -m pip install --break-system-packages \
  adafruit-blinka \
  adafruit-circuitpython-bme280 \
  adafruit-circuitpython-tsl2591 \
  python-tsl2591 \
  adafruit-circuitpython-ahtx0

# NOTE:
# Do NOT apt install portaudio19-dev here (it can force exact-matching -dev deps and break on some Pi repos).
# If you ever *must* use pip's PyAudio instead, the typical requirement is:
#   sudo apt install libportaudio2 libjack0
#   pip3 install pyaudio
# (ideally inside a venv).  [oai_citation:1‡piwheels.org](https://www.piwheels.org/project/pyaudio/?utm_source=chatgpt.com)

sudo apt upgrade -y
