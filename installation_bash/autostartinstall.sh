#!/bin/bash
# BEAMNode Project - Autostart Installation Script
# Target: Raspberry Pi (Node 5)

# 1. Configuration - Update these paths if your project root is different
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
NODE_DIR="$PROJECT_ROOT/scripts/node"
LOG_DIR="$PROJECT_ROOT/logs"
SERVICE_NAME="beamnode.service"

echo "------------------------------------------"
echo "🚀 Initializing BEAMNode Installation..."
echo "------------------------------------------"

# 2. Create Required Directories
echo "[1/4] Creating data, shipping, and log directories..."
mkdir -p "/home/pi/data"
mkdir -p "/home/pi/shipping"
mkdir -p "$LOG_DIR"

# 3. Set Executable Permissions
# This ensures Python can actually launch the scripts
echo "[2/4] Setting script permissions..."
chmod +x "$NODE_DIR/launcher.py"
chmod +x "$NODE_DIR/scheduler.py"
chmod +x "$NODE_DIR/sensor_detection/detect.py"
chmod +x "$NODE_DIR/shipping_queuing/shipping.py"

# 4. Install Systemd Service
echo "[3/4] Installing systemd service..."
if [ -f "$NODE_DIR/$SERVICE_NAME" ]; then
    # Copy the service file to the system directory
    sudo cp "$NODE_DIR/$SERVICE_NAME" /etc/systemd/system/
    
    # Reload systemd to recognize the new service
    sudo systemctl daemon-reload
    
    # Enable the service to start on every boot
    sudo systemctl enable "$SERVICE_NAME"
    
    # Start the service immediately
    sudo systemctl restart "$SERVICE_NAME"
    echo "✅ Service $SERVICE_NAME installed and started."
else
    echo "❌ ERROR: $SERVICE_NAME not found in $NODE_DIR"
    exit 1
fi

# 5. Final Verification
echo "[4/4] Verifying installation..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "------------------------------------------"
    echo "🎉 SUCCESS: BEAMNode is now running!"
    echo "System will now:"
    echo "  1. Run detect.py on startup."
    echo "  2. Run scheduler.py in the background."
    echo "  3. Run shipping.py at 13:00 daily."
    echo "------------------------------------------"
else
    echo "⚠️  Installation finished, but service failed to start."
    echo "Check logs with: journalctl -u $SERVICE_NAME -f"
fi
