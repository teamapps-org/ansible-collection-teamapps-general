# Grafana Role

Install Grafana using Docker compose

## Provisioning

This role allows automatic provisioning of datasources, plugins and dashboards

### Datasources

~~~yaml
# Install Plugins
grafana_plugins:
  - camptocamp-prometheus-alertmanager-datasource

# Provisioned datasources can (only) be deleted with this list
grafana_datasources_delete:
  - name: loki.example.com

# Provision Datasources
# https://grafana.com/docs/grafana/latest/administration/provisioning/#data-sources
grafana_datasources:
  - name: prom:metrics.example.com
    type: prometheus
    access: proxy
    url: https://metrics.example.com
    basicAuth: true
    basicAuthUser: 'grafana'
    secureJsonData:
      basicAuthPassword: '{{ grafana_metrics_password }}'
    jsonData:
      httpMethod: POST

  - name: loki:logs.example.com
    type: loki
    access: proxy
    url: https://logs.example.com
    basicAuth: true
    basicAuthUser: 'grafana'
    secureJsonData:
      basicAuthPassword: '{{ grafana_loki_password }}'
    jsonData:
      maxLines: 1000
  - name: promloki:logs.example.com
    type: prometheus
    access: proxy
    url: https://logs.example.com/loki
    basicAuth: true
    basicAuthUser: 'grafana'
    secureJsonData:
      basicAuthPassword: '{{ grafana_loki_password }}'
    jsonData:
      httpMethod: POST

  - name: alertmanager.example.com
    type: camptocamp-prometheus-alertmanager-datasource
    access: proxy
    url: https://alertmanager.example.com
    basicAuth: true
    basicAuthUser: 'grafana'
    secureJsonData:
      basicAuthPassword: '{{ grafana_alertmanager_password }}'
    jsonData:
      severity_critical: critical
      severity_high: high
      severity_info: info
      severity_warning: warning
~~~

### Custom Dashboards

You can create a wrapper role where you can put your custom dashboards in `files/dashboards/somefolder/somedashboard.json` and add them to `grafana_custom_dashboards`.

The folder structure will be replicated in Grafana.

~~~yaml
- name: import grafana with additional dashboards
  import_role:
    name: grafana
  vars:
    grafana_custom_dashboards:
      - java/application-jvm-metrics.json
      - some/foo/bar/dashboard.json
  tags:
    - grafana
~~~

~~~rb
roles/grafana_custom/
├── files
│   └── dashboards
│       ├── java
│       │   └── application-jvm-metrics.json
│       └── some
│           └── foo
│               └── bar
│                   └── dashboard.json
└── tasks
    └── main.yml
~~~

## Grafana Image Renderer

This role installs grafana-image-renderer as docker container. The container exposes metrics on the configured port. (default `127.0.0.8:18081`)
There's [dashboard](https://grafana.com/grafana/dashboards/12203) published that explains the details of how to configure and monitor the rendering service using Prometheus as a data source.

You can monitor the metrics exposed by the service on that port. Example using vmagent role in this collection:

Add to host_vars:

~~~yaml
vmagent_scrape_configs_custom:
  - job_name: 'grafana-image-rendering-service'
    static_configs:
      - targets: ['127.0.0.8:18081']
        instance: '{{ grafana_domain }}'
~~~
