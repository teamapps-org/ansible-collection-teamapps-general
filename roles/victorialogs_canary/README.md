# VictoriaLogs canary

Emit synthetic journal and container log lines and optionally probe a restricted
VictoriaLogs read endpoint. Use the companion integrations in
`teamapps.general.victorialogs` and `teamapps.general.victoriametrics` to record
delivery health and alert on missing, delayed, or incomplete signals.

The role emits one line per minute with a fixed wire format:

```text
VLCANARY src=<journal|docker> seq=<epoch-seconds>
```

The journal emitter uses a systemd timer. The optional container emitter runs a
small BusyBox container. Enable it when journal and container logs use separate
collector paths.

The optional read-path probe queries the public service endpoint every five
minutes. It covers DNS, TLS, HTTP authentication, and LogsQL, then writes these
metrics to the node exporter textfile directory:

- `victorialogs_canary_readpath_last_run_seconds`
- `victorialogs_canary_readpath_exit_code`

## Usage

```yaml
- name: deploy VictoriaLogs canaries
  hosts: log_shippers
  roles:
    - role: teamapps.general.victorialogs_canary
      vars:
        victorialogs_canary_domain: logs.example.com
```

Enable the container path on applicable hosts:

```yaml
victorialogs_canary_docker_enabled: true
victorialogs_canary_busybox_version: 1.37.0
```

Enable one external read probe per VictoriaLogs service domain:

```yaml
victorialogs_canary_readpath_enabled: true
victorialogs_canary_readpath_url: https://vmauth.logs.example.com
victorialogs_canary_readpath_username: vlcanary-readpath
victorialogs_canary_readpath_password: !vault |
  ...
```

The read credential should only permit the `/select/logsql/query` path used by the probe's GET request and should
enforce filters that restrict queries to exact canary messages. The
`teamapps.general.victorialogs` role can create this endpoint through its
`victorialogs_vmauth_users` and `victorialogs_vmauth_passwords` variables.

The role does not install node exporter or configure a metrics agent. The
caller must expose the textfile directory and send probe metrics to the
VictoriaMetrics instance that evaluates the canary alerts.

## Recording Rules

Enable recording rules on each VictoriaLogs service:

```yaml
victorialogs_canary_recording_rules_enabled: true
```

The `teamapps.general.victorialogs` role records:

- `log_canary_lag_seconds{domain,host,src}` every minute.
- `log_canary_missing_minutes{domain,host,src}` from settled, overlapping
  sequence windows every five minutes.
- `log_canary_duplicate_lines{domain,host,src}` from the same windows, counting
  total entries minus unique exact `seq` values per source.

The default stream selector is suitable for Promtail jobs named `journallogs`
and `docker`. Override `victorialogs_canary_stream_selector` when collectors use
different stream labels, and enforce the same selector in the restricted vmauth
route used by the read probe.

## Alerts

Enable alerts on the VictoriaMetrics instance that stores the recording series:

```yaml
victoriametrics_victorialogs_canary_alerts_enabled: true
victoriametrics_victorialogs_canary_domains:
  - logs.example.com
victoriametrics_victorialogs_canary_alert_labels:
  team: operations
  severity: warning
victoriametrics_victorialogs_canary_dashboard_url: https://grafana.example.com/d/logs
```

`teamapps.general.victoriametrics` discovers expected `(domain, host, src)`
series over seven days. It alerts on complete source disappearance, delivery
lag, missing sequence minutes, duplicate lines, failed read queries, and stopped
read probes. There is no static expected-host list.

`LogCanaryPartialLoss` and `LogCanaryDuplicates` fire on the first positive
settled sample. Short restart gaps and shutdown replays can therefore alert.
Duplicate alerts have severity `info` and should use non-paging notification
routing. Partial-loss alerts retain the configured severity, normally `warning`.
Duplicate lines collapse into one sequence-minute bucket for loss detection,
but the separate duplicate rule counts repeated exact sequences. Different
sequences emitted within the same minute do not count as duplicates.

Both rules inspect ten-minute windows every five minutes, delayed by five
minutes to allow delivery to settle. The alerts clear when a newer sample is
zero. The fifteen-minute `last_over_time` lookbehind keeps delayed recording
samples readable; it does not hold an alert after a newer zero arrives.
With healthy recording and delivery, allow up to about twenty minutes after
the final affected log timestamp for the window and evaluation schedule to
clear, plus alert evaluation and notification time. Silence the affected
`domain` and `host` during maintenance and include this recovery time.

Loss detection counts gaps between the first and last received sequence-minute
buckets in each window. Missing buckets at the window edges and outages with
no received lines are not counted by this rule. Complete outages are covered
by `LogCanaryDeliveryLag` and `LogCanaryMissing`. Duplicate detection requires
the repeated sequences to appear in the same window. A clock step backwards
or two emitters using the same source identity can also repeat a sequence.

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `victorialogs_canary_enabled` | `true` | Deploy the journal emitter. `false` removes every resource managed by this role. |
| `victorialogs_canary_stream_selector` | Promtail journal or Docker jobs | LogsQL stream selector used by the read probe and recording rules. |
| `victorialogs_canary_domain` | `''` | Service domain attached to read-path metrics. Required for the read probe. |
| `victorialogs_canary_docker_enabled` | `false` | Emit a second line through the container log path. |
| `victorialogs_canary_busybox_version` | `''` | BusyBox tag or digest. Required for the container emitter. |
| `victorialogs_canary_docker_path` | `/container/vlcanary` | Container emitter Compose directory. |
| `victorialogs_canary_readpath_enabled` | `false` | Run the external read-path probe. |
| `victorialogs_canary_readpath_url` | `''` | Public VictoriaLogs base URL. |
| `victorialogs_canary_readpath_username` | `''` | Restricted HTTP basic-auth username. |
| `victorialogs_canary_readpath_password` | `''` | Restricted HTTP basic-auth password. Store it with Ansible Vault. |
| `victorialogs_canary_textfile_dir` | node exporter default | Directory for probe metric files. |

## Tags

- `victorialogs_canary`: all emitter, probe, and companion rule tasks.
- `victorialogs_canary_docker`: container emitter lifecycle.
- `victorialogs_canary_readpath`: read probe lifecycle.
