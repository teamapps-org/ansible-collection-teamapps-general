# Ansible Collection - teamapps.general

generic roles for different tools of an organization or company

## Installation

[Official Ansible Documentation for using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)

Add to your `requirements.yml`:

~~~yaml
# requirements.yml

collections:
  # current unreleased from git source, requires ansible 2.10 or higher
  - name: git+https://github.com/teamapps/ansible-collection-teamapps-general.git
    type: git
    version: main
~~~

Run `ansible-galaxy collection install -r requirements.yml -f`

Tip: You can specify the installation path for collections in your project in `ansible.cfg` before running the command above.

~~~ini
# ansible.cfg
[defaults]
collections_paths = collections
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

## License

Apache 2.0
