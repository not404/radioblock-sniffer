# Copyright (c) 2011 - 2012, SimpleMesh AUTHORS
# Eric Gnoske,
# Colin O'Flynn,
# Blake Leverett,
# Rob Fries,
# Colorado Micro Devices Inc..
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1) Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#   2) Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#   3) Neither the name of the SimpleMesh AUTHORS nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Fri Nov  9 15:15:08 2012
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost! (If you change mainwindow.cpp and
# regenerate the mainwindow.py file.

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(734, 737)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 711, 621))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.comboBoxCOMPort = QtGui.QComboBox(self.tab)
        self.comboBoxCOMPort.setGeometry(QtCore.QRect(90, 20, 211, 26))
        self.comboBoxCOMPort.setObjectName("comboBoxCOMPort")
        self.pushButton_2 = QtGui.QPushButton(self.tab)
        self.pushButton_2.setGeometry(QtCore.QRect(0, 120, 121, 32))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_7 = QtGui.QLabel(self.tab)
        self.label_7.setGeometry(QtCore.QRect(10, 50, 71, 16))
        self.label_7.setObjectName("label_7")
        self.textEditRx = QtGui.QTextEdit(self.tab)
        self.textEditRx.setGeometry(QtCore.QRect(20, 210, 512, 100))
        self.textEditRx.setObjectName("textEditRx")
        self.line = QtGui.QFrame(self.tab)
        self.line.setGeometry(QtCore.QRect(10, 170, 521, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_6 = QtGui.QLabel(self.tab)
        self.label_6.setGeometry(QtCore.QRect(10, 20, 62, 16))
        self.label_6.setObjectName("label_6")
        self.comboBoxBAUDRate = QtGui.QComboBox(self.tab)
        self.comboBoxBAUDRate.setGeometry(QtCore.QRect(90, 50, 211, 26))
        self.comboBoxBAUDRate.setObjectName("comboBoxBAUDRate")
        self.line_3 = QtGui.QFrame(self.tab)
        self.line_3.setGeometry(QtCore.QRect(10, 320, 521, 16))
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.pushButton = QtGui.QPushButton(self.tab)
        self.pushButton.setGeometry(QtCore.QRect(0, 80, 121, 32))
        self.pushButton.setObjectName("pushButton")
        self.textEditTx = QtGui.QTextEdit(self.tab)
        self.textEditTx.setGeometry(QtCore.QRect(20, 360, 512, 100))
        self.textEditTx.setObjectName("textEditTx")
        self.label_5 = QtGui.QLabel(self.tab)
        self.label_5.setGeometry(QtCore.QRect(20, 190, 62, 16))
        self.label_5.setObjectName("label_5")
        self.label_8 = QtGui.QLabel(self.tab)
        self.label_8.setGeometry(QtCore.QRect(20, 340, 62, 16))
        self.label_8.setObjectName("label_8")
        self.tabWidget.addTab(self.tab, "")
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.textEditSniffer = QtGui.QTextEdit(self.tab_4)
        self.textEditSniffer.setGeometry(QtCore.QRect(10, 50, 681, 531))
        self.textEditSniffer.setObjectName("textEditSniffer")
        self.label = QtGui.QLabel(self.tab_4)
        self.label.setGeometry(QtCore.QRect(10, 30, 681, 16))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self.tab_4)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 681, 16))
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.tab_4, "")
        self.pushButton_4 = QtGui.QPushButton(self.centralWidget)
        self.pushButton_4.setGeometry(QtCore.QRect(610, 640, 114, 32))
        self.pushButton_4.setObjectName("pushButton_4")
        self.label_24 = QtGui.QLabel(self.centralWidget)
        self.label_24.setGeometry(QtCore.QRect(10, 640, 61, 16))
        self.label_24.setObjectName("label_24")
        self.lineEditSinffChannel = QtGui.QLineEdit(self.centralWidget)
        self.lineEditSinffChannel.setGeometry(QtCore.QRect(70, 640, 113, 22))
        self.lineEditSinffChannel.setObjectName("lineEditSinffChannel")
        self.pushButtonChannel = QtGui.QPushButton(self.centralWidget)
        self.pushButtonChannel.setGeometry(QtCore.QRect(190, 640, 93, 28))
        self.pushButtonChannel.setObjectName("pushButtonChannel")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 734, 26))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MainWindow", "Close COM Port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "BAUD Rate", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "COM Port", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setToolTip(QtGui.QApplication.translate("MainWindow", "additonal settings are \'8,N,1\'...", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "Open COM Port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("MainWindow", "Serial RX", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("MainWindow", "Serial TX", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "COM Port", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "FCF       Seq    PANID      MAC Dst    MAC src  NWK (FCF - Seq)  NWK Src  NWK Dst  Payload        LQI    RSSI", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "2Bytes  1Byte  2Bytes      2Bytes       2Bytes            1Byte-1Byte  2 Bytes    2Bytes     N-Bytes       1Byte  1Byte", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtGui.QApplication.translate("MainWindow", "Sniffer", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.label_24.setText(QtGui.QApplication.translate("MainWindow", "Channel:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonChannel.setText(QtGui.QApplication.translate("MainWindow", "Set Channel", None, QtGui.QApplication.UnicodeUTF8))


import sys
def show_mainwindow(app, MainWindow):
    MainWindow.setWindowTitle("RadioBlocks Sniffer")
    MainWindow.setWindowIcon(QtGui.QIcon('favicon.ico'))
    MainWindow.show()

