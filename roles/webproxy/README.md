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
- Use an nginx image that contains the OTEL module, for example `webproxy_nginx_image: nginx:alpine-otel`.
- For per-vhost nginx overrides, place a file in `data/vhost.d/<hostname>`. The generated config includes it inside the matching `server` block, so you can add OTEL directives there when needed.

**Defaults (Ansible variables in `defaults/main.yml` and `webproxy-otel.conf.j2`):**

- `webproxy_otel_trace: true` → emits `otel_trace on` globally when OTEL is enabled.
- `webproxy_otel_span_name: "webproxy:default"` → global span name fallback.
- `webproxy_otel_trace_context: propagate` → global trace context mode.

### Example (nginx with OTEL enabled)

```yaml
webproxy_nginx_image: "nginx:alpine-otel"
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

### Optional per-vhost override

Create `data/vhost.d/example.org` with directives that should apply only to that vhost. If a container sets multiple domains in `VIRTUAL_HOST`, add the same override file for each domain.

```nginx
otel_trace on;
otel_span_name "webproxy:example";
otel_trace_context propagate;
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
