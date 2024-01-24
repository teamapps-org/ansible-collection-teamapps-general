# Webserver Role

with optional php, mariadb and sftp

This role can also be used in wrapper roles like matomo

## mariadb upgrade

Manual upgrade is no longer needed. [will be automatically upgraded](https://mariadb.com/kb/en/mariadb-server-docker-official-image-environment-variables/#mariadb_auto_upgrade-mariadb_disable_upgrade_backup).

`docker compose exec db sh -c "exec mysql_upgrade -u root -p\"\$MYSQL_ROOT_PASSWORD\" --verbose"`
