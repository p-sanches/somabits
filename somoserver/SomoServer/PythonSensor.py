#!/usr/bin/env python

"https://github.com/jstasiak/python-zeroconf/blob/master/examples/registration.py"

""" Example of announcing a service (in this case, a fake HTTP server) """

import logging
import socket
import ifaddr
import sys
from time import sleep
import numpy as np

from pythonosc import udp_client

from zeroconf import ServiceInfo, Zeroconf
from typing import List

def get_all_addresses() -> List[str]:
    return list(set(
        addr.ip
        for iface in ifaddr.get_adapters()
        for addr in iface.ips
        if addr.is_IPv4 and addr.network_prefix != 32  # Host only netmask 255.255.255.255
    ))


def get_local_ip(starts_with="192"):
    list_ip = get_all_addresses()
    local_ip = [i for i in list_ip if i.startswith(starts_with)]
    return local_ip[0]


def send_sensor_values(sensor_state_, sensor_direction_, server):
    sensor_state = sensor_state_
    sensor_direction = sensor_direction_

    client = udp_client.SimpleUDPClient(server, int(3333))

    while True:
        if sensor_state == 0:
            sensor_direction = 1
        elif sensor_state == 100:
            sensor_direction = 0

        if sensor_direction == 0:
            # not pressed
            sensor_state -= 1
        else:
            # pressed
            sensor_state += 1

        client.send_message("/pressure", float(sensor_state))
        print("Value = %s, Direction = %s" % (sensor_state, sensor_direction))
        sleep(0.1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    initial_sensor_state = np.random.random_integers(0, 100)
    print("Initial sensor state: %s" % initial_sensor_state)
    sensor_direction = np.random.random_integers(0,1)
    print("Initial sensor direction: %s" % sensor_direction)

    desc = {'sensor1': '/pressure:0%100'}

    info = ServiceInfo(type_="_osc._udp.local.",
                       name="PythonSensor._osc._udp.local.",
                       address=socket.inet_aton(get_local_ip()),
                       port=3335,
                       weight=0,
                       priority=0,
                       properties=desc,
                       server="PythonSensor.local.")

    zeroconf = Zeroconf()
    print("Registration of a service PythonSensor")
    zeroconf.register_service(info)

    print("Opening a TCP connection")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(get_local_ip())
    s.bind((str(get_local_ip()), 5555))
    s.listen()

    conn, addr = s.accept()
    print("Connection address:  " + str(addr))

    server_ip = ""
    while True:
        data = conn.recv(20)
        if not data:
            break
        server_ip = str(data.decode())
        print("Server IP is: " + str(data.decode()))

    while True:
        try:
            send_sensor_values(initial_sensor_state, sensor_direction, server_ip)
        except:
            pass

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()
