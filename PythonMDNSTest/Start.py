import logging
import sys
import socket
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal)
import ifaddr


from gui import Ui_MainWindow

from typing import cast
from time import sleep
from zeroconf import ServiceInfo,ServiceBrowser, ServiceStateChange, Zeroconf
from typing import List

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

TYPE = '_osc._udp.local.'
NAME = 'Server'
#<<<<<<< HEAD
#Table_info = pd.DataFrame(columns=['Address', 'Port', 'Server','Select','Device Type','Device Address','Device Range'])
#TABLE_INFO = pd.DataFrame(columns=['Address', 'Port', 'Server','Select','Device Type','Device Address','Device Range'])
#Table_info_selected = pd.DataFrame(columns=['Address', 'Port', 'Server','Select','Device Type','Device Address','Device Range'])
#=======
#Table_info = pd.DataFrame(columns=['Address', 'Port', 'Server','Device Count','Device Type','Device Address','Device Range'])
#Table_info_selected = pd.DataFrame(columns=['Address', 'Port', 'Server','Device Count','Device Type','Device Address','Device Range'])
#>>>>>>> master


class StartQT5(QtWidgets.QMainWindow):
    def __init__(self):
        super(StartQT5, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tableWidget.setColumnCount(5)
        self.ui.tableWidget.setHorizontalHeaderLabels(['Name', 'IP Address', 'Server', 'Device Count', 'Select'])
        self.ui.discover_button.clicked.connect(self.zeroconf_start)
        #self.TABLE_INFO = pd.DataFrame(columns=['Address', 'Port', 'Server','Select','Device Type','Device Address','Device Range'])
        self.TABLE_INFO = pd.DataFrame(columns=['Address', 'Port', 'Server', 'Device Count', 'Device Type', 'Device Address', 'Device Range', '*'])

        self.model = PandasModel(self.TABLE_INFO)
        self.ui.tableView.setModel(self.model)

    def handleCheckboxClicked(self):
        Checkbox = QtWidgets.qApp.focusWidget()
        if Checkbox.isChecked():
            self.discovery.register_service(Checkbox.accessibleName(), Checkbox.accessibleDescription())
        else:
            self.TABLE_INFO = self.TABLE_INFO[self.TABLE_INFO["Address"] != Checkbox.accessibleName()]
            self.TABLE_INFO.index = self.TABLE_INFO.index + 1  # shifting index
            self.TABLE_INFO = self.TABLE_INFO.sort_index()  # sorting by index
            self.discovery.unregister_service(Checkbox.accessibleName(), Checkbox.accessibleDescription())

    def on_device_found(self, zeroconf, service_type, name, state_change):
        global TABLE_INFO
        update_tableView = True
        device_type = []
        device_address = []
        device_range = []

        self.ui.plainTextEdit.appendPlainText(
            "Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self.ui.plainTextEdit.appendPlainText(
                    "  Address: %s:%d" % (socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port)))
                self.ui.plainTextEdit.appendPlainText("  Weight: %d, priority: %d" % (info.weight, info.priority))
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
                    print("  No properties")

#<<<<<<< HEAD
                # FIXME: Just for debugging we show the server
                #if (socket.inet_ntoa(cast(bytes, info.address)) not in TABLE_INFO.index): #or (info.server not in TABLE_INFO['Server']):
                if (socket.inet_ntoa(cast(bytes, info.address)) not in self.TABLE_INFO["Address"].to_list()):
                    #print(self.TABLE_INFO[self.TABLE_INFO.Address])
                    #local_device = pd.DataFrame({'Address': socket.inet_ntoa(cast(bytes, info.address)), 'Port': cast(int, info.port),
                    # 'Server': info.server, 'Select': "", 'Device Type': [device_type],'Device Address': [device_address],'Device Range': [device_range]}, index = [socket.inet_ntoa(cast(bytes, info.address))])
                    #TABLE_INFO.ix[socket.inet_ntoa(cast(bytes, info.address))] = [socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port), info.server, False, device_type, device_address, device_range]
                    self.TABLE_INFO.loc[len(self.TABLE_INFO)] = [
                        socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port), info.server,
                        len(device_type), device_type, device_address, device_range, ""]
                    #Table_info = Table_info.append(local_device)
                    print(self.TABLE_INFO)
                    #print(self.TABLE_INFO[self.TABLE_INFO.Address])
# #=======
#                 if socket.inet_ntoa(cast(bytes, info.address)) not in Table_info.index:
#                     local_device = pd.DataFrame({'Address': socket.inet_ntoa(cast(bytes, info.address)), 'Port': cast(int, info.port),'Server': info.server, 'Device Count': len(device_type), 'Device Type': [device_type],'Device Address': [device_address],'Device Range': [device_range]}, index = [socket.inet_ntoa(cast(bytes, info.address))])
#                     Table_info = Table_info.append(local_device)
#                     numRows = self.ui.tableWidget.rowCount()
#
#
#
#
#                     self.ui.tableWidget.insertRow(numRows)
#                     # Add text to the row
#                     self.ui.tableWidget.setItem(numRows, 0, QtWidgets.QTableWidgetItem(info.name))
#                     self.ui.tableWidget.setItem(numRows, 1, QtWidgets.QTableWidgetItem(socket.inet_ntoa(cast(bytes, info.address))))
#                     self.ui.tableWidget.setItem(numRows, 2, QtWidgets.QTableWidgetItem(info.server))
#                     self.ui.tableWidget.setItem(numRows, 3, QtWidgets.QTableWidgetItem(str(len(device_type))))
#
#
# >>>>>>> master
                    self.Checkbox = QtWidgets.QCheckBox(' ')
                    self.Checkbox.setAccessibleName(socket.inet_ntoa(cast(bytes, info.address)))
                    self.Checkbox.setAccessibleDescription(name)
                    self.Checkbox.clicked.connect(self.handleCheckboxClicked)

