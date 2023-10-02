# Prometheus

Prometheus monitoring role.

NOTE: You can replace prometheus with [victoriametrics](../victoriametrics/README.md) (and vmagent).

## Usage Example

~~~yaml
- name: Prometheus Play
  hosts: prom1.example.com
  roles:
    - role: teamapps.general.prometheus
      tags: ['prometheus']
~~~

`host_vars/prom1.example.com.yml`

~~~yaml
prometheus_custom_file_sd_config:
  - job: http_2xx
    name: production
    config:
      - labels:
          environment: testing
          group: test
        targets:
          - https://test.example.com

      - labels:
          environment: production
          group: website
        targets:
          - https://example.com/home.html

prometheus_alertmanager_domain: 'alertmanager.example.com'
prometheus_alertmanager_user: prom-to-alertmanager
prometheus_alertmanager_password: password

# user in prometheus, for grafana to us it as datasource
prometheus_htpasswd: |
  grafana:$2y$0....
~~~

## Resources

PromQL for Beginners and Humans:  https://valyala.medium.com/promql-tutorial-for-beginners-9ab455142085

Inspiration for Alerting Rules: https://awesome-prometheus-alerts.grep.to/rules.html
