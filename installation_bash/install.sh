#!/bin/bash
set -euo pipefail

sudo apt update
sudo apt install -y \
  python3-pip python3-venv \
  portaudio19-dev python3-pyaudio \
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

# PyAudio (pip version) - optional, since python3-pyaudio is already installed via apt
sudo python3 -m pip install --break-system-packages pyaudio

sudo apt upgrade -y
