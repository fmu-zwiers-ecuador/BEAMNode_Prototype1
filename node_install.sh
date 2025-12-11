#!/bin/bash

# This script performs the initial installation steps on a node
# Intended to be run on the node itself, assuming it has internet access and hostname is set correctly

echo "Detecting node number from hostname..."
HOSTNAME=$(cat /etc/hostname)
NODENUM=${HOSTNAME##*node}

echo "**************************************************"
echo "Starting initial installation on node $NODENUM..."
echo "**************************************************"

echo "**************************************************"
echo "Updating system packages..."
echo "**************************************************"

sudo bash ./installation_bash/install.sh

# set up daemon installation
echo "**************************************************"
echo "Setting up BEAMNode service to run on startup..."
echo "**************************************************"

sudo chmod +x autostartinstall.sh
sudo chown -R pi:pi /home/pi/BEAMNode_Prototype1/logs
sudo ./autostartinstall.sh

# batman installation
echo "**************************************************"
echo "Installing batman-adv for mesh networking..."
echo "**************************************************"

sudo bash ./scripts/Batman_mesh/install_batman.sh