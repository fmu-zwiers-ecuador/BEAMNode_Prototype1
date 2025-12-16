#!/usr/bin/env bash
set -euo pipefail

# ========= CONFIG (edit if paths change) =========
PI_USER="pi"
PI_GROUP="pi"

PY="/usr/bin/python3"
BASE="/home/pi/BEAMNode_Prototype1/scripts/node"
LOG_DIR="/home/pi/logs"

SCHEDULER="$BASE/scheduler.py"
SHIPPING="$BASE/shipping_queuing/shipping.py"
MOVE_SCRIPT="$BASE/move_to_drive.sh"

# move time: 5:00 PM
MOVE_MIN="0"
MOVE_HOUR="17"

# shipping time: 6:00 PM
SHIP_MIN="0"
SHIP_HOUR="18"

# delay after reboot (seconds)
BOOT_DELAY="60"
# ===============================================

die() { echo "[!] $*" >&2; exit 1; }

echo "[*] Running as: $(whoami)"

# --- sanity checks ---
[[ -f "$SCHEDULER" ]]   || echo "[!] WARNING: missing $SCHEDULER"
[[ -f "$SHIPPING"  ]]   || echo "[!] WARNING: missing $SHIPPING"
[[ -f "$MOVE_SCRIPT" ]] || echo "[!] WARNING: missing $MOVE_SCRIPT"
[[ -x "$PY" ]] || die "Python not found/executable at $PY"

# --- create logs directory + files ---
echo "[*] Creating log dir: $LOG_DIR"
mkdir -p "$LOG_DIR"

echo "[*] Creating log files (if missing)"
touch \
  "$LOG_DIR/scheduler.log" \
  "$LOG_DIR/shipping.log" \
  "$LOG_DIR/shipping_move.log" \
  "$LOG_DIR/cron_install.log"

# --- set ownership & permissions ---
echo "[*] Setting ownership to $PI_USER:$PI_GROUP"
if ! chown -R "$PI_USER:$PI_GROUP" "$LOG_DIR" 2>/dev/null; then
  echo "[i] Trying with sudo..."
  sudo chown -R "$PI_USER:$PI_GROUP" "$LOG_DIR"
fi

echo "[*] Setting permissions"
chmod 755 "$LOG_DIR"
chmod 664 "$LOG_DIR"/*.log

# --- cron content ---
BEGIN_MARK="# === BEAMNode cron (managed) BEGIN ==="
END_MARK="# === BEAMNode cron (managed) END ==="

CRON_BOOT_NOTE="@reboot /bin/bash -lc 'sleep 5; echo \"[\$(date -Iseconds)] cron boot hook ran\" >> $LOG_DIR/cron_install.log'"

CRON_SCHED="@reboot /bin/bash -lc 'sleep $BOOT_DELAY; $PY $SCHEDULER >> $LOG_DIR/scheduler.log 2>&1'"

CRON_MOVE="$MOVE_MIN $MOVE_HOUR * * * /bin/bash -lc '$MOVE_SCRIPT >> $LOG_DIR/shipping_move.log 2>&1'"

CRON_SHIP="$SHIP_MIN $SHIP_HOUR * * * /bin/bash -lc '$PY $SHIPPING >> $LOG_DIR/shipping.log 2>&1'"

echo "[*] Installing cron jobs into PI user crontab"

EXISTING="$(crontab -l 2>/dev/null || true)"

CLEANED="$(printf "%s\n" "$EXISTING" | awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
  $0==b {inblock=1; next}
  $0==e {inblock=0; next}
  !inblock {print}
')"

NEW_CRON="$(cat <<EOF
$CLEANED
$BEGIN_MARK
$CRON_BOOT_NOTE
$CRON_SCHED
$CRON_MOVE
$CRON_SHIP
$END_MARK
EOF
)"

printf "%s\n" "$NEW_CRON" | crontab -

echo
echo "[+] Done. Current crontab:"
echo "--------------------------------"
crontab -l
echo "--------------------------------"

echo
echo "[+] Log directory status:"
ls -ld "$LOG_DIR"
ls -l "$LOG_DIR"/*.log
