# Ansible Collection - teamapps.general

generic roles for different tools of an organization or company

## Installation

[Official Ansible Documentation for using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)

Add to your `requirements.yml`:

~~~yaml
# requirements.yml

collections:
  # current unreleased from git source, requires ansible 2.10 or higher
  - name: git+https://github.com/teamapps-org/ansible-collection-teamapps-general.git
    type: git
    version: main
~~~

Run `ansible-galaxy collection install -r requirements.yml -f`

Tip: You can specify the installation path for collections in your project in `ansible.cfg` before running the command above.

~~~ini
# ansible.cfg
[defaults]
collections_path = collections
~~~

## Usage

The roles in this collection can be used by using their full name, prefixed with `teamapps.general`

Check the `defaults.yml` of the roles for information on how to configure them.

~~~yaml
# Ansible Playbook
# site.yml

- name: Zammad Helpdesk Play
  hosts: yourhost.example.com
  vars:
    letsencrypt_email: mail@example.com
    zammad_domain: help.example.com
  roles:
    - role: teamapps.general.webproxy
    - role: teamapps.general.zammad
      tags: zammad

~~~

## Compatibility notes

- The collection now ships the `teamapps.general.to_nice_yaml` filter, which transparently calls `community.general.to_nice_yaml` on newer Ansible releases and falls back to the legacy core implementation on older ones. Add the `community.general` collection to your requirements when targeting ansible-core 2.12 or newer so the upstream filter is available.
- ansible-core newer than 2.19 removed the safe YAML dumper from core. When the `community.general` implementation is missing the collection still falls back to the legacy dumper but now emits a warning because sensitive vault strings could be dumped in clear text (see [ansible/ansible#85722](https://github.com/ansible/ansible/issues/85722)). Install `community.general` to avoid the warning and regain the safe serializer.

## Development setup

See [docs/CONVENTIONS.md](docs/CONVENTIONS.md) for role, secrets, Docker Compose, and documentation conventions. [AGENTS.md](AGENTS.md) covers repository tooling, verification, and agent workflow.

We use [pipenv](https://pipenv.readthedocs.io) to install Ansible and its Python dependencies. `Pipfile` sets the Python version; `Pipfile.lock` pins the package versions.

### First time Setup

One way to set it up on Ubuntu. Other ways to install pipenv and the required Python version work as well.

~~~bash
cd ansible-collection-teamapps-general # where you cloned this repository
sudo apt install pipx
pipx ensurepath
pipx install pipenv
pipenv sync
# check ansible working correctly
pipenv run ansible --version
~~~

`pipenv sync` needs the Python version from `Pipfile`. If it is not installed, install it first, for example with [pyenv](https://github.com/pyenv/pyenv), which pipenv uses automatically.

### Loading pipenv

~~~bash
cd ansible-collection-teamapps-general # where you cloned this repository
pipenv shell
~~~

Alternatively, prefix single commands with `pipenv run`.

### update ansible and other python packages

* Update pipenv: `pipx upgrade pipenv`
* To update your local packages to what's defined in the Pipfile and Pipfile.lock, run `pipenv sync`
* To update the Pipfile.lock, run `pipenv update`
* For a major upgrade of ansible, you will get a warning. use `pipenv --rm` and then `pipenv sync`

### Run checks

Check YAML and Ansible syntax of all roles:

~~~bash
pipenv run ansible-lint roles/*
pipenv run yamllint .
~~~

For a single role, pass its directory, for example `pipenv run ansible-lint roles/zfs` and `pipenv run yamllint roles/zfs`.

## License

Apache 2.0
