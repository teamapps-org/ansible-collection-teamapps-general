# Victoriametrics

Configure [Victoriametrics](https://victoriametrics.com/), Open Source Prometheus-compatible timeseries database

This role installs victoriametrics using docker-compose. To be used with `teamapps.general.webproxy`

Standalone  or together with `teamapps.general.victoria_vmagent`, this is a complete replacement for `teamapps.general.prometheus`

This role uses an additional nginx proxy to manage access to different api endpoints (write/read/admin)

## Usage Example

~~~yaml
- name: Victoriametrics Play
  hosts:
    - vic1.example.com
  roles:
    - role: teamapps.general.victoriametrics
      tags:
        - metrics
        - victoriametrics
~~~

Example `host_vars/vic1.example.com.yml`

~~~yaml
victoriametrics_version: latest
victoriametrics_domain: 'metrics.{{ ansible_fqdn }}'

victoriametrics_htpasswd_read: |
  grafana-read-vic:$2y$...
victoriametrics_htpasswd_write: |
  vmagent-vic-write:$2y$....
victoriametrics_htpasswd_admin: |
  hans:...

victoriametrics_alertmanager_address: alertmanager.example.com
victoriametrics_alertmanager_port: 443
victoriametrics_alertmanager_scheme: https
victoriametrics_alertmanager_url: https://alertmanager.example.com/
victoriametrics_alertmanager_user: vmalert-to-alertmanager
victoriametrics_alertmanager_password: password

victoriametrics_file_sd_config:
  - job: http_2xx
    name: production
    config:
      - labels:
          environment: testing
        targets:
          - https://test.example.com

      - labels:
          environment: production
        targets:
          - https://example.com/home.html

~~~

## Grafana Dashboards

The role includes self-monitoring rules that can link to grafana.

Import the following two dashboards. keep the ID!

* <https://grafana.com/grafana/dashboards/10229>
* <https://grafana.com/grafana/dashboards/12683>

configure the variables:

~~~yaml
victoriametrics_grafana_datasource_name: VictoriaMetrics
victoriametrics_vmalert_external_url: 'https://grafana.yourdomain.com'
~~~

## Useful Prometheus Resources

PromQL for Beginners and Humans:  https://valyala.medium.com/promql-tutorial-for-beginners-9ab455142085

Inspiration for Alerting Rules: https://awesome-prometheus-alerts.grep.to/rules.html
