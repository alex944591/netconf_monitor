#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scrapli.driver.core import IOSXEDriver
from scrapli.driver.core import NXOSDriver
from scrapli.driver.core import EOSDriver
from scrapli.exceptions import ScrapliException
import yaml
import re
import sys
import os


def GetOutput(device: dict, check: dict):
    device_ip = device['host']
    command = check['command']
    service = check['service']
    device_platform = device.pop('platform')
    try:
        if device_platform == "ios":
            with IOSXEDriver(**device) as ssh:
                reply = ssh.send_command(command)
        elif device_platform == "eos":
            with EOSDriver(**device) as ssh:
                reply = ssh.send_command(command)
        elif device_platform == "nxos":
            with NXOSDriver(**device) as ssh:
                reply = ssh.send_command(command)
        else:
            print(f"WARNING: No available driver for ip:platform - "
                            f"{device_ip}:{device_platform}")
            return False
    except ScrapliException as error:
        print(f"ERROR: {error} has happened during {device['transport']} "
                      f"connection to {device_ip}")
        return

    if reply.failed:
        print(f"WARNING:Output from {device_ip} is not recieved!")
    else:
        output = reply.result.split('\n')
        for line in output:
            match1 = re.search(check['regexp1'], line)
            if match1:
                print('OK')
                return None

        for line in output:
            match2 = re.search(check['regexp2'], line)
            if match2:
                print('NOT OK')
                return None

        print('EMPTY')

def FindHostInInventory(host: str):
    with open(f'inventory.yml') as f:
    # with open('/usr/lib/zabbix/externalscripts/inventory.yml') as f:
        devices = yaml.safe_load(f)
    for device in devices:
        if device['host'] == host:
            return device
    return False

def FindExpInChecks(service: str):
    with open(f'checks.yml') as f:
    # with open('/usr/lib/zabbix/externalscripts/checks.yml') as f:
        services = yaml.safe_load(f)
    for check in services:
        if check['service'] == service:
            return check
    return False


def main():
    try:
        with open(f'credentials.yml') as f:
        # with open('/usr/lib/zabbix/externalscripts/credentials.yml') as f:
            cred = yaml.safe_load(f)
    except FileNotFoundError as error:
        print(f"ERROR: {error}")
        return

    host = sys.argv[1]
    service = sys.argv[2]

    device = FindHostInInventory(host)
    check = FindExpInChecks(service)

    if device:
        device['auth_username'] = cred['login']
        device['auth_password'] = cred['password']
        GetOutput(device, check)
    else:
        print(f"WARNING: Host {host} isnt in the inventory.yml file")

if __name__ == "__main__":
    main()
