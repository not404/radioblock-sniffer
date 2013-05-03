# Copyright (c) 2011 - 2013, SimpleMesh AUTHORS
# Eric Gnoske,
# Colin O'Flynn,
# Blake Leverett,
# Rob Fries,
# Clara Ferrando,
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

import ui_sniffer
import ui_about
import sys
import time 
import string

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtGui import QColor, QTextCursor
from threading import Thread, Timer
from multiprocessing import Queue   
from com_handler import comHandler

try:
    from PySide.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")


# ------------------------------------------------------------------------
#                   DEFINITIONS
# ------------------------------------------------------------------------
INTERVAL = 0.2

FCF =[0,0 + 4]
SEQ =[4, 4 + 2]
PID = [6, 6 + 4]
MDST = [10, 10 + 4]
MSRC= [14, 14 + 4]
HDL= [18, 18 + 2]
SEQ2 = [20, 20 + 2]
MACDST = [22, 22 + 4]
MACSRC = [26, 26 + 4]
PAYLOAD = [30, -4]
LQI = [-4, -2]
RSSI = [-2,-1]


FIELDS = [FCF,SEQ,PID,MDST,MSRC,HDL,SEQ2,MACDST,MACSRC,PAYLOAD,LQI]


colNames = ["Timestamp","Channel","FCF",\
            "Sequence" ,"PANID"  ,"MAC Dest",\
            "MAC Src"  ,"NWK FCF" ,"NWK Seq", "NWK Src" ,\
            "NWK Dest" ,"LQI"    ,"RSSI",\
            "PAYLOAD"]


STYLE_ACTIVE = 'QToolButton#<BUTTON> { color: yellow; background-color:#FFff00\
; border:2px solid white; border-radius: 8px; border-bottom-color: \
    grey; border-right-color:black;padding-bottom:5px; font:bold}'


STYLE_INACTIVE = 'QToolButton#<BUTTON> { color: yellow; background-color:#ffff99\
; border:2px solid white; border-radius: 8px; border-bottom-color: \
    grey; border-right-color:black;padding-bottom:5px; font:bold}'


def getDateStamp ():
    now = datetime.datetime.now()
    return ( now.strftime("%d_%m_%Y_%H.%M") )


# ------------------------------------------------------------------------
#                   Classes
# ------------------------------------------------------------------------
# About Dialog Class 
class SM_About(QDialog, ui_about.Ui_Dialog):
    def __init__(self, parent=None):
        super(SM_About, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.RightButton:
            pass
        else:
            self.close()

    def keyPressEvent(self, event):
        self.close()


# Main Window Class 
class RB_MainWindow(QMainWindow, ui_sniffer.Ui_MainWindow):
    def __init__(self, parent=None):
        super(RB_MainWindow, self).__init__(parent)

        self.ctrlQueue = Queue()
        self.respQueue = Queue()
        [self.IDLE,self.PLAY,self.PAUSE]=[0,1,2]
        # Create Com object
        self.ComHandler = comHandler(self.ctrlQueue,self.respQueue)
        self.ComHandler.start()

        self.status = self.IDLE

        self.setupUi(self)

        self.timer = QTimer()
        QObject.connect(self.timer, SIGNAL("timeout()"), self.getFrames)
        self.timer.start(INTERVAL)

        self.comboBoxPorts.addItems(self.ComHandler.ports)
        QObject.connect(self.comboBoxChannel, SIGNAL("currentIndexChanged(QString)"), self.processChannelCmd)

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(False)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setModel(self.proxyModel)
        self.tableView.setSortingEnabled(False)

        self.FlashTimer = QTimer(self)
        self.FlashTimer.timeout.connect(self.flashTimeout)
        self.channel = '15'
        self.filterActive = False
        QObject.connect(self.tableView.selectionModel(), SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.updateRow)
        self.comboBoxField.addItems(colNames[1:11])
        

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)
        
                
    def getFrames (self):
        while not(self.respQueue.empty()):
            self.frameToProcess = self.respQueue.get()
            if self.frameToProcess[0]=="comopen":

                if self.frameToProcess[1]== True:
                    self.statusbar.showMessage("COM port opened",5000)
                    self.toolButtonConnect.setStyleSheet(STYLE_ACTIVE.replace('<BUTTON>',"toolButtonConnect"));            
                    self.ComHandler.serial_port.write("G")
                else:
                    self.statusbar.showMessage("COM port closed",5000)
                    self.toolButtonConnect.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonConnect"));            

            elif self.frameToProcess[0]=="frame":

                if self.status == self.PLAY:
                    self.toolButtonBoard.setStyleSheet(STYLE_ACTIVE.replace('<BUTTON>',"toolButtonBoard"));            
                    self.FlashTimer.start(400)
                    if self.filterActive:
                        self.clearFilter()
                    # -------------------------------------------------
                    addFrame(self.proxyModel, self.arrangeFrame(self.frameToProcess[1:]),self.tableView)    
                    # -------------------------------------------------
                    if self.filterActive:
                        self.applyFilter()

            elif self.frameToProcess[0]=="channel":

                self.channel = self.frameToProcess[1]
                self.statusbar.showMessage("Sniffer channel set to " + self.channel,5000)
                self.comboBoxChannel.blockSignals(True) 
                self.comboBoxChannel.setCurrentIndex(int(self.channel) - 10)
                self.comboBoxChannel.blockSignals(False) 
    

    def flashTimeout (self):
        self.toolButtonBoard.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonBoard"));            


    def arrangeFrame (self, timeframe):
        frame = [timeframe[0]]
        frame.append(self.channel)
        fields = self.getFrameFields (timeframe[1])
        for i in range(len(fields)):
            frame.append(fields[i])
        return frame


    #FIELDS = [FCF,SEQ,PID,MDST,MSRC,HDL,SEQ2,MACDST,MACSRC,LQI,RSSI]
    def getFrameFields (self,frame):
        out = []
        for i in range(len(FIELDS)):
            start = FIELDS[i][0]
            end = FIELDS[i][1]
            out.append(frame[start:end])
        
        # check if it is an ACK frame. If so remove PANID
        if out[0]=="0002":
            out[2] = ""

        out.append(frame[-2:])
        out[-3],out[-1]=out[-1],out[-3]
        return out


    def setColumnWidths (self):
        self.tableView.setColumnWidth(0, 80)
        for i in range(1,len(colNames)-1):
            self.tableView.setColumnWidth(i, 60)
        header = self.tableView.horizontalHeader()
        header.setStretchLastSection(True)
        #QHeaderView.stretchLastSection()
