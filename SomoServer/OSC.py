
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
from PyQt5.QtCore import QThread


class getOSCMessages(QThread):

    def __init__(self, IP=None , Port=None,soma=None):
        QThread.__init__(self)
        self.IP=IP
        self.Port = Port
        self.soma= soma
        self.TABLE_FORWARDING=soma.TABLE_FORWARDING
        self.dispatcher_osc = dispatcher.Dispatcher()
        self.dispatcher_osc.set_default_handler(self.OSC_handler, True)

        self.server = osc_server.ThreadingOSCUDPServer((self.IP, self.Port), self.dispatcher_osc)

    def __del__(self):
        self.wait()

    def run(self):

        print("Serving on {}".format(self.server.server_address))
        self.server.serve_forever()

    def OSC_stop(self):

        self.soma.ui.StartOSC.setEnabled(True)
        self.soma.ui.StartOSC.setStyleSheet("background-color: rgb(170, 255, 127);\n"
                                    "font: 63 10pt \"Adobe Fan Heiti Std B\";\n"
                                    "color: rgb(0, 0, 0);")
        self.soma.ui.tableView_2.setEnabled(True)
        self.soma.ui.tableView.setEnabled(True)
        self.soma.ui.discover_button.setEnabled(True)
        self.soma.ui.save_button.setEnabled(True)
        self.soma.ui.StopOSCButton.setEnabled(False)
        self.soma.ui.StopOSCButton.setStyleSheet(
            "background-color: gray;""font: 63 10pt \"Adobe Fan Heiti Std B\";""color: rgb(255, 255, 255);");
        self.server.server_close()
        self.terminate()

    def OSC_handler(self,address, *args):
        client_IP=address[0]
        client_Port = address[1]
        address_client = args[0]
        message=args[1]
        #print("Client IP= %s" % (address[0]))
        #print("Client Port= %s" % (address[1]))
        #print("Address= %s" % (args[0]))
        #print("Message= %s" % (args[1]))

        for rows in range(len(self.TABLE_FORWARDING)):
            if (self.TABLE_FORWARDING.iloc[rows]['Sensor Address'] == address_client and self.TABLE_FORWARDING.iloc[rows]['Sensor IP']==client_IP):
                sensor_range=self.TABLE_FORWARDING.iloc[rows]['Sensor Range'].split("%")
                actuator_range = self.TABLE_FORWARDING.iloc[rows]['Actuator Range'].split("%")
                value= self.maprange((float(sensor_range[0]), float(sensor_range[1])), (float(actuator_range[0]), float(actuator_range[1])), float(message))
                #client = udp_client.SimpleUDPClient(str(self.TABLE_FORWARDING.iloc[rows]['Actuator IP']),
                #                                    int(5008))
                client = udp_client.SimpleUDPClient(str(self.TABLE_FORWARDING.iloc[rows]['Actuator IP']), int(self.TABLE_FORWARDING.iloc[rows]['Actuator Port']))
                #client = udp_client.SimpleUDPClient("192.168.11.103",
                #                                    int(self.TABLE_FORWARDING.iloc[rows]['Actuator Port']))
                client.send_message(self.TABLE_FORWARDING.iloc[rows]['Actuator Address'], value)
                print("Value= %s" % value)
                print("IP= %s" % self.TABLE_FORWARDING.iloc[rows]['Actuator IP'])
                print("Port= %s" % int(self.TABLE_FORWARDING.iloc[rows]['Actuator Port']))
                print("Path= %s" % self.TABLE_FORWARDING.iloc[rows]['Actuator Address'])

    def maprange(self, a, b, s):
        (a1, a2), (b1, b2) = a, b
        return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))



