#!/usr/bin/env bash
set -euo pipefail

# ===== CONFIG =====
SRC_DIR="/home/pi/shipping"            # <-- change if needed
MOUNT_POINT="/media/pi/BEAMdrive"
DEST_ROOT="$MOUNT_POINT/shipping_archive"
LOG_FILE="/home/pi/logs/shipping_move.log"
HOST="$(hostname)"
RUN_ID="$(date +%Y%m%dT%H%M%S)"
DEST_DIR="$DEST_ROOT/${HOST}-${RUN_ID}"
# ==================

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log(){ echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"; }

log "=== Shipping move started ==="
log "SRC:  $SRC_DIR"
log "DEST: $DEST_DIR"

[[ -d "$SRC_DIR" ]] || { log "ERROR: source folder not found"; exit 1; }
[[ -d "$MOUNT_POINT" ]] || { log "ERROR: BEAMdrive not mounted"; exit 1; }

mkdir -p "$DEST_DIR"

# If empty, exit
if [[ -z "$(ls -A "$SRC_DIR" 2>/dev/null || true)" ]]; then
  log "Nothing to move (source empty)."
  exit 0
fi

log "Sanitizing filenames (replace ':' with '-') to support exFAT/NTFS..."
# rename files and folders safely (deepest first)
while IFS= read -r -d '' p; do
  new="${p//:/-}"
  if [[ "$p" != "$new" ]]; then
    mv -n -- "$p" "$new"
  fi
done < <(find "$SRC_DIR" -depth -name '*:*' -print0)

log "Rsync to drive (no chown/perms), then remove source files..."
rsync -rtv --remove-source-files \
  --no-owner --no-group --no-perms --omit-dir-times \
  "$SRC_DIR"/ "$DEST_DIR"/ 2>&1 | tee -a "$LOG_FILE"

# clean up empty dirs
find "$SRC_DIR" -type d -empty -delete || true

log "Move complete."
log "=== Shipping move finished ==="
