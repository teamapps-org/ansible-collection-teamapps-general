Webserver
=========

Webserver using nginx with optional php and sftp

Requirements
------------

--

Role Variables
--------------

see `defaults/main.yml`

Dependencies
------------

- webproxy

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

~~~yaml
- hosts: servers
  vars:
    webproxy_domain: example.com
    webproxy_php_enable: True
    webproxy_sftp_enable: True
    webproxy_sftp_port: 8822
  roles:
     - role: webproxy
~~~

License
-------

BSD

Author Information
------------------

Philipp Gassmann <phiphi@phiphi.ch>
