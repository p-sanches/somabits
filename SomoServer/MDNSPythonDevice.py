#!/usr/bin/env python

"https://github.com/jstasiak/python-zeroconf/blob/master/examples/registration.py"

""" Example of announcing a service (in this case, a fake HTTP server) """

import logging
import socket
import sys
from time import sleep

from zeroconf import ServiceInfo, Zeroconf

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    desc = {'sensor1': '/light:0-127', 'sensor2': '/accelerometer', 'actuator1': '/sound'}

    info = ServiceInfo(type_="_osc._udp.local.",
                       #name="Paul's Test Web Site._http._udp.local.",
                       name="PythonDevice._osc._udp.local.",
                       #name="Server._osc._udp.local.",
                       address=socket.inet_aton("192.168.11.172"),
                       port=80,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="PythonDevice.local.")

    zeroconf = Zeroconf()
    print("Registration of a service, press Ctrl-C to exit...")
    zeroconf.register_service(info)
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()