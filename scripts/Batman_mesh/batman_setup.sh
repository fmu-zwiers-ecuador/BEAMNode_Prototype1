#!/bin/bash

# Stop and disable conflicting services
systemctl stop wpa_supplicant
systemctl disable wpa_supplicant
systemctl stop NetworkManager
systemctl disable NetworkManager

# Load BATMAN module (kernel mesh networking driver)
modprobe batman-adv

# Configure wlan0 for IBSS (ad-hoc mode)
ip link set wlan0 down
iw dev wlan0 set type ibss
ip link set wlan0 up
sudo iw dev wlan0 ibss join <network_name> <frequency>  
# Example: sudo iw dev wlan0 ibss join myadhoc 2412

# Add wlan0 to BATMAN
batctl if add wlan0
ip link set up dev bat0

# Assign static IP address to bat0
ip addr add 192.168.x.x/24 dev bat0  
# Example: ip addr add 192.168.1.2/24 dev bat0
