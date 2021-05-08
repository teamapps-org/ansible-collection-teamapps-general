# Netdata

Netdata is installed and started on host to have a complete view of the system.

netdata can be used as standalone monitoring tool on a server, but also as a metrics collector. Netdata has a prometheus api, that can be scraped by prometheus or victoriametrics' vmagent. See their respective roles.

## Docker Webproxy integration

The docker-compose.yml file is used to forward requests from the docker network (webproxy) to netdata listening on localhost:19999.

## Usage Example

~~~yaml
- name: Netdata Monitoring Play
  hosts: all
  roles:
    - role: teamapps.general.netdata
~~~

`group_vars/dockerhosts.yml`

~~~yaml
netdata_docker_integration: True
~~~
