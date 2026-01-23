# Webproxy

Role for Webproxy based on https://github.com/nginx-proxy with three separate containers:

- nginx
- docker-gen
- letsencrypt (acme-companion)

## Documentation

- nginx-proxy project: https://github.com/nginx-proxy/nginx-proxy
- nginx-proxy docs: https://github.com/nginx-proxy/nginx-proxy/tree/main/docs
- docker-gen: https://hub.docker.com/r/nginxproxy/docker-gen
- acme-companion: https://github.com/nginx-proxy/acme-companion (docs: https://github.com/nginx-proxy/acme-companion/tree/main/docs)

## Requirements

- Docker

## Role Variables

See `defaults/main.yml`.

## OpenTelemetry tracing

- Set `webproxy_otel_tracing_enabled: true` to render OTEL configs and start the collector sidecar.
- Defaults mirror the Hetzner LB implementation (`webproxy_otel_service_name`, `webproxy_otel_stack_name`, `webproxy_environment_name`, OTLP HTTP endpoint/auth headers, spanmetrics namespace, VictoriaMetrics remote write credentials).
- Use an image that contains the OTEL module (e.g. `webproxy_nginx_image: docker.angie.software/angie:{{ angie_version }}`) and set `webproxy_webserver` (`nginx` default, `angie` supported).

**Defaults (Ansible variables in `defaults/main.yml` and `webproxy-otel.conf.j2`):**

- `webproxy_otel_trace: true` → emits `otel_trace on` globally when OTEL is enabled.
- `webproxy_otel_span_name: "webproxy:default"` → global span name fallback.
- `webproxy_otel_trace_context: propagate` → global trace context mode.

**Per-service (container) overrides via env vars:**

- `WEBPROXY_OTEL_TRACE` → `true` / `false` / unset (inherits global). Use boolean-friendly values (`true|false|1|0|yes|no`); `on/off` are not valid for `parseBool`.
- `WEBPROXY_OTEL_SPAN_NAME` → overrides span name for that vhost (falls back to upstream name if unset).
- `WEBPROXY_OTEL_TRACE_CONTEXT` → overrides trace context for that vhost.

These env vars are read from the upstream service containers (not docker-gen) and applied at server level when `/etc/angie/http.d/conf.d/otel.conf` is present. Compose uses YAML 1.2, so unquoted `off` is treated as a string—keep to `true`/`false` to avoid template errors. If none are set, the global defaults above apply.

### Example (Angie with OTEL enabled)

```yaml
webproxy_webserver: angie
webproxy_nginx_image: "docker.angie.software/angie:{{ angie_version }}"
webproxy_nginx_otel_module_path: modules/ngx_otel_module.so

webproxy_otel_tracing_enabled: true
webproxy_otel_service_name: "nginx"
webproxy_otel_stack_name: "webproxy-{{ ansible_facts.hostname }}"
webproxy_environment_name: "prod"

# Traces backend (basic auth)
webproxy_otel_tracing_http_endpoint: "https://traces-prod.example.com/insert/opentelemetry"
webproxy_otel_tracing_http_user: "otel-user"
webproxy_otel_tracing_http_password: "otel-pass"
webproxy_otel_tracing_http_headers:
  X-API-Key: "abcd1234"

# Metrics backend (VictoriaMetrics)
webproxy_victoriametrics_remotewrite_url: "https://vm-prod.example.com/api/v1/write"
webproxy_victoriametrics_remotewrite_username: "vm-user"
webproxy_victoriametrics_remotewrite_password: "vm-pass"

# Optional: custom namespace for spanmetrics
webproxy_otel_spanmetrics_namespace: "otel"
```

## Example Playbook

With collection referenced in play:

```yaml
- hosts: localhost
  collections:
    - teamapps.general
  roles:
    - role: webproxy
```

With fully qualified role name:

```yaml
- hosts: localhost
  roles:
    - role: teamapps.general.webproxy
```

## License

Apache 2.0
