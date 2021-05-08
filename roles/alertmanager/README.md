# Alertmanager Role

Alertmanager is used by prometheus, victoriametrics and loki logserver as distributor for alerts.

This role installs alertmanager using docker-compose. To be used together with `teamapps.general.webproxy`

## Usage Example

`host_vars/alert1.example.com.yml`:

~~~yaml
# please note the {% raw %}, {% endraw %} directives, for preventing j2 from parsing the Go Template {{ variables }}
alertmanager_receivers:
  - name: slack-operations-alerts
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/asdf/asdf/asdf'
        send_resolved: true
        title: '{% raw %} {{ if eq .Status "firing" }}:fire:{{ else }}:ok:{{ end }}[{{ .Status | toUpper }}] {{ .CommonAnnotations.summary }} {% endraw %}'
        text: >
          {% raw %}
          {{ range .Alerts }}
            {{ if .Labels.host }}*Host*: `{{ .Labels.host }}` {{ end }}
            *Alert*: {{ .Annotations.description }}
            {{ if .Labels.container_name }}*Container*: `{{ .Labels.container_name }}` {{ end }}
            {{ if .Annotations.dashboard }}*Dashboard*: {{ .Annotations.dashboard }} {{ end }}
          {{ end }}
          {% endraw %}

alertmanager_route:
  receiver: slack-operations-alerts # default receiver
  routes: # custom routers based on tag
    - receiver: slack-operations-alerts
      match_re:
        team: ops|operations

# basic auth for alertmanager access
alertmanager_htpasswd: |
  example-to-alertmanager:$2y$05$9M9lv1OtK2sJPTasRDvStevjkTdUCIZROyXTp.YWPF5TP6H1zPJQ2

# white list hosts that do not require basic auth
alertmanager_allowed_hosts:
  - loki1.example.com


~~~

Playbook:

~~~yaml
- name: Alertmanager Play
  hosts: alert1.example.com
  roles:
    # - role: teamapps.general.webproxy
    - role: teamapps.general.alertmanager
      tags:
        - alertmanager
~~~
