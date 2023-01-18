# Webserver Role

with optional php, mariadb and sftp

This role can also be used in wrapper roles like matomo

## mariadb upgrade

`docker-compose exec db sh -c "exec mysql_upgrade -u root -p\"\$MYSQL_ROOT_PASSWORD\" --verbose"`
