# zammad Help Desk

Community Edition. Deployment based on [zammad-docker-compose](https://github.com/zammad/zammad-docker-compose)

* [zammad community website](https://zammad.org/)
* [zammad Enterprise website](https://zammad.com/)
* [Admin Docs](https://admin-docs.zammad.org/en/latest/index.html)
* [Zammad Docs](https://docs.zammad.org/en/latest/index.html)

## Backup and Restore

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

## Role Variables

See `default/main.yml`

## Dependencies

Docker, docker-compose. Designed for use with webproxy role

## Example Playbook

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

## Disable automatic reindex on big instances

by default, zammad rebuilds the elasticsearch index on every fresh start
for big installations it can take more than 1h (27'000 Tickets)
alternative: reindex manually.

Set variable

* `zammad_elasticsearch_reindex: False`

and run after every update:

* `docker-compose exec zammad-railsserver rake zammad:searchindex:rebuild`

## Grafana Zammad Integration

You can expose elasticsearch through the webproxy with basic auth and limit to GET and POST requests for connecting to Elasticsearch from Grafana.

* [Zammad Grafana Integration](https://zammad.com/de/produkt/features/grafana-integration)
* [Zammad Grafana Documentation](https://docs.zammad.org/en/latest/appendix/reporting-tools-thirdparty/grafana.html)

Elasticsearch Datasource Settings:

* URL: `https://{{ zammad_elasticsearch_domain }}`
* Basic Auth: Username and Password configured in `zammad_elasticsearch_htpasswd`
* Version: 7.0+
* Index name and Time Field name from [Zammad Grafana Documentation](https://docs.zammad.org/en/latest/appendix/reporting-tools-thirdparty/grafana.html#setting-up-required-data-sources)

[Grafana Datasource Provisioning](https://grafana.com/docs/grafana/latest/datasources/elasticsearch/#configure-the-data-source-with-provisioning) Example:

~~~yaml
apiVersion: 1
datasources:
  - name: Zammad ES - Chat Sessions
    type: elasticsearch
    access: proxy
    url: https://{{ zammad_elasticsearch_domain }}
    basicAuth: true
    basicAuthUser: '{{ grafana_zammad_user }}'
    secureJsonData:
      basicAuthPassword: '{{ grafana_zammad_password }}'
    database: zammad_production_chat_session
    jsonData:
      timeField: 'created_at'
      esVersion: '7.0.0'

  - name: Zammad ES - CTI Log
    type: elasticsearch
    access: proxy
    url: https://{{ zammad_elasticsearch_domain }}
    basicAuth: true
    basicAuthUser: '{{ grafana_zammad_user }}'
    secureJsonData:
      basicAuthPassword: '{{ grafana_zammad_password }}'
    database: zammad_production_cti_log
    jsonData:
      timeField: 'start_at'
      esVersion: '7.0.0'

  - name: Zammad ES - Ticket Articles
    type: elasticsearch
    access: proxy
    url: https://{{ zammad_elasticsearch_domain }}
    basicAuth: true
    basicAuthUser: '{{ grafana_zammad_user }}'
    secureJsonData:
      basicAuthPassword: '{{ grafana_zammad_password }}'
    database: zammad_production_ticket
    jsonData:
      timeField: 'article.created_at'
      esVersion: '7.0.0'

  - name: Zammad ES - Tickets by closed_at
    type: elasticsearch
    access: proxy
    url: https://{{ zammad_elasticsearch_domain }}
    basicAuth: true
    basicAuthUser: '{{ grafana_zammad_user }}'
    secureJsonData:
      basicAuthPassword: '{{ grafana_zammad_password }}'
    database: zammad_production_ticket
    jsonData:
      timeField: 'close_at'
      esVersion: '7.0.0'

  - name: Zammad ES - Tickets by created_at
    type: elasticsearch
    access: proxy
    url: https://{{ zammad_elasticsearch_domain }}
    basicAuth: true
    basicAuthUser: '{{ grafana_zammad_user }}'
    secureJsonData:
      basicAuthPassword: '{{ grafana_zammad_password }}'
    database: zammad_production_ticket
    jsonData:
      timeField: 'created_at'
      esVersion: '7.0.0'

  - name: Zammad ES - Tickets by first_response_at
    type: elasticsearch
    access: proxy
    url: https://{{ zammad_elasticsearch_domain }}
    basicAuth: true
    basicAuthUser: '{{ grafana_zammad_user }}'
    secureJsonData:
      basicAuthPassword: '{{ grafana_zammad_password }}'
    database: zammad_production_ticket
    jsonData:
      timeField: 'first_response_at'
      esVersion: '7.0.0'
~~~

## Postgres Update for new deployment. Postgres Backup restore

these commands should be run manually

~~~bash
## upgrade postgres to version 15.

cd /container/zammad

. .env

# stop services to prevent data change
docker-compose stop zammad-scheduler zammad-nginx

# create new backup
docker-compose restart zammad-backup

# watch backup directory until new backups are completed
# wait for _db.psql.gz to have the same size as older backups
ls data/zammad-backup/ -lah

# stop everything
docker-compose stop

# save old postgres-data
mv ./data/postgresql-data ./data/postgresql-data-old

# create new postgres-data
mkdir ./data/postgresql-data
chown 77:0 ./data/postgresql-data

# create temporary
docker run -it --rm --name postgres-restore \
  -v $PWD/data/zammad-backup:/var/tmp/zammad:ro \
  -v $PWD/data/postgresql-data:/var/lib/postgresql/data \
  -e POSTGRES_USER=$POSTGRES_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_PASS \
  postgres:15.0-alpine

# in separate shell:

# create zammad_production db
docker exec -it postgres-restore bash -c "psql -U zammad --command='CREATE DATABASE zammad_production'"

# show available backups
docker exec -it postgres-restore bash -c "ls -al /var/tmp/zammad/"


# restore old data with adjusted filename you got from the ls command above
# CHANGE filename!
docker exec -it postgres-restore bash -c "gunzip -kc /var/tmp/zammad/20221117130512_zammad_db.psql.gz | psql -U zammad -d zammad_production"

# stop the restore container
docker stop postgres-restore

## deploy new version of compose using ansible

# delete old postgres data
rm ./data/postgresql-data-old -rf
~~~

## Upgrade to Zammad 6

~~~bash
cd /container/zammad
docker-compose down
mv ./data/zammad-data/storage ./data/zammad-storage
# apply ansible config with new version variables for version 6+
~~~
