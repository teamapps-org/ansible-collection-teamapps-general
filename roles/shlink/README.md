# Shlink

Configure [Shlink](https://shlink.io/), a self-hosted URL shortener. This role deploys Shlink with Docker Compose and integrates with `teamapps.general.webproxy`.

## Usage Example

~~~yaml
- name: Shlink play
  hosts:
    - shlink1.example.com
  roles:
    - role: teamapps.general.shlink
      tags:
        - shlink
        - urls
~~~

Example `host_vars/shlink1.example.com.yml`

~~~yaml
shlink_version: stable
shlink_domain: 'link.{{ ansible_facts.fqdn }}'
shlink_manage_domain: 'manage.{{ shlink_domain }}'
shlink_timezone: Europe/Berlin

shlink_mariadb_version: 11
shlink_db_name: shlink

shlink_mariadb_root_password: strong-root-password
shlink_mariadb_password: strong-app-password
shlink_geolite_license_key: your-maxmind-license-key # https://www.maxmind.com/en/geolite2/signup

shlink_deploy_web_client: false
~~~

## First Time Setup

Generate an API key after the containers are running:

~~~bash
cd /container/shlink
./shlink api-key:generate --name admin
./shlink api-key:list
~~~

## Web Client (Optional)

You can deploy the official Shlink web client on a separate domain or use the hosted UI.

* Go To <https://app.shlink.io/manage-servers>
  * Alternatively enable self-hosted web-client with the following ansible vars

    ~~~yaml
    shlink_deploy_web_client: true
    shlink_manage_domain: 'manage.{{ shlink_domain }}'
    ~~~

* Register with configured domain and api key
* Connection to your server is done directly from your browser. Whitelist connections to your domain if you use uMatrix or other adblockers that prevent requests third party domains.
* Configure domain
  * Manage Domain
  * Base path redirect
