# Logserver with Loki

## References

* [Getting Started with Loki (Youtube)](https://www.youtube.com/watch?v=1obKa6UhlkY)
* [Docker Compose file starter](https://github.com/grafana/loki/tree/master/production)

## Usage Example

`host_vars/loki1.example.com.yml`:

~~~yaml
loki_domain: "loki.example.com"

# htpasswd -B -n username
loki_htpasswd: |
  hans:$2y$...
  grafana1:$2y$05$...

loki_htpasswd_push_only: |
  server-logs:$2y$0....
  logs-push-user:$2y$05$...

loki_alertmanager_url: "https://alertmanager.example.com"

loki_rules:
  - name: Matomo
    interval: 10m
    rules:
      - alert: MatomoArchiveError
        expr: |
          count_over_time({filename="/var/log/matomo-archive.log"} |= "ERROR"[20m]) > 0
        labels:
          team: ops
        annotations:
          description: "`ERROR` occured during matomo archive process"
          dashboard: '{% raw %}https://grafana.example.com/explore?orgId=1&left=%5B%22now-1h%22,%22now%22,%22Loki%22,%7B%22expr%22:%22%7Bhost%3D%5C%22website1%5C%22,%20filename%3D%5C%22%2Fvar%2Flog%2Fmatomo-archive.log%5C%22%7D%20%7C%3D%20%5C%22ERROR%5C%22%22%7D%5D{% endraw %}'

~~~

Playbook

~~~yaml
# Logserver Playbook

- name: Logserver with Loki Play
  hosts:
    - loki1.example.com
  roles:
    - role: teamapps.general.webproxy
    - role: teamapps.general.loki
      tags:
        - logserver
        - loki
~~~
