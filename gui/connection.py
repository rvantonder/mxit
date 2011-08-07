#!/usr/bin/env python

import socket
import sys
import select
from logger import Logger
from messages import *

class Connection:

  def __init__(self, ip, port, username, password, nick):
    self.host = ip
    self.port = port 
    self.size = 1024
    self.socket = None

    properties = {
      'username':username,
      'password':password,
      'nick':nick,
      'version':'P- 5.9.0-Y-PURPLE', 
      'getContacts':'1',
      'capabilities':'utf8=true;cid=LP',
      'dc':'4DF78289-3578-4701-81C1-760225BAE46C',
      'features':255,
      'dialingCode':27,
      'locale':'en',
      'maxReplyLen':150000,
      'protocolVer':60,
      'splashName':0
    }

    set_attrs(self,properties,**params)

  def connect(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((self.host, self.port))

  def disconnect(self):
    self.socket.close()

  def login(self):
     
       
