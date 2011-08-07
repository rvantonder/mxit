class GenericMessage:
  def __init__(self, conn, cmd, data):
    self.conn = conn
    self.data = data
    self.cmd = cmd


  def send(self):
    

class LoginMessage:
  def __init__(self, conn):
    GenericMessage.__init__(self, conn, Mxit.LOGIN, conn.properties) 
