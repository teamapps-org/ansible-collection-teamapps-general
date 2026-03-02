# Zammad Help Desk

Community Edition deployment based on [zammad-docker-compose](https://github.com/zammad/zammad-docker-compose).

- [Zammad Community](https://zammad.org/)
- [Zammad Enterprise](https://zammad.com/)
- [Zammad Admin Docs](https://admin-docs.zammad.org/en/latest/index.html)
- [Zammad User Docs](https://docs.zammad.org/en/latest/index.html)

## Backup and restore

Database and file backups are created by the `zammad-backup` service and written to `./data/zammad-backup`.

- Backup documentation: <https://docs.zammad.org/en/latest/appendix/backup-and-restore.html>

## Role variables

See `defaults/main.yml`.

## Dependencies

- Docker Engine
- Docker Compose v2 (`docker compose`)
- `teamapps.general.webproxy` role

## Example playbook

~~~yaml
- name: zammad Play
  hosts:
    - zammad1.example.com
  vars:
    zammad_domain: helpdesk.example.com
    zammad_postgres_pass: "<secret>"
  roles:
    - role: teamapps.general.zammad
~~~

## Large instances and search reindex

By default, Zammad rebuilds the Elasticsearch index on fresh starts. For large instances this can take a long time.

- Disable automatic reindex: `zammad_elasticsearch_reindex: false`
- Rebuild manually after upgrades:
  - `docker compose exec zammad-railsserver rake zammad:searchindex:rebuild`

## Grafana integration

You can expose Elasticsearch through the webproxy with basic auth and restricted methods for Grafana access.

- Feature overview: <https://zammad.com/de/produkt/features/grafana-integration>
- Setup guide (index names, time fields, datasource details): <https://docs.zammad.org/en/latest/appendix/reporting-tools-thirdparty/grafana.html>
- Grafana datasource provisioning reference: <https://grafana.com/docs/grafana/latest/datasources/elasticsearch/#configure-the-data-source-with-provisioning>

Typical datasource settings:

- URL: `https://{{ zammad_elasticsearch_domain }}`
- Basic auth: credentials from `zammad_elasticsearch_htpasswd`
- Elasticsearch version/index settings: use values from the current Zammad Grafana docs
