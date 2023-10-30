# OAuth2 Proxy for Webproxy

Add single sign on protection to any service exposed using the webproxy (nginx-proxy).

This setup uses nginx auth_request to authenticate visitors, no additional proxy is added between webproxy and service.

oauth2_proxy Documentation: <https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/overview/>

Every oauth2_proxy instance should have its own Application Registration in GitLab.

## Register Application in Gitlab

[Gitlab Auth Provicer Documentation](https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/oauth_provider#gitlab-auth-provider)

* Go to Gitlab Group / Settings / Application,
* Add new Application
* Set Name
* Redirect URL needs to point to the service.example.com/oauth2/callback
* Select openid, profile, email
* Save Application.
* Copy Application ID and Secret to `client_id` and `client_secret`

## Configure oauth proxy for service

~~~yaml
- name: Oauth2 Proxy
  hosts:
    - web1.example.com
  vars:
    oauth2_proxy_instances:
      - domain: service.example.com
        htpasswd: '' # Optional, allow local login with basic auth credentials
        cookie_secret: RANDOM_STRING # generate!
        gitlab_url: https://git.example.com
        client_id: APPLICATION_ID # from Gitlab Application Registration
        client_secret: SECRET     # from Gitlab Application Registration
        whitelist_domains: # redirect restriction
          - '.example.com'
        email_domains: # restrict to users with these email domains
          - 'example.com'
        gitlab_groups: # restrict service to members of these gitlab groups
          - 'allowed_group'
        # additional config added to the bottom of oauth2-proxy.cfg
        additional_config: '' # optional
  roles:
    - role: teamapps.general.oauth2_proxy
      tags:
        - oauth2_proxy

- name: Example Web Service
  hosts:
    web1.example.com
  vars:
    webserver_domain: service.example.com
  roles:
    - role: teamapps.general.webproxy
    - role: teamapps.general.webserver
~~~

Be aware, that without defining `gitlab_groups` restriction, anyone who can login to your Gitlab instance can use your oauth2_proxy-protected service, independent of where the application is registered.
Registering an appliation in a GitLab group does not restrict the users!

for cookie_secret, create random string, see https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/overview#generating-a-cookie-secret

with python3: `python3 -c 'import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'`

## Shared oauth proxy example

If there are multiple similar services that should be protected by a single OAuth2 Prox Instance. E.g. a service that runs on every host. The services need to share a common parent domain, configured in cookie_domain.

In that case, the `oauth2_proxy_webproxy_sso_configs` variable can be used to configure the Webproxy without setting up a oauth2_proxy instance.

~~~yaml
## configure webproxy integration for auth_request to standalone or shared instance
oauth2_proxy_webproxy_sso_configs:
  - service_domain: netdata.ops1.example.com
    oauth2_proxy_host: netdata-sso.example.com
    cookie_name: _oauth2_netdata_sso # fixed cookie_name
~~~

For the shared, standalone oauth2_proxy instance, set `standalone: True` to directly configure the service, so that the domain is exposed by the webproxy.

~~~yaml
oauth2_proxy_instances:
  # configure a shared instance (exposed through webproxy)
  - domain: netdata-sso.example.com
    standalone: True
    htpasswd: '{{ admin_htpasswd | default("") }}'
    cookie_secret: 9R4DqdKnGjoi_u29EC8sEDA_uP-Luux7KdxVOxFPF14=
    cookie_name: _oauth2_netdata_sso # fixed cookie_name
    cookie_domain: .example.com # cookie_domain is on parent domain
    gitlab_url: https://git.example.com
    client_id:
    client_secret:
    whitelist_domains:
      - '.example.com'
    email_domains:
      - 'example.com'
    gitlab_groups:
      - 'netdata-sso_group'
~~~

## Sign in link

To logout and test login, one can use the /oauth2/sign_in endpoint with a redirect url

* `/oauth2/sign_out?rd=https%3A%2F%2Fservice.example.com%2F`
* `/oauth2/sign_in?rd=https%3A%2F%2Fservice.example.com`
