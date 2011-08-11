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
  def __init__(self, host, port, username, password, dc):
    super(ClientForm, self).__init__()
    self.connection = Connection(host, port, username, password, dc)

    self.connection.connect()

    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.ui.lineEdit.setFocus()
    self.running = 1
    if os.path.isfile('client.log'):
      os.remove('client.log')
    self.clientLogger = Logger('client.log')

    self.receiver = Receiver(self.connection)
    self.connect(self.receiver, QtCore.SIGNAL("Activated ( QString ) "), self.activated)
    self.connect(self.receiver, QtCore.SIGNAL("update_userlist"), self.update_userlist)
    self.receiver.start()

    self.connection.login() 

  def activated(self, text):
    self.ui.textEdit.append(text)

  def on_lineEdit_returnPressed(self):
    if self.ui.lineEdit.displayText() != '':
      data = str(self.ui.lineEdit.displayText())
      if not data.startswith(r'\msg'):
        self.ui.lineEdit.setText('Format: \msg <user> <message>')
      else:
        print data.split(' ')[1:] #TODO translate user to proper user
        self.connection.send_message(data.split(' ')[1:]) #send the user and message as a list
        self.ui.lineEdit.setText('')
    
  def update_userlist(self, l):
    for i in l:
      string = i[0] + ' (status:'+i[1]+')' + ' (mood:'+i[2]+')' #TODO translate this
      self.ui.listWidget.addItem(QtGui.QListWidgetItem(string))

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
        if not response:
          display = 'error'
          self.connection.disconnect()
        else: 
          display = self.parse_message(response) 
          display = filter(lambda x: ord(x) > 0x19, response)
          
        self.emit(QtCore.SIGNAL("Activated( QString )"), display)
        #return
      except socket.error:
        return
          
    self.connection.disconnect() #TODO fix

  def parse_message(self, response):
    split_packets = response.split('ln=')[1:] #very nice
    l = []
    for i in split_packets:
      msg = self.parse_packet(i)
      print msg
      if msg[1] == '3': #command is login
        for user in msg[3:-1]: #data lists of users 
          l.append((user[2],user[3],user[5])) #0: group 1: contact address 2:nick 3: presence 4: type 5: mood 6: flags 7: subtype
          self.emit(QtCore.SIGNAL("update_userlist"), l)
      elif msg[1] == '7': #command is 7
        print 'command: 7'

        self.emit(QtCore.SIGNAL("update_userlist"), l)
        

  def parse_packet(self, packet):
    split_records = packet.split('\0')
    split_fields = map(lambda x: x.split('\1') if len(x.split('\1')) > 1 else x, split_records)
    return split_fields

