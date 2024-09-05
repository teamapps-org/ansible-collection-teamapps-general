# Victoria Logs

## Web User Interface

VictoriaLogs also provides Web User Interfaces. The following endpoints are exposed. These endpoints are protected by htpasswd_admin

* VMUI <https://victorialogs_domain/vmui>

## OAuth2 login with oauth2_proxy

Deploy oauth2_proxy for the victorialogs_domain


~~~yaml
- name: Oauth2 Proxy for VictoriaLogs
  hosts:
    - victorialogs-server.example.com
  vars:
    victorialogs_oauth2_proxy_integration: true
    # other victorialogs_vars

    oauth2_proxy_instances:
      - domain: '{{ victorialogs_domain }}'
        htpasswd: '{{ victorialogs_htpasswd_admin }}'
        webproxy_integration: false # don't deploy location to webproxy, as authentication is done in separate authproxy nginx
        cookie_secret:
        gitlab_url: https://git.example.com
        # Registerd in to operations group https://git.example.com/groups/operations/-/settings/applications
        client_id:
        client_secret:
        whitelist_domains:
          - '.example.com'
        email_domains:
          - 'example.com'
        gitlab_groups:
          - 'admin_group'
  roles:
    - role: teamapps.general.oauth2_proxy
      tags:
        - oauth2_proxy
        - metrics
        - victorialogs
    - role: teamapps.general.victorialogs
      tags:
        - metrics
        - victorialogs
~~~

## Querying VictoriaLogs

* Use VMUI at <https://victorialogs_domain/vmui>
* Set up Grafana victorialogs-datasource plugin
* Use curl for querying victorialogs. <https://docs.victoriametrics.com/victorialogs/querying/#command-line>
* [./files/logsQL.py](./files/logsQL.py) wrapper script, [README for logsQL.py](./files/README.md)

### Grafana VictoriaLogs Datasource

* VictoriaLogs datasource for Grafana <https://docs.victoriametrics.com/victorialogs/querying/#command-line>

Using ansible and [teamapps.general.grafana](./../grafana/README.md):

hostvars

~~~yaml
# grafana.ini content
grafana_config_ini: |
  [plugins]
  allow_loading_unsigned_plugins = victorialogs-datasource

# https://github.com/VictoriaMetrics/victorialogs-datasource/releases/
grafana_victorialogs_plugin_version: v0.2.4
grafana_plugins:
  - https://github.com/VictoriaMetrics/victorialogs-datasource/releases/download/{{ grafana_victorialogs_plugin_version }}/victorialogs-datasource-{{ grafana_victorialogs_plugin_version }}.zip;victorialogs-datasource


grafana_datasources:
  - name: VictoriaLogs
    type: victorialogs-datasource
    access: proxy
    url: https://victorialogs.example.com
    isDefault: false
    basicAuth: true
    basicAuthUser: 'grafana-victorialogs'
    secureJsonData:
      basicAuthPassword: '{{ grafana_victorialogs_password }}'
    jsonData:
      maxLines: 5000
~~~
