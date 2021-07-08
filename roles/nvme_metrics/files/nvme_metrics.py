#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Description: collect nvme metrics
# Author: pgassmann
# SPDX-License-Identifier: Apache 2.0

# NVME well explained: https://vatiminxuyu.gitbooks.io/xuyu/content/blog/nvme-what.html

import subprocess
import json
import argparse
import os
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def pretty_print_json(obj):
    json_formatted_str = json.dumps(obj, indent=4)
    print(json_formatted_str)


def get_nvme_list(device_path=""):

    proc = subprocess.Popen("/usr/sbin/nvme list %s -o json" % device_path,
                            shell=True,
                            stdout=subprocess.PIPE,
                            encoding='utf-8')
    err = proc.wait()

    (stdout, stderr) = proc.communicate()

    if proc.returncode != 0:
        eprint("nvme command failed %d %s %s" % (proc.returncode, stdout, stderr))
        json_data = {'error': "nvme command failed %d %s %s" % (
            proc.returncode, stdout, stderr)}
        exit(1)
    else:
        json_data = json.loads(stdout)

    return json_data


def get_smart_log(device_path):
    proc = subprocess.Popen("/usr/sbin/nvme smart-log %s -o json" % device_path,
                            shell=True,
                            stdout=subprocess.PIPE,
                            encoding='utf-8')
    err = proc.wait()

    (stdout, stderr) = proc.communicate()

    if proc.returncode != 0:
        eprint("nvme command failed %d %s %s" % (proc.returncode, stdout, stderr))
        json_data = {'error': "nvme command failed %d %s %s" % (
            proc.returncode, stdout, stderr)}
    else:
        json_data = json.loads(stdout)

    return json_data


def get_ctrl_regs(device_path):
    proc = subprocess.Popen("/usr/sbin/nvme show-regs %s -o json" % device_path,
                            shell=True,
                            stdout=subprocess.PIPE,
                            encoding='utf-8')
    err = proc.wait()

    (stdout, stderr) = proc.communicate()

    if proc.returncode != 0:
        eprint("nvme command failed %d %s %s" % (proc.returncode, stdout, stderr))
        json_data = {'error': "nvme command failed %d %s %s" % (
            proc.returncode, stdout, stderr)}
    else:
        json_data = json.loads(stdout)

    return json_data


def normalize_raw_data(smart_log_json, ctrl_json):
    normalized_data = {}

    # interpret bitfield critical_warning using bitshift
    if smart_log_json['critical_warning'] & 1:
        normalized_data['critical_warning_avail_spare'] = 1
    else:
        normalized_data['critical_warning_avail_spare'] = 0

    if smart_log_json['critical_warning'] & (1 << 1):
        normalized_data['critical_warning_temp_threshold'] = 1
    else:
        normalized_data['critical_warning_temp_threshold'] = 0

    if smart_log_json['critical_warning'] & (1 << 2):
        normalized_data['critical_warning_nvm_subsystem_reliability'] = 1
    else:
        normalized_data['critical_warning_nvm_subsystem_reliability'] = 0

    if smart_log_json['critical_warning'] & (1 << 3):
        normalized_data['critical_warning_read_only'] = 1
    else:
        normalized_data['critical_warning_read_only'] = 0

    if smart_log_json['critical_warning'] & (1 << 4):
        normalized_data['critical_warning_volatile_backup_failed'] = 1
    else:
        normalized_data['critical_warning_volatile_backup_failed'] = 0

    if smart_log_json['critical_warning'] & (1 << 5):
        normalized_data['critical_warning_persistent_memory_read_only'] = 1
    else:
        normalized_data['critical_warning_persistent_memory_read_only'] = 0

    normalized_data['temperature_celcius'] = round(
        smart_log_json['temperature'] - 273.15, 2)

    if not 'error' in ctrl_json:
        # cc = controller configuration
        if ctrl_json['cc'] & 1:
            normalized_data['controller_enabled'] = 1
        else:
            normalized_data['controller_enabled'] = 0
        # csts = controller status
        if ctrl_json['csts'] & 1:
            normalized_data['controller_ready'] = 1
        else:
            normalized_data['controller_ready'] = 1

    return normalized_data


