#!/usr/bin/env python

import socket
import sys
import select
from logger import Logger
from messages import *

class Connection:

  def __init__(self, ip, port, username, password):
    self.host = ip
    self.port = port 
    self.size = 1024
    self.socket = None

    self.id = username

    self.properties = { 
      'password':password,
      'version':'P-5.9.0-Y-PURPLE', 
      'getContacts':'1',
      'capabilities':'utf8=true;cid=LP',
      #'dc':'4DF78289-3578-4701-81C1-760225BAE46C',
      'dc':'E2379B55-94E1-4947-9497-5D3D2C946BFB',
      #'features':255,
      'features':1339754,
      #'dialingCode':27,
      'dialingCode':264,
      'locale':'en',
      'maxReplyLen':150000,
      'protocolVer':60,
    }


  def connect(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((self.host, self.port))

  def disconnect(self):
    self.socket.close()

  def login(self):
    g = GenericMessage(self,1, [self.properties['password'], self.properties['version'], self.properties['getContacts'], self.properties['capabilities'], self.properties['dc'], 
                                self.properties['features'], self.properties['dialingCode'], self.properties['locale'], self.properties['maxReplyLen'], self.properties['protocolVer']]) #looks retarded
    g.send()
    pass
