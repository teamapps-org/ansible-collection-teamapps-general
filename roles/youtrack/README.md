# YouTrack Setup with Docker Compose

Based on Docker Installation Documentation: <https://www.jetbrains.com/help/youtrack/standalone/youtrack-docker-installation.html>

## Requirements

Role [webproxy](../webproxy/README.md) / [Evertramos reverse proxy](https://github.com/evertramos/docker-compose-letsencrypt-nginx-proxy-companion)

## Role Variables

See `defaults/main.yml`

## Update YouTrack

* Update variable `youtrack_version:` in inventory/host_vars with latest release from https://hub.docker.com/r/jetbrains/youtrack/tags
* Run playbook `ansible-playbook playbooks/site.yml -i inventory/production_internal.yml --diff --tags youtrack`
* check docker logs. copy configuration wizard url. Access Service URL
* To execute the upgrade, you need the wizard_token from the server: `cat /container/youtrack/conf/internal/services/configurationWizard/wizard_token.txt`
