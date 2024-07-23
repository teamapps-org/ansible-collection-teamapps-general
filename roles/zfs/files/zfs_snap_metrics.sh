#!/bin/bash
# output zfs snapshot metrics per dataset
# zfs_snap_count = number of snapshots
# zfs_snap_oldest_seconds: timestamp of oldest snapshot in seconds
# zfs_snap_latest_seconds: timestamp of latest snapshot in seconds
# zfs_snap_script_duration_seconds: duration of the script run in seconds
# zfs_snap_last_run_timestamp_seconds: timestamp of the last run in seconds

# usage:
# ./zfs_snap_metrics.sh > /tmp/zfs_snap_metrics.prom.new && mv /tmp/zfs_snap_metrics.prom.new /var/lib/node_exporter/zfs_snap_metrics.prom

set -euo pipefail

LOCKFILE="/tmp/zfs_snap_metrics.lock"

# Function to remove lockfile on exit
cleanup() {
    rm -f "$LOCKFILE"
}
trap cleanup EXIT

# Ensure only one instance of the script is running
exec 200>"$LOCKFILE"
flock -n 200 || exit 1

# Write PID to lockfile
echo $$ > "$LOCKFILE"

# Check for stale lockfile
if [ -f "$LOCKFILE" ]; then
    lock_pid=$(cat "$LOCKFILE")
    if ! kill -0 "$lock_pid" 2>/dev/null; then
        echo "Removing stale lockfile"
        rm -f "$LOCKFILE"
        # Re-acquire lock
        exec 200>"$LOCKFILE"
        flock -n 200 || exit 1
        echo $$ > "$LOCKFILE"
    fi
fi

# Start time for duration metric
start_time=$(date +%s)

{
    for dataset in $(/usr/sbin/zfs list -H -o name -r | grep -v docker); do
        snaps=$(/usr/sbin/zfs list -H -t snap -o creation -p -s creation "${dataset}")
        count=$(echo -n "${snaps}" | wc -l)
        echo "zfs_snap_count{ds=\"${dataset}\"} ${count}"
        if [ "$count" -gt 0 ]; then
            oldest=$(echo "${snaps}" | head -n1)
            latest=$(echo "${snaps}" | tail -n1)
            echo "zfs_snap_oldest_seconds{ds=\"${dataset}\"} ${oldest}"
            echo "zfs_snap_latest_seconds{ds=\"${dataset}\"} ${latest}"
        fi
    done

    # End time for duration metric
    end_time=$(date +%s)
    duration=$(( end_time - start_time ))
    echo "zfs_snap_script_duration_seconds ${duration}"
    echo "zfs_snap_last_run_timestamp_seconds $(date +%s)"
}
