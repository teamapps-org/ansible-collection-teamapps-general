# Victoriametrics

Configure [Victoriametrics](https://victoriametrics.com/), Open Source Prometheus-compatible timeseries database

This role installs victoriametrics using docker-compose. To be used with `teamapps.general.webproxy`

Standalone  or together with `teamapps.general.vmagent`, this is a complete replacement for `teamapps.general.prometheus`

This role uses an additional nginx proxy to manage access to different api endpoints (write/read/admin)

## Restricted access with vmauth

Set `victoriametrics_vmauth_users` to expose an additional entrypoint at `victoriametrics_vmauth_domain`, which defaults to `vmauth.{{ victoriametrics_domain }}`. The existing nginx auth proxy remains unchanged.

`victoriametrics_vmauth_users` is rendered directly into the vmauth auth config. Every user password must be a `%{ENV_VAR}` reference with one matching key in the `victoriametrics_vmauth_passwords` mapping. Store password values with Ansible Vault; the role writes them to `.vmauth.env` with mode `0600` and `no_log: true`.

~~~yaml
victoriametrics_vmauth_domain: vmauth.metrics.example.com
victoriametrics_vmauth_users:
  - name: application-metrics-reader
    username: application-metrics-reader
    password: '%{APPLICATION_METRICS_READER_PASSWORD}'
    url_map:
      - src_paths:
          - /api/v1/query.*
        url_prefix: http://victoriametrics:8428/
victoriametrics_vmauth_passwords:
  APPLICATION_METRICS_READER_PASSWORD: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    ...
~~~

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
victoriametrics_domain: 'metrics.{{ ansible_facts.fqdn }}'

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
          group: test
        targets:
          - https://test.example.com

      - labels:
          environment: production
          group: website
        targets:
          - https://example.com/home.html

~~~

## Testing the alerting rules

`files/rules/tests/` holds `vmalert-tool` unit tests for the shipped rule files.
Run them with the `vmalert-tool` binary from the VictoriaMetrics `vmutils`
release archive, pinned to the vmalert version you deploy:

~~~bash
VM_VERSION=v1.147.0
curl -sSL -o /tmp/vmutils.tgz \
  "https://github.com/VictoriaMetrics/VictoriaMetrics/releases/download/${VM_VERSION}/vmutils-linux-amd64-${VM_VERSION}.tar.gz"
tar xzf /tmp/vmutils.tgz -C /tmp vmalert-tool-prod
cd roles/victoriametrics/files/rules/tests
/tmp/vmalert-tool-prod unittest --files='*.test.yml'
~~~

Run this in CI when changing a rule expression. A staleness or absence rule can
keep passing a syntax check while it silently stops firing, and the unit tests
pin the firing behaviour instead.

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

## Search Cache Timestamp Offset

`victoriametrics_search_cache_timestamp_offset` configures VictoriaMetrics'
`-search.cacheTimestampOffset` setting. It defines how far behind the current
time samples may be while still being considered safe for rollup result cache
reuse.

Increase this value when queried metrics are produced less frequently than the
default `5m`, for example by `vmalert` rule groups with `interval: 10m`. Without
enough offset, VictoriaMetrics can log `resetting rollup result cache` warnings
for valid but infrequently updated series such as `ALERTS`.

## Useful Prometheus Resources

PromQL for Beginners and Humans:  https://valyala.medium.com/promql-tutorial-for-beginners-9ab455142085

Inspiration for Alerting Rules: https://awesome-prometheus-alerts.grep.to/rules.html

## Web User Interface

Victoriametrics also provides Web User Interfaces. The following endpoints are exposed. These endpoints are protected by htpasswd_admin

* VMUI <https://victoriametrics_domain/vmui>
* vmalert <https://victoriametrics_domain/vmalert/>
* vmagent <https://victoriametrics_domain/vmagent/>

## OAuth2 login with oauth2_proxy

Deploy oauth2_proxy for the victoriametrics_domain


~~~yaml
- name: Oauth2 Proxy for Victoriametrics
  hosts:
    - metrics-server.example.com
  vars:
    victoriametrics_oauth2_proxy_integration: true
    # other victoriametrics_vars

    oauth2_proxy_instances:
      - domain: '{{ victoriametrics_domain }}'
        htpasswd: '{{ victoriametrics_htpasswd_admin }}'
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
        - victoriametrics
    - role: teamapps.general.victoriametrics
      tags:
        - metrics
        - victoriametrics
~~~
