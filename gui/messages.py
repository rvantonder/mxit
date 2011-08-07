def construct_msg(data):
  msg = '\1'.join(map(lambda x: str(x) if isinstance(x,int) else x, data))
  return msg

  

class GenericMessage:
  def __init__(self, conn, cmd, data):
    self.conn = conn
    self.data = data
    self.cmd = cmd


  def send(self):
    rawstring = construct_msg(self.data)
   
    messageToSend = "id=" + self.conn.id + "\0cm=" + str(self.cmd) + "\0ms=" + rawstring
    messageToSend = "ln=" + str(len(messageToSend)) + "\0" + messageToSend

    print 'sending ',messageToSend

    self.conn.socket.sendall(messageToSend)
    

class LoginMessage:
  def __init__(self, conn):
    GenericMessage.__init__(self, conn, 1, conn.properties.values())  #enum with Mxit.LOGIN = 1 
