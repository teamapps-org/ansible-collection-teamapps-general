# ansible-hetzner-robot

Automated Server installation on Hetzner Robot. Set up ZFS Pool(s) for data.

## Requirements

Boot the server into rescue system first.

Understand the roles tasks before using it.

## Variables

See defaults/main.yml

Default variables are for a server with 2 NVME disks

## Usage example

inventory:

~~~yaml
robot_setup:
  hosts:
    test2.example.com:
      ansible_host: 1.2.3.4
~~~

Playbook:

~~~yaml
# Playbook to install a server from Hetzner Robot

# ANSIBLE_DISPLAY_OK_HOSTS='yes' ANSIBLE_DISPLAY_SKIPPED_HOSTS='yes' ansible-playbook playbooks/hetzner_robot.yml --diff -l test2.example.com

- name: Server Setup from Hetzner Robot Rescue System
  hosts: robot_setup
  gather_facts: no
  # serial: 1
  tags:
    - skip_ansible_lint
  roles:
    - role: teamapps.general.hetzner_robot
~~~

## Configuration examples

Configure in host_vars or playbook vars

### Mirrored setup with 10 disks (SX133)

also configure 2x200GB zfs cache (l2arc) on nvme

~~~yaml
## Setup config:

# extend partitions with additional partitions:
# -part3: 2G for zfsbulk log,
# -part4: 250G for zfsbulk cache,
# -part5: rest (~150G) for zfsdata
hetzner_robot_installimage_partitions: 'swap:swap:{{ hetzner_robot_swap_size }},/:ext4:{{ hetzner_robot_root_size }},none:none:2G,none:none:250G,none:none:all'
hetzner_robot_stop_mdraid:
  - /dev/md2 # 2g zfs write intent log
  - /dev/md3 # zfsbulk cache
  - /dev/md4 # zfsdata

hetzner_robot_clear_mdraid_partitions:
  # - /dev/md2 # 2g zfs write intent log
  - /dev/nvme0n1p3
  - /dev/nvme1n1p3
  # - /dev/md3 # zfsbulk cache
  - /dev/nvme0n1p4
  - /dev/nvme1n1p4
  # - /dev/md4 # zfsdata
  - /dev/nvme0n1p5
  - /dev/nvme1n1p5

hetzner_robot_zfsbulk_pool_type: mirror
hetzner_robot_zfsbulk_partitions_by_id:
  - "{{ ansible_device_links.ids['sda'][0] }}"
  - "{{ ansible_device_links.ids['sdb'][0] }}"

hetzner_robot_zfsbulk_extend_groups:
  - - "{{ ansible_device_links.ids['sdc'][0] }}"
    - "{{ ansible_device_links.ids['sdd'][0] }}"
  - - "{{ ansible_device_links.ids['sde'][0] }}"
    - "{{ ansible_device_links.ids['sdf'][0] }}"
  - - "{{ ansible_device_links.ids['sdg'][0] }}"
    - "{{ ansible_device_links.ids['sdh'][0] }}"
  - - "{{ ansible_device_links.ids['sdi'][0] }}"
    - "{{ ansible_device_links.ids['sdj'][0] }}"

hetzner_robot_zfsbulk_log_file: false
hetzner_robot_zfsbulk_log_partitions_by_id:
  - "{{ ansible_device_links.ids['nvme0n1'][0] }}-part3"
  - "{{ ansible_device_links.ids['nvme1n1'][0] }}-part3"

hetzner_robot_zfsbulk_log_device: "mirror {{ hetzner_robot_zfsbulk_log_partitions_by_id | join(' ') }}"

hetzner_robot_zfsbulk_cache: true
hetzner_robot_zfsbulk_cache_partitions_by_id:
  - "{{ ansible_device_links.ids['nvme0n1'][0] }}-part4"
  - "{{ ansible_device_links.ids['nvme1n1'][0] }}-part4"

~~~

### RAIDZ3 setup with 10 disks (SX133)

~~~yaml
hetzner_robot_zfsbulk: true
hetzner_robot_zfsbulk_pool_type: raidz3
hetzner_robot_zfsbulk_partitions_by_id:
  - "{{ ansible_device_links.ids['sda'][0] }}"
  - "{{ ansible_device_links.ids['sdb'][0] }}"
  - "{{ ansible_device_links.ids['sdc'][0] }}"
  - "{{ ansible_device_links.ids['sdd'][0] }}"
  - "{{ ansible_device_links.ids['sde'][0] }}"
  - "{{ ansible_device_links.ids['sdf'][0] }}"
  - "{{ ansible_device_links.ids['sdg'][0] }}"
  - "{{ ansible_device_links.ids['sdh'][0] }}"
  - "{{ ansible_device_links.ids['sdi'][0] }}"
  - "{{ ansible_device_links.ids['sdj'][0] }}"
~~~

### Mirror Setup with 4 HDD (no nvme) (SX64)

~~~yaml
hetzner_robot_root_size: '80G'
hetzner_robot_raid_disks:
  - /dev/sda
  - /dev/sdb

# part4 on big disks with gpt partition table
hetzner_robot_zfsdata_partitions_by_id:
  - "{{ ansible_device_links.ids['sda'][0] }}-part4"
  - "{{ ansible_device_links.ids['sdb'][0] }}-part4"

# groups of devices, extending the pool with additional vdevs
# for pool type mirror
# list of lists with 2 devices.
hetzner_robot_zfsdata_extend_groups:
  - - "{{ ansible_device_links.ids['sdc'][0] }}"
    - "{{ ansible_device_links.ids['sdd'][0] }}"
~~~

## clean partitions from old zfspool (for reinstall)

* list known pools that could be imported
  * `zpool import`
* clean zfs labels from partitions
  * `pool labelclear -f nvme-SAMSUNG_MZVL2512HCJQ-asdf-part3`
* run hetzner_robot playbook again