def collect_nvme_data(nvme_list_json):

    nvme_data = []

    for nvme_info in nvme_list_json['Devices']:
        device_path = nvme_info['DevicePath']
        smart_log_json = get_smart_log(device_path)
        ctrl_regs_json = get_ctrl_regs(device_path)

        device_data = {
            'info': nvme_info,
            'smart_log': smart_log_json,
            'ctrl_regs': ctrl_regs_json,
            'normalized_data': normalize_raw_data(smart_log_json, ctrl_regs_json),
        }
        nvme_data.append(device_data)

    return nvme_data

def metric_entry(metric, labels, value):
    labels_string = ', '.join(labels)
    return "%s{%s} %s"%(metric, labels_string, value)

def print_prometheus_metrics(nvme_data):

    for nvme_device in nvme_data:
        labels = [
            'device="%s"'%nvme_device['info']['DevicePath'],
        ]

        info_labels = labels.copy()
        for info_key in ['ProductName','ModelNumber', 'SerialNumber', 'Firmware']:
            info_labels += [
                '%s="%s"'%(info_key, nvme_device['info'][info_key])
            ]
        print(metric_entry('nvme_info',  info_labels, 1))

        print(metric_entry('nvme_sector_size',  labels, nvme_device['info']['SectorSize']))
        print(metric_entry('nvme_used_bytes',  labels, nvme_device['info']['UsedBytes']))
        print(metric_entry('nvme_physical_size',  labels, nvme_device['info']['PhysicalSize']))
        print(metric_entry('nvme_maximum_lba',  labels, nvme_device['info']['MaximumLBA']))

        for normalized_metric in [
            "critical_warning_avail_spare",
            "critical_warning_temp_threshold",
            "critical_warning_nvm_subsystem_reliability",
            "critical_warning_read_only",
            "critical_warning_volatile_backup_failed",
            "critical_warning_persistent_memory_read_only",
            'controller_enabled',
            'controller_ready',
        ]:
            if normalized_metric in nvme_device['normalized_data']:
                print(metric_entry('nvme_%s'%normalized_metric,  labels, nvme_device['normalized_data'][normalized_metric]))

        smart_metrics = [
            # "critical_warning",
            # "temperature",
            "avail_spare",
            "spare_thresh",
            "percent_used",
            "data_units_read",
            "data_units_written",
            "host_read_commands",
            "host_write_commands",
            "controller_busy_time",
            "power_cycles",
            "power_on_hours",
            "unsafe_shutdowns",
            "media_errors",
            "num_err_log_entries",
            "warning_temp_time",
            "critical_comp_time",
            "thm_temp1_trans_count",
            "thm_temp2_trans_count",
            "thm_temp1_total_time",
            "thm_temp2_total_time"
        ]
        for smart_metric in smart_metrics:
            print(metric_entry('nvme_smart_%s'%smart_metric,  labels, nvme_device['smart_log'][smart_metric]))


def parse_args():
    parser = argparse.ArgumentParser(
        description='NVME Metrics'
    )
    parser.add_argument(
        '-d', '--device',
        required=False,
        type=str,
        help='Device to read, all if emtpy',
        dest='device',
        default=''
    )
    parser.add_argument(
        '-o', '--output',
        required=False,
        choices=('json', 'prometheus'),
        type=str,
        help='Format',
        dest='output',
        default='json'
    )
    return parser.parse_args()

if __name__ == '__main__':


    try:
        args = parse_args()
        # nvme_list_json = get_nvme_list("/dev/nmve0")
        nvme_list_json = get_nvme_list(args.device)
        if args.output == 'json':
            nvme_data = collect_nvme_data(nvme_list_json)
            pretty_print_json(nvme_data)
        if args.output == 'prometheus':
            nvme_data = collect_nvme_data(nvme_list_json)
            print_prometheus_metrics(nvme_data)


    except KeyboardInterrupt:
        print("\nInterrupted")
        exit(0)


    # pretty_print_json(nvme_list_json)

    # smart_log_json = get_smart_log("/dev/nmve0")
    # print_smart_log(smart_log_json)
    # pretty_print_json(smart_log_json)

    # ctrl_regs_json = get_ctrl_regs("/dev/nmve0")
    # pretty_print_json(ctrl_regs_json)

    # nvme_data = collect_nvme_data(nvme_list_json)
    # pretty_print_json(nvme_data)
    # print_prometheus_metrics(nvme_data)
