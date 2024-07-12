#!/usr/bin/env python3

import argparse
import os
import requests
import sys
import json
from getpass import getpass
import signal
import subprocess

# Function to handle broken pipe error gracefully
def handle_broken_pipe(signal, frame):
    try:
        sys.stderr.close()
    except:
        pass
    try:
        sys.stdout.close()
    except:
        pass
    os._exit(0)

# Register signal handler for broken pipe
signal.signal(signal.SIGPIPE, handle_broken_pipe)

def print_debug(message):
    """Print debug messages to stderr if debug mode is enabled."""
    if args.debug:
        print(message, file=sys.stderr)

def is_tty():
    """Check if the output is a TTY."""
    return sys.stdout.isatty()

def query_victorialogs(server, params, auth):
    """Send a query to VictoriaLogs."""
    url = f"https://{server}/select/logsql/query"
    print_debug(f"Debug: Sending request to URL: {url}")
    response = requests.post(url, auth=auth, data=params, stream=True)
    print_debug(f"Debug: Response status code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.reason}", file=sys.stderr)
        sys.exit(1)
    return response

def process_response(response, pretty):
    """Process the response from VictoriaLogs."""
    last_stream = None
    jq_process = None

    if pretty:
        jq_process = subprocess.Popen(['jq', '.'], stdin=subprocess.PIPE, text=True)

    try:
        for line in response.iter_lines():
            if not line:
                print_debug("Debug: Received an empty line")
                continue

            log_entry = line.decode("utf-8")
            print_debug(f"Debug: Received log entry: {log_entry}")

            try:
                log_json = json.loads(log_entry)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {log_entry}", file=sys.stderr)
                continue

            if pretty:
                jq_process.stdin.write(json.dumps(log_json) + "\n")
            else:
                print_log_entry(log_json, last_stream)

            sys.stdout.flush()  # Ensure output is flushed immediately

        if pretty:
            jq_process.stdin.close()
            jq_process.wait()

    except BrokenPipeError:
        handle_broken_pipe(None, None)
    except Exception as e:
        print(f"Unhandled exception: {e}", file=sys.stderr)
        if pretty and jq_process:
            jq_process.stdin.close()
            jq_process.wait()
        sys.exit(1)

def print_log_entry(log_json, last_stream):
    """Print a log entry based on the specified output format."""
    stream = log_json.get("_stream")
    timestamp = log_json.get("_time")
    msg = log_json.get("_msg")

    if args.text:
        if stream != last_stream:
            print(f"_stream: {stream}")
            last_stream = stream

        if args.timestamps:
            print(f"[{timestamp}] {msg}")
        else:
            print(msg)
    else:
        print(json.dumps(log_json))

def get_config_value(arg_value, env_var, prompt):
    """Retrieve configuration value with fallback from cmdline to env."""
    if arg_value:
        return arg_value
    value = os.getenv(env_var)
    if value:
        return value
    print(f"{prompt} (or set {env_var} environment variable): ", end='', file=sys.stderr)
    return input() if env_var != 'VICTORIALOGS_PASSWORD' else getpass()

def get_config(args):
    """Retrieve VictoriaLogs configuration."""
    server = get_config_value(args.server, "VICTORIALOGS_SERVER", "Enter VictoraLogs server")
    username = get_config_value(None, "VICTORIALOGS_USER", "Enter VictoraLogs username")
    password = get_config_value(None, "VICTORIALOGS_PASSWORD", "Enter VictoraLogs password")
    return username, password, server

# Argument parser setup
parser = argparse.ArgumentParser(
    description="Query VictoraLogs and format the output.",
    formatter_class=argparse.RawTextHelpFormatter,
    epilog="""
You can also set the following environment variables:
  VICTORIALOGS_SERVER    - The server to query
  VICTORIALOGS_USER      - Your VictoraLogs username
  VICTORIALOGS_PASSWORD  - Your VictoraLogs password
"""
)
parser.add_argument("--server", help="The server to query")
parser.add_argument("--limit", type=int, help="Limit the number of results")
parser.add_argument("--start", help="Start time for the query (e.g., 1h, 30m)")
parser.add_argument("--end", help="End time for the query (e.g., 5m)")
parser.add_argument("-d", "--timeout", help="Timeout for the query (e.g., 5s)")
parser.add_argument("--text", action="store_true", help="Display formatted output")
parser.add_argument("-t", "--timestamps", action="store_true", help="Display timestamps")
parser.add_argument("--debug", action="store_true", help="Print debug output to stderr")
parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
parser.add_argument("query", nargs=argparse.REMAINDER, help="The LogsQL query string to pass")

args = parser.parse_args()

# Get configuration details
username, password, server = get_config(args)

# Authentication details
auth = (username, password)

# Build the query parameters
query = " ".join(args.query).strip()
params = {"query": query}
if args.limit:
    params["limit"] = args.limit
if args.start:
    params["start"] = args.start
if args.end:
    params["end"] = args.end
if args.timeout:
    params["timeout"] = args.timeout

print_debug("Debug: Query parameters being sent:")
print_debug(params)

# Query VictoriaLogs and process the response
response = query_victorialogs(server, params, auth)
process_response(response, args.pretty)
