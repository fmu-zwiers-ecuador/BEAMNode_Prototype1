#!/bin/bash

# This script automates the installation and activation of the BEAMNode systemd service.

# --- Configuration ---
# File names and paths are relative to this script's location (the repo root)
SERVICE_FILE="beamnode.service"
LAUNCHER_RELATIVE_PATH="scripts/node/launcher.py"

# Absolute system destinations
SERVICE_DESTINATION="/etc/systemd/system/$SERVICE_FILE"
LAUNCHER_FULL_PATH="/home/pi/BEAMNode_Prototype1/$LAUNCHER_RELATIVE_PATH"

echo "Starting BEAMNode Service Installation..."

# 1. Check for root privileges (required for copying to /etc/systemd/system)
if [ "$(id -u)" -ne 0 ]; then
   echo "ERROR: This script must be run with 'sudo'."
   echo "Please run: sudo bash autostartinstall.sh"
   exit 1
fi

# 2. Set executable permissions for the launcher script
echo "Setting executable permission on $LAUNCHER_FULL_PATH..."
chmod +x "$LAUNCHER_FULL_PATH"

# 3. Copy the service file from the repository root to the system directory
echo "Copying $SERVICE_FILE to $SERVICE_DESTINATION..."
cp "$SERVICE_FILE" "$SERVICE_DESTINATION"

# 4. Reload systemd daemon to recognize the new service
echo "Reloading systemd daemon..."
systemctl daemon-reload

# 5. Enable the service to run on boot
echo "Enabling $SERVICE_FILE to run on startup..."
systemctl enable "$SERVICE_FILE"

# 6. Start the service immediately
echo "Starting $SERVICE_FILE now..."
systemctl start "$SERVICE_FILE"

echo "Installation complete. Service is running and enabled for startup."
echo "---------------------------------------------------------"
echo "To check the status: sudo systemctl status $SERVICE_FILE"
echo "To view logs: sudo journalctl -u $SERVICE_FILE -f"
echo "---------------------------------------------------------"
