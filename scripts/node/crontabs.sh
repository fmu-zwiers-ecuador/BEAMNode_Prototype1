#!/usr/bin/env bash
set -euo pipefail

# ====== CONFIG (change these if your paths move) ======
PY="/usr/bin/python3"
BASE="/home/pi/BEAMNode_Prototype1/scripts/node"
LOG_DIR="/home/pi/logs"

DETECT="$BASE/sensor_detection/detect.py"
SCHEDULER="$BASE/scheduler.py"
SHIPPING="$BASE/shipping_queuing/shipping.py"

# Run time (shipping): 18:00 = 6 PM
SHIP_MIN="0"
SHIP_HOUR="18"

# Delay after reboot (seconds)
BOOT_DELAY="60"
# ======================================================

echo "[*] Creating log directory: $LOG_DIR"
mkdir -p "$LOG_DIR"

# Build cron lines
CRON_DETECT="@reboot /bin/bash -lc 'sleep $BOOT_DELAY; $PY $DETECT >> $LOG_DIR/detect.log 2>&1'"
CRON_SCHED="@reboot /bin/bash -lc 'sleep $BOOT_DELAY; $PY $SCHEDULER >> $LOG_DIR/scheduler.log 2>&1'"
CRON_SHIP="$SHIP_MIN $SHIP_HOUR * * * $PY $SHIPPING >> $LOG_DIR/shipping.log 2>&1"

# Marker comments so we can manage this block safely
BEGIN_MARK="# === BEAMNode cron (managed) BEGIN ==="
END_MARK="# === BEAMNode cron (managed) END ==="

echo "[*] Installing crontab entries for user: $(whoami)"

# Read existing crontab (if none, start empty)
EXISTING="$(crontab -l 2>/dev/null || true)"

# Remove old managed block if present
CLEANED="$(printf "%s\n" "$EXISTING" | awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
  $0==b {inblock=1; next}
  $0==e {inblock=0; next}
  !inblock {print}
')"

# Append new managed block
NEW_CRON="$(cat <<EOF
$CLEANED
$BEGIN_MARK
$CRON_DETECT
$CRON_SCHED
$CRON_SHIP
$END_MARK
EOF
)"

# Install
printf "%s\n" "$NEW_CRON" | crontab -

echo
echo "[+] Done. Current crontab is:"
echo "--------------------------------"
crontab -l
echo "--------------------------------"
echo
echo "[i] Logs will be written to:"
echo "  $LOG_DIR/detect.log"
echo "  $LOG_DIR/scheduler.log"
echo "  $LOG_DIR/shipping.log"
