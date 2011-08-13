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
from enums import *

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
    self.connect(self.receiver, QtCore.SIGNAL("update_user"), self.update_user)
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
        #print data.split(' ')[1:] #TODO translate user to proper user
        self.connection.send_message(data.split(' ')[1:]) #send the user and message as a list
        self.ui.lineEdit.setText('')
    
  def update_userlist(self, l):
    self.ui.listWidget.clear()
    for i in l:
      user_id = i[0]
      status = i[1]
      mood = i[2]
      status_text = Presence.status_list[int(status)]
      mood_text = Mood.mood_list[int(mood)]
      item = None

      if status == Presence.OFFLINE: 
        string = user_id + ' (' + status_text + ')'
        item = QtGui.QListWidgetItem(string)
        item.setTextColor(QtCore.Qt.gray)
      elif status == Presence.ONLINE:
        string = user_id + ' ('+status_text+')' + ' ('+mood_text+')'
        item = QtGui.QListWidgetItem(string)
        item.setTextColor(QtCore.Qt.darkGreen)
      elif status == Presence.AWAY: #TODO remove
        string = user_id + ' ('+status_text+')' + ' ('+mood_text+')'
        item = QtGui.QListWidgetItem(string)
        item.setTextColor(QtCore.Qt.orange)
      elif status == Presence.DO_NOT_DISTURB:#TODO remove
        string = user_id + ' ('+status_text+')' + ' ('+mood_text+')'
        item = QtGui.QListWidgetItem(string)
        item.setTextColor(QtCore.Qt.red)

      self.ui.listWidget.addItem(item)

  def update_user(self, user_id, presence, mood, status_message):
    pass

class Receiver(QtCore.QThread):
  def __init__(self, connection): #parent = None
    parent = None
    QtCore.QThread.__init__(self,parent) #self,parent
    self.running = 1
    self.connection = connection
    self.message_command = ''

  def run(self):
    while self.running:
      try:
        response = self.connection.socket.recv(self.connection.size)
        if not response:
          display = 'error'
          self.connection.disconnect()
        else: 
          display = self.parse_message(response) 
          #filter(lambda x: ord(x) > 0x19, response)
          
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
      if self.message_command == Command.GET_CONTACTS:
        response = LoginResponse(msg)
        returnValue = response.process()
        self.emit(QtCore.SIGNAL("update_userlist"), returnValue)
      elif self.message_command == Command.PRESENCE: #command is 7 presence
        response = PresenceResponse(msg)
        returnValue = response.process()
        self.emit(QtCore.SIGNAL("update_user"), returnValue) #returnValue contains the status, mood, and message
        pass
      elif self.message_command == Command.GET_MESSAGE: #new message
        response = TextMessageResponse(msg)
        returnValue = response.process()
        return returnValue
    
#    if not self.message_command == Command.GET_CONTACTS:
    print msg

    return 'Not Implemented Yet'

  def parse_packet(self, packet):
    split_records = packet.split('\0')
    split_fields = map(lambda x: x.split('\1') if len(x.split('\1')) > 1 else x, split_records)
    self.message_command = split_fields[1]
    return split_fields

