Webproxy
========

Role for Webproxy based on https://github.com/evertramos/docker-compose-letsencrypt-nginx-proxy-companion

Documentation
-------------

* nginx-proxy Project: https://github.com/nginx-proxy/nginx-proxy
* docker-gen https://hub.docker.com/r/nginxproxy/docker-gen
* acme-companion: https://github.com/nginx-proxy/acme-companion

Requirements
------------

--

Role Variables
--------------

See `defaults/main.yml`

Dependencies
------------

Docker

Example Playbook
----------------

With collection referenced in play

~~~yaml
- hosts: localhost
  collections:
    - teamapps.general
  roles:
    - role: webproxy
~~~

With fully qualified role name

~~~yaml
- hosts: localhost
  roles:
    - role: teamapps.general.webproxy
~~~

License
-------

Apache 2.0
