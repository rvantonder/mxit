#!/usr/bin/env python

import sip
sip.setapi('QVariant', 2)
import sys
from connection import * 
import select
import threading
from logger import Logger
import pickle
import os

from PyQt4 import QtCore, QtGui
from mxitwindow import Ui_Form

"""
The Client GUI class.
"""

def from_raw(msg):
  return ''.join(map(lambda x:chr(x), msg))

class ClientForm(QtGui.QWidget):
  def __init__(self, host, port, username, password):
    super(ClientForm, self).__init__()
    self.connection = Connection(host, port, username, password)

    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.ui.lineEdit.setFocus()
    self.auth = False
    self.colour_list = (QtCore.Qt.red, QtCore.Qt.darkRed, QtCore.Qt.blue, QtCore.Qt.darkGreen, QtCore.Qt.magenta, QtCore.Qt.darkBlue, QtCore.Qt.darkCyan,QtCore.Qt.darkMagenta, QtCore.Qt.darkYellow, QtCore.Qt.darkGray, QtGui.QColor('#00CC99'), QtGui.QColor('#0099FF'), QtGui.QColor('#005555'), QtGui.QColor('#FF6600'), QtGui.QColor('#660033'), QtGui.QColor('#9900FF'))
    self.user_colour_list = {}
    self.running = 1
    if os.path.isfile('client.log'):
      os.remove('client.log')
    self.clientLogger = Logger('client.log')

    self.receiver = Receiver(self.connection)
    self.connect(self.receiver, QtCore.SIGNAL("Activated ( QString ) "), self.activated)
    self.receiver.start()

    self.msg = [0x6c, 0x6e, 0x3d, 0x31, 0x34, 0x35, 0x00, 0x69, 
0x64, 0x3d, 0x66, 0x6c, 0x61, 0x74, 0x2e, 0x65, 
0x72, 0x69, 0x63, 0x00, 0x63, 0x6d, 0x3d, 0x31, 
0x00, 0x6d, 0x73, 0x3d, 0x47, 0x2f, 0x67, 0x58, 
0x41, 0x74, 0x59, 0x77, 0x38, 0x56, 0x64, 0x43, 
0x5a, 0x4e, 0x4f, 0x61, 0x30, 0x41, 0x41, 0x73, 
0x4b, 0x41, 0x3d, 0x3d, 0x01, 0x50, 0x2d, 0x35, 
0x2e, 0x39, 0x2e, 0x30, 0x2d, 0x59, 0x2d, 0x50, 
0x55, 0x52, 0x50, 0x4c, 0x45, 0x01, 0x31, 0x01, 
0x75, 0x74, 0x66, 0x38, 0x3d, 0x74, 0x72, 0x75, 
0x65, 0x3b, 0x63, 0x69, 0x64, 0x3d, 0x4c, 0x50, 
0x01, 0x45, 0x32, 0x33, 0x37, 0x39, 0x42, 0x35, 
0x35, 0x2d, 0x39, 0x34, 0x45, 0x31, 0x2d, 0x34, 
0x39, 0x34, 0x37, 0x2d, 0x39, 0x34, 0x39, 0x37, 
0x2d, 0x35, 0x44, 0x33, 0x44, 0x32, 0x43, 0x39, 
0x34, 0x36, 0x42, 0x46, 0x42, 0x01, 0x31, 0x33, 
0x33, 0x39, 0x37, 0x35, 0x34, 0x01, 0x32, 0x36, 
0x34, 0x01, 0x65, 0x6e, 0x01, 0x31, 0x35, 0x30, 
0x30, 0x30, 0x30, 0x01, 0x36, 0x30, 0x01, 0x30 ]

    self.connection.connect()
    print 'RIGHT'
    print messageToHex(from_raw(self.msg)) 
    print from_raw(self.msg)
#    self.connection.socket.send(from_raw(self.msg))
    self.connection.login() 

  def activated(self, text):
    self.ui.textEdit.append(text)

  def on_lineEdit_returnPressed(self):
    if self.ui.lineEdit.displayText() != '':
      #print 'sending',''.join(map(lambda x:chr(x), self.msg))
      print 'no action'
      #self.connection.socket.send(str(''.join(map(lambda x:chr(x), self.msg))))
                   
    self.ui.lineEdit.setText('')

class Receiver(QtCore.QThread):
  def __init__(self, connection): #parent = None
    parent = None
    QtCore.QThread.__init__(self,parent) #self,parent
    self.running = 1
    self.connection = connection

  def run(self):
    while self.running:
      try:
        response = self.connection.socket.recv(self.connection.size)
        #print response
        display = filter(lambda x: ord(x) > 0x30, response)
        self.emit(QtCore.SIGNAL("Activated( QString )"), display)
      except socket.error:
        return
          
    self.client.close_socket()

