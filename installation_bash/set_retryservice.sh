#!/bin/bash
# BEAMNode Project - Supervisor Queue Installation (Scheduled for 2PM)
# Location: /home/pi/BEAMNode_Prototype1/installation_bash/set_retryservice.sh

# 1. Configuration
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
QUEUE_SCRIPT="$PROJECT_ROOT/scripts/node/shipping_queuing/retryqueue.py"
SERVICE_NAME="retryqueue"
LOG_DIR="/home/pi/logs"
DATA_DIR="/home/pi/data"

echo "[1/4] Preparing supervisor directories..."
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$PROJECT_ROOT/installation_bash"

# 2. Set Permissions
echo "[2/4] Setting execution permissions..."
if [ -f "$QUEUE_SCRIPT" ]; then
    chmod +x "$QUEUE_SCRIPT"
else
    echo "ERROR: Could not find $QUEUE_SCRIPT"
    exit 1
fi

# 3. Create Systemd Files
echo "[3/4] Generating systemd unit files..."

# Create the Service
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.service <<EOF
[Unit]
Description=RetryQueue Data Transfer Task
After=network-online.target

[Service]
Type=oneshot
User=pi
ExecStart=/usr/bin/python3 $QUEUE_SCRIPT
EOF"

# Create the Timer (Set to 14:00 daily)
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME.timer <<EOF
[Unit]
Description=Run RetryQueue daily at 11:50 PM

[Timer]
OnCalendar=*-*-* 11:50:00
Persistent=true
Unit=$SERVICE_NAME.service

[Install]
WantedBy=timers.target
EOF"

# 4. Activation
echo "[4/4] Activating timer..."
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME.timer"

# Verification
echo "------------------------------------------------"
if systemctl is-active --quiet "$SERVICE_NAME.timer"; then
    echo "SUCCESS: Supervisor Queue is active!"
    echo "The script is scheduled to run every day at 11:50 (11:50 PM)."
    echo "Next run info:"
    systemctl list-timers "$SERVICE_NAME.timer"
else
    echo "Timer failed to start."
fi
echo "------------------------------------------------"
