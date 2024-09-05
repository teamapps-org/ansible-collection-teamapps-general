# Loki Promtail Collector

Read Logs and send them to a loki server.

## Usage Example

~~~yaml
- name: Promtail Play
  hosts:
    - gitlab
  vars:
    promtail_loki_server: "loki.example.com"
    promtail_loki_username: promtail-to-loki
    promtail_loki_password: foo
    promtail_deploy_mode: binary
    promtail_scrape_configs:
      - job_name: gitlab
        static_configs:
          - targets:
              - localhost
            labels:
              category: 'serverlogs'
              service: 'gitlab'
              job: gitlab-logs
              __path__: /var/log/gitlab/*/*.log
  roles:
    - role: teamapps.general.promtail
      tags:
        - promtail
~~~

## Example 2: Promtail in docker to collect docker logs and send to VictoriaLogs

Separate Promtail instance deployed with docker compose, collecting system and docker container logs and sending them to [VictoriamLogs](https://docs.victoriametrics.com/victorialogs/)

~~~yaml
- name: Promtail VictoriaLogs Play
  hosts:
    - dockerhosts
  roles:
    - role: teamapps.general.promtail
      vars:
        promtail_path: '/container/promtail-victorialogs'
        promtail_loki_url: https://victorialogs.example.com/insert/loki/api/v1/push?_stream_fields=instance,job,host,category,service,container_name,compose_project,compose_service,systemd_unit,filename
        promtail_loki_username: promtail-to-victorialogs
        promtail_loki_password: '{{ promtail_victorialogs_password }}'
        promtail_deploy_mode: docker
        promtail_scrape_docker_enabled: true
      tags:
        - promtail
~~~
