#!/usr/bin/env python3

# Copyright 2023 Claus Gebel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import os
import subprocess
from argparse import ArgumentParser


# Options that can be used when macAddressChanger is launched.
def get_terminal_arguments():
    parser = ArgumentParser(prog="macAddressChanger.py", description="Tool to change the MAC address of an interface.")
    parser.add_argument("-i", "--interface", help="Interface to change the MAC address.")
    parser.add_argument("-m", "--mac", help="with -i, change MAC address.")
    parser.add_argument("-si", "--show_info", action="store_true", help = "Shows the interfaces and MAC addresses.")
    if bool(parser.parse_args().interface) ^ bool(parser.parse_args().mac):
        return parser.error("Options --interface and --mac must be given together.")
    else:
        return parser.parse_args()


# Change MAC address
def change_mac_address(interface, mac_address):
    print("[+] MAC address for '" + interface + "' gets altered to " + mac_address + ".")
    subprocess.Popen(["ip", "link", "set", "dev", interface, "down"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.Popen(["ip", "link", "set", "dev", interface, "address", mac_address],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT).wait()
    subprocess.Popen(["ip", "link", "set", "dev", interface, "up"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


# Receive information of all interfaces
def get_ip_info():
    popen_result = subprocess.Popen(["ip", "address", "show"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen_result.wait()
    ip_result, ip_errors = popen_result.communicate()
    return ip_result, ip_errors


# Get MAC address of interface
def get_mac_address(interface):
    ip_result, ip_errors = get_ip_info()
    pattern = interface + r":.*? ([0-9a-fA-F]{2}(:[0-9a-fA-F][0-9a-fA-F]){5}.*?)"
    mac_address = re.findall(rf"{pattern}", str(ip_result), re.DOTALL)
    return mac_address[0][0]


# Find out if MAC address of the interface is correct
def mac_address_exists(interface, mac_address):
    if get_mac_address(interface) == mac_address:
        return True
    else:
        return False

# Show all active interfaces and their MAC addresses
def getInfo():
    ip_result, ip_errors = get_ip_info()
    print("Interfaces:\tMAC Adresses:")
    print("-----------\t-------------")
    pattern = r"[0-9]+: (\w+): <.+?([0-9a-fA-F]{2}(:[0-9a-fA-F][0-9a-fA-F]){5}.*?)"
    filtered = re.findall(rf"{pattern}", str(ip_result), re.DOTALL)
    for r in filtered:
        print(r[0] + "\t\t" + r[1])

def root_check():
    if os.geteuid() != 0:
        exit("You need to have root privileges. Program halted.")


arguments = get_terminal_arguments()
if (arguments.mac is None or arguments.interface is None) and arguments.show_info is None:
    print("Enter './python macAddressChanger.py --help' for further information!")
    exit(-1)

if not arguments.mac is None and not arguments.interface is None or arguments.show_info is None:
    root_check()
    print("The MAC address before changed is " + get_mac_address(arguments.interface) + ".")
    change_mac_address(arguments.interface, arguments.mac)

    if mac_address_exists(arguments.interface, arguments.mac):
        print("[+] MAC was successfully changed to " + arguments.mac + ".")
    else:
        print("[-] MAC address could not be changed!")
elif arguments.show_info == True:
    getInfo()
else:
    print("Enter './python macAddressChanger.py --help' for further information!")
    exit(-1)