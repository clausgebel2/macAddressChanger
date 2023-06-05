#!/usr/bin/env python3

# Copyright 2024 Claus Gebel
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
import subprocess
from argparse import ArgumentParser


# Options that can be used when macAddressChanger is launched.
def get_terminal_arguments():
    parser = ArgumentParser(prog="macAddressChanger.py", description="Tool to change the MAC address of an interface.")
    parser.add_argument("-i", "--interface", help="Interface to change the MAC address.")
    parser.add_argument("-m", "--mac", help="The new MAC address.")
    if bool(parser.parse_args().interface) ^ bool(parser.parse_args().mac):
        return parser.error("Options --interface and --mac must be given together.")
    else:
        return parser.parse_args()


# Change MAC address
def change_mac_address(interface, mac_address):
    print("[+] MAC address for '" + interface + "' gets altered to " + mac_address + ".")
    subprocess.run(["ip", "link", "set", "dev", interface, "down"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.run(["ip", "link", "set", "dev", interface, "address", mac_address],
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.run(["ip", "link", "set", "dev", interface, "up"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


# Receive information of all interfaces
def get_ip_info():
    popen_result = subprocess.Popen(["ip", "address", "show"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    popen_result.wait()
    ip_result, ip_errors = popen_result.communicate()
    return ip_result, ip_errors


# Get MAC address of interface
def get_mac_address(interface):
    ip_result, ip_errors = get_ip_info()
    pattern = interface + r":.*? (\w\w(:\w\w){5}.*?)"
    mac_address = re.findall(rf"{pattern}", str(ip_result), re.DOTALL)
    return mac_address[0][0]


# Find out if MAC address of the interface is correct
def mac_address_exists(interface, mac_address):
    if get_mac_address(interface) == mac_address:
        return True
    else:
        return False


arguments = get_terminal_arguments()
if arguments.mac is None or arguments.interface is None:
    print("Enter './python macAddressChanger.py --help' for further information!")
    exit(-1)

print("The MAC address before changed is " + get_mac_address(arguments.interface) + ".")
change_mac_address(arguments.interface, arguments.mac)

if mac_address_exists(arguments.interface, arguments.mac):
    print("[+] MAC was successfully changed to " + arguments.mac + ".")
else:
    print("[-] MAC address could not be changed!")
