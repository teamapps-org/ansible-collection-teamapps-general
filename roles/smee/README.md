# Ansible Role: Gosmee

This role sets up a Gosmee server using Docker Compose. Gosmee is a webhook forwarder/relayer and replayer that allows you to receive webhooks on your local machine or forward them to internal services that are not publicly accessible.

* [Gosmee Project Website on GitHub]<https://github.com/chmouel/gosmee>

## Features

- Webhook forwarding with secure defaults
- Support for webhook signature validation
- IP address restrictions for webhook POST requests
- Payload size protection (25MB limit by default)
- Channel name protection (64 characters max)
- Integration with reverse proxy

## Requirements

- Docker
- Docker Compose
- Running instance of [jwilder/nginx-proxy](https://github.com/nginx-proxy/nginx-proxy) or similar reverse proxy

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Basic Configuration
smee_path: '/container/smee'
smee_domain: 'smee.{{ ansible_facts.fqdn }}'

# Security Features
smee_webhook_signatures: []  # List of secrets for webhook signature validation
smee_allowed_ips: []        # List of allowed IPs/CIDR ranges
```

### IP Restriction Examples

You can restrict webhook POST requests to specific IP ranges. If configured, only these sources can send POST requests that will be forwarded to the clients.

Check documentation for [Webhook IP Restrictions]<https://github.com/chmouel/gosmee?tab=readme-ov-file#webhook-ip-restrictions>

Here are some common examples:

```yaml
# GitHub webhook ranges
smee_allowed_ips:
  - 192.30.252.0/22
  - 185.199.108.0/22
  - 140.82.112.0/20

# GitLab.com webhook ranges
smee_allowed_ips:
  - 35.231.145.151
  - 34.74.90.64
  - 34.74.226.93

# Bitbucket Cloud webhook ranges
smee_allowed_ips:
  - 34.199.54.113
  - 34.232.119.183
  - 34.236.25.177
  - 35.171.175.212
```

## Dependencies

None.

## Example Playbook

Basic usage:

```yaml
- name: Gosmee Server Play
  hosts: servers
  roles:
    - role: teamapps.general.smee
      vars:
        smee_domain: "smee.example.com"
```

Advanced usage with security features:

```yaml
- name: Gosmee Server Play
  hosts: servers
  roles:
    - role: teamapps.general.smee
      vars:
        smee_domain: "smee.example.com"
        smee_webhook_signatures:
          - "your-webhook-secret-1"
          - "your-webhook-secret-2"
        smee_allowed_ips:
          - "192.30.252.0/22"  # GitHub webhook range
          - "35.231.145.151"   # GitLab webhook IP
```

## Usage

After deployment:

1. Access your Gosmee server at `https://your-domain/new` to generate a new channel
2. Use the generated URL as your webhook endpoint
3. The webhook payloads will be forwarded to your specified target

### Channel URLs

Channel URLs follow the format: `https://your-domain/RANDOM_ID`, where RANDOM_ID is a 12-character string containing a-zA-Z0-9_-

### Security Notes

1. The server enforces a 25MB payload size limit (GitHub standard)
2. Channel names are limited to 64 characters
3. When using IP restrictions, only POST requests are affected - UI access remains unrestricted
4. Webhook signatures can be validated using multiple secrets
5. The service automatically trusts proxy headers for proper IP forwarding

## License

MIT
