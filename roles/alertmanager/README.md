# Alertmanager Role

Alertmanager is used by prometheus, victoriametrics and loki logserver as distributor for alerts.

This role installs alertmanager using docker compose. To be used together with `teamapps.general.webproxy`

## Usage Example

`host_vars/alert1.example.com.yml`:

~~~yaml
# basic auth for alertmanager access
alertmanager_htpasswd: |
  example-to-alertmanager:$2y$05$9M9lv1OtK2sJPTasRDvStevjkTdUCIZROyXTp.YWPF5TP6H1zPJQ2

# white list hosts that do not require basic auth
alertmanager_allowed_hosts:
  - loki1.example.com

## Alertmanager config
# https://www.prometheus.io/docs/alerting/latest/configuration/

alertmanager_global:
  resolve_timeout: '5m'
  slack_api_url: 'https://hooks.slack.com/services/foo'

# please note the {% raw %}, {% endraw %} directives, for preventing j2 from parsing the Go Template {{ variables }}
alertmanager_receivers:
  - name: slack-alerts # Using the templates included in this role by default
    slack_configs:
      - channel: '#monitoring'
        title: '{% raw %}{{ template "common.status.slack" . }} {{ template "common.title.slack" . }}{% endraw %}'
        text: >
          {% raw %}
          {{ template "common.text.slack" . }}
          {% endraw %}

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

  - name: telegram-alert
    webhook_configs:
      - url: http://telegram-bot:9087/alert/-123456789
        send_resolved: True
        max_alerts: 10

alertmanager_route:
  receiver: slack-alerts # default receiver
  routes: # custom routers based on tag
    - receiver: telegram-alert
      matchers:
        - label="critical"
      continue: True
    - receiver: slack-operations-alerts
      matchers:
        - team=~"ops|operations"

alertmanager_telegram_enabled: True
alertmanager_telegram_token: 1234567890:AABCCDEs123_bXYZ123xYZ

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

## Telegram Bot

Setup instructions:

* Go to BotFather, https://t.me/botfather
* create new bot `/newbot`
* Copy Token to `alertmanager_telegram_token`
* Configure and start the bot container (apply the role)
* Add Bot to your group or open direct conversation with the bot.
* write `/help` in the group and the Bot will respond with the Chat ID. For Groups, the '-' is part of the ID.
* use ID to create receiver like in the example above.

## Test Slack Alert Templates

https://juliusv.com/promslack/
