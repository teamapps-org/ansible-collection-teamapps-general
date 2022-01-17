# Node Exporter

Node Exporter and Victoriametrics vmagent integration

## Dependencies

- role [`cloudalchemy.node_exporter`](https://github.com/cloudalchemy/ansible-node-exporter) from ansible galaxy
- role `teamapps.general.vmagent` (optional)

## Usage Example

`group_vars/all.yml`

~~~yaml
## node_exporter vars
manage_node_exporter: '{{ ansible_virtualization_role in [ "host", "NA" ] }}' # only on physical servers
node_exporter_version: 1.3.1 # or latest
node_exporter_web_listen_address: "127.0.0.9:9100"
node_exporter_web_telemetry_path: "/metrics"

node_exporter_textfile_dir: "/var/lib/node_exporter"

node_exporter_enabled_collectors:
  - systemd:
      unit-include: "\\.service$"
  #     unit-exclude: ^(nginx)\.service$
  - textfile:
      directory: "{{ node_exporter_textfile_dir }}"
  - filesystem:
      mount-points-exclude: "^/(sys|proc|dev)($|/)"
      fs-types-exclude: "^(sysfs|procfs|autofs|overlay|nsfs|nfs)$"
  - netdev:
      device-exclude: "^(docker[0-9]|br-.{12}|veth.{7})$"
  - netclass:
      ignored-devices: "^(docker[0-9]|br-.{12}|veth.{7})$"

node_exporter_download_dir: '{{ local_cache_dir }}'
~~~

playbook:

~~~yaml
- name: Victoriametrics vmagent Play
  hosts:
    - production
  roles:
    - role: teamapps.general.victoria_vmagent
      tags:
        - metrics
        - vmagent

- name: Node Exporter Monitoring Play
  hosts: all:!nodefault
  roles:
    - role: teamapps.general.node_exporter
      tags:
        - node_exporter
        - node
      when: manage_node_exporter | default(False)

- name: nvme metrics play
  hosts: all:!nodefault
  roles:
    - role: teamapps.general.nvme_metrics
      tags: nvme
      when: manage_node_exporter | default(False)
~~~
