from mxitgui import ClientForm
from PyQt4 import QtCore, QtGui
import sys

if __name__ == '__main__':
    try:
      app = QtGui.QApplication(sys.argv)
      gui = ClientForm('41.191.124.10', 9119, '0716223917', '3NZjbv5S02qK0YkoOjiQrw==', '4DF78289-3578-4701-81C1-760225BAE46C')
      #gui = ClientForm('41.191.124.10', 9119, 'flat.eric', r'G/gXAtYw8VdCZNOa0AAsKA==', 'E2379B55-94E1-4947-9497-5D3D2C946BFB') 
      gui.show()
      sys.exit(app.exec_())
    except IndexError:
      print 'Usage: python main.py <server> <port>'


