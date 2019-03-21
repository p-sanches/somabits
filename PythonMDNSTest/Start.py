import logging
import sys
import socket
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal)


from gui import Ui_MainWindow

from typing import cast
from time import sleep
from zeroconf import ServiceInfo,ServiceBrowser, ServiceStateChange, Zeroconf

TYPE = '_osc._udp.local.'
NAME = 'Server'
Table_info = pd.DataFrame(columns=['Address', 'Port', 'Server','Select','Device Type','Device Address'])
Table_info_selected = pd.DataFrame(columns=['Address', 'Port', 'Server','Select','Device Type','Device Address'])


class StartQT5(QtWidgets.QMainWindow):
    def __init__(self):
        super(StartQT5, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.discover_button.clicked.connect(self.zeroconf_start)
        self.ui.save_button.clicked.connect(self.save_button_clicked)

    def close(self, app):
        #self.zeroconf.close()
        #self.neighbor_discovery
        print("Closing App")
        #self.neighbor_discovery.close()
        #return app.exec_()


    def handleCheckboxClicked(self):
        global Table_info_selected
        global Table_info
        Checkbox = QtWidgets.qApp.focusWidget()
        index = self.ui.tableView.indexAt(Checkbox.pos())
# <<<<<<< HEAD
#         print(index)
#         print(Checkbox.accessibleName())
#         if Checkbox.isChecked():
#             pass
#             # register device
#             # if index.isValid():
#             #     print(Table_info.loc[Table_info.iloc[index.row(), 2]])
#             #     print(index.row())
#             #     print(Table_info[index.row()])
#                 #Table_info_selected = Table_info_selected.append(Table_info.loc[Table_info.iloc[index.row(), 2]],
#                 #                                                 ignore_index=False)
#
#         else:
#             # unregister device
#             pass
#
#
#         # global Table_info
#         # global Table_info_selected
#         # Checkbox = QtWidgets.qApp.focusWidget()
#         # # or button = self.sender()
#         # #index = self.table.indexAt(button.pos())
#         # index = self.ui.tableView.indexAt(Checkbox.pos())
#         # if index.isValid():
#         #     Table_info_selected=Table_info_selected.append(Table_info.loc[Table_info.iloc[index.row(),2]], ignore_index=False)
# =======
        if index.isValid():
            print(index.row(), index.column())
            print(Table_info.iloc[index.row(),0])
            Table_info_selected=Table_info_selected.append(Table_info.loc[Table_info.iloc[index.row(),0]], ignore_index=False)
            print(Table_info_selected)
#>>>>>>> master


    def save_button_clicked(self,zeroconf):
        global Table_info
        global Table_info_selected
        TXT_record = {'server': 'hello'}
        print(len(Table_info_selected.index))

        for index in range(len(Table_info_selected.index)):
            TXT_record.update({'name' + str(index): Table_info_selected.iloc[index, 0]})
        print(TXT_record)

        info = ServiceInfo(type_="_osc._udp.local.",
                           name=NAME + "." + TYPE,
                           address=socket.inet_aton("192.168.11.172"),
                           port=80,
                           weight=0,
                           priority=0,
                           properties=TXT_record,
                           server=NAME + ".local.")

        print("Registration of a service")
        zeroconf.register_service(info)


    def on_device_found(self, zeroconf, service_type, name, state_change):
        global Table_info
        self.ui.plainTextEdit.appendPlainText(
            "Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:

                self.ui.plainTextEdit.appendPlainText(
                    "  Address: %s:%d" % (socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port)))
                self.ui.plainTextEdit.appendPlainText("  Weight: %d, priority: %d" % (info.weight, info.priority))
                self.ui.plainTextEdit.appendPlainText("  Server: %s" % (info.server,))
                device_type = []
                device_address = []

                if info.properties:
                    self.ui.plainTextEdit.appendPlainText("  Properties are:")

                    for key, value in info.properties.items():
                        self.ui.plainTextEdit.appendPlainText("    %s: %s" % (key, value))
                        key_str = str(key)
                        a, b, c = key_str.split("'")
                        print(b)

                        value_str = str(value)
                        d, e, f = value_str.split("'")
                        print(e)

                        device_type.append(b)
                        device_address.append(e)
                else:
                    print("  No properties")


                if socket.inet_ntoa(cast(bytes, info.address)) not in Table_info.index:
                    local_device = pd.DataFrame({'Address': socket.inet_ntoa(cast(bytes, info.address)), 'Port': cast(int, info.port),'Server': info.server, 'Select': "", 'Device Type': [device_type],'Device Address': [device_address]}, index = [socket.inet_ntoa(cast(bytes, info.address))])
                    Table_info = Table_info.append(local_device)

            else:
                print("  No info")

            self.ui.plainTextEdit.appendPlainText('\n')

            model = PandasModel(Table_info)
            self.ui.tableView.setModel(model)
            for index in range(model.rowCount()):
                self.Checkbox = QtWidgets.QCheckBox(' ')
                self.Checkbox.setAccessibleName(name)
                self.Checkbox.clicked.connect(self.handleCheckboxClicked)
                item = model.index(index, 3);
                self.ui.tableView.setIndexWidget(item, self.Checkbox)

    def zeroconf_start(self):
        discovery = NeighborDiscovery()
        discovery.neighbor_signal.connect(self.on_device_found)


class NeighborDiscovery(QtCore.QThread):
    neighbor_signal = QtCore.pyqtSignal(object, object, object, object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, TYPE, handlers=[self.on_service_state_change])

    def on_service_state_change(self,zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange, ) -> None:
        self.neighbor_signal.emit(zeroconf, service_type, name, state_change)


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df = pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
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

    def setData(self, index, value, role):
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