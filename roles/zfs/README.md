# Ansible ZFS Role

manage zpool properties, enable autotrim, create zfs datesets by variable.

does not create zpools. only manages the pool properties if they already exist.

## Usage example

Playbook:

~~~yaml
- name: manage ZFS and zpool properties
  hosts:
    - production
    - testing
  roles:
    - role: teamapps.general.zfs
      tags: [zfs, zpool]
~~~

Variables

~~~yaml

zfs_managed_pools:
  - zfsdata
  - zfsbulk

zfs_zpool_properties:
  atime: on
  relatime: on
  xattr: sa
  acltype: posix # posixacl for older ZFS versions
  # snapdir: visible

zfs_datasets:
  - name: zfsbulk/hotspare
  - name: zfsbulk/hotspare/test1
    extra_zfs_properties:
      relatime: off

~~~
