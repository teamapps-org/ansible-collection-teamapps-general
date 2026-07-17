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

### Restricted access with vmauth

Set `victorialogs_vmauth_users` to expose an additional entrypoint at `victorialogs_vmauth_domain`, which defaults to `vmauth.{{ victorialogs_domain }}`. The existing nginx auth proxy remains unchanged.

`victorialogs_vmauth_users` is rendered directly into the vmauth auth config. Every user password must be a `%{ENV_VAR}` reference with one matching key in the `victorialogs_vmauth_passwords` mapping. Store password values with Ansible Vault; the role writes them to `.vmauth.env` with mode `0600` and `no_log: true`.

~~~yaml
victorialogs_vmauth_domain: vmauth.vlogs.example.com
victorialogs_vmauth_users:
  - name: frontend-logs-viewer
    username: frontend-viewer
    password: '%{VMAUTH_FRONTEND_PASSWORD}'
    url_map:
      - src_paths:
          - /select/.*
        # Percent-encoded _stream:{service=frontend-logs}
        url_prefix: http://victorialogs:9428/?extra_stream_filters=_stream%3A%7Bservice%3Dfrontend-logs%7D
victorialogs_vmauth_passwords:
  VMAUTH_FRONTEND_PASSWORD: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    ...
~~~

Use `extra_stream_filters` for stream fields where possible. `extra_filters` can enforce a LogsQL filter on all subqueries in the same way. Do not add either parameter to `merge_query_args`, because the configured restriction must override client-supplied values.

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
