# NVMe metrics

Installs a simple python script to collect metrics of NVMe devices for monitoring nvme devices.

Installs cronjob that writes to a prom file for node_exporter textfile collector

## Usage example

~~~yaml
- name: nvme metrics play
  vars:
    # install only on physical servers
    manage_node_exporter: '{{ ansible_virtualization_role in [ "host", "NA" ] }}'
  hosts: all:!nodefault
  roles:
    - role: teamapps.general.nvme_metrics
      tags: nvme
      when: manage_node_exporter | default(False)
~~~

## Useful Resources

* NVME well explained: https://vatiminxuyu.gitbooks.io/xuyu/content/blog/nvme-what.html
* Inspired by https://github.com/yongseokoh/nvme_exporter
* Node Exporter Ansible Role: https://github.com/cloudalchemy/ansible-node-exporter
