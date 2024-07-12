# logsQL.py

`logsQL.py` is a script to query VictoriaLogs and format the output. It supports querying logs from a specified server, formatting the output with various options, and stream processing and limiting using unix command line tools.

## Official documentation

- VictoriaLogs <https://docs.victoriametrics.com/victorialogs/>
- LogsQL <https://docs.victoriametrics.com/victorialogs/logsql/>
- Commandline processing <https://docs.victoriametrics.com/victorialogs/querying/#command-line>

## Script Features

- Query VictoriaLogs using specified parameters.
- Limit the number of results.
- Specify the start and end times for the query.
- Display formatted output with timestamps.
- Pretty print JSON output.
- Supports environment variables for configuration.

## Requirements

- Python 3.x
- `requests` library

## Installation

1. Clone the repository or download the `logsQL.py` script.
2. Ensure you have Python 3.x installed.
3. Install the `requests` library if not already installed:

   ```sh
   pip install requests
   ```

## Usage

```sh
usage: logsQL.py [-h] [--server SERVER] [--limit LIMIT] [--start START] [--end END] [-d TIMEOUT] [--text] [-t] [--debug] [--pretty] ...

Query VictoriaLogs and format the output.

positional arguments:
  query                 The LogsQL query string to pass

options:
  -h, --help            show this help message and exit
  --server SERVER       The server to query
  --limit LIMIT         Limit the number of results
  --start START         Start time for the query (e.g., 1h, 30m)
  --end END             End time for the query (e.g., 5m)
  -d TIMEOUT, --timeout TIMEOUT
                        Timeout for the query (e.g., 5s)
  --text                Display formatted output
  -t, --timestamps      Display timestamps
  --debug               Print debug output to stderr
  --pretty              Pretty print JSON output

You can also set the following environment variables:
  VICTORIALOGS_SERVER    - The server to query
  VICTORIALOGS_USER      - Your VictoriaLogs username
  VICTORIALOGS_PASSWORD  - Your VictoriaLogs password
```

## Examples

### Example 1: Basic Query

Query VictoriaLogs with a basic query string:

```sh
./logsQL.py --server victorialogs.example.com 'service_name: my-service'
```

### Example 2: Using Environment Variables

Set environment variables for server, username, and password, and run the script:

```sh
export VICTORIALOGS_SERVER=victorialogs.example.com
export VICTORIALOGS_USER=myusername
export VICTORIALOGS_PASSWORD=mypassword

./logsQL.py 'service_name: my-service'
```

### Example 3: Pretty Print JSON Output

Query and pretty print the JSON output:

```sh
./logsQL.py --server victorialogs.example.com --pretty 'service_name: my-service'
```

### Example 4: Display Timestamps

Query and display formatted output with timestamps:

```sh
./logsQL.py --server victorialogs.example.com --text --timestamps 'service_name: my-service'
```

### Example 5: Debug Mode

Enable debug mode to print debug output to stderr:

```sh
./logsQL.py --server victorialogs.example.com --debug 'service_name: my-service'
```

### Example 6: Pipe for further processing using command line tools

Examples: <https://docs.victoriametrics.com/victorialogs/querying/#command-line>

Query VictoriaLogs and pipe the output to `head`:

```sh
./logsQL.py --server victorialogs.example.com 'service_name: my-service' | head -n 10
```

## Environment Variables

You can also set the following environment variables for configuration:

- `VICTORIALOGS_SERVER` - The server to query
- `VICTORIALOGS_USER` - Your VictoriaLogs username
- `VICTORIALOGS_PASSWORD` - Your VictoriaLogs password

These variables can be set in your shell profile or exported in your current session.

## Handling Broken Pipe Errors

The script gracefully handles broken pipe errors to ensure smooth termination when the output is interrupted, such as when piping the output to `head`:

```sh
./logsQL.py --server victorialogs.example.com 'service_name: my-service' | head -n 10
```

## Documentation

For more information on VictoriaLogs, visit the [official documentation](https://docs.victoriametrics.com/victorialogs).

For detailed information on the LogsQL query language syntax, refer to the [LogsQL documentation](https://docs.victoriametrics.com/victorialogs/logsql).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
