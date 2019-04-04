import logging
import sys
import socket
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal, QModelIndex)

# TODO: Fix the checkbox color

from SomoServer.gui import Ui_MainWindow
from SomoServer.TableModel import PandasModel, CheckBoxDelegate
from SomoServer.ZeroConf import NeighborDiscovery
from SomoServer.OSC import getOSCMessages



from typing import cast
from zeroconf import ServiceInfo,ServiceBrowser, ServiceStateChange, Zeroconf
from typing import List

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

class StartQT5(QtWidgets.QMainWindow):
    def __init__(self):
        super(StartQT5, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.discover_button.clicked.connect(self.zeroconf_start)
        self.ui.save_button.clicked.connect(self.start_forwarding)
        self.ui.StartOSC.clicked.connect(self.start_OSC)
        self.btn_stop.clicked.connect(self.stop_OSC)
        self.TABLE_INFO = pd.DataFrame(columns=['Address', 'Port', 'Host Name', 'Device Count', 'Device Type', 'Device Address', 'Device Range', 'ServiceName','isSelected','isServer', 'isTaken', '*'])
        self.TABLE_INFO_CHECKBOX = 11
        self.TABLE_FORWARDING = pd.DataFrame(columns=['Sensor Address', 'Sensor IP', 'Sensor Port', 'Sensor Range', 'Actuator Address', 'Actuator IP', 'Actuator Port','Actuator Range'])

        self.model = PandasModel(self.TABLE_INFO, checkbox=self.TABLE_INFO_CHECKBOX, signal_values_of_interest=['Address', 'Host Name'])
        self.model.pandas_signal.connect(self.handleCheckboxClicked)

        self.ui.tableView.setModel(self.model)
        self.ui.tableView.hideColumn(7)
        self.ui.tableView.hideColumn(8)
        self.ui.tableView.hideColumn(9)
        self.ui.tableView.hideColumn(10)
        delegate = CheckBoxDelegate(self)
        self.ui.tableView.setItemDelegateForColumn(self.TABLE_INFO_CHECKBOX, delegate)

    def stop_OSC(self):
        self.ui.StartOSC.setEnabled(True)
        self.ui.tableView_2.setEnabled(True)
        self.ui.tableView.setEnabled(True)
        self.ui.discover_button.setEnabled(True)
        self.ui.save_button.setEnabled(True)
        self.ui.StopOSCButton.setEnabled(False)

    def start_OSC(self):
        self.get_thread = getOSCMessages(NeighborDiscovery().get_local_ip(),3333,self)
        self.get_thread.start()
        self.ui.StartOSC.setEnabled(False)
        self.ui.tableView_2.setEnabled(False)
        self.ui.tableView.setEnabled(False)
        self.ui.discover_button.setEnabled(False)
        self.ui.save_button.setEnabled(False)
        self.ui.StopOSCButton.setEnabled(True)
        self.get_thread.terminate




    def ForwardCheckboxClicked(self):
        Checkbox = QtWidgets.qApp.focusWidget()
        if Checkbox.isChecked():
            sensors,sensors_IP,sensors_Port,sensors_Range = str(Checkbox.accessibleName()).split(":")
            actuators, actuators_IP, actuators_Port, actuators_Range = str(Checkbox.accessibleDescription()).split(":")
            self.TABLE_FORWARDING.loc[len(self.TABLE_FORWARDING)] =[sensors,sensors_IP,sensors_Port,sensors_Range,actuators, actuators_IP, actuators_Port, actuators_Range]
            print(self.TABLE_FORWARDING)
        else:
            sensors, sensors_IP, sensors_Port, sensors_Range = str(Checkbox.accessibleName()).split(":")
            actuators, actuators_IP, actuators_Port, actuators_Range = str(Checkbox.accessibleDescription()).split(":")
            indexNames = self.TABLE_FORWARDING[(self.TABLE_FORWARDING['Sensor Address'] == sensors) & (self.TABLE_FORWARDING['Sensor IP'] == sensors_IP) & (self.TABLE_FORWARDING['Sensor Port'] == sensors_Port) & (self.TABLE_FORWARDING['Sensor Range'] == sensors_Range) & (self.TABLE_FORWARDING['Actuator Address'] == actuators) & (self.TABLE_FORWARDING['Actuator IP'] == actuators_IP) & (self.TABLE_FORWARDING['Actuator Port'] == actuators_Port) & (self.TABLE_FORWARDING['Actuator Range'] == actuators_Range)].index
            self.TABLE_FORWARDING.drop(indexNames, inplace=True)
            print(self.TABLE_FORWARDING)


    def start_forwarding(self):

        sensors = []
        sensors_IP = []
        sensors_Port = []
        sensors_Range = []
        actuators = []
        actuators_IP = []
        actuators_Port = []
        actuators_Range = []
        forward_table=pd.DataFrame()
        for rows in range(len(self.TABLE_INFO)):
            for devices in range(self.TABLE_INFO.iloc[rows]['Device Count']):

                if(self.TABLE_INFO.iloc[rows]['isSelected']==True):
                    if('sensor' in str(self.TABLE_INFO.iloc[rows]['Device Type'][devices])):
                        sensors.append(self.TABLE_INFO.iloc[rows]['Device Address'][devices])
                        sensors_IP.append(self.TABLE_INFO.iloc[rows]['Address'])
                        sensors_Port.append(self.TABLE_INFO.iloc[rows]['Port'])
                        sensors_Range.append(self.TABLE_INFO.iloc[rows]['Device Range'][devices])
                    else:
                        actuators.append(self.TABLE_INFO.iloc[rows]['Device Address'][devices])
                        actuators_IP.append(self.TABLE_INFO.iloc[rows]['Address'])
                        actuators_Port.append(self.TABLE_INFO.iloc[rows]['Port'])
                        actuators_Range.append(self.TABLE_INFO.iloc[rows]['Device Range'][devices])

        forward_table = pd.DataFrame(index=sensors,columns=actuators)
        model=PandasModel(forward_table)
        self.ui.tableView_2.setModel(model)

        for rows in range(model.rowCount()):
            for column in range(model.columnCount()):
                self.Checkbox = QtWidgets.QCheckBox(' ')
                sensor_data = str(sensors[rows]) + ':' + str(sensors_IP[rows]) + ':' + str(sensors_Port[rows]) + ':' + str(sensors_Range[
                    rows])
                actuator_data = str(actuators[column]) + ':' + str(actuators_IP[column]) + ':' + str(actuators_Port[column]) + ':' + str(actuators_Range[
                    column])
                self.Checkbox.setAccessibleName(sensor_data)
                self.Checkbox.setAccessibleDescription(actuator_data)
                self.Checkbox.clicked.connect(self.ForwardCheckboxClicked)

                checkBoxWidget = QtWidgets.QWidget()
                layoutCheckBox = QtWidgets.QHBoxLayout(checkBoxWidget)
                layoutCheckBox.addWidget(self.Checkbox)
                layoutCheckBox.setAlignment(Qt.AlignCenter);

                item = model.index(rows, column )
                self.ui.tableView_2.setIndexWidget(item, self.Checkbox)

        self.ui.tableView_2.setModel(model)

    def resizeEvent(self, event):
        tableSize = self.ui.tableView.width()  # Retrieves your QTableView width
        sideHeaderWidth = self.ui.tableView.verticalHeader().width()  # Retrieves the left header width
        tableSize -= sideHeaderWidth  # Perform a substraction to only keep all the columns width
        numberOfColumns = self.model.columnCount()  # Retrieves the number of columns

        for columnNum in range(self.model.columnCount()):  # For each column
            self.ui.tableView.setColumnWidth(columnNum,
                                     int(tableSize / numberOfColumns))  # Set the width = tableSize / nbColumns
        super(StartQT5, self).resizeEvent(event)  # Restores the original behaviour of the resize event

    def update_view(self):
        self.model.update()
        for row in range(self.model.rowCount()):
            self.ui.tableView.setRowHidden(row, False)

        df = self.TABLE_INFO[self.TABLE_INFO["isServer"] == True]
        rows_to_hide = df.index.values.tolist()
        df = self.TABLE_INFO[self.TABLE_INFO["isTaken"] == True]
        rows_to_hide.append(df.index.values.tolist())

        comps = []
        for sublist in rows_to_hide:
            if type(sublist) is list:
                for item in sublist:
                    comps.append(item)
            else:
                comps.append(sublist)

        if len(comps) > 0:
            for row in comps:
                self.ui.tableView.setRowHidden(row, True)
        self.model.update()

    def handleCheckboxClicked(self, value, ip, host):
        if value is 1:
            self.discovery.register_service(ip, host)
        elif value is 0:
            self.discovery.unregister_service(ip, host)

    def handleServiceAdded(self, info, name):
        device_type = []
        device_address = []
        device_range = []

        device_ip = socket.inet_ntoa(cast(bytes, info.address))

        self.ui.plainTextEdit.appendPlainText(
            "  Address: %s:%d" % (device_ip, cast(int, info.port)))
        self.ui.plainTextEdit.appendPlainText(
            "  Weight: %d, priority: %d" % (info.weight, info.priority))
        self.ui.plainTextEdit.appendPlainText("  Server: %s" % (info.server,))

        if info.properties:
            self.ui.plainTextEdit.appendPlainText("  Properties are:")

            for key, value in info.properties.items():
                self.ui.plainTextEdit.appendPlainText("    %s: %s" % (key, value))
                key_str = str(key).split("'")[1]
                device_type.append(key_str)
                if ":" in str(value):
                    # the device has sensor values
                    value_str = str(value).split("'")[1].split(':')
                    device_address.append(value_str[0])
                    device_range.append(value_str[1])
                else:
                    # the device does not have sensor values
                    value_str = str(value).split("'")[1]
                    device_address.append(value_str)
                    device_range.append('0-1')
        else:
            self.ui.plainTextEdit.appendPlainText("  No properties")
        self.ui.plainTextEdit.appendPlainText('\n')

        if device_ip not in self.TABLE_INFO["Address"].to_list() or name not in self.TABLE_INFO["ServiceName"].to_list():
            # The IP is not in TABLE_INFO yet
            if device_ip == NeighborDiscovery().get_local_ip() and 'Server' in str(info.server):
                # It is a service from this server
                # Check if service already exists (happens if two users click on the same device at the same time)
                if info.server in self.TABLE_INFO['Host Name'].to_list():
                    # This should not have happend. We have two services with the same name
                    #self.discovery.unregister_service(device_ip, info.server)
                    self.ui.plainTextEdit.appendPlainText(
                        "[INFO] Sorry, another server with IP %s has allocated the device" % (device_ip))
                else:
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, True, False, 0]
                    # Mark the entry of the specific device as selected
                    self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_address[1]])].tolist()[0], 'isSelected'] = True
            elif device_ip != NeighborDiscovery().get_local_ip() and 'Server' in str(info.server):
                # It is a message from another server
                # Check if service already exists (happens if two users click on the same device at the same time)
                if info.server in self.TABLE_INFO['Host Name'].to_list():
                    #self.discovery.unregister_service(device_ip, info.server)
                    self.ui.plainTextEdit.appendPlainText(
                        "[INFO] Sorry, another server with IP %s has allocated the device" % (device_ip))
                else:
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, True, False, 0]
                    # Mark the entry of the specific device as taken
                    # First check, if the entry exists
                    if device_address[1] in self.TABLE_INFO["Address"].to_list():
                        self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_address[1]])].tolist()[0], 'isTaken'] = True
            else:
                # Check if a server has already announced to allocate the device
                flat_device_address_list = [item for sublist in self.TABLE_INFO['Device Address'].to_list() for item in sublist]

                if device_ip in flat_device_address_list:

                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, False, True, 0]

                else:
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, False, False, 0]
        else:
            # The IP is already in TABLE_INFO
            # Check if service already exists (happens if two users click on the same device at the same time)
            if info.server in self.TABLE_INFO['Host Name'].to_list():
                self.ui.plainTextEdit.appendPlainText(
                    "[INFO] Sorry, another server with IP %s has allocated the device" % (device_ip))
                self.discovery.unregister_service(device_ip, info.server)
            else:
                print("[WARNING] Either IP or Service are in TABLE_INFO, but not the host name: %s" % (info.server))
        self.update_view()

    def handleServiceRemoved(self, name):
        if name in self.TABLE_INFO["ServiceName"].to_list():
            df = self.TABLE_INFO[self.TABLE_INFO["ServiceName"] == name]
            device_to_free = [item for sublist in df['Device Address'].to_list() for item in sublist]

            if df["Address"].to_list()[0] == NeighborDiscovery().get_local_ip() and 'Server' in name:
                # This server has released the device
                self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_to_free[1]])], 'isSelected'] = False
                # Delete the service
                self.TABLE_INFO.drop(self.TABLE_INFO.loc[self.TABLE_INFO['ServiceName'] == name].index, inplace=True)

            elif df["Address"].to_list()[0] != NeighborDiscovery().get_local_ip() and 'Server' in name:
                # Another server has released a device
                # First check if the device exists
                if device_to_free[1] in self.TABLE_INFO["Address"].to_list():
                    self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_to_free[1]])], 'isTaken'] = False
                # Remove server from TABLE_INFO
                self.TABLE_INFO.drop(self.TABLE_INFO.loc[self.TABLE_INFO['ServiceName'] == name].index, inplace=True)

            else:
                # A device has unregistered
                print("[WARNING] A device has unregistered")
                #pass
        self.update_view()

    def on_device_found(self, zeroconf, service_type, name, state_change):
        self.ui.plainTextEdit.appendPlainText(
            "Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self.handleServiceAdded(info, name)
        elif state_change is ServiceStateChange.Removed:
            self.handleServiceRemoved(name)

    def zeroconf_start(self):
        self.discovery = NeighborDiscovery()
        self.discovery.neighbor_signal.connect(self.on_device_found)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)


    app = QtWidgets.QApplication(sys.argv)
    myapp = StartQT5()
    myapp.show()
    sys.exit(app.exec_())
    #sys.exit(myapp.close(app))