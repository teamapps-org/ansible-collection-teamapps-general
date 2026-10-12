# Webproxy

Deploy an nginx reverse proxy with automatic Let's Encrypt certificates. The role runs nginx, docker-gen and acme-companion as separate containers using Docker Compose v2. Each has a health check and rotating JSON logs. An optional OpenTelemetry collector exports traces and span metrics.

The role creates the external Docker network `webproxy` with subnet `172.28.0.0/16` and stores configuration, certificates, HTML assets, htpasswd files and ACME state under `webproxy_path`.

## Requirements

- Docker Engine and the Docker Compose v2 plugin on the managed host, compatible with the installed `community.docker.docker_compose_v2` module.
- The `community.docker` collection available to Ansible.
- Privileges to manage Docker, create networks and write root-owned configuration files.
- The shared variable `container_path`, used to create the parent container directory. Set it to `/container` for the default layout.
- Ports 80 and 443 available on the host. For public certificates, domain DNS and inbound HTTP/HTTPS access must reach the proxy.
- The subnet `172.28.0.0/16` available for the proxy network. It is currently fixed in the role.

## Example playbook

```yaml
- hosts: proxy_servers
  become: true
  vars:
    container_path: /container
  roles:
    - role: teamapps.general.webproxy
```

Run the proxy role before starting applications that reference its external network. Tasks carry the `webproxy` tag.

## Role variables

See [defaults/main.yml](defaults/main.yml) for all defaults.

### Containers and networking

| Variable | Default | Description |
| --- | --- | --- |
| `webproxy_path` | `/container/webproxy` | Compose project and persistent data directory. |
| `webproxy_nginx_image` | `nginx:alpine` | Frontend proxy image. |
| `webproxy_dockergen_image` | `nginxproxy/docker-gen:latest` | Docker event watcher and nginx config generator. |
| `webproxy_letsencrypt_image` | `nginxproxy/acme-companion:latest` | Certificate management image. |
| `webproxy_letsencrypt_default_email` | `{{ letsencrypt_email \| default('') }}` | Optional acme-companion account email. Empty values omit `DEFAULT_EMAIL`. Preserve existing values to reuse the same account directory. |
| `webproxy_docker_pull` | `{{ global_docker_pull \| default(False) }}` | Use Compose pull policy `always` when true, otherwise `policy`. |
| `webproxy_additional_networks` | `[]` | Extra external networks joined by nginx, docker-gen and acme-companion. |
| `webproxy_ignore_missing_network` | `true` | Ignore the role's failed network precheck. Compose still requires the networks to exist. |
| `webproxy_nginx_tmpl_file` | `nginx.tmpl` | Source file copied for docker-gen to generate server blocks. |

### Proxy configuration

| Variable | Default | Description |
| --- | --- | --- |
| `webproxy_nginx_worker_connections` | `8096` | Maximum connections per nginx worker. |
| `webproxy_ssl_policy` | `Mozilla-Intermediate-PQ` | `SSL_POLICY` passed to docker-gen. Selects the local post-quantum TLS policy; upstream `Mozilla-Intermediate` remains unchanged. |
| `webproxy_default_host` | `""` | Hostname used for unmatched requests. The target service must list it first in `VIRTUAL_HOST`. |
| `webproxy_access_log_off` | `false` | Disable access logging in the HTTP configuration and default location snippet. |
| `webproxy_proxy_read_timeout` | `60s` | Upstream read timeout. |
| `webproxy_proxy_connect_timeout` | `60s` | Upstream connection timeout. |
| `webproxy_proxy_send_timeout` | `60s` | Upstream send timeout. |
| `webproxy_nginx_custom_options` | `""` | Extra nginx directives in the HTTP context. |
| `webproxy_default_location_custom` | `""` | Extra directives in the default location snippet. |
| `webproxy_default_vhost_custom` | `""` | Extra directives in the default server snippet. |
| `webproxy_cookies_secure_only` | `false` | Rewrite upstream cookie paths with `HTTPOnly; Secure` flags using `proxy_cookie_path`. |
| `webproxy_security_txt` | `""` | Shared disclosure policy served at `/.well-known/security.txt` through the default server snippet. |

## Connecting applications

