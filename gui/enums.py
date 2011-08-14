'''
   An enum class to help manage the various requests and
   replies to and from client and server.
'''

class Command:
  '''
     Command numbers used for requests to the server.
  '''
  LOGIN = '1'
  LOGOUT = '2'
  GET_CONTACTS = '3'
  PRESENCE = '7'
  GET_MESSAGE = '9'
  SEND_MESSAGE = '10'

class Msg_Type:
  '''
     The type of message. Used in SEND_MESSAGE command.
  '''
  DEFAULT = '1'

class Error:
  '''
    Error messages.
  '''
  NONE = '0'

class Presence:
  '''
     Included in the server reply of a GET_CONTACTS request.
  '''
  OFFLINE = '0'
  ONLINE = '1'
  AWAY = '2'
  DO_NOT_DISTURB = '4'

  status_list = ['Offline', 'Online', 'Away', '', 'Do not disturb']

class Type:
  '''
     Included in the server reply of a GET_CONTACTS request.
  '''
  MXIT = '0'
  GOOGLE_TALK = '18'

class Mood:
  '''
     Included in the server reply of a GET_CONTACTS request.
  '''
  NONE = '0'
  ANGRY = '1'
  EXCITED = '2'
  GRUMPY = '3'
  HAPPY = '4'
  IN_LOVE = '5'
  INVINCIBLE = '6'
  SAD = '7'
  HOT = '8'
  SICK = '9'
  SLEEPY = '10'

  mood_list = ['None', 'Angry', 'Excited', 'Grumpy', 'Happy', 'In love', 'Invincible', 'Sad', 'Hot', 'Sick', 'Sleepy']

if __name__ == '__main__':
  print Command.LOGIN
  print Mood.SLEEPY
