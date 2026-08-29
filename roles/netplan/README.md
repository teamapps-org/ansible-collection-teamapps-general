# Netplan Role

This role configures Netplan ethernet interfaces on an Ubuntu system. It can
add addresses to the default interface, render an explicit `ethernets` mapping,
or do both.

When enabled, the role writes an additional file. Netplan merges that file with
the other configuration files during `netplan generate` and `netplan apply`.

Set `netplan_manage_addresses: true` to manage the default-interface
configuration; it defaults to `true`. Set `netplan_ethernets` to render an
explicit mapping. Set
`netplan_manage_addresses: false` to render only `netplan_ethernets`.
When both options render, they must configure different interfaces.

## Example Usage

~~~yaml
---
- name: Add Floating IP
  hosts:
    - server1.example.com
  vars:
    netplan_manage_addresses: true
    netplan_addresses:
      - 172.16.16.16/32
      - 2001:cafe:face:beef::dead:dead/64
  roles:
    - role: teamapps.general.netplan

- name: Remove Floating IPs
  hosts:
    - server1.example.com
  vars:
    netplan_manage_addresses: true
    netplan_addresses: []
  roles:
    - role: teamapps.general.netplan
~~~

For configurations that must survive PCI bus renumbering, match interfaces by
MAC address:

~~~yaml
netplan_manage_addresses: false
netplan_ethernets:
  lan:
    match:
      macaddress: 00:11:22:33:44:55
    addresses:
      - 192.0.2.10/24
~~~

## Config Validation

The config is validated before being applied. Example with an invalid address:

~~~yaml
TASK [netplan : Netplan validate config] *************
fatal: [server1.example.com]: FAILED! => changed=false
  cmd:
  - netplan
  - generate
  delta: '0:00:00.127330'
  end: '2021-06-07 15:02:36.722722'
  msg: non-zero return code
  rc: 1
  start: '2021-06-07 15:02:36.595392'
  stderr: |-
    /etc/netplan/90-ansible.yaml:22:13: Error in network definition: invalid prefix length in address '172.16.16.16/33'
                - 172.16.16.16/33
                ^
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
~~~
