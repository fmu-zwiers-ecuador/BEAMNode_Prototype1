#!/bin/bash

### ============================================================
### BEAM Automatic Cron Setup Script
### Creates crontab for:
###   - ping_nodes_10min.py   (every 10 minutes)
###   - retryqueue.py         (daily at 19:00)
###
### LOG FILES GO TO: /home/pi/logs/
### If you move files later, update:
###   BASE_DIR, PING_PY, RETRY_PY
### ============================================================

BASE_DIR="/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing"
PING_PY="$BASE_DIR/ping_nodes_10min.py"
RETRY_PY="$BASE_DIR/retryqueue.py"

LOG_DIR="/home/pi/logs"
PING_LOG="$LOG_DIR/ping.log"
QUEUE_LOG="$LOG_DIR/queue.log"

echo "=== BEAM CRON AUTO-SETUP STARTED ==="

### ----------------------------------------
### 1. Create /home/pi/logs folder + log files
### ----------------------------------------
echo "[INFO] Creating log directory and log files..."

mkdir -p "$LOG_DIR"

touch "$PING_LOG"
touch "$QUEUE_LOG"

chmod 666 "$PING_LOG"
chmod 666 "$QUEUE_LOG"

echo "[INFO] Logs created in $LOG_DIR:"
echo "   $PING_LOG"
echo "   $QUEUE_LOG"

### ----------------------------------------
### 2. Install cron jobs properly
### ----------------------------------------
echo "[INFO] Installing cron jobs..."

(
crontab -l 2>/dev/null | grep -v "$PING_PY"
crontab -l 2>/dev/null | grep -v "$RETRY_PY"

echo "*/10 * * * * /usr/bin/python3 $PING_PY >> $PING_LOG 2>&1"
echo "0 19 * * * /usr/bin/python3 $RETRY_PY >> $QUEUE_LOG 2>&1"
) | crontab -

### ----------------------------------------
### 3. Show final crontab
### ----------------------------------------
echo "=== FINAL CRONTAB ==="
crontab -l
echo "======================"

echo "=== SETUP COMPLETE ==="
echo "Ping log:  $PING_LOG"
echo "Queue log: $QUEUE_LOG"
echo ""
echo "[NOTE] If you move script paths later, update the variables at the top of this file."
