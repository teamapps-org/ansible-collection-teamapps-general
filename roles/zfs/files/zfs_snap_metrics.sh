#!/bin/bash
# output zfs snapshot metrics per dataset
# zfs_snap_count = number of snapshots
# zfs_snap_oldest_seconds: timestamp of oldest snapshot in seconds
# zfs_snap_latest_seconds: timestamp of latest snapshot in seconds

# usage:
# ./zfs_snap_metrics.sh > /tmp/zfs_snap_metrics.prom.new && mv /tmp/zfs_snap_metrics.prom.new /var/lib/node_exporter/zfs_snap_metrics.prom

set -eu
# set -o pipefail
# set -x

for i in $(/usr/sbin/zfs list -H -o name -r | grep -v docker); do
  # echo "snaps for ${i}:"
  snaps=$(/usr/sbin/zfs list -H -t snap -o creation -p -s creation "${i}")
  count=$(echo -n "${snaps}" | wc -l)
  echo "zfs_snap_count{ds=\"${i}\"} ${count}"
  if [ "$count" -gt 0 ]; then
    oldest=$(echo "${snaps}" | head -n1)
    latest=$(echo "${snaps}" | tail -n1)
    echo "zfs_snap_oldest_seconds{ds=\"${i}\"} ${oldest}"
    echo "zfs_snap_latest_seconds{ds=\"${i}\"} ${latest}"
  fi
done
