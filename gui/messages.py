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
    GenericMessage.__init__(self, conn, 1, conn.login_properties)  #enum with Mxit.LOGIN = 1 

class TextMessage(GenericMessage):
  def __init__(self, conn, data): #data is a list specifying the user id and the message
    GenericMessage.__init__(self, conn, 10, data) #TODO enum


class MessageTree: #this will parse the message into a tree
  def __init__(self):
