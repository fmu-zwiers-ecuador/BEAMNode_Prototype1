#!/bin/bash

# --- CONFIGURATION ---
# Paths derived from the provided image
PROJECT_ROOT="/home/pi/BEAMNode_Prototype1"
SCRIPTS_DIR="$PROJECT_ROOT/scripts/node"
LOGS_DIR="/home/pi/logs"

# Ensure log directory exists
mkdir -p "$LOGS_DIR"

# --- STEP 1: SET PERMISSIONS ---
# Grant execution permissions to the relevant scripts
echo "Setting execution permissions..."
chmod +x "$SCRIPTS_DIR/scheduler.py"
chmod +x "$SCRIPTS_DIR/move_to_drive.sh"
chmod +x "$SCRIPTS_DIR/shipping_queuing/shipping.py"

# --- STEP 2: CONSTRUCT CRONTAB ENTRIES ---
# We use a temporary file to safely manage crontab updates
TMP_CRON=$(mktemp)

# Export current crontab to the temporary file
crontab -l > "$TMP_CRON" 2>/dev/null

# Define the new BEAMNode block
# Note: Using single quotes to prevent local shell expansion of variables like $(date)
CRON_BLOCK="
# === BEAMNode cron (managed) BEGIN ===
@reboot /bin/bash -lc 'sleep 5; echo \"[\$(date -Is)] cron boot hook ran\" >> $LOGS_DIR/cron_install.log'
@reboot /bin/bash -lc 'sleep 60; /usr/bin/python3 $SCRIPTS_DIR/scheduler.py >> $LOGS_DIR/scheduler.log 2>&1'
0 17 * * * /bin/bash -lc '$SCRIPTS_DIR/move_to_drive.sh >> $LOGS_DIR/shipping_move.log 2>&1'
0 18 * * * /bin/bash -lc '/usr/bin/python3 $SCRIPTS_DIR/shipping_queuing/shipping.py >> $LOGS_DIR/shipping.log 2>&1'
# === BEAMNode cron (managed) END ===
"

# --- STEP 3: UPDATE CRONTAB ---
# Remove any existing BEAMNode block to prevent duplicates
sed -i '/# === BEAMNode cron (managed) BEGIN ===/,/# === BEAMNode cron (managed) END ===/d' "$TMP_CRON"

# Append the new block
echo "$CRON_BLOCK" >> "$TMP_CRON"

# Install the updated crontab
crontab "$TMP_CRON"
rm "$TMP_CRON"

echo "Success: Permissions set and crontabs installed."
