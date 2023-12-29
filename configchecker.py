#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

from scrapli.driver.core import IOSXEDriver
from scrapli.driver.core import NXOSDriver
from scrapli.driver.core import EOSDriver
from scrapli.exceptions import ScrapliException
import yaml
import logging
import re
from sys import argv
from sys import platform
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
            logging.warning(f"No available driver for ip:platform - "
                            f"{device_ip}:{device_platform}")
            return False
    except ScrapliException as error:
        logging.error(f"ERROR: {error} has happened during {device['transport']} "
                      f"connection to {device_ip}")

    #Check if a reply isn't failed. If so - return the result.
    if reply.failed:
        logging.warning(f"Output from {device_ip} is not recieved!")
    else:
        output = reply.result.split('\n')
        for line in output:
            match1 = re.search(check['regexp1'], line)
            if match1:
                #print(f"<<{service} config correct on the {device_ip}>>\n")
                print('OK')
                return None

        for line in output:
            match2 = re.search(check['regexp2'], line)
            if match2:
                #print(f"<<{service} isn't correct on the {device_ip}>>\n")
                print('NOT OK')
                return None

        #print(f"<<Empty {service} config section on the {device_ip}>>\n")
        print ('EMPTY')

def FindHostInInventory(host: str, cwd: str):
    with open(f'{cwd}inventory.yml') as f:
        devices = yaml.safe_load(f)
    for device in devices:
        if device['host'] == host:
            return device
    return False

def FindExpInChecks(service: str, cwd: str):
    with open(f'{cwd}checks.yml') as f:
        services = yaml.safe_load(f)
    for check in services:
        if check['service'] == service:
            return check
    return False


def main():
    cwd = os.getcwd()
    if 'linux' in platform:
        cwd = cwd + '/'
    else:
        cwd = cwd + '\\'

    logging.basicConfig(filename=f'{cwd}journal.log', format='{asctime} {levelname} {message}',
                        level=logging.INFO, style='{', datefmt='%Y-%m-%d %H:%M')

    #LOGIN = os.environ.get('LOGIN_REMOTE_ACCESS')
    #PASSWORD = os.environ.get('PASS_REMOTE_ACCESS')

    LOGIN = 'kolenkoay'
    PASSWORD = '1q2w3e4r%'

    host = argv[1]
    service = argv[2]

    device = FindHostInInventory(host, cwd)
    check = FindExpInChecks(service, cwd)

    if device:
        device['auth_username'] = LOGIN
        device['auth_password'] = PASSWORD
        GetOutput(device, check)
        #result = GetOutput(device, check)
        #return result
    else:
        logging.warning(f"Host {host} isnt in the inventory.yml file")

if __name__ == "__main__":
    main()
