# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(888, 647)
        MainWindow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.466, y1:0, x2:0.46, y2:1, stop:0 rgba(82, 175, 210, 255), stop:1 rgba(23, 51, 61, 255));")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setStyleSheet("background-color: rgb(19, 41, 50);\n"
"font: 63 9pt \"Adobe Fan Heiti Std B\";\n"
"border-color: rgb(0, 0, 0);\n"
"gridline-color: rgb(0, 0, 0);\n"
"alternate-background-color: rgb(7, 16, 20);")
        self.tabWidget.setIconSize(QtCore.QSize(20, 20))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.save_button = QtWidgets.QPushButton(self.tab)
        self.save_button.setStyleSheet("background-color: rgb(124, 124, 124);\n"
"color: rgb(255, 255, 255);")
        self.save_button.setObjectName("save_button")
        self.gridLayout.addWidget(self.save_button, 8, 0, 1, 1)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab)
        self.plainTextEdit.setStyleSheet("color: rgb(223, 223, 223);")
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 7, 0, 1, 1)
        self.tableView = QtWidgets.QTableView(self.tab)
        self.tableView.setStyleSheet("background-color: rgb(214, 214, 214);\n"
"font: 8pt \"MS Shell Dlg 2\";\n"
"border-color: rgb(0, 0, 0);")
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tableView, 5, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 63 9pt \"Adobe Fan Heiti Std B\";")
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 6, 0, 1, 1)
        self.discover_button = QtWidgets.QPushButton(self.tab)
        self.discover_button.setStyleSheet("background-color: rgb(124, 124, 124);\n"
"font: 63 10pt \"Adobe Fan Heiti Std B\";\n"
"color: rgb(255, 255, 255);\n"
"")
        self.discover_button.setObjectName("discover_button")
        self.gridLayout.addWidget(self.discover_button, 0, 0, 2, 1)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resx/Google-Noto-Emoji-Objects-62971-gear.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab, icon, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("resx/Custom-Icon-Design-Pretty-Office-13-Arrows-Sync.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_2, icon1, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("resx/Oxygen-Icons.org-Oxygen-Apps-preferences-system-windows.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_3, icon2, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Soma"))
        self.save_button.setText(_translate("MainWindow", "Save"))
        self.label.setText(_translate("MainWindow", "For Debugging only"))
        self.discover_button.setText(_translate("MainWindow", "Discover"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Control"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Forwarding"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Applications"))


