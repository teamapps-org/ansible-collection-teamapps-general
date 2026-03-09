# Redirect Webserver

Simple webserver with nginx in docker that redirects all requests to your configured destination.

To be used together with the role `teamapps.general.webproxy`

For the domain and the addon domains, it will try to fetch and configure a letsencrypt certificate so redirects work properly if they are used with https://. Just configure your DNS Zone to point the domains to an IP of your host.

If you configure the main domain as the webproxy_default_host, then all requests to any domains that are not configured for another service behind the webproxy will be redirected, also if they are not listed in the addon_domains. Just configure their DNS. For those, https requests will have a certificate error. but currently the browser default is still http:// if the domain is typed without the protocol.

## Example usage

~~~yaml
# Ansible Playbook
- name: Web Domain Redirect Play
  vars:
    webserver_redirect_domain: www.example.com
    webserver_redirect_addon_domains:
      - example.net
      - foo.example.com
    webserver_redirect_destination: https://example.com
    webserver_redirect_locations:
      - location: ~ ^/(.+)$
        target: https://example.com/$1$is_args$args

    webserver_redirect_custom_domains:
      - domains:
          - example.net
          - www.example.net
        destination: https://special.example.com
        locations:
          - location: = /shop
            target: https://shop.example.com/

    # configure teamapps.general.webproxy to forward requests for unknown domains to this container.
    webproxy_default_host: www.example.com
  hosts:
    - web1.example.com
  roles:
    - role: teamapps.general.webproxy
    - role: teamapps.general.webserver_redirect
      tags: webserver_redirect
~~~

## Custom domain redirects

- `webserver_redirect_domain` and `webserver_redirect_addon_domains` keep the existing default redirect behavior.
- `webserver_redirect_custom_domains` adds host-specific redirect rules with one nginx `server` block per entry.
- Each entry may define multiple host names with `domains`.
- Custom domains must be unique and must not overlap with `webserver_redirect_domain` or `webserver_redirect_addon_domains`.
