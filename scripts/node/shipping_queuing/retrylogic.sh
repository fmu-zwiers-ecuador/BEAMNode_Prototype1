#!/bin/bash

### ============================================================
### BEAM Automatic Cron Setup Script (User: pi)
###
### Installs:
###   - ping_nodes_10min.py (every 10 min)
###   - retryqueue.py       (daily at 19:00)
###
### LOG FILES STORED BY PYTHON SCRIPTS ONLY — NO REDIRECTION
### ============================================================

BASE_DIR="/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing"
PING_PY="$BASE_DIR/ping_nodes_10min.py"
RETRY_PY="$BASE_DIR/retryqueue.py"

LOG_DIR="/home/pi/logs"
PING_LOG="$LOG_DIR/ping.log"
QUEUE_LOG="$LOG_DIR/queue.log"

echo "=== BEAM CRON SETUP STARTED ==="

### ----------------------------------------
### 1. Create /home/pi/logs folder for Python logs
### ----------------------------------------
echo "[INFO] Creating log directory..."

mkdir -p "$LOG_DIR"
touch "$PING_LOG"
touch "$QUEUE_LOG"

chmod 666 "$PING_LOG"
chmod 666 "$QUEUE_LOG"

echo "[INFO] Log directory ready: $LOG_DIR"


### ----------------------------------------
### 2. Install cron jobs FOR USER PI ONLY
### ----------------------------------------
echo "[INFO] Installing cron jobs for user pi..."

# Get existing pi crontab
EXISTING=$(crontab -l 2>/dev/null)

# Remove old duplicate entries if script was run before
CLEANED=$(echo "$EXISTING" | grep -v "$PING_PY" | grep -v "$RETRY_PY")

# Put final cron table together
echo "$CLEANED" > /tmp/beamcron.tmp
echo "*/10 * * * * /usr/bin/python3 $PING_PY" >> /tmp/beamcron.tmp
echo "0 19 * * * /usr/bin/python3 $RETRY_PY" >> /tmp/beamcron.tmp

# Install as the pi user (NOT root)
crontab /tmp/beamcron.tmp
rm /tmp/beamcron.tmp


### ----------------------------------------
### 3. Show final cron table for user pi
### ----------------------------------------
echo "=== FINAL USER (pi) CRONTAB ==="
crontab -l
echo "================================"

echo "=== SETUP COMPLETE ==="
echo "Ping log:  $PING_LOG"
echo "Queue log: $QUEUE_LOG"
echo ""
echo "[NOTE] Python scripts handle logs internally — no cron redirection needed."
