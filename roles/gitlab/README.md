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

## GitLab Pages

This role can configure GitLab Pages for the Omnibus package.

Use a separate wildcard certificate automation role and point GitLab Pages at the resulting certificate and key paths.

Typical setup:

- GitLab UI on the primary public IP
- GitLab Pages on a secondary public IP
- wildcard DNS for the Pages domain
- a wildcard certificate present at `gitlab_pages_cert_path` and `gitlab_pages_key_path`

The role verifies the configured certificate files exist before enabling Pages.

### Access control

This role can enable Pages access control through Omnibus configuration. After deployment, verify the Pages OAuth application in GitLab Admin if the callback protocol or host changed.

### GitLab Let's Encrypt integration

GitLab's Pages Let's Encrypt integration only covers project custom domains. It does not issue the wildcard certificate required for the main Pages domain.

After deploying the Pages daemon and wildcard certificate:

1. Go to GitLab Admin.
2. Open `Settings` -> `Preferences` -> `Pages`.
3. Enable Let's Encrypt integration.
4. Set the contact email.
5. Keep custom domain verification enabled.

### Security notes

- Do not use a Pages domain that is a subdomain of the GitLab instance parent domain if that widens cookie scope unexpectedly.
- If untrusted users can create Pages sites, consider adding the Pages domain to the Public Suffix List.
- Keep custom domain verification enabled.
- HTTPS termination on an external load balancer is not the preferred topology if you also want GitLab Pages to serve custom-domain certificates directly.

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

## Upstream

This role is part of the `teamapps.general` collection. If you change the collection role here, also create a corresponding MR in the upstream `teamapps.general` repository.
