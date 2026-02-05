#!/bin/bash

# retryqueue.sh: A script that requests and queues data from each node.
# Author: Gabriel Gonzalez, Noel Challa, Alex Lance, Jackson Roberts, and Jaylen Small
# Last Updated: 2-5-26

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
JSON_FILEPATH="/home/pi/BEAMNode_Prototype1/scripts/node/shipping_queuing/node_states.json"
SUPERVISOR_DATA_ROOT="/home/pi/data"
REMOTE_SHIP_DIR="/home/pi/shipping"
LOG_FILE="/home/pi/logs/queue.log"

MAX_RETRIES=5
PING_COUNT=1

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# ---------------------------------------------------
# HELPER FUNCTIONS (No-jq JSON Parsing)
# ---------------------------------------------------

log() {
    local msg="$1"
    local ts=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$ts] $msg" | tee -a "$LOG_FILE"
}

# Extracts a value from the JSON for a specific node
# Usage: get_val "node1" "hostname"
get_val() {
    local node="$1"
    local key="$2"
    # Logic: Find the node line, look at subsequent lines for the key, extract value between quotes
    sed -n "/\"$node\"/,/}/p" "$JSON_FILEPATH" | grep "\"$key\"" | sed -E 's/.*: ?"([^"]*)".*/\1/'
}

# Updates a value in the JSON file
# Usage: update_val "node1" "node_state" "alive"
update_val() {
    local node="$1"
    local key="$2"
    local new_val="$3"

    # This creates a temporary file and uses sed to swap the value within the node block
    # It targets the line containing the key that immediately follows the node name
    sed -i "/\"$node\"/,/}/ s/\(\"$key\": \)\"[^\"]*\"/\1\"$new_val\"/" "$JSON_FILEPATH"
}

# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------

if [[ ! -f "$JSON_FILEPATH" ]]; then
    log "ERROR: node state file missing: $JSON_FILEPATH"
    exit 1
fi

log "=== STARTING DAILY SHIPPING QUEUE (mDNS Mode) ==="

# Get list of top-level keys (nodes) from the JSON
node_keys=$(grep -E '^    "[^"]+": \{' "$JSON_FILEPATH" | sed -E 's/.*"([^"]+)".*/\1/')

# STEP 1 — Ping & State Check
log "=== PINGING ALL NODES ==="
for name in $node_keys; do
    raw_host=$(get_val "$name" "hostname")
    [[ -z "$raw_host" ]] && raw_host="$name"
    [[ "$raw_host" == *.local ]] && full_host="$raw_host" || full_host="${raw_host}.local"
    
    was_alive=$(get_val "$name" "node_state")

    if ping -c "$PING_COUNT" -W 2 "$full_host" > /dev/null 2>&1; then
        update_val "$name" "node_state" "alive"
        [[ "$was_alive" != "alive" ]] && log "$full_host: RECOVERED"
    else
        update_val "$name" "node_state" "dead"
        [[ "$was_alive" == "alive" ]] && log "$full_host: LOST CONNECTION"
    fi
done

# STEP 2 — Initial Transfer Attempt
log "=== INITIAL DATA TRANSFER ATTEMPT ==="
failed_nodes=""

for name in $node_keys; do
    raw_host=$(get_val "$name" "hostname")
    [[ -z "$raw_host" ]] && raw_host="$name"
    [[ "$raw_host" == *.local ]] && full_host="$raw_host" || full_host="${raw_host}.local"
    
    state=$(get_val "$name" "node_state")

    if [[ "$state" == "dead" ]]; then
        log "$full_host: SKIPPED (DEAD)"
        failed_nodes="$failed_nodes $name"
        continue
    fi

    # Check for remote data (rsync listing returns empty if no files)
    if ! rsync -d "pi@$full_host:$REMOTE_SHIP_DIR/" 2>/dev/null | grep -qvE '(\.|\.\.)$|^$'; then
        update_val "$name" "transfer_fail" "false"
        continue
    fi

    log "$full_host: Pulling data..."
    mkdir -p "$SUPERVISOR_DATA_ROOT"
    
    if rsync -avz --partial --ignore-existing "pi@$full_host:$REMOTE_SHIP_DIR/" "$SUPERVISOR_DATA_ROOT"; then
        log "$full_host: SUCCESS — transferred"
        update_val "$name" "transfer_fail" "false"
        
        if ssh "pi@$full_host" "sudo rm -rf $REMOTE_SHIP_DIR/*"; then
            log "$full_host: SUCCESS clearing remote data"
        else
            log "$full_host: ERROR — Could not clear remote data."
        fi
    else
        log "$full_host: FAILURE — transfer failed"
        update_val "$name" "transfer_fail" "true"
        failed_nodes="$failed_nodes $name"
    fi
done

# STEP 3 — Retries
if [[ -n $(echo $failed_nodes | tr -d ' ') ]]; then
    log "=== RETRYING FAILED NODES ==="
    for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
        [[ -z $(echo $failed_nodes | tr -d ' ') ]] && break
        log "--- RETRY ROUND $attempt ---"
        
        still_failing=""
        for name in $failed_nodes; do
            raw_host=$(get_val "$name" "hostname")
            [[ -z "$raw_host" ]] && raw_host="$name"
            [[ "$raw_host" == *.local ]] && full_host="$raw_host" || full_host="${raw_host}.local"

            # Check health and data existence
            if ! ping -c 1 -W 2 "$full_host" >/dev/null 2>&1 || \
               ! rsync -d "pi@$full_host:$REMOTE_SHIP_DIR/" 2>/dev/null | grep -qvE '(\.|\.\.)$|^$'; then
                still_failing="$still_failing $name"
                continue
            fi

            if rsync -avz --partial --ignore-existing "pi@$full_host:$REMOTE_SHIP_DIR/" "$SUPERVISOR_DATA_ROOT"; then
                log "$full_host: SUCCESS on retry"
                update_val "$name" "transfer_fail" "false"
                ssh "pi@$full_host" "sudo rm -rf $REMOTE_SHIP_DIR/*"
            else
                still_failing="$still_failing $name"
            fi
        done
        failed_nodes="$still_failing"
    done
fi

# STEP 4 — Finalize
if [[ -z $(echo $failed_nodes | tr -d ' ') ]]; then
    log "=== FINAL STATUS: ALL NODES SUCCEEDED ==="
else
    log "=== FINAL STATUS: SOME NODES FAILED ($failed_nodes) ==="
fi
