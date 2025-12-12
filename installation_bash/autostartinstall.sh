#!/bin/bash

# This script automates the installation and activation of the BEAMNode systemd service.

# --- Resolve paths relative to this script ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Configuration ---
SERVICE_FILE="$REPO_ROOT/beamnode.service"
LAUNCHER_FULL_PATH="/home/pi/BEAMNode_Prototype1/scripts/node/launcher.py"

# Absolute system destinations
SERVICE_DESTINATION="/etc/systemd/system/$(basename "$SERVICE_FILE")"

echo "Starting BEAMNode Service Installation..."

if [ "$(id -u)" -ne 0 ]; then
   echo "ERROR: This script must be run with 'sudo'."
   exit 1
fi

# 1. Set executable permissions for the launcher script
echo "Setting executable permission on $LAUNCHER_FULL_PATH..."
chmod +x "$LAUNCHER_FULL_PATH"

# 2. Copy the service file from the repository root to the system directory
echo "Copying $(basename "$SERVICE_FILE") to $SERVICE_DESTINATION..."
cp "$SERVICE_FILE" "$SERVICE_DESTINATION"

# 3. Reload systemd daemon to recognize the new service
echo "Reloading systemd daemon..."
systemctl daemon-reload

# 4. Enable the service to run on boot
echo "Enabling $SERVICE_FILE to run on startup..."
systemctl enable "$SERVICE_FILE"

# 5. Start the service immediately
echo "Starting $SERVICE_FILE now..."
systemctl start "$SERVICE_FILE"

echo "Installation complete."
