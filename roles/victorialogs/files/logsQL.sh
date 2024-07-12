#!/bin/bash

# Function to display usage information
usage() {
  echo "Usage: $0 <hostname> [--limit=N] [--start=time] [--end=time] [-d timeout=duration] [--text] [-h] <query>"
  echo
  echo "Arguments:"
  echo "  hostname       The host to query"
  echo "  --limit=N      Limit the number of results"
  echo "  --start=time   Start time for the query (e.g., 1h, 30m)"
  echo "  --end=time     End time for the query (e.g., 5m)"
  echo "  -d timeout=duration  Timeout for the query (e.g., 5s)"
  echo "  --text         Display formatted output"
  echo "  -h             Display this help message"
  echo "  query          The query string to pass"
  echo
  echo "Environment Variables:"
  echo "  VICTORIALOGS_USER     Username for authentication"
  echo "  VICTORIALOGS_PASSWORD Password for authentication"
  exit 1
}

# Function to encode URL parameters
urlencode() {
  local length="${#1}"
  for ((i = 0; i < length; i++)); do
    local c="${1:i:1}"
    case $c in
      [a-zA-Z0-9.~_-]) printf "$c" ;;
      *) printf '%%%02X' "'$c" ;;
    esac
  done
}

# Function to construct and execute the curl command
execute_curl() {
  local hostname="$1"
  local query="$2"
  local limit="$3"
  local start="$4"
  local end="$5"
  local timeout="$6"
  local formatted_output="$7"

  local curl_cmd=(
    curl -s -X POST -u "$VICTORIALOGS_USER:$VICTORIALOGS_PASSWORD"
    "https://$hostname/select/logsql/query"
    -d "query=$query"
  )

  if [ -n "$limit" ]; then
    curl_cmd+=(-d "limit=$limit")
  fi
  if [ -n "$start" ]; then
    curl_cmd+=(-d "start=$start")
  fi
  if [ -n "$end" ]; then
    curl_cmd+=(-d "end=$end")
  fi
  if [ -n "$timeout" ]; then
    curl_cmd+=(-d "timeout=$timeout")
  fi

  local last_stream=""

  "${curl_cmd[@]}" | while IFS= read -r line; do
    if $formatted_output; then
      stream=$(echo "$line" | jq -r '._stream')
      timestamp=$(echo "$line" | jq -r '._time')
      msg=$(echo "$line" | jq -r '._msg')

      if [ "$stream" != "$last_stream" ]; then
        echo -e "\e[32m_stream: ${stream}\e[0m"
        last_stream="$stream"
      fi

      echo -e "[\e[33m$timestamp\e[0m]\t $msg"
    else
      echo "$line"
    fi
  done
}

# Check if at least one argument is provided
if [ "$#" -lt 1 ]; then
  usage
fi

# Check if help is requested
if [ "$1" == "-h" ]; then
  usage
fi

# Initialize variables
HOSTNAME=""
LIMIT=""
START=""
END=""
TIMEOUT=""
QUERY=""
FORMATTED_OUTPUT=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case "$1" in
    --limit=*)
      LIMIT="${1#*=}"
      ;;
    --start=*)
      START="${1#*=}"
      ;;
    --end=*)
      END="${1#*=}"
      ;;
    -d)
      shift
      TIMEOUT="$1"
      ;;
    --text)
      FORMATTED_OUTPUT=true
      ;;
    -h)
      usage
      ;;
    *)
      if [ -z "$HOSTNAME" ]; then
        HOSTNAME="$1"
      else
        QUERY="$QUERY $1"
      fi
      ;;
  esac
  shift
done

# Remove leading whitespace from query
QUERY=$(echo "$QUERY" | sed 's/^ *//g')

# Encode the query
ENCODED_QUERY=$(urlencode "$QUERY")

# Prompt for credentials if not set
if [ -z "$VICTORIALOGS_USER" ]; then
  read -p "Enter Victoria Logs username: " VICTORIALOGS_USER
fi
if [ -z "$VICTORIALOGS_PASSWORD" ]; then
  read -sp "Enter Victoria Logs password: " VICTORIALOGS_PASSWORD
  echo
fi

# Execute the curl command and process the response
execute_curl "$HOSTNAME" "$ENCODED_QUERY" "$LIMIT" "$START" "$END" "$TIMEOUT" "$FORMATTED_OUTPUT"
