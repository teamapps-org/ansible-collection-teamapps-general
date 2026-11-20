# Hardware sensors

Loads the Super-I/O sensor driver of bare-metal hosts, so node_exporter's hwmon collector exports mainboard fan
speeds and fan-control state.

## What it does

For each driver in `hardware_sensors_candidate_modules`, the role runs `community.general.modprobe` with
`persistent: present`:

- a driver whose chip is on the board is loaded and written to `/etc/modules-load.d/<driver>.conf`
- a driver whose chip is not on the board fails with "No such device" (or "Device or resource busy" when ACPI owns
  the chip) and is skipped; any other error fails the task

No per-host or per-board configuration is needed, and a replaced board is picked up by the next run. A driver file
is not removed when a later board no longer has that chip; remove it by hand.

The driver only reads the chip. Fan control stays with the mainboard unless something writes to `pwm*` in sysfs.

On some server boards the fan headers are wired to the BMC, not the Super-I/O chip: the driver loads, but every fan
input reads 0 RPM. Those fans can only be read through the BMC (IPMI), and only if it has a host interface.

node_exporter's hwmon collector (enabled by default) then exports the chip's readings, among them
`node_hwmon_fan_rpm`, `node_hwmon_pwm` (duty 0–255) and `node_hwmon_pwm_enable` (control mode), with `chip` and
`sensor` labels. CPU temperature drivers (`k10temp`, `coretemp`) load automatically.

Requires the `community.general` collection.

## Variables

| Variable                             | Default     | Purpose                         |
| ------------------------------------ | ----------- | ------------------------------- |
| `hardware_sensors_candidate_modules` | `[nct6775]` | Super-I/O sensor drivers to load |

`nct6775` covers the Nuvoton NCT67xx chips. Other chip families need their driver added, for example `it87` for ITE
chips.

## Usage example

```yaml
- name: hardware sensors play
  vars:
    # physical servers only: VMs have no sensor chips
    manage_hardware_sensors: '{{ ansible_facts.virtualization_role in ["host", "NA"] }}'
  hosts: all:!nodefault
  roles:
    - role: teamapps.general.hardware_sensors
      tags: hardware_sensors
      when: manage_hardware_sensors | default(false)
```

## Alerts

The `victoriametrics` role ships alert rules for these metrics in
[hardware.rules.yml](../victoriametrics/files/rules/hardware.rules.yml).
