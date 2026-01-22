#!/bin/bash
# BEAMNode Project - Node 5 Autostart Installation
# Location: /home/pi/BEAMNode_Prototype1/autostartinstall.sh

# 1. Configuration
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
NODE_DIR="$PROJECT_ROOT/scripts/node"
SERVICE_SRC="$PROJECT_ROOT/beamnode.service"
SERVICE_NAME="beamnode.service"
LOG_DIR="$PROJECT_ROOT/logs"

echo "------------------------------------------------"
echo "🚀 Starting BEAMNode Node 5 Installation..."
echo "------------------------------------------------"

# 2. Create Required Folders
echo "[1/4] Preparing directories..."
mkdir -p "/home/pi/data"
mkdir -p "/home/pi/shipping"
mkdir -p "$LOG_DIR"

# 3. Set Permissions
echo "[2/4] Setting execution permissions..."
chmod +x "$NODE_DIR/launcher.py"
chmod +x "$NODE_DIR/scheduler.py"
chmod +x "$NODE_DIR/sensor_detection/detect.py"
chmod +x "$NODE_DIR/shipping_queuing/shipping.py"

# 4. Install Systemd Service
echo "[3/4] Registering systemd service..."
if [ -f "$SERVICE_SRC" ]; then
    # Copy from project root to system services folder
    sudo cp "$SERVICE_SRC" /etc/systemd/system/
    
    # Reload and Enable
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    # Start the service now
    sudo systemctl restart "$SERVICE_NAME"
    echo "✅ Service $SERVICE_NAME installed and started."
else
    echo "❌ ERROR: Could not find $SERVICE_SRC"
    echo "Please ensure beamnode.service is in $PROJECT_ROOT"
    exit 1
fi

# 5. Verification
echo "[4/4] Verifying system status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "------------------------------------------------"
    echo "🎉 SUCCESS: Installation Complete!"
    echo "The Launcher is now running in the background."
    echo "------------------------------------------------"
else
    echo "⚠️ Service installed but failed to start."
    echo "Check logs with: journalctl -u $SERVICE_NAME -f"
fi
