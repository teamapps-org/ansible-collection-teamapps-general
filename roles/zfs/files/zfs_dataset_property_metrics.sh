#!/bin/bash
set -eu

# Default values for include and exclude filters
include_filters=()
exclude_filters=()

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --include-datasets REGEX  Include datasets matching the regex. Can be specified multiple times."
    echo "  --exclude-datasets REGEX  Exclude datasets matching the regex. Can be specified multiple times."
    echo "  -h, --help                Display this help message."
    echo
    echo "Examples:"
    echo "  $0 --include-datasets 'zfsdata/sync'"
    echo "  $0 --exclude-datasets 'zfsdata/sync'"
    echo "  $0 --include-datasets 'zfsdata/sync.*' --exclude-datasets 'zfsdata/sync/old'"
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --include-datasets) include_filters+=("^$2$"); shift ;;
        --exclude-datasets) exclude_filters+=("^$2$"); shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown parameter passed: $1"; usage; exit 1 ;;
    esac
    shift
done

# Function to check if any pattern in an array matches a string
matches_any() {
    local string="$1"
    shift
    local patterns=("$@")
    for pattern in "${patterns[@]}"; do
        if [[ $string =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Function to convert boolean values to 1 and 0
bool_to_int() {
    if [ "$1" == "yes" ]; then
        echo 1
    else
        echo 0
    fi
}

# Function to convert keystatus to integer values
keystatus_to_int() {
    if [ "$1" == "available" ]; then
        echo 1
    elif [ "$1" == "unavailable" ]; then
        echo 0
    else
        echo -1  # for non-encrypted datasets
    fi
}

# Function to output metrics for a single dataset
output_metrics() {
    local name=$1
    local keystatus=$2
    local mounted=$3
    local encryption=$4

    # Convert boolean values
    mounted_int=$(bool_to_int "$mounted")
    keystatus_int=$(keystatus_to_int "$keystatus")

    # Determine if the dataset is encrypted
    if [ "$encryption" == "off" ]; then
        encrypted=0
    else
        encrypted=1
    fi

    # Output metrics
    echo "zfs_dataset_property_encryption_status{name=\"$name\",encryption=\"$encryption\"} $encrypted"
    echo "zfs_dataset_property_keystatus{name=\"$name\"} $keystatus_int"
    echo "zfs_dataset_property_mounted{name=\"$name\"} $mounted_int"
}

# Get ZFS dataset properties and output metrics
/usr/sbin/zfs list -H -t filesystem -o name,keystatus,mounted,encryption -p -s name | while read -r line; do
    IFS=$'\t' read -r -a props <<< "$line"
    name=${props[0]}
    keystatus=${props[1]}
    mounted=${props[2]}
    encryption=${props[3]}

    # Apply include and exclude filters
    if matches_any "$name" "${include_filters[@]}" && ! matches_any "$name" "${exclude_filters[@]}"; then
        output_metrics "$name" "$keystatus" "$mounted" "$encryption"
    fi
done
