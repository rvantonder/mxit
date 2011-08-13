import time
from enums import *

def messageToHex(msg):
  print ' '.join(map(lambda x:hex(ord(x)), msg))

def construct_msg(data):
  return '\1'.join(map(lambda x: str(x) if isinstance(x,int) else x, data))

class GenericMessage:
  def __init__(self, conn, cmd, data):
    self.conn = conn
    self.data = data
    self.cmd = cmd


  def send(self):
    rawstring = construct_msg(self.data)
   
    messageToSend = "id=" + self.conn.id + "\0cm=" + str(self.cmd) + "\0ms=" + rawstring 
    messageToSend = "ln=" + str(len(messageToSend)) + "\0" + messageToSend

    self.conn.socket.sendall(messageToSend)

  def __str__(self):
    return str(self.cmd) + str(self.data)

class LoginMessage(GenericMessage):
  def __init__(self, conn):
    GenericMessage.__init__(self, conn, Command.LOGIN, conn.login_properties)  #enum with Mxit.LOGIN = 1 

class TextMessage(GenericMessage):
  def __init__(self, conn, data): #data is a list specifying the user id and the message
    GenericMessage.__init__(self, conn, Command.SEND_MESSAGE, data) #TODO enum

class GetContactsMessage(GenericMessage):
  def __init__(self, conn):
    GenericMessage.__init__(self, conn, Command.GET_CONTACTS, '') 

  def send(self):
    messageToSend = "id=" + self.conn.id + "\0cm=" + str(self.cmd)  
    messageToSend = "ln=" + str(len(messageToSend)) + "\0" + messageToSend

    self.conn.socket.sendall(messageToSend)


class MessageResponse: #this will parse the message into a tree
  def __init__(self, msg):
    self.msg = msg
    self.ln = msg[0]
    self.cmd = msg[1]
    self.error = msg[2]

  def process(self):
    pass

  def check_error(self):
    return not self.error == Error.NONE
      

class LoginResponse(MessageResponse):
  def __init__(self, msg):
    MessageResponse.__init__(self, msg)

  def process(self): #return list of users
    if self.check_error(): return None 
    l = []
    for user in self.msg[3:-1]: #data lists of users 
      l.append((user[1],user[2],user[3],user[5])) #0: group 1: contact address 2:nick 3: presence 4: type 5: mood 6: flags 7: subtype
    return l

class PresenceResponse(MessageResponse):
  def __init__(self, msg):
    MessageResponse.__init__(self, msg)
    self.user_id = msg[3][0]
    self.presence = msg[3][1]
    self.mood = msg[3][2]
    self.status_message = msg[3][4]

  def process(self):
    if self.check_error(): return None
    return [self.user_id, self.presence, self.mood, self.status_message] 

class TextMessageResponse(MessageResponse):
  def __init__(self, msg):
    MessageResponse.__init__(self, msg)

  def process(self): #return message to display
    if self.check_error(): return None

    t = time.ctime(int(self.msg[3][1])).split()[3]
    return '[' + t + '] ' + self.msg[3][0] +': ' + self.msg[-1]
 
    
    
