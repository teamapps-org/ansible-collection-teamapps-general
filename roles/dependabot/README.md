# Dependabot

Deployment of [dependabot-gitlab](https://gitlab.com/dependabot-gitlab/dependabot)

Uses basic auth feature of webproxy and whitelist of gitlab host ip to secure access to api and web UI.

* web UI with list of registered projects. Basic auth. https://dependabot.example.com/

## Usage example

Playbook:

~~~yaml

- name: Dependabot Play
  vars:
    dependabot_domain: dependabot.example.com
  hosts:
    - server1.example.com
  roles:
    - role: teamapps.general.dependabot
      tags:
        - dependabot
~~~

Check [defaults/main.yml](defaults/main.yml) for the nessessary configuration variables

## API Access from Command line

~~~bash
docker-compose exec web bash
curl -s -H "X-Gitlab-Token: $SETTINGS__GITLAB_AUTH_TOKEN" localhost:3000/api/projects | python -m json.tool
~~~

## Setup

Once:

* create dependabot user in gitlab to have commits as dependabot and not as your personal user
* Get Access token

To configure a project:

See [detailed documentation](https://gitlab.com/dependabot-gitlab/dependabot#dependabotyml) for more information

* configure dependabot in repository file:

`.gitlab/dependabot.yml`:

~~~yaml
# dependabot configuration
version: 2

registries:
  maven-nexus-example:
    type: maven-repository
    url: https://nexus.example.com
    username: dependabot
    password: ${{NEXUS_DEPENDABOT_PASSWORD}}

updates:
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 20
    rebase-strategy: auto
    auto-merge: false
    registries:
      - maven-nexus-example
    commit-message:
      # Prefix all commit messages
      prefix: "depbot"
~~~

* add dependabot user to project as Maintainer (temporary for setup)
* run `docker-compose exec worker bundle exec rake 'dependabot:validate[aviloo/signal-db]'`
* run `docker-compose exec worker bundle exec rake 'dependabot:register[aviloo/aviloo-platform]'`
* (Optional) change dependabot Role in Project to Developer

manually trigger check: `docker-compose exec worker bundle exec rake 'dependabot:update[example/example-project,maven,/]'`

## Web UI

Web UI with list of registered projects. Basic auth. <https://dependabot.example.com/> (as configured in `dependabot_domain`)
