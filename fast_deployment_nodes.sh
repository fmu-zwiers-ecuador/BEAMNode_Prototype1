#!/bin/bash

# This script executes the autostartinstall.sh script on all Node Pis via SSH.

# --- CONFIGURATION (Update these variables) ---
INSTALLER_SCRIPT="installation_bash/autostartinstall.sh"
REPO_DIR="BEAMNode_Prototype1"
USER="pi" 

# IMPORTANT: Update these IP addresses
NODE_IPS=(
    "192.168.1.1" 
    "192.168.1.2" 
    "192.168.1.3" 
    "192.168.1.4" 
    "192.168.1.5" 
)

# --- DEPLOYMENT LOOP ---

echo "--- Starting fast remote installation on all Node Pis ---"

for IP in "${NODE_IPS[@]}"; do
    echo "=========================================================="
    echo "Processing Node Pi: $IP"
    echo "=========================================================="
    
    # 1. Connection Check
    if ! ssh -q $USER@$IP exit; then
        echo "--> ❌ ERROR: Could not connect to $IP. Please check network/IP/SSH keys."
        continue
    fi
    
    # 2. CRITICAL FIX: Fix Line Endings on the remote installer script using 'tr'
    # This ensures the remote script runs cleanly, preventing the "$'\r': command not found" error.
    echo "Fixing Windows line endings on remote installer ($INSTALLER_SCRIPT) using 'tr'..."
    SSH_CMD_FIX="cd ~/$REPO_DIR && tr -d '\r' < $INSTALLER_SCRIPT > temp_fixed.sh && mv temp_fixed.sh $INSTALLER_SCRIPT"
    ssh $USER@$IP "$SSH_CMD_FIX"

    # 3. Ensure installer script is executable on the node
    echo "Setting executable permission on remote installer..."
    SSH_CMD_CHMOD="chmod +x ~/$REPO_DIR/$INSTALLER_SCRIPT"
    ssh $USER@$IP "$SSH_CMD_CHMOD"

    # 4. Execute the installation script remotely 
    echo "Executing the installer script remotely (requires sudo)..."
    SSH_CMD_INSTALL="cd ~/$REPO_DIR && sudo bash $INSTALLER_SCRIPT"
    if ssh $USER@$IP "$SSH_CMD_INSTALL"; then
        echo "--> ✅ INSTALLATION SUCCESSFUL on $IP."
        
        # 5. Verify the service status
        echo "Verifying service status..."
        ssh $USER@$IP "sudo systemctl status beamnode.service | grep Active"
    else
         echo "--> ❌ INSTALLATION FAILED on $IP. See output above for details."
    fi
    
    echo "Node $IP processing complete."
done

echo "********************************************************"
echo "Deployment process finished."
echo "********************************************************"
