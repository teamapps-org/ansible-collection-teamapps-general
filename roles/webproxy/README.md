Webproxy
========

Role for Webproxy based on https://github.com/nginx-proxy with three separate containers

* nginx
* docker-gen
* letsencrypt (acme-companion)

Documentation
-------------

* nginx-proxy Project: https://github.com/nginx-proxy/nginx-proxy
* nginx-proxy docs section: https://github.com/nginx-proxy/nginx-proxy/tree/main/docs
* docker-gen https://hub.docker.com/r/nginxproxy/docker-gen
* acme-companion: https://github.com/nginx-proxy/acme-companion
* acme-companion docs section https://github.com/nginx-proxy/acme-companion/tree/main/docs

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
