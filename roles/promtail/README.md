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
