# Nexus

Sonatype Nexus 3 OSS. Service-Path: {{ nexus_domain }}

Using Docker image [sonatype/nexus3](https://hub.docker.com/r/sonatype/nexus3/tags)

Default user is `admin` and the uniquely generated password can be found in the admin.password file inside the volume (`/container/nexus/data/admin.password`).

It can take some time (2-3 minutes) for the service to launch in a new container. You can tail the log to determine once Nexus is ready:

## Requirements

Role [webproxy](../webproxy/README.md) / Evertramos reverse proxy <https://github.com/evertramos/docker-compose-letsencrypt-nginx-proxy-companion>

## Role Variables

See [defaults/main.yml](defaults/main.yml)

## Usage Example

~~~yaml
- name: Nexus Play
  hosts:
    - nexus1.example.com
  roles:
    - role: teamapps.general.nexus
      tags:
        - nexus
~~~