##<<<<<<< HEAD
                    checkBoxWidget = QtWidgets.QWidget()
                    layoutCheckBox = QtWidgets.QHBoxLayout(checkBoxWidget)
                    layoutCheckBox.addWidget(self.Checkbox)
                    layoutCheckBox.setAlignment(Qt.AlignCenter);

                    item = self.model.index(self.model.rowCount() - 1, self.model.columnCount()-1)
                    self.ui.tableView.setIndexWidget(item, self.Checkbox)

                    self.model.insertRows()
# =======
#                     checkBoxWidget= QtWidgets.QWidget()
#                     layoutCheckBox =  QtWidgets.QHBoxLayout(checkBoxWidget)
#                     layoutCheckBox.addWidget(self.Checkbox)
#                     layoutCheckBox.setAlignment(Qt.AlignCenter);
#
#                     self.ui.tableWidget.setCellWidget(numRows, 4, self.Checkbox)
#
# >>>>>>> master
                else:
                    update_tableView = False

            else:
                print("  No info")

            self.ui.plainTextEdit.appendPlainText('\n')

#<<<<<<< HEAD
            #if update_tableView:
            #    model = PandasModel(Table_info)
            #    self.ui.tableView.setModel(model)
            #    print(range(model.rowCount()))
            #    #for index in range(model.rowCount()):
            #    self.Checkbox = QtWidgets.QCheckBox(' ')
            #    self.Checkbox.setAccessibleName(socket.inet_ntoa(cast(bytes, info.address)))
            #    self.Checkbox.setAccessibleDescription(name)
            #    self.Checkbox.clicked.connect(self.handleCheckboxClicked)
            #    #item = model.index(index, 3);
            #    item = model.index(model.rowCount() - 1, 3)
            #    self.ui.tableView.setIndexWidget(item, self.Checkbox)
            print(self.model.rowCount())
            #print(self.model.index(self.model.rowCount(), 3))
            #self.model.insertRow()
            #print(self.model.index(self.model.rowCount(), 3))
            #self.model.setData(self.model.index(self.model.rowCount(), 3), "")
            #print(self.model.rowCount())
        if state_change is ServiceStateChange.Removed:
            print("Service Removed")
#=======
            # if update_tableView:
            #     model = PandasModel(Table_info)
            #     self.ui.tableView.setModel(model)



#>>>>>>> master

    def zeroconf_start(self):
        self.discovery = NeighborDiscovery()
        self.discovery.neighbor_signal.connect(self.on_device_found)


class NeighborDiscovery(QtCore.QThread):
    neighbor_signal = QtCore.pyqtSignal(object, object, object, object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, TYPE, handlers=[self.on_service_state_change])

    def on_service_state_change(self,zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange, ) -> None:
        self.neighbor_signal.emit(zeroconf, service_type, name, state_change)

    def register_service(self, ip, service_name):
        TXT_record = {'server': self.get_local_ip()}
        TXT_record.update({"device": ip})

        name = service_name.split('.')[0]
        name = NAME + "_" + name

        info = ServiceInfo(type_="_osc._udp.local.",
                           name=name + "." + TYPE,
                           address=socket.inet_aton("192.168.11.172"),
                           port=80,
                           weight=0,
                           priority=0,
                           properties=TXT_record,
                           server=name + ".local.")
        print(info)
        print("Registration of a service %s" % (name))
        self.zeroconf.register_service(info)

    def unregister_service(self, ip, name_):
        print(name_)
        name = NAME + "_" + name_
        info = self.zeroconf.get_service_info(TYPE, name)
        print(info)
        self.zeroconf.unregister_service(info)
        print("Unregistering service %s with IP %s" % (name, ip))


    def get_all_addresses(self) -> List[str]:
        return list(set(
            addr.ip
            for iface in ifaddr.get_adapters()
            for addr in iface.ips
            if addr.is_IPv4 and addr.network_prefix != 32  # Host only netmask 255.255.255.255
        ))

    def get_local_ip(self, starts_with="192"):
        list_ip = self.get_all_addresses()
        local_ip = [i for i in list_ip if i.startswith(starts_with)]
        return local_ip[0]


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df = pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        print(index.row())
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

    # def removeRows(self, position, rows=1, index=QModelIndex()):
    #     print("\n\t\t ...removeRows() Starting position: '%s'" % position, 'with the total rows to be deleted: ', rows)
    #     self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
    #     self.items = self.items[:position] + self.items[position + rows:]
    #     self.endRemoveRows()
    #
    #     return True

    # def insertRows(self, position, rows=1, index=QModelIndex()):
    #     print
    #     "\n\t\t ...insertRows() Starting position: '%s'" % position, 'with the total rows to be inserted: ', rows
    #     indexSelected = self.index(position, 0)
    #     itemSelected = indexSelected.data().toPyObject()
    #
    #     self.beginInsertRows(QModelIndex(), position, position + rows - 1)
    #     for row in range(rows):
    #         self.items.insert(position + row, "%s_%s" % (itemSelected, self.added))
    #         self.added += 1
    #     self.endInsertRows()
    #     return True

    def insertRows(self):
        #row = self._df.index[index.row()]
        #column = 0
        self.layoutAboutToBeChanged.emit()
        self._df.append(self._df.tail(1))
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()



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