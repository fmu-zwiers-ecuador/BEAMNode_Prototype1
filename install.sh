#!/bin/bash

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