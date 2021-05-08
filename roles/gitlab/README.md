# Gitlab Role

Data is stored in /srv/git

Recommendation: mount an external volume to /srv before installing gitlab.

This role installs gitlab from the apt repository and does not use docker.

## Backup

Backups are created by backuppc prebackup.sh script. it creates a tar file `/srv/backup/auto_gitlab_backup.tar` that is then backed up.

Following data is excluded by default: `registry` (Container Registry images), `artifacts` (CI job artifacts) and `builds` (CI job output logs).

## Backup Restore

Restore first the /etc/gitlab/ directory or at least the file `/etc/gitlab/gitlab-secrets.json`

Restore desired backup file to /srv/backup

Execute restore from tar: `gitlab-backup restore BACKUP=auto`

Version has to be exactly the same as when the backup was created.
If not, downgrade to the version of the backup: `apt install gitlab-ce=13.0.3-ce.0`

[Detailed official documentation](https://docs.gitlab.com/ee/raketasks/backup_restore.html#restore-gitlab)
