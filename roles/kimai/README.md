# Kimai Time-Tracking

Run the open source [Kimai](https://www.kimai.org/) Time Tracking App on your server with docker-compose.

Wrapper for teamapps.general.webserver role with custom nginx.conf, composer and env file.

This uses standard nginx, php and mariadb docker containers. The kimai application is installed as "content" to the filesystem.

## Setup

kimai is installed using composer

there are convenience wrapper for useful commands in `bin/console` and `bin/composer`

### Create admin user

`bin/console kimai:create-user username admin@example.com ROLE_SUPER_ADMIN`

## Updating

for updating, it should be enough to increase `kimai_version` to the new tag. https://www.kimai.org/documentation/updates.html

## Backup & Restore

mysqlbackup is defined in the webserver role. run `./mysqlbackup.sh` to create a manual backup into `dbdumps`

To restore, there is a script `./mysqlrestore.sh` inside the project folder to restore from `dbdumps/kimai.sql.gz`

Files to restore/migrate:

* ./code/config/packages/local.yaml
* ./code/var
  * or individual:
  * ./code/var/data/
  * ./code/var/invoices/
  * ./code/var/export/
  * ./code/var/plugins/

### Restore db from older version

Either install the old version first. or delete the database before restoring and then update the kimai database:

~~~bash
docker-compose down
rm db/* -rf
docker-compose up
./mysqlrestore.sh
bin/console kimai:update
~~~

## configure logging to stderr

By default kimai logs to `code/var/log/prod.log`

[Logging to stderr](https://www.kimai.org/documentation/logging.html#logging-to-stderr)

Example config with additional overview and logging to stderr: `./code/config/packages/local.yaml`

This file is not managed by this role.

~~~yaml
kimai:
    widgets:
        userDurationLastWeek: { title: 'Working hours last week', query: duration, user: true, begin: 'monday last week 00:00:00', end: 'sunday last week 23:59:59', icon: duration, color: blue }
        userDurationLastMonth: { title: 'Working hours last month', query: duration, user: true, begin: 'first day of last month 00:00:00', end: 'last day of last month 23:59:59', icon: duration, color: purple }
        userDurationLastYear: { title: 'Working hours last year', query: duration, user: true, begin: '01 january last year 00:00:00', end: '31 december last year 23:59:59', icon: duration, color: yellow }

    dashboard:
        user_old_duration:
            title: 'Last working hours'
            order: 15
            permission: view_own_timesheet
            widgets: [userDurationLastWeek, userDurationLastMonth, userDurationLastYear]
        user_rates:
            title: 'My Revenue'
            order: 20
            permission: view_rate_own_timesheet
            widgets: [userAmountToday, userAmountWeek, userAmountMonth, userAmountYear]
monolog:
    handlers:
        main:
            path: php://stderr
~~~
