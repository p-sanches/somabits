import logging
import sys
import socket
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal, QModelIndex)


from SomoServer.gui import Ui_MainWindow
from SomoServer.TableModel import PandasModel, CheckBoxDelegate
from SomoServer.ZeroConf import NeighborDiscovery

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
        delegate = CheckBoxDelegate(self.model)
        self.ui.tableView.setItemDelegateForColumn(self.TABLE_INFO_CHECKBOX, delegate)

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

    def handleCheckboxClicked(self, value, ip, host):
        print(value)

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
            "  Weight: %d, priority: %d, ttl: %s" % (info.weight, info.priority, info.ttl))
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
        else:
            self.ui.plainTextEdit.appendPlainText("  No properties")
        self.ui.plainTextEdit.appendPlainText('\n')

        if device_ip not in self.TABLE_INFO["Address"].to_list() or name not in self.TABLE_INFO["ServiceName"].to_list():
            # The IP is not in TABLE_INFO yet
            if device_ip == NeighborDiscovery().get_local_ip() and 'Server' in str(info.server):
                # It is a message from this server
                self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                    device_ip, cast(int, info.port), info.server,
                    len(device_type), device_type, device_address, device_range, name, False, True, False, 0]
                # Mark the entry of the specific device as selected
                self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_address[1]])].tolist()[0], 'isSelected'] = True
            elif device_ip != NeighborDiscovery().get_local_ip() and 'Server' in str(info.server):
                # It is a message from another server
                self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                    device_ip, cast(int, info.port), info.server,
                    len(device_type), device_type, device_address, device_range, name, False, True, False, 0]
                self.model.removeRows(device_ip)
                # Mark the entry of the specific device as taken
                # First check, if the entry exists
                if device_address[1] in self.TABLE_INFO["Address"].to_list():
                    self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_address[1]])].tolist()[0], 'isTaken'] = True
                    self.model.removeRows(device_address[1])

            else:
                # Check if a server has already announced to allocate the device
                flat_device_address_list = [item for sublist in self.TABLE_INFO['Device Address'].to_list() for item in sublist]

                if device_ip in flat_device_address_list:

                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        device_ip, cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, name, False, False, True, 0]

                else:
                    #ds = {'Address': device_ip, 'Port': cast(int, info.port), 'Host Name': info.server, 'Device Count': len(device_type), 'Device Type': device_type, 'Device Address': device_address, 'Device Range': device_range, 'ServiceName': name, 'isSelected': False, 'isServer': False, 'isTaken': False, '*': False}
                    #self.TABLE_INFO.append(ds, ignore_index=True)
                    #self.TABLE_INFO.append(ds, ignore_index=True)
                    ds = [device_ip, cast(int, info.port), info.server, len(device_type), device_type, device_address, device_range, name, False, False, False, 0]
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = ds
                    #self.ui.tableView.openPersistentEditor(self.model.index(self.model.rowCount(), 11))
                    #self.TABLE_INFO.loc[len(self.TABLE_INFO)] = ds#[
                        #device_ip, cast(int, info.port), info.server,
                        #len(device_type), device_type, device_address, device_range, name, False, False, False, False]

                    # self.Checkbox = QtWidgets.QCheckBox(' ')
                    # self.Checkbox.setAccessibleName(socket.inet_ntoa(cast(bytes, info.address)))
                    # self.Checkbox.setAccessibleDescription(info.server)
                    # self.Checkbox.clicked.connect(self.handleCheckboxClicked)
                    #
                    # checkBoxWidget = QtWidgets.QWidget()
                    # layoutCheckBox = QtWidgets.QHBoxLayout(checkBoxWidget)
                    # layoutCheckBox.addWidget(self.Checkbox)
                    # layoutCheckBox.setAlignment(Qt.AlignCenter);
                    #
                    # item = self.model.index(self.model.rowCount() - 1, self.model.columnCount() - 1)
                    # self.ui.tableView.setIndexWidget(item, self.Checkbox)
                    #for i, cell in enumerate(ds):
                    #    print(i)
                    #    print(cell)
                    #    print(self.model.rowCount())
                    #    index = self.model.index(self.model.rowCount(), i, QModelIndex())
                    #    self.model.setData(index, cell)
                    #self.model.layoutChanged().emit()
                    self.model.insertRows(ds)
                    #self.ui.tableView.openPersistentEditor(self.model.index(self.model.rowCount(), 11))

        print(self.TABLE_INFO)

    def handleServiceRemoved(self, name):
        if name in self.TABLE_INFO["ServiceName"].to_list():
            df = self.TABLE_INFO[self.TABLE_INFO["ServiceName"] == name]
            print(df)
            device_to_free = [item for sublist in df['Device Address'].to_list() for item in sublist]

            if df["Address"].to_list()[0] == NeighborDiscovery().get_local_ip() and 'Server' in name:
                # This server has released the device
                self.TABLE_INFO.at[self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_to_free[1]])], 'isSelected'] = False
            elif df["Address"].to_list()[0] != NeighborDiscovery().get_local_ip() and 'Server' in name:
                # Another server has released a device
                self.TABLE_INFO.at[
                    self.TABLE_INFO.index[self.TABLE_INFO["Address"].isin([device_to_free[1]])], 'isTaken'] = False
                # Remove server from TABLE_INFO
                self.TABLE_INFO = self.TABLE_INFO[self.TABLE_INFO['Address'] != df["Address"].to_list()[0]]


                # self.Checkbox = QtWidgets.QCheckBox(' ')
                # self.Checkbox.setAccessibleName(socket.inet_ntoa(cast(bytes, info.address)))
                # self.Checkbox.setAccessibleDescription(info.server)
                # self.Checkbox.clicked.connect(self.handleCheckboxClicked)
                #
                # checkBoxWidget = QtWidgets.QWidget()
                # layoutCheckBox = QtWidgets.QHBoxLayout(checkBoxWidget)
                # layoutCheckBox.addWidget(self.Checkbox)
                # layoutCheckBox.setAlignment(Qt.AlignCenter);
                #
                # item = self.model.index(self.model.rowCount() - 1, self.model.columnCount() - 1)
                # self.ui.tableView.setIndexWidget(item, self.Checkbox)
                #
                # self.model.insertRows()
            else:
                # A device has unregistered
                pass
        print(self.TABLE_INFO)
        #self.model.removeRows(df)


    def on_device_found(self, zeroconf, service_type, name, state_change):
        self.ui.plainTextEdit.appendPlainText(
            "Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self.handleServiceAdded(info, name)
        elif state_change is ServiceStateChange.Removed:
            print("Service Removed")
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