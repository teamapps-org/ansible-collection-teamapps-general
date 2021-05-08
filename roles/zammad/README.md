zammad Help Desk
=========

Community Edition. Deployment based on [zammad-docker-compose](https://github.com/zammad/zammad-docker-compose)

* [zammad community website](https://zammad.org/)
* [zammad Enterprise website](https://zammad.com/)
* [Admin Docs](https://admin-docs.zammad.org/en/latest/index.html)
* [Zammad Docs](https://docs.zammad.org/en/latest/index.html)

Backup and Restore
------------------

Backups are created by a separate container, that packs the files and the database in an archive in .`/data/zammad-backup`. Other directories can be excluded from the backup.

* Documentation of Backup for traditional installation: <https://docs.zammad.org/en/latest/appendix/backup-and-restore.html>
* Backup Script source: <https://github.com/zammad/zammad-docker-compose/blob/master/containers/zammad-postgresql/backup.sh>

~~~yaml
zammad_backup_hold_days: 2
backuppcclient_files_exclude_extra:
  - /container/zammad/data/elasticsearch-data
  - /container/zammad/data/postgresql-data
  - /container/zammad/data/zammad-data
~~~

Role Variables
--------------

See `default/main.yml`

Dependencies
------------

Docker, docker-compose. Designed for use with webproxy role

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

~~~yaml
- name: zammad Play
  vars:
    zammad_domain:
    zammad_postgres_pass:
  hosts:
    - zammad1.example.com
  roles:
    - role: teamapps.general.zammad
~~~
