"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.

The code was initially copied from from https://pypi.org/project/python-osc/

"""

__author__ = "Martina Brachmann"
__email__  = "martina.brachmann.uni@gmail.com"

import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="192.168.11.130", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/light", print)
    dispatcher.map("/accelerometer", print)
    dispatcher.map("/oscControl/slider4", print)
    dispatcher.map("/oscControl/toggle1", print)
    dispatcher.map("/toggle1", print)
    # Test UNO Wifi Board
    dispatcher.map("/test", print)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
