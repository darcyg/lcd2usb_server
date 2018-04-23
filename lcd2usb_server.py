#!/bin/python2
import time
import sys
import threading
import socket 

from lcd2usb import LCD

# Argument Variables
noDisplay = False  #"-n"
verbose = False  #"-v"
allowExternal = False #"-e"

# Default Line Variables
line0_default = "%I:%M%p"
line1_default = " "
line2_default = "Waiting for"
line3_default = "connection..."

# Socket Default values
portNum = 8080
server_address = ('localhost', portNum)

class lcd_thread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.lcd = LCD.find_or_die()
    self.refresh_interval = 2
    self.line0 = line0_default
    self.line1 = line1_default
    self.line2 = line2_default
    self.line3 = line3_default
  def run(self):
    self.lcd_refresh_loop()
  def lcd_refresh(self):
    import datetime
    dt = datetime.datetime.now()
    self.lcd.home()
    self.lcd.fill_center(dt.strftime(self.line0),0)
    self.lcd.fill_center(dt.strftime(self.line1),1)
    self.lcd.fill_center(dt.strftime(self.line2),2)
    self.lcd.fill_center(dt.strftime(self.line3),3)
  def lcd_refresh_loop(self):
    while True:
      self.lcd_refresh()
      time.sleep(self.refresh_interval)   
  def set_line0(self, new_string):
    self.line0 = new_string
    self.lcd_refresh()
  def set_line1(self, new_string):
    self.line1 = new_string
    self.lcd_refresh()
  def set_line2(self, new_string):
    self.line2 = new_string
    self.lcd_refresh()
  def set_line3(self, new_string):
    self.line3 = new_string
    self.lcd_refresh()
  def set_brightness(self, brightness):
    self.lcd.set_brightness(brightness)
  def set_refresh_interval(self, new_interval):
    self.refresh_interval = new_interval

def input_handler(ctl_data, str_data, lcd_thread):
  global line_0, line_1, line_2, line_3, lcd
  if ctl_data == "0":
    if (verbose):
      print "Setting line 0 to: ", str_data
    if (not noDisplay):
      lcd_thread.set_line0(str_data)
  elif ctl_data == "1":
    if (verbose):
      print "Setting line 1 to: ", str_data
    if (not noDisplay):
      lcd_thread.set_line1(str_data)
  elif ctl_data == "2":
    if (verbose):
      print "Setting line 2 to: ", str_data
    if (not noDisplay):
      lcd_thread.set_line2(str_data)
  elif ctl_data == "3":
    if (verbose):
      print "Setting line 3 to: ", str_data
    if (not noDisplay):
      lcd_thread.set_line3(str_data)
  elif ctl_data == "@":
    if (verbose):
      print "Setting brightness to: ", str_data
    if (not noDisplay):
      lcd_thread.set_brightness(int(str_data))
  else:
    print "Bad ctl_data value"

if (__name__ == "__main__"):

  for arg in sys.argv:
    if (arg == "-n"):
      noDisplay = True
    elif (arg == "-v"):
      verbose = True
    elif (arg == "-e"):
      allowExternal = True
    elif (arg == sys.argv[0]):
      #Do nothing, script name
      print "lcd2usb_server" 
    else:
      print "Invalid Argument"
      exit()
    
  if (not noDisplay):
    lcd_update = lcd_thread()
    lcd_update.start()

  serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  if (allowExternal):
    serversocket.bind(socket.gethostname, portNum)
  else:
    #only alow connections from localhost
    serversocket.bind(server_address)
  
  serversocket.listen(5)
  print "Listening on port 8080"
  #Wait for connection
  try:
    while True:
      connection, client_address = serversocket.accept()
      try: 
        print 'connection from', client_address
        while True:
          ctldata = connection.recv(1)
          if ctldata:
            lendata = connection.recv(2)
            if lendata:  
              lendata = int(lendata)
              data = connection.recv(lendata+1)
              if data:
                data = data[:lendata] 
                input_handler(ctldata, data,lcd_update)
              else:
                break
            else:
              break
          else:
            break
      finally:
        print "Disconnected"
        connection.close()
  except KeyboardInterrupt:
    sys.exit()



