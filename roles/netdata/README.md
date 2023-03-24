# Netdata

Netdata is installed and started on host to have a complete view of the system.

netdata can be used as standalone monitoring tool on a server, but also as a metrics collector. Netdata has a prometheus api, that can be scraped by prometheus or victoriametrics' vmagent. See their respective roles.

## Docker Webproxy integration

The docker-compose.yml file is used to forward requests from the docker network (webproxy) to netdata listening on localhost:19999.

## Usage Example

~~~yaml
- name: Netdata Monitoring Play
  hosts: all
  roles:
    - role: teamapps.general.netdata
~~~

`group_vars/dockerhosts.yml`

~~~yaml
netdata_docker_integration: True
~~~

## Netdata Resource usage

<https://learn.netdata.cloud/docs/deployment-in-production/metric-retention---database/change-how-long-netdata-stores-metrics>

### Disk storage

<https://github.com/netdata/netdata/blob/master/docs/store/change-metrics-storage.md#calculate-the-system-resources-ram-disk-space-needed-to-store-metrics>

~82.4M / 1000 metrics for a full day of per second retention.
a server has 3000-6000 metrics.
get the number of metrics (dimensions): `curl -s 'http://localhost:19999/api/v1/allmetrics?format=prometheus' | wc -l`

for 6000 metrics and ~1 day retention: 82.4M*6 = 495 M

* tier 0: 1 point every second, ~82.4 MiB for 1000 metrics for a full day
* tier 1: 1 point every minute, 4 bytes per point per point ~ 5.5 MiB per 1000 metrics per DAY.
* tier 2: 1 point every hour, 4 bytes per point, ~ 0.64 MiB per 1000 metrics per WEEK.

### memory usage

Memory usage depends on the amount of currently collected metrics.

* <https://github.com/netdata/netdata/tree/master/database/engine#memory-requirements>
* <https://learn.netdata.cloud/docs/deployment-in-production/metric-retention---database/change-how-long-netdata-stores-metrics#memory-for-concurrently-collected-metrics>

The quick rule of thumb, for a high level estimation is

~~~bash
DBENGINE memory in MiB = METRICS x (TIERS - 1) x 8 / 1024 MiB
Total Netdata memory in MiB = Metric ephemerality factor x DBENGINE memory in MiB + "dbengine page cache size MB" from netdata.conf
~~~

The ephemerality factor is usually between 3 or 4 and depends on how frequently the identifiers of the collected metrics change, increasing their cardinality.

`dbengine page cache size MB = 128`, ephemerality factor 2, 6000 Metrics:

`2x(6000×2×8/1024)+128` = 2 x 93.75 MiB + 128 MiB = 315.5
