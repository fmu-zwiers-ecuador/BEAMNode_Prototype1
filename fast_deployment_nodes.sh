#!/bin/bash

# This script executes the autostartinstall.sh script on all Node Pis via SSH.

# --- CONFIGURATION (Update these variables) ---
INSTALLER_SCRIPT="autostartinstall.sh"
REPO_DIR="BEAMNode_Prototype1"
USER="pi" 

# IMPORTANT: Update these IP addresses
NODE_IPS=(
    "192.168.1.101" # Node Pi 1 IP
    "192.168.1.102" # Node Pi 2 IP
    "192.168.1.103" # Node Pi 3 IP
    "192.168.1.104" # Node Pi 4 IP
    "192.168.1.105" # Node Pi 5 IP
)

# --- DEPLOYMENT LOOP ---

echo "--- Starting fast remote installation on all Node Pis ---"

for IP in "${NODE_IPS[@]}"; do
    echo "=========================================================="
    echo "Processing Node Pi: $IP"
    echo "=========================================================="
    
    # Check for passwordless SSH connectivity
    if ! ssh -q $USER@$IP exit; then
        echo "ERROR: Could not connect to $IP. Check SSH keys or IP address."
        continue
    fi
    
    # --- 1. Ensure installer script is executable on the node ---
    echo "Setting executable permission on remote installer..."
    SSH_CMD_CHMOD="chmod +x ~/$REPO_DIR/$INSTALLER_SCRIPT"
    ssh $USER@$IP "$SSH_CMD_CHMOD"

    # --- 2. Execute the installation script remotely ---
    # The installer handles copying the service file, reloading, enabling, and starting.
    echo "Executing the installer script remotely (requires sudo)..."
    SSH_CMD_INSTALL="cd ~/$REPO_DIR && sudo bash $INSTALLER_SCRIPT"
    ssh $USER@$IP "$SSH_CMD_INSTALL"

    # --- 3. Verify the service status ---
    echo "Verifying service status..."
    ssh $USER@$IP "sudo systemctl status beamnode.service | grep Active"
    
    echo "Node $IP installation complete."
done

echo "********************************************************"
echo "Deployment process finished."
echo "********************************************************"
