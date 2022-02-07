# VMagent

Role to install and configure vmagent. Installs by using binare from Github releases.

## Usage Example

~~~yaml
- name: Victoriametrics vmagent Play
  hosts:
    - all
  vars:
    # local vmagent to scrape netdata and send to victoriametrics
    vmagent_remotewrite_url: https://metrics.vic1.example.com/api/v1/write
    vmagent_remotewrite_username: vmagent-to-vic-write
    vmagent_remotewrite_password: password

    vmagent_promscrape_config:
      global:
        scrape_interval: 10s
        external_labels:
          scraper_instance: "{{ ansible_fqdn | default(ansible_host) | default(inventory_hostname) }}"
      scrape_configs:
        - job_name: "netdata"
          metrics_path: /api/v1/allmetrics
          params:
            format: [prometheus]
          honor_labels: true
          static_configs:
            - targets: [127.0.0.1:19999]
              labels:
                host: '{{ ansible_hostname }}'
        - job_name: "vmagent"
          static_configs:
            - targets: [127.0.0.9:8429]
              labels:
                instance: '{{ ansible_fqdn }}'
                host: '{{ ansible_hostname }}'

  roles:
    - role: teamapps.general.victoria_vmagent
      tags:
        - metrics
        - vmagent
~~~

## Parameters

See [defaults](defaults/main.yml)

## License

Apache 2.0

Based on <https://github.com/VictoriaMetrics/ansible-playbooks/tree/master/roles/victoria_vmagent>
