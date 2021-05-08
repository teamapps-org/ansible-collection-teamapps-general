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
    - role: loki
      tags:
        - logserver
        - loki
~~~

## Docker logging driver

UPDATE: recommend using [vector](https://vector.dev) to send logs instead of loki log driver. driver was unstable, locking up and difficult to upgrade.

There's a ansible role for installing and configuring [vector](../vector/README.md)

Install https://github.com/grafana/loki/blob/v1.6.0/docs/sources/clients/docker-driver/_index.md
docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions

Use/Configure https://github.com/grafana/loki/blob/v1.6.0/docs/sources/clients/docker-driver/configuration.md

~~~yaml
version: "3.7"

# custom element for reusable logging definition
# using yaml anchors https://anil.io/blog/symfony/yaml/using-variables-in-yaml-files/
x-logging:
    &default-logging
    driver: loki
    options:
      loki-url: "https://dockerlogs:<password>@loki.example.com/loki/api/v1/push"
      loki-retries: '10'
      loki-batch-size: '102400'
      loki-external-labels: 'container_name={{.Name}},category=dockerlogs'
    # driver: json-file

services:
  example:
    image: grafana/grafana
    logging: *default-logging
~~~

### Docker Default driver

~~~json
{
    "log-driver": "loki",
    "log-opts": {
        "loki-url": "https://logs-push-user:<password>@loki.example.com/loki/api/v1/push",
        "loki-external-labels": "container_name={{.Name}},category=dockerlogs",
        "loki-batch-size": "102400",
        "loki-retries": "10"
    }
}
~~~

After changing the log driver, all containers need to be recreated (down, up) not just restarted!

The default driver is only used when there is no specific logging configuration for a docker container or compose service.

#### Upgrade Loki Driver

~~~yaml
# Play
- name: update docker stuff
  serial: '{{ serial_hosts | default(5) }}'
  hosts:
    - dockerhosts
  tasks:
    - block:
        - name: disable docker loki plugin
          command: docker plugin disable loki -f

        - name: upgrade docker loki plugin
          command: docker plugin upgrade loki grafana/loki-docker-driver:latest --grant-all-permissions --skip-remote-check

        - name: re-enable docker loki plugin
          command: docker plugin enable loki

        - name: restart docker service
          systemd:
            name: docker
            state: restarted
      when:
        - docker_install_loki_driver | default (False)
~~~
