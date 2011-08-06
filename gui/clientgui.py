#!/usr/bin/env python

import sip
sip.setapi('QVariant', 2)
import sys
from subprocess import Popen
import subprocess
from client import *  #import the client
import select
import threading
from logger import Logger
import socket
import pickle
import os

from PyQt4 import QtCore, QtGui
from clientwindow import Ui_Form

"""
The Client GUI class.
"""

class ClientForm(QtGui.QWidget):
  def __init__(self, host, port):
    super(ClientForm, self).__init__()
    self.client = Client(host,port)

    self.client.open_socket()    

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

    self.receiver = Receiver(self.client)
    self.connect(self.receiver, QtCore.SIGNAL("Activated ( QString ) "), self.activated)
    self.receiver.start()

#    self.msg = 'ln=145\x00id=0716223917\x00cm=1\x00ms=3NZjbv5S02qK0YkoOjiQrw==\x01P-5.9.0-Y-PURPLE\x011\x01utf8=true;cid=LP\x014DF78289-3578-4701-81C1-760225BAE46C\x011339754\x0127\x01en\x01150000\x0160\x010'
    self.msg = [0x6c, 0x6e, 0x3d, 0x31, 0x34, 0x35, 0x00, 0x69, 
0x64, 0x3d, 0x30, 0x37, 0x31, 0x36, 0x32, 0x32, 
0x33, 0x39, 0x31, 0x37, 0x00, 0x63, 0x6d, 0x3d, 
0x31, 0x00, 0x6d, 0x73, 0x3d, 0x33, 0x4e, 0x5a, 
0x6a, 0x62, 0x76, 0x35, 0x53, 0x30, 0x32, 0x71, 
0x4b, 0x30, 0x59, 0x6b, 0x6f, 0x4f, 0x6a, 0x69, 
0x51, 0x72, 0x77, 0x3d, 0x3d, 0x01, 0x50, 0x2d, 
0x35, 0x2e, 0x39, 0x2e, 0x30, 0x2d, 0x59, 0x2d, 
0x50, 0x55, 0x52, 0x50, 0x4c, 0x45, 0x01, 0x31, 
0x01, 0x75, 0x74, 0x66, 0x38, 0x3d, 0x74, 0x72, 
0x75, 0x65, 0x3b, 0x63, 0x69, 0x64, 0x3d, 0x4c, 
0x50, 0x01, 0x34, 0x44, 0x46, 0x37, 0x38, 0x32, 
0x38, 0x39, 0x2d, 0x33, 0x35, 0x37, 0x38, 0x2d, 
0x34, 0x37, 0x30, 0x31, 0x2d, 0x38, 0x31, 0x43, 
0x31, 0x2d, 0x37, 0x36, 0x30, 0x32, 0x32, 0x35, 
0x42, 0x41, 0x45, 0x34, 0x36, 0x43, 0x01, 0x31, 
0x33, 0x33, 0x39, 0x37, 0x35, 0x34, 0x01, 0x32, 
0x37, 0x01, 0x65, 0x6e, 0x01, 0x31, 0x35, 0x30, 
0x30, 0x30, 0x30, 0x01, 0x36, 0x30, 0x01, 0x30]

  def activated(self, text):
    self.ui.textEdit.setText(text)

  def on_lineEdit_returnPressed(self):
    if self.ui.lineEdit.displayText() != '':
      #stringToSend = self.ui.lineEdit.displayText()
      print 'sending',''.join(map(lambda x:chr(x), self.msg))
      self.client.socket.send(str(''.join(map(lambda x:chr(x), self.msg))))
                   
    self.ui.lineEdit.setText('')

class Receiver(QtCore.QThread):
  def __init__(self, client): #parent = None
    parent = None
    QtCore.QThread.__init__(self,parent) #self,parent
    self.running = 1
    self.client = client

  def run(self):
    while self.running:
      try:
        response = self.client.socket.recv(self.client.size)
        print response
        self.emit(QtCore.SIGNAL("Activated( QString )"), response)
      except socket.error:
        return
          
    self.client.close_socket()

