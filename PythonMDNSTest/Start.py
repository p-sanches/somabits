import logging
import sys
import socket
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_MainWindow

from typing import cast
from time import sleep
from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf

TYPE = '_osc._udp.local.'
NAME = 'Server'
Table_info = pd.DataFrame(columns=['Address', 'Port', 'Server', 'Select'])


class StartQT5(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QApplication.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # here we connect signals with our slots
        self.ui.discover_button.clicked.connect(self.zeroconf_start)



    def on_service_state_change(self,zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange, ) -> None:
        global Table_info
        print("Service %s of type %s state changed: %s" % (name, service_type, state_change))
        self.ui.plainTextEdit.appendPlainText("Service %s of type %s state changed: %s" % (name, service_type, state_change))

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                cb = QtWidgets.QCheckBox('hello', self)
                local_device = pd.DataFrame({'Address':socket.inet_ntoa(cast(bytes, info.address)), 'Port':cast(int, info.port), 'Server':info.server, 'Select':cb}, index=[info.server])
                Table_info =Table_info.append(local_device)
                print("  Address: %s:%d" % (socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port)))
                self.ui.plainTextEdit.appendPlainText("  Address: %s:%d" % (socket.inet_ntoa(cast(bytes, info.address)), cast(int, info.port)))
                print("  Weight: %d, priority: %d" % (info.weight, info.priority))
                self.ui.plainTextEdit.appendPlainText("  Weight: %d, priority: %d" % (info.weight, info.priority))
                print("  Server: %s" % (info.server,))
                self.ui.plainTextEdit.appendPlainText("  Server: %s" % (info.server,))
                if info.properties:
                    print("  Properties are:")
                    self.ui.plainTextEdit.appendPlainText("  Properties are:")
                    for key, value in info.properties.items():
                        print("    %s: %s" % (key, value))
                        self.ui.plainTextEdit.appendPlainText("    %s: %s" % (key, value))
                else:
                    print("  No properties")
            else:
                print("  No info")
            print('\n')
            self.ui.plainTextEdit.appendPlainText('\n')
            print(Table_info)
            model = PandasModel(Table_info)
            #self.tableView.setModel(model)
            self.ui.tableView.setModel(model)


    def zeroconf_start(self):
        zeroconf = Zeroconf()
        browser = ServiceBrowser(zeroconf, TYPE, handlers=[self.on_service_state_change])



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