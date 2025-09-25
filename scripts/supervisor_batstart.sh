#!/bin/bash

#IMPORTANT - THIS SCRIPT IS MEANT FOR DEBIAN MACHINES

sudo killall wpa_supplicant
sudo rfkill ublock all

#Load BATMAN module
sudo modprobe batman-adv

# Set wlan0 to ibss
sudo ip link set wlan0 down
sudo iw dev wlan0 set type ibss
sudo ip link set wlan0 up
sudo iw dev wlan0 ibss join myadhoc 2412

#attach wlan0 to batman

sudo batctl if add wlan0
sudo ip link set up dev bat0

#Assign IP address

sudo ip addr add 192.168.1.20/24 dev bat0