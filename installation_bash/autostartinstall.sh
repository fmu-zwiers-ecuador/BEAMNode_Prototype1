#!/bin/bash

# BEAMNode Autostart Installation Script
# Target: Raspberry Pi (Node 5)

PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
SERVICE_NAME="beamnode.service"
LOG_DIR="$PROJECT_ROOT/logs"
SCRIPT_DIR="$PROJECT_ROOT/scripts/node"

echo "🚀 Starting BEAMNode installation..."

# 1. Create necessary directories
mkdir -p "$LOG_DIR"
mkdir -p "/home/pi/data"
mkdir -p "/home/pi/shipping"

# 2. Set permissions
chmod +x "$SCRIPT_DIR/launcher.py"
chmod +x "$SCRIPT_DIR/sensor_detection/detect.py"
chmod +x "$SCRIPT_DIR/scheduler.py"
chmod +x "$SCRIPT_DIR/shipping_queuing/shipping.py"

# 3. Handle Systemd Service
echo "⚙️ Configuring systemd service..."
sudo cp "$SCRIPT_DIR/$SERVICE_NAME" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

# 4. Install Dependencies
echo "📦 Installing Python dependencies..."
sudo apt-get update
sudo apt-get install -y i2c-tools python3-pip
pip3 install spidev RPi.GPIO pandas_ta yfinance python-dotenv picamera2 --break-system-packages

echo "✅ Installation complete. Start service with: sudo systemctl start $SERVICE_NAME"
