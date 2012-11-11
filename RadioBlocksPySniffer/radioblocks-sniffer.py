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

__author__ = 'egnoske'

# Hey, this is a pyside application!
import PySide
from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *


from PySide.QtGui import QColor, QTextCursor

# Needed for string handling (I think)...
try:
    from PySide.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

# This is used in the signal/slot setup in the Com_Port class.
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

# Need sys to play with paths.
import sys

# The mainwindow GUI class is one directory level up.
sys.path.append('../')
path = sys.path # A debug ine to examine the path...

# With path set, we can import the module (file) containing the mainwindow class.
import mainwindow

# This enables the serial port.
import serial
import scanlinux
import scan

# When we scan we need to know which OS we're operating on.
import os
import platform


###############################################################################

class Com_Port(object):

    com_port_opened = ''
    serial_frame = ''
    #-------------------------------------------------------------------------#

    def __init__(self, name):
        self.name = name

    def printme(self):
        print(self.name)
    #-------------------------------------------------------------------------#

    def findComPorts(self, ui, serial_port):
        # This function just prints them to the terminal/console.
        if platform.system() == 'Windows':
            ports = []
            port_index = 0
            win_ports = scan.scan()
            # For Windows, we need to get just the name not the tuple...
            for each_tuple in win_ports:
                ports.append(each_tuple[1])

        elif platform.system() == 'Linux':
            ports = scanlinux.scan()
        else: # We're a Mac
            ports = scanlinux.scan()

        # Populate the drop down list box for the COM ports
        for item in ports:
            ui.comboBoxCOMPort.addItem(item)

        # Create a list of typical BAUD rates and populate the Combo Box with those.
        baud = ['9600','14400','19200','28800','38400','57600','115200','230400','256000']
        for item in baud:
            ui.comboBoxBAUDRate.addItem(item)

        # Setup a signal slot to test that when a user selects a BAUD rate we can 'use' that BAUD rate in
        # another method/function...
        QtCore.QObject.connect(ui.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.openComPort)

        # Setup the signal/slot for the quit button too.
        QtCore.QObject.connect(ui.pushButton_4, QtCore.SIGNAL(_fromUtf8("clicked()")), self.quitTheApp)

        # Setup the signal/slot for the close COM Port button too.
        QtCore.QObject.connect(ui.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), self.closeComPort)

        # Override the built in keyPressEvent to handle it with our logic.
#        ui.textEditTx.keyPressEvent = self.keyPressEvent

        # Setup the signal/slot for the channel button too.
        QtCore.QObject.connect(ui.pushButtonChannel, QtCore.SIGNAL(_fromUtf8("clicked()")), self.changeChannel)
    #-------------------------------------------------------------------------#
    def changeChannel(self):
        stuff = 'C'
        tmp = ui.lineEditSinffChannel.text()

        num = int(tmp)

        # This transmits the data in the serial frame!
        self.com_port_opened.write(stuff)
        self.com_port_opened.write(num)

    def openComPort(self):
        # This gets the text of the user selected item
        baud = QString(ui.comboBoxBAUDRate.currentText())
        baudnum = int(baud, 10) # The '10' indicates decimal.

        # Get the serial port to connect to.
        comport = QString(ui.comboBoxCOMPort.currentText())

        # Using pyserial and the user entered GUI stuff, open the damn serial port
        serial_port = serial.Serial(comport, baudnum,  timeout=5)

        if serial_port.isOpen():
            ui.textEditRx.setTextColor(QColor("green"))
            ui.textEditRx.setText("COM port is open!")
        else:
            ui.textEditRx.setTextColor(QColor("red"))
            ui.textEditRx.setText("COM port is closed!")
        # Revert back to black text.
        ui.textEditRx.setTextColor(QColor("black"))

        # This fires the timer that get's us into this application's while(1) loop!
        QtCore.QTimer.singleShot(1000, com.radioLegoApp(serial_port))

        return serial_port
    #-------------------------------------------------------------------------#

    def closeComPort(self):
        serial_port.close()
        ui.textEditRx.setTextColor(QColor("red"))
        ui.textEditRx.setText("COM port is closed!")
        ui.textEditRx.setTextColor(QColor("black"))
    #-------------------------------------------------------------------------#

    def quitTheApp(self):
        sys.exit(app.exec_())
        # This works but I get a 'Process finished with exit code 255' message?
        # Something about 'QCoreApplication::exec: The event loop is already running'...
    #-------------------------------------------------------------------------#

    def readComPort(self, serial_port, num_bytes):
        c =  ui.textEditSniffer.textCursor()
        ui.textEditSniffer.moveCursor(QTextCursor.End)
        ui.textEditSniffer.setTextCursor(c)

        # Get the data and post it to the box.
        rxdata = serial_port.read(num_bytes)
        print('rx data received = ', rxdata)

        for ch in rxdata:
            ui.textEditSniffer.insertPlainText(ch)

    #-------------------------------------------------------------------------#

    def getSerialPort(self):
        return self.com_port_opened

    #-------------------------------------------------------------------------#

    def sendData(self, dat):
        print('In sendData...')


###############################################################################

    def radioLegoApp(self, serial_port):
        while True:
            # Yield control back to the main application loop to process its stuff.
            QtGui.QApplication.processEvents()

            if serial_port._isOpen:
                # Set the class variable.
                com.com_port_opened = serial_port

                # How many bytes are in the receive queue?
                num_bytes = serial_port.inWaiting()
                if num_bytes > 0:
                    # Go check to see if we've received characters.
                    self.readComPort(serial_port, num_bytes)
###############################################################################

if __name__ == '__main__':
    # More or less a test to call a function to display the mainwindow GUI...
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = mainwindow.Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Set up fonts for sniffer window
    database = QFontDatabase()
    font = QFont()
    if 'Monospace' in database.families():
        font = QFont('Monospace', 8)
    else:
        for family in database.families():
            if database.isFixedPitch(family):
                font = QFont(family, 8)
    ui.textEditSniffer.setFont(font)

    # Display a default channel for sniffer
    tmp = ui.lineEditSinffChannel.setText('15')

    # Show the window
    mainwindow.show_mainwindow(app, MainWindow)

    # Use PySerial to setup the COM ports and the GUI.
    serial_port = serial.Serial()
    com = Com_Port('printing: com = radioblocks-sniffer.Com_Port')
    com.printme()
    com.findComPorts(ui, serial_port)

    # A call to the application code is in the 'openComPort' method - that's the only time we have valid
    # COM port data...

    # Start the application loop...
    sys.exit(app.exec_())






