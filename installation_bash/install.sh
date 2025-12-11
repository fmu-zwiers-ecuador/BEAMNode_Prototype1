#!/bin/bash
set -euo pipefail

sudo apt update

# System deps (PyAudio build deps + batctl)
sudo apt install -y batctl python3-dev portaudio19-dev

# If you want the distro PyAudio, uncomment this line and remove the pip install below:
# sudo apt install -y python3-pyaudio

# Python packages (system python; you’re opting into --break-system-packages)
sudo python3 -m pip install --break-system-packages \
  adafruit-blinka \
  adafruit-circuitpython-bme280 \
  adafruit-circuitpython-tsl2591 \
  adafruit-circuitpython-ahtx0 \
  pyaudio

# If you truly need this specific library, make it python3 + consistent:
sudo python3 -m pip install --break-system-packages python-tsl2591

sudo apt upgrade -y
