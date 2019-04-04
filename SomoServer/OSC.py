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

        client_IP=address[0]
        client_Port = address[1]
        address_client = args[0]
        message=args[1]
        print("Client IP= %s" % (address[0]))
        print("Client Port= %s" % (address[1]))
        print("Address= %s" % (args[0]))
        print("Message= %s" % (args[1]))

        for rows in range(len(self.TABLE_FORWARDING)):
            if (self.TABLE_FORWARDING.iloc[rows]['Sensor Address'] == address_client & self.TABLE_FORWARDING.iloc[rows]['Sensor IP']==client_IP):
                sensor_range=self.TABLE_FORWARDING.iloc[rows]['Sensor Range'].split("-")
                actuator_range = self.TABLE_FORWARDING.iloc[rows]['Actuator Range'].split("-")
                value= self.maprange((float(sensor_range[0]), float(sensor_range[1])), (float(actuator_range[0]), float(actuator_range[1])), float(message))
                client = udp_client.SimpleUDPClient(self.TABLE_FORWARDING.iloc[rows]['Actuator IP'], self.TABLE_FORWARDING.iloc[rows]['Actuator Port'])
                client.send_message(self.TABLE_FORWARDING.iloc[rows]['Actuator Address'], value)

    def maprange(a, b, s):
        (a1, a2), (b1, b2) = a, b
        return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))



