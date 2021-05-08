# BackupPC Client

Configure BackupPC Client and registration

## Requirements

BackupPC Server installation is not part of this role. Also ansible needs to be able to connect to the BackupPC server to register the client and write the `hostconfig.pl` file.

Check and configure the `backuppcclient_server*` vars from main/defaults.yml

## Role Variables

See [defaults/main.yml](defaults/main.yml)

## Example Playbook

```yaml
---
- hosts: all
  vars:
    backuppcclient_server: backup1.example.com
    backuppcclient_authorized_key: ssh-rsa AAAAB3Nz...I9wKZ
  roles:
      - role: backuppcclient
```
