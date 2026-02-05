#!/bin/bash

# retryqueue.sh: A script that requests and queues data from each node.
# Author: Gabriel Gonzalez, Noel Challa, Alex Lance, Jackson Roberts, and Jaylen Small
# Last Updated: 2-4-26

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
# HELPER FUNCTIONS
# ---------------------------------------------------

log() {
    local msg="$1"
    local ts=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$ts] $msg" | tee -a "$LOG_FILE"
}

# Update a specific field for a node in the JSON file
update_node_state() {
    local node_key="$1"
    local field="$2"
    local value="$3"
    
    # Use jq to update the JSON in-place
    tmp_json=$(mktemp)
    jq --arg node "$node_key" --arg field "$field" --arg val "$value" \
       '.[$node][$field] = $val' "$JSON_FILEPATH" > "$tmp_json" && mv "$tmp_json" "$JSON_FILEPATH"
}

# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------

if [[ ! -f "$JSON_FILEPATH" ]]; then
    log "ERROR: node state file missing: $JSON_FILEPATH"
    exit 1
fi

log "=== STARTING DAILY SHIPPING QUEUE (mDNS Mode) ==="

# Get list of node keys from JSON
node_keys=$(jq -r 'keys[]' "$JSON_FILEPATH")

# STEP 1 — Ping & State Check
log "=== PINGING ALL NODES ==="
for name in $node_keys; do
    raw_host=$(jq -r ".\"$name\".hostname // \"$name\"" "$JSON_FILEPATH")
    [[ "$raw_host" == *.local ]] && full_host="$raw_host" || full_host="${raw_host}.local"
    
    was_alive=$(jq -r ".\"$name\".node_state" "$JSON_FILEPATH")

    if ping -c "$PING_COUNT" -W 2 "$full_host" > /dev/null 2>&1; then
        update_node_state "$name" "node_state" "alive"
        [[ "$was_alive" != "alive" ]] && log "$full_host: RECOVERED"
    else
        update_node_state "$name" "node_state" "dead"
        [[ "$was_alive" == "alive" ]] && log "$full_host: LOST CONNECTION"
    fi
done

# STEP 2 — Initial Transfer Attempt
log "=== INITIAL DATA TRANSFER ATTEMPT ==="
failed_nodes=()

for name in $node_keys; do
    raw_host=$(jq -r ".\"$name\".hostname // \"$name\"" "$JSON_FILEPATH")
    [[ "$raw_host" == *.local ]] && full_host="$raw_host" || full_host="${raw_host}.local"
    state=$(jq -r ".\"$name\".node_state" "$JSON_FILEPATH")

    if [[ "$state" == "dead" ]]; then
        log "$full_host: SKIPPED (DEAD)"
        failed_nodes+=("$name")
        continue
    fi

    # Check for remote data using rsync listing
    if ! rsync -d "pi@$full_host:$REMOTE_SHIP_DIR/" | grep -qvE '(\.|\.\.)$|^$'; then
        update_node_state "$name" "transfer_fail" "false"
        continue
    fi

    log "$full_host: Pulling data..."
    mkdir -p "$SUPERVISOR_DATA_ROOT"
    
    if rsync -avz --partial --ignore-existing "pi@$full_host:$REMOTE_SHIP_DIR/" "$SUPERVISOR_DATA_ROOT"; then
        log "$full_host: SUCCESS — transferred"
        update_node_state "$name" "transfer_fail" "false"
        
        # Clear remote data
        if ssh "pi@$full_host" "sudo rm -rf $REMOTE_SHIP_DIR/*"; then
            log "$full_host: SUCCESS clearing remote data"
        else
            log "$full_host: ERROR — Could not clear remote data."
        fi
    else
        log "$full_host: FAILURE — transfer failed"
        update_node_state "$name" "transfer_fail" "true"
        failed_nodes+=("$name")
    fi
done

# STEP 3 — Retries
if [[ ${#failed_nodes[@]} -gt 0 ]]; then
    log "=== RETRYING FAILED NODES ==="
    for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
        [[ ${#failed_nodes[@]} -eq 0 ]] && break
        log "--- RETRY ROUND $attempt ---"
        
        still_failing=()
        for name in "${failed_nodes[@]}"; do
            raw_host=$(jq -r ".\"$name\".hostname // \"$name\"" "$JSON_FILEPATH")
            [[ "$raw_host" == *.local ]] && full_host="$raw_host" || full_host="${raw_host}.local"

            # Check health and data existence
            if ! ping -c 1 -W 2 "$full_host" >/dev/null 2>&1 || \
               ! rsync -d "pi@$full_host:$REMOTE_SHIP_DIR/" | grep -qvE '(\.|\.\.)$|^$'; then
                still_failing+=("$name")
                continue
            fi

            if rsync -avz --partial --ignore-existing "pi@$full_host:$REMOTE_SHIP_DIR/" "$SUPERVISOR_DATA_ROOT"; then
                log "$full_host: SUCCESS on retry"
                update_node_state "$name" "transfer_fail" "false"
                ssh "pi@$full_host" "sudo rm -rf $REMOTE_SHIP_DIR/*"
            else
                still_failing+=("$name")
            fi
        done
        failed_nodes=("${still_failing[@]}")
    done
fi

# STEP 4 — Finalize
if [[ ${#failed_nodes[@]} -eq 0 ]]; then
    log "=== FINAL STATUS: ALL NODES SUCCEEDED ==="
else
    log "=== FINAL STATUS: SOME NODES FAILED ==="
fi