Attach each application to a network shared with nginx and set its proxy environment variables. Application ports need to be reachable inside Docker; publishing them on the host is unnecessary. Use the image's exposed port, Compose `expose`, or an explicit `VIRTUAL_PORT` to select the upstream port. Set `VIRTUAL_PORT` when automatic selection would be ambiguous.

This standalone Compose example serves one application under two domains:

```yaml
services:
  app:
    image: nginx:alpine
    expose:
      - "80"
    environment:
      VIRTUAL_HOST: app.example.com,www.app.example.com
      VIRTUAL_PORT: "80"
      LETSENCRYPT_HOST: app.example.com,www.app.example.com
    networks:
      - webproxy

networks:
  webproxy:
    external: true
    name: webproxy
```

- `VIRTUAL_HOST` selects the hostnames routed to the container.
- `VIRTUAL_PORT` selects the container port, not a published host port.
- `LETSENCRYPT_HOST` lists the certificate names. Each domain must resolve to the proxy.
- `LETSENCRYPT_EMAIL` optionally overrides the proxy's account email. Neither email setting is required for Let's Encrypt.

Applications can also join a private network for databases or other internal services. If an application uses another external network instead of `webproxy`, create that network first and add it to `webproxy_additional_networks`.

### Let's Encrypt account email

Let's Encrypt [ended expiration notification emails on June 4, 2025](https://letsencrypt.org/2025/01/22/ending-expiration-emails/) and [no longer stores ACME account contact information](https://community.letsencrypt.org/t/did-you-change-the-response-of-new-account/238188). New deployments can omit email configuration. Use certificate monitoring for expiry alerts.

Keep existing email settings when updating an installation: acme-companion uses `/etc/acme.sh/<email>` for an email-configured account and `/etc/acme.sh/default` without one. Removing an effective email value changes the local account directory and can trigger new account registration. The role preserves the `letsencrypt_email` fallback and per-application `LETSENCRYPT_EMAIL` overrides for continuity. Other ACME providers may still require email.

## Custom nginx configuration

The role renders these files under `webproxy_path`:

| File | Purpose |
| --- | --- |
| `data/nginx.conf` | Main nginx configuration and worker settings. |
| `data/conf.d/custom_options.conf` | HTTP-context defaults, timeouts, cookie rewrites and `webproxy_nginx_custom_options`. |
| `data/vhost.d/default` | Default server-context snippet, including the optional security.txt location and `webproxy_default_vhost_custom`. |
| `data/vhost.d/default_location` | Default location-context snippet, written when access logging is disabled or location customizations are nonempty. |
| `nginx.tmpl` | docker-gen template used to create nginx server configuration. |

Changes to the nginx configuration templates, including `data/vhost.d/default`, notify `webproxy_nginx_reload`. That handler sends HUP to nginx through Docker Compose. Changes to `nginx.tmpl` restart docker-gen.

### Per-host snippets

Manage `data/vhost.d/<hostname>` separately to configure a specific server, or `data/vhost.d/<hostname>_location` for its locations. With the bundled `nginx.tmpl`, host-specific snippets replace the corresponding default snippets. They do not automatically include the defaults. Add any shared directives or an explicit default-file include when needed.

For containers serving multiple domains, provide a snippet for each hostname that needs the override. Changes to files managed outside this role need their own reload notification. Newly added snippets may also require docker-gen to regenerate its includes.

The role does not remove an existing `default_location` file when both `webproxy_access_log_off` and `webproxy_default_location_custom` are reset to their defaults. Remove stale customizations explicitly when retiring them.

### Shared security.txt

```yaml
webproxy_security_txt: |
  Contact: mailto:security@example.com
  Expires: 2027-12-31T23:59:59Z
```

The role writes `data/html/security.txt` and adds an unauthenticated `/.well-known/security.txt` location to the default server snippet. Host-specific server snippets must include that configuration themselves. Clearing the variable removes the default location configuration but does not delete the previously written HTML file.

## OpenTelemetry tracing

Set `webproxy_otel_tracing_enabled: true` and use an nginx image containing the OTEL module, such as `nginx:alpine-otel`. The collector receives nginx traces over gRPC, exports traces over OTLP HTTP and derives span metrics for Prometheus remote write.

