Webproxy
========

Role for Webproxy based on https://github.com/evertramos/docker-compose-letsencrypt-nginx-proxy-companion

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
