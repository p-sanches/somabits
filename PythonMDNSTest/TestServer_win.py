#!/usr/bin/env python3

""" Example of resolving a service with a known name """

import logging
import sys
import socket

from typing import cast
from time import sleep
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

#TYPE = '_osc._udp.local.'
TYPE = '_osc._udp.local.'
NAME = 'Server'

def on_service_state_change(
    zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange,
) -> None:
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
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, TYPE, handlers=[on_service_state_change])

    try:
        while True:
            #print(zeroconf.get_service_info(TYPE, NAME + '.' + TYPE, timeout=30000))
            sleep(0.1)

    finally:
        zeroconf.close()