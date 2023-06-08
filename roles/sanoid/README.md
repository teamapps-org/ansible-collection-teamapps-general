# Sanoid Ansible role

* [Sanoid Project and Documentation](https://github.com/jimsalterjrs/sanoid)

## Usage Example

~~~yaml
- name: zfs Play
  hosts:
    - test1.example.com
    - spare1.example.com
  roles:
    - role: teamapps.general.zfs

- name: sanoid
  hosts:
    - test1.example.com
    - spare1.example.com
  tasks:
    - import_role:
        name: teamapps.general.sanoid
      tags: sanoid

- name: syncoid sync target
  hosts:
    - spare1.example.com
  tasks:
    - import_role:
        name: teamapps.general.syncoid
      tags:
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


# requires teamapps.general.zfs role to be applied before syncoid
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

## sanoid.conf help

~~~ini
######################################
# This is a sample sanoid.conf file. #
# It should go in /etc/sanoid.       #
######################################

# name your backup modules with the path to their ZFS dataset - no leading slash.
[zpoolname/datasetname]
  # pick one or more templates - they're defined (and editable) below. Comma separated, processed in order.
  # in this example, template_demo's daily value overrides template_production's daily value.
  use_template = production,demo

  # if you want to, you can override settings in the template directly inside module definitions like this.
  # in this example, we override the template to only keep 12 hourly and 1 monthly snapshot for this dataset.
  hourly = 12
  monthly = 1

# you can also handle datasets recursively.
[zpoolname/parent]
  use_template = production
  recursive = yes
  # if you want sanoid to manage the child datasets but leave this one alone, set process_children_only.
  process_children_only = yes

# you can selectively override settings for child datasets which already fall under a recursive definition.
[zpoolname/parent/child]
  # child datasets already initialized won't be wiped out, so if you use a new template, it will
  # only override the values already set by the parent template, not replace it completely.
  use_template = demo

# you can also handle datasets recursively in an atomic way without the possibility to override settings for child datasets.
[zpoolname/parent2]
  use_template = production
  recursive = zfs
~~~
