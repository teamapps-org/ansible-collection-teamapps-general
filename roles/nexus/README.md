# Nexus

Sonatype Nexus 3 OSS. Service-Path: {{ nexus_domain }}

Using Docker image [sonatype/nexus3](https://hub.docker.com/r/sonatype/nexus3/tags)

Default user is `admin` and the uniquely generated password can be found in the admin.password file inside the volume (`/container/nexus/data/admin.password`).

It can take some time (2-3 minutes) for the service to launch in a new container. You can tail the log to determine once Nexus is ready:

## Secret encryption key

Without a custom key, Nexus encrypts stored secrets (repository and LDAP credentials etc.) with a built-in default key
and warns about it in the UI. Set `nexus_secrets_keys` and `nexus_secrets_active_key` to deploy a secrets file and
pass it to Nexus via `NEXUS_SECRETS_KEY_FILE`:

~~~yaml
nexus_secrets_active_key: key-2026
nexus_secrets_keys:
  - id: key-2026
    key: !vault |  # openssl rand -base64 32 | tr -d '\n' | ansible-vault encrypt_string
      ...
~~~

After the deploy, re-encrypt the existing secrets with the active key (an admin user is needed):

~~~bash
curl -u admin -X PUT -H 'Content-Type: application/json' \
  -d '{"secretKeyId": "key-2026"}' \
  https://nexus.example.com/service/rest/v1/secrets/encryption/re-encrypt
~~~

This starts a task; let it finish. From then on Nexus needs the key on every start, so back it up and never remove it.
To rotate, add a new key, make it active, deploy and call the API again with the new id. Keep the old key listed.
See [Re-encryption in Nexus Repository](https://help.sonatype.com/en/re-encryption-in-nexus-repository.html).

## Requirements

Role [webproxy](../webproxy/README.md) / Evertramos reverse proxy <https://github.com/evertramos/docker-compose-letsencrypt-nginx-proxy-companion>

## Role Variables

See [defaults/main.yml](defaults/main.yml)

## Usage Example

~~~yaml
- name: Nexus Play
  hosts:
    - nexus1.example.com
  roles:
    - role: teamapps.general.nexus
      tags:
        - nexus
~~~
