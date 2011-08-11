#!/usr/bin/env python

import socket
import sys
import select
from logger import Logger
from messages import *

class Connection:

  def __init__(self, ip, port, username, password, dc):
    self.host = ip
    self.port = port 
    self.size = 1024
    self.socket = None

    self.id = username

    self.properties = { 
      'password':password,
      'version':'P-5.9.0-Y-PURPLE', 
      'getContacts':1,
      'capabilities':'utf8=true;cid=LP',
      'dc':dc,
      'features':255,
      'dialingCode':27,
      'locale':'en',
      'maxReplyLen':150000,
      'protocolVer':60,
    }
  
    self.login_properties = [password, 'P-5.9.0-Y-PURPLE', 1, 'utf8=true;cid=LP', dc, 255, 27, 'en', 150000, 60] 

  def connect(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((self.host, self.port))

  def disconnect(self):
    self.socket.close()

  def login(self):
#    g = GenericMessage(self,1, self.login_properties)  
    #g.send()
    l = LoginMessage(self)
    l.send()

  def parse_message(self, response):
    print '-------------------------------------'
    split_packets = response.split('ln=')[1:] #very nice
    print 'response length',len(split_packets)
    for i in split_packets:
      self.parse_packet(i)
    print '-------------------------------------'

  def parse_packet(self, packet):
    split_records = packet.split('\0')
    split_fields = map(lambda x: x.split('\1') if len(x.split('\1')) > 1 else x, split_records)
    print split_fields

