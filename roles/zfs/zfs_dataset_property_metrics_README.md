# ZFS Dataset Property Metrics

This script exports ZFS dataset properties as metrics suitable for Grafana dashboards and alerting. The metrics are output in a format compatible with Prometheus.

## Usage

```bash
./zfs_dataset_property_metrics.sh [OPTIONS]
```

### Options

- `--include-datasets REGEX` : Include datasets matching the regex. Can be specified multiple times.
- `--exclude-datasets REGEX` : Exclude datasets matching the regex. Can be specified multiple times.
- `-h, --help` : Display this help message.

### Examples

**Basic usage without filters:**

```bash
./zfs_dataset_property_metrics.sh
```

**With an include filter to match the whole name:**

```bash
./zfs_dataset_property_metrics.sh --include-datasets 'zfsdata/sync'
```

**With an include filter to match all children:**

```bash
./zfs_dataset_property_metrics.sh --include-datasets 'zfsdata/sync.*'
```

**With an exclude filter:**

```bash
./zfs_dataset_property_metrics.sh --exclude-datasets 'zfsdata/sync'
```

**With both include and exclude filters:**

```bash
./zfs_dataset_property_metrics.sh --include-datasets 'zfsdata.*' --exclude-datasets 'zfsdata/sync/old'
```

## Example Output for Various States

**Not Encrypted:**

```plaintext
zfs_dataset_property_encryption_status{name="zfsdata",encryption="off"} 0
zfs_dataset_property_keystatus{name="zfsdata"} -1
zfs_dataset_property_mounted{name="zfsdata"} 1
```

**Encrypted, Key Not Loaded:**

```plaintext
zfs_dataset_property_encryption_status{name="zfsdata/sync",encryption="aes-256-gcm"} 1
zfs_dataset_property_keystatus{name="zfsdata/sync"} 0
zfs_dataset_property_mounted{name="zfsdata/sync"} 0
```

**Encrypted, Key Loaded, Mounted:**

```plaintext
zfs_dataset_property_encryption_status{name="zfsdata/sync",encryption="aes-256-gcm"} 1
zfs_dataset_property_keystatus{name="zfsdata/sync"} 1
zfs_dataset_property_mounted{name="zfsdata/sync"} 1
```

**Encrypted, Key Loaded, Not Mounted:**

```plaintext
zfs_dataset_property_encryption_status{name="zfsdata/sync",encryption="aes-256-gcm"} 1
zfs_dataset_property_keystatus{name="zfsdata/sync"} 1
zfs_dataset_property_mounted{name="zfsdata/sync"} 0
```

## Instructions

1. Save the script to a file, e.g., `zfs_dataset_property_metrics.sh`.
2. Make the script executable:

   ```bash
   chmod +x zfs_dataset_property_metrics.sh
   ```

3. Run the script with desired filters (if any).

To redirect the output to a file:

```bash
./zfs_dataset_property_metrics.sh > /path/to/metrics_output.prom
```

You can configure this script to run periodically with a cron job or a systemd timer to continuously collect and export ZFS dataset properties for monitoring with Grafana.
