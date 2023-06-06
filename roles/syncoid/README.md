# Syncoid Ansible role

* [Sanoid Project and Documentation](https://github.com/jimsalterjrs/sanoid)

## Usage Example

~~~yaml

- name: sanoid
  hosts:
    - test1.example.com
    - spare1.example.com
  tasks:
    - import_role:
        name: sanoid
      tags: sanoid

- name: syncoid sync target
  hosts:
    - spare1.example.com
  tasks:
    - import_role:
        name: syncoid
      tags:
        - sanoid
        - syncoid
~~~

~~~yaml
# host config spare1.example.com:

sanoid_conf_datasets: |
  [zfsbulk]
    recursive = yes
    use_template = production

  [zfsdata]
    recursive = yes
    use_template = production

  [zfsdata/container]
    recursive = yes
    frequently = 200
    # frequent_period in minutes
    frequent_period = 15
    pre_snapshot_script = /usr/local/bin/prebackup.sh
    # script_timeout in seconds
    script_timeout = 60

  [zfsdata/docker]
    recursive = yes
    use_template = ignore
    pre_snapshot_script = /bin/false

  [zfsdata/hotspare]
    recursive = yes
    use_template = hotspare

  [zfsbulk/hotspare]
    recursive = yes
    use_template = hotspare


# requires zfs role to be applied before syncoid
zfs_datasets:
  - name: zfsbulk/hotspare
  - name: zfsbulk/hotspare/test1
  - name: zfsdata/hotspare
  - name: zfsdata/hotspare/test1

# destination root dataset needs to be existing. see above.
syncoid_jobs:
  # zfsbulk@test1 -> zfsbulk/hotspare/test1@spare1
  - source_host: test1
    source_host_ssh: 'test1.example.com'
    source_dataset: zfsbulk
    source_bwlimit: 60m
    cron_minute: 35
    cron_hour: '*'
    dest_root_dataset: zfsbulk/hotspare

  # zfsdata@test1 -> zfsdata/hotspare/test1@spare1
  - source_host: test1
    source_host_ssh: 'test1.example.com'
    source_dataset: zfsdata
    exclude: # defaults:
      - /docker/
      - /hotspare/
    source_bwlimit: 60m
    cron_minute: 12
    cron_hour: '*'
    dest_root_dataset: zfsdata/hotspare
~~~
