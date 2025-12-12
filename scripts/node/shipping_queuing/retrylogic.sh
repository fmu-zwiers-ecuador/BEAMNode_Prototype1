#!/bin/bash

### ============================================================
### BEAM Automatic Cron Setup Script (User: pi)
###
### Installs:
###   - ping_nodes_10min.py (every 10 min)
###   - retryqueue.py       (daily @ 19:00)
###
### Handles:
###   - /home/pi/logs/ creation
###   - Permissions for json + scripts
###   - Cron under the correct user
###
### ============================================================

BASE_DIR="/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing"
PING_PY="$BASE_DIR/ping_nodes_10min.py"
RETRY_PY="$BASE_DIR/retryqueue.py"

LOG_DIR="/home/pi/logs"
PING_LOG="$LOG_DIR/ping.log"
QUEUE_LOG="$LOG_DIR/queue.log"

echo "=== BEAM CRON SETUP STARTED ==="


### ------------------------------------------------------------
### 1. Fix permissions on BEAM folder (IMPORTANT)
### ------------------------------------------------------------
echo "[INFO] Fixing permissions on BEAM project directory..."

sudo chown -R pi:pi "$BASE_DIR"
sudo chmod -R u+rwX,go+rX "$BASE_DIR"

echo "[INFO] Permissions fixed for:"
echo "      $BASE_DIR"


### ------------------------------------------------------------
### 2. Create /home/pi/logs folder for Python logs
### ------------------------------------------------------------
echo "[INFO] Creating log directory..."

mkdir -p "$LOG_DIR"
touch "$PING_LOG"
touch "$QUEUE_LOG"

chmod 666 "$PING_LOG"
chmod 666 "$QUEUE_LOG"

echo "[INFO] Log directory ready: $LOG_DIR"


### ------------------------------------------------------------
### 3. Install cron jobs under user pi
### ------------------------------------------------------------
echo "[INFO] Installing cron jobs..."

# Get existing pi crontab
EXISTING=$(crontab -l 2>/dev/null)

# Remove duplicates from previous runs
CLEANED=$(echo "$EXISTING" | grep -v "$PING_PY" | grep -v "$RETRY_PY")

# Write final crontab
echo "$CLEANED" > /tmp/beamcron.tmp
echo "*/10 * * * * /usr/bin/python3 $PING_PY" >> /tmp/beamcron.tmp
echo "0 19 * * * /usr/bin/python3 $RETRY_PY" >> /tmp/beamcron.tmp

# Install as pi
crontab /tmp/beamcron.tmp
rm /tmp/beamcron.tmp


### ------------------------------------------------------------
### 4. Show final crontab
### ------------------------------------------------------------
echo "=== FINAL USER (pi) CRONTAB ==="
crontab -l
echo "================================"

echo "=== SETUP COMPLETE ==="
echo "Ping log:  $PING_LOG"
echo "Queue log: $QUEUE_LOG"
echo "[NOTE] Python scripts handle logging internally."
echo "[DONE]"
