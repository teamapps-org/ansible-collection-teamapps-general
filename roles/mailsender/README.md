# Mailsender Ansible Role

## Overview

The `mailsender` role provisions a secure SMTP submission service on Ubuntu 24.04 using Postfix with SMTP AUTH and TLS via Let's Encrypt. This setup is designed for devices like scanners that need to send emails through a reliable SMTP relay.

## Key Features

- **Secure SMTP submission** on port 587 with mandatory TLS and authentication
- **Let's Encrypt certificates** for TLS encryption
- **Direct MX delivery** - no external relay dependencies
- **User authentication** with password hashing via Dovecot
- **Firewall configuration** with ufw
- **Sender address restrictions** (optional)

## Requirements

- Ubuntu 24.04 LTS on a cloud instance (tested with Hetzner Cloud)
- DNS configuration:
  - A record for the SMTP hostname pointing to the server IP
  - PTR (reverse DNS) record set to the same hostname
  - SPF TXT record authorizing the server's public IP
- Network access:
  - Inbound: ports 587 (SMTP submission) and 80 (Let's Encrypt)
  - Outbound: port 25 (SMTP to recipient MX servers)

## Quick Start

### 1. Configure Variables

Set these variables in your inventory or group_vars:

```yaml
mailsender_hostname: "relay.sender.domain.tld"
mailsender_domain: "sender.domain.tld"
mailsender_contact_email: "admin@sender.domain.tld"

mailsender_users:
  - username: "scanner@sender.domain.tld"
    password: "SuperSecure#123"
    allow_senders:
      - "scanner@sender.domain.tld"
```

### 2. Run the Playbook

```yaml
- name: Setup SMTP relay
  hosts: mail_servers
  become: true
  roles:
    - role: teamapps.general.mailsender
```

### 3. Configure Your Device

Configure your scanner or device with:
- **SMTP server**: relay.sender.domain.tld
- **Port**: 587
- **Security**: STARTTLS
- **Username**: scanner@sender.domain.tld
- **Password**: SuperSecure#123

## Configuration Variables

### Essential Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `mailsender_hostname` | `"relay.sender.domain.tld"` | FQDN of the mail server |
| `mailsender_domain` | `"sender.domain.tld"` | Email domain |
| `mailsender_contact_email` | `"admin@sender.domain.tld"` | Contact email for Let's Encrypt |
| `mailsender_users` | `[]` | List of SMTP users (see below) |

### User Configuration

Each user in `mailsender_users` can have:

```yaml
mailsender_users:
  - username: "user@domain.tld"           # Required: SMTP username
    password: "plaintext-password"        # Required: Will be hashed automatically
    # OR provide a pre-hashed password:
    # password_hash: "{SHA512-CRYPT}$6$..."
    allow_senders:                        # Optional: Restrict sender addresses
      - "user@domain.tld"
      - "noreply@domain.tld"
```

### Additional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `mailsender_enable_ipv6` | `false` | Enable IPv6 support |
| `mailsender_message_size_limit` | `26214400` | Max message size (~25MB) |
| `mailsender_disable_inbound_smtp25` | `true` | Block inbound SMTP (port 25) |
| `mailsender_use_ufw` | `true` | Configure firewall with ufw |
| `mailsender_install_testing_tools` | `true` | Install swaks for testing |

## Testing

### Verify TLS Certificate

```bash
openssl s_client -connect relay.sender.domain.tld:587 -starttls smtp
```

### Test SMTP Authentication

```bash
swaks --server relay.sender.domain.tld --port 587 --tls \
      --auth LOGIN --auth-user scanner@sender.domain.tld \
      --auth-password 'SuperSecure#123' \
      --from scanner@sender.domain.tld \
      --to recipient@example.com
```

## DNS Configuration

### Required DNS Records

1. **A Record**:
   ```
   relay.sender.domain.tld.  IN  A  YOUR_SERVER_IP
   ```

2. **PTR Record** (set in your hosting provider's control panel):
   ```
   YOUR_SERVER_IP  PTR  relay.sender.domain.tld.
   ```

3. **SPF Record**:
   ```
   sender.domain.tld.  IN  TXT  "v=spf1 ip4:YOUR_SERVER_IP ~all"
   ```

## Troubleshooting

### Common Issues

1. **Certificate errors**: Ensure DNS A record is correct and port 80 is accessible
2. **Authentication failures**: Check user credentials and Dovecot logs
3. **Delivery issues**: Verify SPF records and PTR (reverse DNS) configuration
4. **Port blocked**: Ensure your cloud provider allows outbound SMTP (port 25)

### Log Files

- Postfix: `/var/log/postfix.log`
- Dovecot: `/var/log/dovecot.log`
- System: `journalctl -u postfix -u dovecot`

## Security Notes

- All SMTP submission requires TLS encryption and authentication
- Inbound SMTP (port 25) is blocked by default to prevent abuse
- User passwords are hashed with SHA512-CRYPT
- Sender address restrictions can be enforced per user
- Let's Encrypt certificates are automatically renewed

## License

This role is part of the teamapps.general collection and follows the same license.
