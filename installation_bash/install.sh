#!/bin/bash

# Core for Adafruit
sudo pip3 install adafruit-blinka --break-system-packages

# install bme280 library
sudo pip3 install adafruit-circuitpython-bme280 --break-system-packages

# install PyAudio library
sudo apt install portaudio19-dev python3-pyaudio -y
sudo pip3 install pyaudio --break-system-packages

# install TSL2591 library
pip3 install adafruit-circuitpython-tsl2591 --break-system-packages
sudo pip3 install adafruit-circuitpython-tsl2591 --break-system-packages

# Installation for the original Python TSL2591 library
pip install python-tsl2591 --break-system-packages

# install AHXT0 library
pip3 install adafruit-circuitpython-ahtx0 --break-system-packages
sudo pip3 install adafruit-circuitpython-ahtx0 --break-system-packages

# installing Batctl packages
sudo apt install batctl

#update and upgrade system
sudo apt update && sudo apt upgrade 

