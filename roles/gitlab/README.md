# Gitlab Role

Data is stored in /srv/git

Recommendation: mount an external volume to /srv before installing gitlab.

This role installs gitlab from the apt repository and does not use docker.

## Usage Example

~~~yaml
- name: Gitlab
  hosts: git1.example.com
  vars:
    gitlab_domain: git.example.com
  roles:
    - role: teamapps.general.gitlab
      tags:
        - gitlab
~~~

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

## Customize gitlab.rb

To configure SSO with omniauth, you can use the `gitlab_custom_config` variable.

Example for SSO with Microsoft 365:

~~~yaml
gitlab_custom_config: |
  # SSO Settings: https://docs.gitlab.com/ee/integration/omniauth.html
  gitlab_rails['omniauth_allow_single_sign_on'] = ['azure_activedirectory_v2'] # auto create users
  gitlab_rails['omniauth_block_auto_created_users'] = true
  gitlab_rails['omniauth_auto_link_user'] = ["azure_activedirectory_v2"] # allow sso login for existing accounts
  gitlab_rails['omniauth_allow_bypass_two_factor'] = ['azure_activedirectory_v2'] # 2FA is enabled on MS365
  # gitlab_rails['omniauth_sync_profile_from_provider'] = ['azure_activedirectory_v2']
  # gitlab_rails['omniauth_sync_profile_attributes'] = ['name', 'email', 'location']

  gitlab_rails['omniauth_providers'] = [
  ## Microsoft 365 SSO (Azure OAuth 2.0)
  # https://docs.gitlab.com/ee/integration/azure.html
    {
      name: "azure_activedirectory_v2",
      label: "Microsoft 365", # optional label for login button, defaults to "Azure AD"
      args: {
        client_id: "{{ gitlab_omniauth_azure_client_id }}",
        client_secret: "{{ gitlab_omniauth_azure_client_secret }}",
        tenant_id: "{{ gitlab_omniauth_azure_tenant_id }}",
      }
    },
  ]
~~~
