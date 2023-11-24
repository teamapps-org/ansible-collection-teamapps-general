# Nextcloud Ansible Role

Nextcloud with docker for reverse-proxy

## Requirements

Automated Reverse Proxy in Docker. Use one of:

* Ansible Role [teamapps.general.webproxy](../webproxy/README.md)
* [nginx-proxy](https://github.com/nginx-proxy/nginx-proxy)
* [evertramos/proxy-automation]( https://github.com/evertramos/nginx-proxy-automation)

## Configuration

See [defaults/main.yml](defaults/main.yml)

## Migration

The nextcloud-setup does not work fully out of the box on a fresh install. I used it to migrate nextcloud to a docker-based setup.

When migrating, make sure, all the relevant options in the config.php are also set on the new instance.
Important: if the datadirectory changes, you need to change the path in the database, otherwise the file_cache and the shares don't work anymore.

I edited the dbdump and replaced the old path with the new one in the oc_storage table

Dump database with the right character-set:
mysqldump nextcloud  --default-character-set=utf8mb4 --skip-dump-date > nextcloud-utf8mb4.sql

Import database:
mysql --default-character-set=utf8mb4 -p"$MYSQL_ROOT_PASSWORD" nextcloud < /db-dumps/nextcloud-utf8mb4.sql

## config settings

~~~bash
./occ config:list
./occ config:system:get default_phone_region
./occ config:system:get default_phone_region
./occ config:system:set default_phone_region --value "DE"
./occ config:app:set files max_chunk_size --value 0
./occ config:app:delete files max_chunk_size
./occ config:system:set filelocking.enabled --value true --type boolean
~~~

## high performance backend with docker

https://github.com/nextcloud/notify_push
https://help.nextcloud.com/t/solved-progress-report-on-getting-the-new-hpb-working-with-docker/108832/2

~~~bash
./occ app:enable notify_push
./occ notify_push:setup https://cloud.example.com/push
./occ config:system:set trusted_proxies 0 --value=172.16.0.0/16
# ./occ config:system:set trusted_proxies 1 --value=172.28.0.0/16
# ./occ config:system:set trusted_proxies 2 --value=172.18.0.0/16
~~~

## Improvements

* php and server tuning values?: https://docs.nextcloud.com/server/latest/admin_manual/installation/server_tuning.html#tune-php-fpm
* external preview generation: https://docs.nextcloud.com/server/latest/admin_manual/installation/server_tuning.html#previews

## License

Apache 2.0

## Author Information

Philipp Gassmann