# ------------------------------------------------------------------------
#                   EVENTS
# ------------------------------------------------------------------------
    def closeEvent (self, event):
        self.ComHandler.quit()
        self.close()


    @Slot("")
    def on_toolButtonConnect_clicked(self):
        port = self.comboBoxPorts.currentText()
        if len(port):
            if self.ComHandler.serial_port.isOpen():
                self.ComHandler.closeComPort()
                self.status = self.IDLE
                self.toolButtonPlay.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonPlay"));            
                self.toolButtonPause.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonPause"));            
            else:
                self.ComHandler.openComPort(port)


    @Slot("")
    def on_toolButtonPlay_clicked(self):
        if (self.status == self.IDLE \
            and self.ComHandler.serial_port.isOpen()):
            self.status = self.PLAY
            self.toolButtonPlay.setStyleSheet(STYLE_ACTIVE.replace('<BUTTON>',"toolButtonPlay"));            
    
    
    @Slot("")
    def on_toolButtonPause_clicked(self):
        if self.status == self.PLAY:
            self.status = self.PAUSE
            self.toolButtonPlay.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonPlay"));            
            self.toolButtonPause.setStyleSheet(STYLE_ACTIVE.replace('<BUTTON>',"toolButtonPause"));            

        elif self.status == self.PAUSE:
            self.status = self.PLAY
            self.toolButtonPlay.setStyleSheet(STYLE_ACTIVE.replace('<BUTTON>',"toolButtonPlay"));            
            self.toolButtonPause.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonPause"));            


    @Slot("")
    def on_toolButtonTrash_clicked(self):
        self.tableView.blockSignals(True) 
        while self.proxyModel.rowCount():
            self.proxyModel.removeRow(0)
        self.tableView.blockSignals(False) 
        self.textEdit.setText("")

    @Slot("")
    def on_toolAbout_clicked(self):
        aboutDialog = SM_About()
        aboutDialog.show()
        aboutDialog.exec_()


    def updateFrameInformation (self,idx):
        if self.proxyModel.rowCount() == 0:
            print "no Rows!"
            return
        self.tableView.blockSignals(True) 
        self.textEdit.setText("")
        payload = self.proxyModel.data(self.proxyModel.index(idx.row(), len(colNames)-1), Qt.DisplayRole)
        timestamp = '<span style="background-color:yellow;">Timestamp</span>:&nbsp;' + self.proxyModel.data(self.proxyModel.index(idx.row(), 0), Qt.DisplayRole)
        channel = '<span style="background-color:yellow;">Channel</span>:&nbsp;' + self.proxyModel.data(self.proxyModel.index(idx.row(), 1), Qt.DisplayRole)
        macsrc = '<span style="background-color:yellow;">MAC Src</span>:&nbsp;' + self.proxyModel.data(self.proxyModel.index(idx.row(), 6), Qt.DisplayRole)
        self.textEdit.append('<table><tr><td>' +timestamp + '</td><td>&nbsp;&nbsp;' + channel + '</td><td>&nbsp;&nbsp;' + macsrc + "</td></tr>")
        self.setPayloadText(payload)
        self.tableView.blockSignals(False) 


    @Slot(QModelIndex)
    def on_tableView_clicked(self,idx):
        self.updateFrameInformation(idx)


    def updateRow (self, selon, seloff):
        if selon.row()>0:
            self.updateFrameInformation (selon)


    def getHexString (self,hexstr):
        out = ''
        for i in range(len(hexstr) >> 1):
            out += hexstr[i*2: i*2 + 2] + " "
        return out


    def getAsciiString (self,hexstr):
        ascii = hexstr.decode('hex')
        out = ''
        i = 0
        while i < (len(ascii) ):
            if ascii[i] in string.printable :
                out += ascii[i]
            else:
                hexnumber = str(hex(ord(ascii[i])))[2:]
                if len(hexnumber)==1:
                    hexnumber = '0' + hexnumber
                nonp = "[" + hexnumber + "]"                
                out += nonp
            i += 1
        return out


    def setPayloadText (self,payload):
        self.textEdit.append('<tr><td><span style="background-color:yellow;">Payload</span></td></tr><tr><td><span style="background-color:yellow;">[hex]</span>  : ' + self.getHexString(payload) + "</td></tr>")
        self.textEdit.append('<tr><td><span style="background-color:yellow;">[ascii]</span>: ' +  self.getAsciiString(payload) + "</td></tr></table>")


    def getColumn (self):
        field = self.comboBoxField.currentText()
        return colNames.index(field)
    

    def clearFilter (self):
        column = self.comboBoxField.currentText()
        value = self.lineEditValue.text()

        self.proxyModel.setFilterKeyColumn(self.getColumn())
        self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)

        # 0 Reg exp, 1 wildcard , 2 fixed string
        syntax = QRegExp.PatternSyntax(0)

        # unfilter first
        regExp = QRegExp("" ,Qt.CaseInsensitive, syntax)
        self.proxyModel.setFilterRegExp(regExp)


    def applyFilter (self):
        column = self.comboBoxField.currentText()
        value = self.lineEditValue.text()

        self.proxyModel.setFilterKeyColumn(self.getColumn())
        self.proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)

        # 0 Reg exp, 1 wildcard , 2 fixed string
        syntax = QRegExp.PatternSyntax(0)

        # unfilter first
        regExp = QRegExp("" ,Qt.CaseInsensitive, syntax)

        # apply filter now
        regExp = QRegExp(self.lineEditValue.text() ,Qt.CaseInsensitive, syntax)
        self.proxyModel.setFilterRegExp(regExp)


    @Slot("")
    def on_toolButtonFilterClear_clicked(self):
        self.lineEditValue.setText("")
        self.filterActive = False
        self.clearFilter()
        self.toolButtonFilter.setStyleSheet(STYLE_INACTIVE.replace('<BUTTON>',"toolButtonFilter"));            
        
            
    @Slot("")
    def on_toolButtonFilter_clicked(self):
        if len(self.lineEditValue.text()):
            self.filterActive = True
            self.toolButtonFilter.setStyleSheet(STYLE_ACTIVE.replace('<BUTTON>',"toolButtonFilter"));            
        self.applyFilter()


    @Slot("")
    def on_toolButtonLog_clicked(self):
        fname = getDateStamp () + ".log"
        fhandler = open(fname, "wb")
        for i in range(self.proxyModel.rowCount()-1,-1,-1):
            print i
            for j in range(len(colNames)):
                print self.proxyModel.data(self.proxyModel.index(i, j), Qt.DisplayRole),
                fhandler.write(self.proxyModel.data(self.proxyModel.index(i, j), Qt.DisplayRole))
                if j < len(colNames) - 1:
                    fhandler.write(",")
            print 
            fhandler.write("\n")
        fhandler.close()
        self.statusbar.showMessage("Log file " + fname + " created",5000)


    @Slot("")
    def on_toolButtonExit_clicked(self):
        pass


    def processChannelCmd (self,channel):
        if self.ComHandler.serial_port.isOpen():
            command = "C" + str(channel) 
            self.ComHandler.serial_port.write(command)
            time.sleep(0.1)
            self.ComHandler.serial_port.write("G")
        else:
            self.comboBoxChannel.setCurrentIndex(0)


def addFrame(model, fields, tableview):
    model.insertRow(0)
    for i in range(len(fields)):
        model.setData(model.index(0, i), fields[i])


def createModel(parent):
    model = QStandardItemModel(0, len(colNames), parent)
    for i in range(len(colNames)):
        model.setHeaderData(i, Qt.Horizontal, colNames[i])
    return model


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = RB_MainWindow()
    form.setSourceModel(createModel(form))
    form.setColumnWidths()
    form.show()
    app.exec_()



