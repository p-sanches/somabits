#!/usr/bin/env python3

""" Example of resolving a service with a known name """

import logging
import sys
import socket
import os

from typing import cast
from time import sleep
from zeroconf import ServiceInfo, ServiceBrowser, ServiceStateChange, Zeroconf

TYPE = "_osc._udp.local."
NAME = ""


def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        #fd = sys.stdin.fileno()
        fd = sys.stdin

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

def simulate_save_button():
    TXT_record = {'server': str(len(browser.services))}

    # TODO: Check if a service has timed out. If so, unregister device.

    for i, service in enumerate(browser.services.items()):
        print(service)
        record = str(service[1]).replace('[', ", ").replace(']', ", ").split(',')
        record_name = record[len(record) - 2]

        info  = zeroconf.get_service_info(TYPE, record_name)
        if info:
            TXT_record.update({'name' + str(i): info.server})
        else:
            print("Service type not found")

    info = ServiceInfo(type_="_osc._udp.local.",
                       name=NAME + "." + TYPE,
                       address=socket.inet_aton("192.168.11.172"),
                       port=80,
                       weight=0,
                       priority=0,
                       properties=TXT_record,
                       server=NAME + ".local.")

    print("Registration of a service")
    zeroconf.register_service(info)



def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange,) -> None:
    print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        if info:
            print("  Address: %s:%d" % (socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port)))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print("  Server: %s" % (info.server,))
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print("    %s: %s" % (key, value))
            else:
                print("  No properties")
        else:
            print("  No info")
        print('\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 2:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    elif len(sys.argv) > 1:
        NAME = sys.argv[1]

    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, TYPE, handlers=[on_service_state_change])

    try:
        while True:
            key = wait_key()
            if key != None:
                simulate_save_button()
            else:
                sleep(0.1)
    finally:
        zeroconf.close()
