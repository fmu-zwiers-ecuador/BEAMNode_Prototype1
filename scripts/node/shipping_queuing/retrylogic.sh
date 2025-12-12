#!/bin/bash

### ================================================
###  BEAM Automatic Cron Setup Script
###  This script installs:
###    - ping job (every 10 min)
###    - retry queue job (daily @ 19:00)
###  It also creates log files and ensures permissions.
###
###  If you move your .py files later, update:
###    PING_PY
###    RETRY_PY
### ================================================

BASE_DIR="/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing"

# Python scripts
PING_PY="$BASE_DIR/ping_nodes_10min.py"
RETRY_PY="$BASE_DIR/retryqueue.py"

# Log Files
PING_LOG="$BASE_DIR/ping.log"
QUEUE_LOG="$BASE_DIR/queue.log"

echo "=== BEAM CRON AUTO-SETUP STARTED ==="

### ----------------------------------------
### 1. Create logs + fix permissions
### ----------------------------------------
echo "[INFO] Creating log files..."

touch "$PING_LOG"
touch "$QUEUE_LOG"

chmod 666 "$PING_LOG"
chmod 666 "$QUEUE_LOG"

echo "[INFO] Logs ready:"
echo "   $PING_LOG"
echo "   $QUEUE_LOG"

### ----------------------------------------
### 2. Install cron jobs
### ----------------------------------------
echo "[INFO] Installing CRON jobs..."

# Build cron content
CRON_CONTENT="*/10 * * * * /usr/bin/python3 $PING_PY >> $PING_LOG 2>&1
0 19 * * * /usr/bin/python3 $RETRY_PY >> $QUEUE_LOG 2>&1
"

# Write cron jobs to user's crontab
echo "$CRON_CONTENT" | crontab -

echo "[INFO] Cron jobs installed."

### ----------------------------------------
### 3. Show final cron table
### ----------------------------------------
echo "=== FINAL CRON TABLE ==="
crontab -l
echo "========================"

echo "=== SETUP COMPLETE ==="
echo "Ping log:   $PING_LOG"
echo "Queue log:  $QUEUE_LOG"
echo ""
echo "[NOTE] If you move your scripts later, update the paths in this setup script."
