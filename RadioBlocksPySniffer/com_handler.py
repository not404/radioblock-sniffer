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

from threading import Thread, Timer
import serial
import platform
import scanlinux
import scan
import datetime
import sys
import time

TOKEN = '0a0b0c0d'

def getTimeStamp ():
    datetimestamp = datetime.datetime.now()
    return ( datetimestamp.strftime("%H:%M:%S.%f")[:-3] )


class comHandler (Thread):
    # Com port related defines
    PARITY_NAMES = {
        'none' :serial.PARITY_NONE,
        'even' :serial.PARITY_EVEN,  
        'odd'  :serial.PARITY_ODD,  
        'mark' :serial.PARITY_MARK,  
        'space':serial.PARITY_SPACE, 
    }


    def __init__(self,ctrlQueue,respQueue):
        # Init serial object and find available com ports
        self.serial_port = serial.Serial()
        self.ports = self.findComPorts(self.serial_port)
        self.comReconfigureRequest = False

        # set queue objects
        self.ctrlQ = ctrlQueue
        self.respQ = respQueue

        #set RX parser objects
        [self.START,self.TOKEN,self.LENGTH_HI,self.LENGTH_LO,self.PAYLOAD]= [0,1,2,3,4]

        self.state = self.START
        self.frame = []
        self.length = 0
        self.cmdid = 0
        self.crc = [0x00,0x00]

        #self.respQ.put({'ports': self.ports})
        self.go = True

        self.dict = {'open':self.openComPort,
                     'close':self.closeComPort,
                     'quit':self.quit,   
                     }

        self._baudrate = None          
        self._bytesize = None          
        self._parity   = None          
        self._stopbits = None          
        self.timeout = None
        self.runningScript = sys.argv[0] 
        Thread.__init__(self)


    def run (self):
        while self.go:
            if self.serial_port.isOpen():
                 try:
                     num = self.serial_port.inWaiting()
                     bytes = self.serial_port.read(num)
                     idx = 0
                     while (num):
                         rxbyte = bytes[idx]
                         idx = idx + 1
                         num = num -1
                         self.parseRxData(rxbyte)    
                 except:
                     pass
            else:
                pass


    def findComPorts(self, serial_port):
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
        return ports


    def setComDefaults(self):
        self._bytesize = 8
        self._parity = 'N'
        self._stopbits = 1
        self._baudrate = 115200


    def openComPort(self, comport, baudrate = 115200, databits=8, parity='N',stopbits = 1):
        if self.serial_port.isOpen():
            return

        self.setComDefaults()

        if databits in self.serial_port.BYTESIZES:
            self._bytesize = databits

        if parity in self.PARITY_NAMES.keys():
            self._parity = parity

        if stopbits in self.serial_port.STOPBITS:
            self._stopbits = stopbits

        if baudrate in self.serial_port.BAUDRATES:
            self._baudrate = baudrate

        self.serial_port = serial.Serial(comport, self._baudrate, self._bytesize,  self._parity, self._stopbits, \
                                         timeout=5)

        if self.serial_port.isOpen():
            self.respQ.put(["comopen" , True])
        else:
            self.respQ.put(["comopen" , False])
        return self.serial_port


    def closeComPort(self):
        if self.serial_port.isOpen():
            self.serial_port.close()
            self.respQ.put(["comopen" , False])


    def parseRxData (self,rxbyte):
        if self.state == self.START:
            self.token = ""
            
            if rxbyte == TOKEN[0]:
                self.state += 1
                self.token = TOKEN[0]

            elif ord(rxbyte)>=11 and ord(rxbyte)<=25:
                self.respQ.put(["channel" , str(ord(rxbyte))])
                
            return
    
        elif self.state == self.TOKEN:
            if TOKEN == self.token + rxbyte:
                self.state += 1
            elif TOKEN.startswith(self.token + rxbyte):
                self.token += rxbyte
            else:
                self.state = self.START
            return
    
        elif self.state == self.LENGTH_HI:
            self.framelen = rxbyte
            self.state += 1
            return
    
        elif self.state == self.LENGTH_LO:
            self.framelen = self.framelen + rxbyte
            self.length = int(self.framelen,16)*2
            self.state += 1
            self.frame = ""
            return

        elif self.state == self.PAYLOAD:
            if self.length >= 1:
                self.frame += rxbyte
                self.length = self.length - 1
                if self.length == 0:
                    self.state = self.START
                    frame = ["frame",getTimeStamp(), ''.join(self.frame)]
                    self.respQ.put(frame)
            else:
                self.state = self.START
                frame = ["frame",getTimeStamp(), ''.join(self.frame)]
                self.respQ.put(frame)
            return


    def quit(self):
        self.go = False
        if self.serial_port.isOpen():
            self.serial_port.close()
        
        

