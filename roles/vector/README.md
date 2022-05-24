# Vector Role

Vector Log & Metric Collector Agent

## Usage

Usage Example for collecting docker logs and send them to loki.

There are more variables that allow any configuration. You can also deploy config files to `/etc/vector/*.toml` using your own ansible role and `notfify: reload vector`

~~~yaml
- name: Vector Log Collector for Dockerhosts Play
  hosts:
    - dockerhosts
  vars:
    vector_add_docker_group: Yes
    vector_docker_to_loki: Yes
    vector_loki_endpoint: https://loki.example.com:443
    vector_loki_username: loki-push-user
    vector_loki_password: password
  roles:
    - role: teamapps.general.vector
      tags:
        - vector
~~~

## Example query for docker logs in loki

~~~go
{category="dockerlogs", compose_service="foo"}
~~~

### extended LogQL example

~~~go
{host=~"$host",category="dockerlogs",compose_project=~"$project",compose_service=~"$service"} |~ "$search"
  # parse container_labels json, values are added as individual labels
  | line_format "{{ .container_labels }}" | json
  # format printed line
  | line_format "{{ .com_docker_compose_project }}/{{ .compose_service }}\t| {{ __line__ }}"
~~~