| Variable | Default | Description |
| --- | --- | --- |
| `webproxy_otel_tracing_enabled` | `false` | Deploy OTEL configuration and the collector sidecar. |
| `webproxy_nginx_otel_module_path` | `modules/ngx_otel_module.so` | nginx module to load when tracing is enabled. |
| `webproxy_otel_service_name` | `nginx` | Service name attached to nginx traces. |
| `webproxy_otel_stack_name` | `webproxy-{{ ansible_facts.hostname }}` | Deployment stack and project span attributes. |
| `webproxy_environment_name` | `default` | Environment attribute. |
| `webproxy_otel_trace` | `true` | Enable trace emission in nginx. |
| `webproxy_otel_span_name` | `webproxy:default` | Default span name. |
| `webproxy_otel_trace_context` | `propagate` | nginx trace context mode. |
| `webproxy_otel_collector_version` | `latest` | OpenTelemetry Collector Contrib image tag. |
| `webproxy_otel_tracing_http_endpoint` | `https://traces.example.com/insert/opentelemetry` | Trace endpoint base URL; the template appends `/v1/traces`. |
| `webproxy_otel_tracing_http_headers` | `{}` | Additional HTTP headers for trace export. |
| `webproxy_otel_tracing_http_user` | unset | Trace exporter basic-auth username. |
| `webproxy_otel_tracing_http_password` | unset | Trace exporter basic-auth password. |
| `webproxy_otel_spanmetrics_namespace` | `otel` | Namespace for generated span metrics. |
| `webproxy_victoriametrics_remotewrite_url` | unset | Full remote-write endpoint for span metrics. Required when enabling the collector. |
| `webproxy_victoriametrics_remotewrite_username` | unset | Optional remote-write basic-auth username. Set together with the password. |
| `webproxy_victoriametrics_remotewrite_password` | unset | Optional remote-write basic-auth password. Set together with the username. |

The trace exporter sets a basic-auth header from the trace credentials. Metrics remote write uses the collector's `basicauth/remotewrite` extension when both remote-write credentials are set. Leave both unset for an unauthenticated endpoint; supplying only one fails role validation.

The collector loads `otel-collector-config.yml` and a separate `otel-collector-secrets.yml` overlay. The secrets file contains remote-write credentials and all trace exporter headers; its template task uses `no_log: true`. Both files are owned by root, readable by group `10001`, have mode `0640`, and are mounted read-only. Changes to either file restart the collector, and both files are removed when tracing is disabled.

Main configuration diffs remain visible. When upgrading from inline credentials, run once without `--diff` to avoid exposing the old file's secrets. Keep credentials out of endpoint URLs and other non-secret settings, which remain visible in diffs.

```yaml
webproxy_nginx_image: nginx:alpine-otel
webproxy_otel_tracing_enabled: true
webproxy_environment_name: prod
webproxy_otel_tracing_http_endpoint: https://traces.example.com/insert/opentelemetry
webproxy_otel_tracing_http_user: "{{ vault_traces_user }}"
webproxy_otel_tracing_http_password: "{{ vault_traces_password }}"
webproxy_victoriametrics_remotewrite_url: https://metrics.example.com/api/v1/write
webproxy_victoriametrics_remotewrite_username: "{{ vault_metrics_user }}"
webproxy_victoriametrics_remotewrite_password: "{{ vault_metrics_password }}"
```

Define the referenced Vault variables in your inventory. Both endpoints must be reachable from the collector. For a Docker-internal metrics endpoint such as `http://victoriametrics:8428/api/v1/write`, attach the metrics service to the `webproxy` network, which is the collector's only network, and omit credentials if the endpoint does not require authentication.

To override tracing for a host, put directives such as these in `data/vhost.d/example.org`, alongside any required default server configuration:

```nginx
include /etc/nginx/vhost.d/default;
otel_trace on;
otel_span_name "webproxy:example";
otel_trace_context propagate;
```

## Upstream documentation

- [nginx-proxy](https://github.com/nginx-proxy/nginx-proxy)
- [nginx-proxy configuration](https://github.com/nginx-proxy/nginx-proxy/tree/main/docs)
- [docker-gen](https://hub.docker.com/r/nginxproxy/docker-gen)
- [acme-companion](https://github.com/nginx-proxy/acme-companion/tree/main/docs)

## License

Apache 2.0
