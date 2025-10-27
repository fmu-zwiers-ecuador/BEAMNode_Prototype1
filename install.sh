#!/bin/bash

# Core for Adafruit
sudo pip3 install adafruit-blinka --break-system-packages


# install bme280 library
sudo pip3 install adafruit-circuitpython-bme280 --break-system-packages

# install camera module
sudo apt update
sudo apt install build-essential meson ninja-build pkg-config libyaml-dev python3-yaml python3-ply python3-jinja2 libssl-dev openssl git
git clone https://git.libcamera.org/libcamera/libcamera.git
cd libcamera
meson setup build
ninja -C build
sudo ninja -C build install

# install PyAudio library
sudo apt install python3-pyaudio portaudio-dev -y
sudo pip3 install pyaudio --break-system-packages

# install TSL2591 library
pip3 install adafruit-circuitpython-tsl2591 --break-system-packages
sudo pip3 install adafruit-circuitpython-tsl2591

# Installation for the original Python TSL2591 library
pip install python-tsl2591

# install AHXT0 library
pip3 install adafruit-circuitpython-ahtx0 --break-system-packages
sudo pip3 install adafruit-circuitpython-ahtx0

