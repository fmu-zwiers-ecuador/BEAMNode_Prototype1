#!/usr/bin/env bash
set -euo pipefail

# ========= CONFIG =========
PI_USER="pi"

SRC_DIR="/home/pi/shipping"
MOUNT_POINT="/media/pi/BEAMdrive"
DEST_DIR="$MOUNT_POINT/shipping_archive"
LOG_FILE="/home/pi/logs/shipping_move.log"
# ==========================

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log() {
  echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

log "=== Shipping move started ==="

# --- sanity checks ---
if [[ ! -d "$SRC_DIR" ]]; then
  log "ERROR: Source directory does not exist: $SRC_DIR"
  exit 1
fi

if [[ ! -d "$MOUNT_POINT" ]]; then
  log "ERROR: BEAMdrive is not mounted at $MOUNT_POINT"
  exit 1
fi

# --- create destination folder ---
mkdir -p "$DEST_DIR"

# --- check if source is empty ---
if [[ -z "$(ls -A "$SRC_DIR")" ]]; then
  log "Nothing to move. Shipping folder is empty."
  exit 0
fi

# --- move data ---
log "Moving files from:"
log "  $SRC_DIR"
log "to:"
log "  $DEST_DIR"

mv "$SRC_DIR"/* "$DEST_DIR"/

log "Move complete."

# --- ownership sanity ---
chown -R "$PI_USER:$PI_USER" "$DEST_DIR"

log "Permissions fixed."
log "=== Shipping move finished ==="
