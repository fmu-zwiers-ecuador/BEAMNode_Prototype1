#!/bin/bash

# --- CONFIGURATION ---
# Paths derived from the BEAMNode Project structure
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
SCRIPTS_DIR="$PROJECT_ROOT/scripts/node"
LOGS_DIR="/home/pi/logs"

# Ensure the log directory exists to capture cron output
mkdir -p "$LOGS_DIR"

# --- STEP 1: SET PERMISSIONS ---
# Granting execution permissions to essential BEAMNode scripts
echo "Setting execution permissions..."
chmod +x "$SCRIPTS_DIR/scheduler.py"
chmod +x "$SCRIPTS_DIR/shipping_queuing/shipping.py"
chmod +x "$SCRIPTS_DIR/sensor_detection/detect.py"
chmod +x "$SCRIPTS_DIR/launcher.py"

# --- STEP 2: CONSTRUCT CRONTAB ---
# Create a temporary file to safely handle crontab installation
TMP_CRON=$(mktemp)

# Load existing user crontab into the temp file
crontab -l > "$TMP_CRON" 2>/dev/null

# Define the BEAMNode cron block as seen in the system reference
# Using markers allows this script to be re-run without creating duplicates
CRON_BLOCK="
# === BEAMNode cron (managed) BEGIN ===
@reboot /bin/bash -lc 'sleep 5; echo \"[\$(date -Is)] cron boot hook ran\" >> $LOGS_DIR/cron_install.log'
@reboot /bin/bash -lc 'sleep 60; /usr/bin/python3 $SCRIPTS_DIR/scheduler.py >> $LOGS_DIR/scheduler.log 2>&1'
0 17 * * * /bin/bash -lc '$SCRIPTS
