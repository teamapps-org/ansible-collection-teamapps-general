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

We use [pipenv](https://pipenv.readthedocs.io) to install ansible and dependency package.

### First time Setup

This is my current way I do it on Ubuntu. There are other ways to install ansible and manage the python dependencies.

~~~bash
cd ansible-collection-teamapps-general # where you cloned this repository
sudo apt install python3-pip
# set PATH so it includes user's ~/.local/bin
echo $PATH | grep '\.local/bin' || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.profile && export PATH="$HOME/.local/bin:$PATH"
pip3 install --user --upgrade pip pipenv
pipenv shell --three
pipenv sync
# check ansible working correctly
ansible --version
~~~

### Loading pipenv

~~~bash
cd ansible-collection-teamapps-general # where you cloned this repository
pipenv shell
~~~

### update ansible and other python packages

* Update your pip and pipenv packages: `pip3 install --user --upgrade pip pipenv`
* To update your local packages to what's defined in the Pipfile and Pipfile.lock, run `pipenv sync`
* To update the Pipfile.lock, run `pipenv update`
* For a major upgrade of ansible, you will get a warning. use `pipenv --rm` and then `pipenv sync`

### Run checks

Check YAML and ansible syntax

~~~bash
ansible-lint roles/*
~~~

## License

Apache 2.0
