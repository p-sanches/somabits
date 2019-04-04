from pythonosc import osc_message_builder
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio

from PyQt5.QtCore import QThread


class getOSCMessages(QThread):

    def __init__(self, IP=None , Port=None):
        QThread.__init__(self)
        self.IP=IP
        self.Port = Port

    def __del__(self):
        self.wait()

    def run(self):
        self.dispatcher_osc = dispatcher.Dispatcher()
        self.dispatcher_osc.set_default_handler(self.OSC_handler)
        self.server = osc_server.ThreadingOSCUDPServer((self.IP, self.Port), self.dispatcher_osc)
        print("Serving on {}".format(self.server.server_address))
        self.server.serve_forever()

    def OSC_handler(address, *args):
        print(f"{address}: {args}")
        # client = udp_client.SimpleUDPClient(args.ip, args.port)
        # client.send_message("/filter", 1)