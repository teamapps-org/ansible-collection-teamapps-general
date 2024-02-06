# Ansible Role: ZFS exporter

N.B.: This role is a soft fork of Jeff Geerling's excellent
[node_exporter](https://github.com/geerlingguy/node_exporter) role, with some
strategic find-and-replace to install and manage the very similar zfs_exporter
package.

This role installs [zfs_exporter](https://github.com/pdf/zfs_exporter) on Linux
hosts, and configures a systemd unit file so the service can run and be
controlled by systemd.

[Upstream Project by Andrew Roberts](https://github.com/aroberts/ansible-role-zfs_exporter) with scrape config deployment option for vmagent or prometheus.

## Requirements

N/A

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

    zfs_exporter_version: '2.2.5'

The version of zfs exporter to install. Available releases can be found on the [tags](https://github.com/pdf/zfs_exporter/tags) listing in the zfs exporter repository. Drop the `v` off the tag.

If you change the version, the `zfs_exporter` binary will be replaced with the updated version, and the service will be restarted.

    zfs_exporter_arch: 'amd64'
    zfs_exporter_download_url: https://github.com/pdf/zfs_exporter/releases/download/v{{ zfs_exporter_version }}/zfs_exporter-{{ zfs_exporter_version }}.linux-{{ zfs_exporter_arch }}.tar.gz

The architecture and download URL for zfs exporter. If you're on a Raspberry Pi running Raspbian, you may need to override the `arch` value with `armv7`.

    zfs_exporter_bin_path: /usr/local/bin/zfs_exporter

The path where the `zfs_exporter` output will be written

    zfs_exporter_options: ''

Any additional options to pass to `zfs_exporter` when it starts, e.g. `--no-collector.dataset-filesystem` if you want to ignore zfs filesystem data. [Usage here.](https://github.com/pdf/zfs_exporter#usage)

    zfs_exporter_sponge_package_name: moreutils

Package to install for `sponge` binary, necessary for safely teeing the output. Set to '' to skip the install

    zfs_exporter_state: started
    zfs_exporter_enabled: true

Controls for the `zfs_exporter` service.

## Dependencies

None.

## Example Playbook

    - hosts: all
      roles:
        - role: teamapps.general.zfs_exporter

## License

MIT / BSD

## Author Information

by Andrew Roberts, 2022

Based on a role created by [Jeff Geerling](https://www.jeffgeerling.com/).
