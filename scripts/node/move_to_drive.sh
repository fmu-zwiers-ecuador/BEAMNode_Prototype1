#!/usr/bin/env bash
set -euo pipefail

# ===== CONFIG =====
SRC_DIR="/home/pi/shipping"                  # <-- change if needed
MOUNT_POINT="/media/pi/BEAMdrive"
DEST_ROOT="$MOUNT_POINT/shipping_archive"
LOG_FILE="/home/pi/logs/shipping_move.log"
BOOT_ID="$(date +%Y%m%dT%H%M%S)"
HOST="$(hostname)"
DEST_DIR="$DEST_ROOT/${HOST}-${BOOT_ID}"
# ==================

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() { echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"; }

log "=== Shipping move started ==="
log "SRC:  $SRC_DIR"
log "MOUNT:$MOUNT_POINT"
log "DEST: $DEST_DIR"

# Checks
[[ -d "$SRC_DIR" ]] || { log "ERROR: source folder not found"; exit 1; }
[[ -d "$MOUNT_POINT" ]] || { log "ERROR: BEAMdrive not mounted"; exit 1; }

mkdir -p "$DEST_DIR"

# Nothing to move?
if [[ -z "$(ls -A "$SRC_DIR" 2>/dev/null || true)" ]]; then
  log "Nothing to move (source empty)."
  exit 0
fi

# Copy + remove source files safely
log "Rsync copy to drive (then remove source files)..."
rsync -a --remove-source-files --info=stats2,progress2 \
  "$SRC_DIR"/ "$DEST_DIR"/ | tee -a "$LOG_FILE"

# Remove empty dirs left behind
find "$SRC_DIR" -type d -empty -delete || true

log "Move complete."
log "=== Shipping move finished ==="
