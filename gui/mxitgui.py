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

from PyQt4 import QtCore, QtGui, Qt
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
      if not data.startswith(r'\msg '):
        self.ui.lineEdit.setText('Format: \msg <user_id> <message>')
      else:
        msg = ' '.join(data.split(' ')[2:])
        u = data.split(' ')[1]
        if u == '' or msg == '':
          self.ui.lineEdit.setText('Format: \msg <user_id> <message>')
        else:
          try:
            self.connection.send_message([u,msg]) #send the user and message as a list
            self.ui.textEdit.append(self.connection.id + ': ' + u + ', ' + msg)
          except socket.error:
            self.ui.lineEdit.setText('You cannot send messages because you are not connected')
          self.ui.lineEdit.setText('')
    
  def update_userlist(self, l):
    self.ui.listWidget.clear()
    for i in l:
      user_id = i[0]
      nick = i[1]
      status = i[2]
      mood = i[3]
      status_text = Presence.status_list[int(status)]
      mood_text = Mood.mood_list[int(mood)]
      item = None

      if status == Presence.OFFLINE: 
        string = nick + ' (' + status_text + ')' + ' (' + user_id + ')'
        item = QtGui.QListWidgetItem(string)
        item.setTextColor(QtCore.Qt.gray)
      elif status == Presence.ONLINE:
        string = nick + ' ('+status_text+')' + ' ('+mood_text+')' + ' (' + user_id + ')'
        item = QtGui.QListWidgetItem(string)
        item.setTextColor(QtCore.Qt.darkGreen)

      self.ui.listWidget.addItem(item)

  def update_user(self, l):
    user_id, presence, mood, status_message = l
    status = presence 
    mood = mood
    status_text = Presence.status_list[int(status)]
    mood_text = Mood.mood_list[int(mood)]

    try:
      item = self.ui.listWidget.findItems(user_id,QtCore.Qt.MatchContains)[0]

      if status == Presence.OFFLINE:
        item.setText(str(item.text()).split()[0] + ' (' + status_text + ')' + ' (' + user_id + ')')
        item.setTextColor(QtCore.Qt.gray)
      elif status == Presence.ONLINE:
        item.setText(str(item.text()).split()[0] + ' (' + status_text + ')' + ' (' + mood_text + ')' + ' (' + status_message + ')' + ' (' + user_id + ')')
        item.setTextColor(QtCore.Qt.darkGreen)
      elif status == Presence.AWAY:
        item.setText(str(item.text()).split()[0] + ' (' + status_text + ')' + ' (' + mood_text + ')' + ' (' + status_message + ')' + ' (' + user_id + ')')
        item.setTextColor(QtGui.QColor('#FF6600'))
      elif status == Presence.DO_NOT_DISTURB:
        item.setText(str(item.text()).split()[0] + ' (' + status_text + ')' + ' (' + mood_text + ')' + ' (' + status_message + ')' + ' (' + user_id + ')')
        item.setTextColor(QtCore.Qt.red)
    except IndexError:
      print 'Error in creating user list'

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
          self.connection.disconnect()
          self.emit(QtCore.SIGNAL("Activated( QString )"), 'A connection error occurred, disconnected')
        else: 
          display = self.parse_message(response) 
          if not display == None:
            self.emit(QtCore.SIGNAL("Activated( QString )"), display)
      except socket.error:
        print 'An unexpected error occurred, disconnecting.'
        return
          
    self.connection.disconnect() #if the loop is exited, disconnect 

  def parse_message(self, response):
    split_packets = response.split('ln=')[1:] #very nice
    l = []
    for i in split_packets:
      msg = self.parse_packet(i)
      print msg
      if self.message_command == Command.LOGIN: #this happens when a user logs in while mxit already sees them as being logged in
        response = LoginResponse(msg)
        returnValue = response.process()
        if returnValue: #there was an error
          return response.get_error()
        else:
          self.emit(QtCore.SIGNAL("Activated( QString )"), 'Login successful, this is your current session')  
      elif self.message_command == Command.LOGOUT:
        response = LogoutResponse(msg)
        returnValue = response.process()
        if returnValue: #an error, such as logging in from another location
          return response.get_error()
        else:
          return 'Logout Successful'
      elif self.message_command == Command.GET_CONTACTS:
        response = GetContactsResponse(msg)
        returnValue = response.process()
        self.emit(QtCore.SIGNAL("update_userlist"), returnValue)
        return None
      elif self.message_command == Command.PRESENCE: 
        response = PresenceResponse(msg)
        returnValue = response.process()
        self.emit(QtCore.SIGNAL("update_user"), returnValue) #returnValue contains the status, mood, and message
        return None
      elif self.message_command == Command.GET_MESSAGE: 
        response = TextMessageResponse(msg)
        returnValue = response.process()
        return returnValue
      elif self.message_command == Command.SEND_MESSAGE:
        response = MessageSentResponse(msg)
        returnValue = response.process()
        if returnValue: #there was an error
          return response.get_error()
        else:
          return None #the message was successfully sent
      else:
        response = MessageResponse(msg)
        returnValue = response.process()
        return returnValue
    
    #print msg
    #return 'Not Implemented Yet'

  def parse_packet(self, packet):
    split_records = packet.split('\0')
    split_fields = map(lambda x: x.split('\1') if len(x.split('\1')) > 1 else x, split_records)
    self.message_command = split_fields[1]
    return split_fields

