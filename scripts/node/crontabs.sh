#!/usr/bin/env bash
set -euo pipefail

# ========= CONFIG (edit if paths change) =========
PI_USER="pi"
PI_GROUP="pi"

PY="/usr/bin/python3"
BASE="/home/pi/BEAMNode_Prototype1/scripts/node"
LOG_DIR="/home/pi/logs"

DETECT="$BASE/sensor_detection/detect.py"
SCHEDULER="$BASE/scheduler.py"
SHIPPING="$BASE/shipping_queuing/shipping.py"

# shipping time: 18:00 = 6 PM daily
SHIP_MIN="0"
SHIP_HOUR="18"

# delay after reboot (seconds)
BOOT_DELAY="60"
# ===============================================

die() { echo "[!] $*" >&2; exit 1; }

echo "[*] Running as: $(whoami)"
if [[ "$(whoami)" != "$PI_USER" ]]; then
  echo "[i] Tip: run as pi for best permissions: ./install_beam_cron.sh"
fi

# --- sanity checks (don’t hard fail on missing, but warn) ---
[[ -f "$DETECT" ]]    || echo "[!] WARNING: missing $DETECT"
[[ -f "$SCHEDULER" ]] || echo "[!] WARNING: missing $SCHEDULER"
[[ -f "$SHIPPING" ]]  || echo "[!] WARNING: missing $SHIPPING"
[[ -x "$PY" ]]        || die "Python not found/executable at $PY"

# --- create logs directory + files ---
echo "[*] Creating log dir: $LOG_DIR"
mkdir -p "$LOG_DIR"

echo "[*] Creating log files (if missing)"
touch "$LOG_DIR/detect.log" "$LOG_DIR/scheduler.log" "$LOG_DIR/shipping.log" "$LOG_DIR/cron_install.log"

# --- set ownership & permissions ---
echo "[*] Setting ownership to $PI_USER:$PI_GROUP"
# If you run as pi, chown may fail if files already owned by root; try sudo if needed.
if ! chown -R "$PI_USER:$PI_GROUP" "$LOG_DIR" 2>/dev/null; then
  echo "[i] Could not chown without sudo. Trying with sudo..."
  sudo chown -R "$PI_USER:$PI_GROUP" "$LOG_DIR"
fi

echo "[*] Setting permissions"
chmod 755 "$LOG_DIR"
chmod 664 "$LOG_DIR"/*.log

# --- cron content ---
BEGIN_MARK="# === BEAMNode cron (managed) BEGIN ==="
END_MARK="# === BEAMNode cron (managed) END ==="

CRON_DETECT="@reboot /bin/bash -lc 'sleep $BOOT_DELAY; $PY $DETECT >> $LOG_DIR/detect.log 2>&1'"
CRON_SCHED="@reboot /bin/bash -lc 'sleep $BOOT_DELAY; $PY $SCHEDULER >> $LOG_DIR/scheduler.log 2>&1'"
CRON_SHIP="$SHIP_MIN $SHIP_HOUR * * * /bin/bash -lc '$PY $SHIPPING >> $LOG_DIR/shipping.log 2>&1'"

# optional: log that cron was installed each reboot (helps debugging)
CRON_BOOT_NOTE="@reboot /bin/bash -lc 'sleep 5; echo \"[$(date -Iseconds)] cron boot hook ran\" >> $LOG_DIR/cron_install.log'"

echo "[*] Installing cron jobs into PI user crontab (not root)"
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
$CRON_DETECT
$CRON_SCHED
$CRON_SHIP
$END_MARK
EOF
)"

printf "%s\n" "$NEW_CRON" | crontab -

echo "[+] Done. Current crontab:"
echo "--------------------------------"
crontab -l
echo "--------------------------------"

echo "[+] Log directory status:"
ls -ld "$LOG_DIR"
ls -l "$LOG_DIR"/*.log
