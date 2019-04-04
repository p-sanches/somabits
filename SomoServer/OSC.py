from pythonosc import osc_message_builder
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import logging
import sys
import socket

from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio

from PyQt5.QtCore import QThread


class getOSCMessages(QThread):

    def __init__(self, IP=None , Port=None,soma=None):
        QThread.__init__(self)
        self.IP=IP
        self.Port = Port
        self.TABLE_FORWARDING=soma.TABLE_FORWARDING

    def __del__(self):
        self.wait()

    def run(self):
        self.dispatcher_osc = dispatcher.Dispatcher()
        self.dispatcher_osc.set_default_handler(self.OSC_handler,True)

        self.server = osc_server.ThreadingOSCUDPServer((self.IP, self.Port), self.dispatcher_osc)
        print("Serving on {}".format(self.server.server_address))
        self.server.serve_forever()

    def OSC_handler(self,address, *args):

        print("Client IP= %s" % (address[0]))
        print("Client Port= %s" % (address[1]))
        print("Address= %s" % (args[0]))
        print("Message= %s" % (args[1]))
        print(self.TABLE_FORWARDING)


