# BackupPC Server

Install a BackupPC server using Docker compose

## Requirements

Requires to generate a backuppc ssh key: ssh-keygen -f /tmp/backuppc -t ed25519
copy to `{{ backuppc_datapath }}/home/.ssh/id_ed25519.pub`

## Role Variables

See `defaults/main.yml`

## Example Playbook

~~~yaml
- name: BackupPC Server Play
  hosts:
    - backup1.example.com
  vars:
    # generate lines with htpasswd -B -n username
    backuppc_htpasswd: |
      hans:$2y$.....
    backuppc_admin_users:
      - hans
    # prevent backuppc from backing up its own data
    backuppcclient_files_exclude_extra:
      - '{{ backuppc_datapath }}/data/'
  roles:
      - role: teamapps.general.backuppc
~~~

Author Information
------------------

Philipp Gassmann
