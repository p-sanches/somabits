
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_bundle_builder
from pythonosc import osc_message_builder
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
        msg_x = args[2]
        msg_y = args[4]
        msg_z = args[6]

        for rows in range(len(self.TABLE_FORWARDING)):
            if (self.TABLE_FORWARDING.iloc[rows]['Sensor Address'] == address_client and self.TABLE_FORWARDING.iloc[rows]['Sensor IP']==client_IP):
                sensor_range = self.TABLE_FORWARDING.iloc[rows]['Sensor Range'].split("%")
                actuator_range = self.TABLE_FORWARDING.iloc[rows]['Actuator Range'].split("%")
                # Map values
                value_x = self.maprange((float(sensor_range[0]), float(sensor_range[1])),
                                        (float(actuator_range[0]), float(actuator_range[1])), float(msg_x))
                value_y = self.maprange((float(sensor_range[0]), float(sensor_range[1])),
                                        (float(actuator_range[0]), float(actuator_range[1])), float(msg_y))
                value_z = self.maprange((float(sensor_range[0]), float(sensor_range[1])),
                                        (float(actuator_range[0]), float(actuator_range[1])), float(msg_z))
                # Send values
                client = udp_client.SimpleUDPClient(str(self.TABLE_FORWARDING.iloc[rows]['Actuator IP']), int(self.TABLE_FORWARDING.iloc[rows]['Actuator Port']))

                bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
                msg = osc_message_builder.OscMessageBuilder(address=self.TABLE_FORWARDING.iloc[rows]['Actuator Address'])
                msg.add_arg("/X")
                bundle.add_content(msg.build())
                msg.add_arg(value_x)
                bundle.add_content(msg.build())
                msg.add_arg("/Y")
                bundle.add_content(msg.build())
                msg.add_arg(value_y)
                bundle.add_content(msg.build())
                msg.add_arg("/Z")
                bundle.add_content(msg.build())
                msg.add_arg(value_z)
                bundle.add_content(msg.build())
                bundle = bundle.build()
                print(bundle)
                client.send(bundle)

                #client.send_message(str(self.TABLE_FORWARDING.iloc[rows]['Actuator Address']) + "/X", value_x)
                #client.send_message(str(self.TABLE_FORWARDING.iloc[rows]['Actuator Address']) + "/Y", value_y)
                #client.send_message(str(self.TABLE_FORWARDING.iloc[rows]['Actuator Address']) + "/X", value_z)

                print("X = %s, Y = %s, Z = %s" % value_x, value_y, value_z)

    def maprange(self, a, b, s):
        (a1, a2), (b1, b2) = a, b
        return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))



