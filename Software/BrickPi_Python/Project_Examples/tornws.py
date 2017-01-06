#!/usr/bin/env python
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from BrickPi import *
import time

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        BrickPiSetup()
        BrickPiSetupSensors()
        BrickPi.MotorEnable[PORT_A] = 1 #left motor
        BrickPi.MotorEnable[PORT_D] = 1 #right motor
        print 'New Connection'
        #self.write_message("Hello World")
      
    def on_message(self, message):
        #print 'message received %s' % message #dont print.. makes RPi slow
        msg = message.split(" ")
        lr = (float(msg[0]))*2 #change 2 if necessary
        fw = (float(msg[1]))/40*250 #change the numbers if necessary
        #following 2 lines must work well if the car is running in reverse add - after = in both lines 
        BrickPi.MotorSpeed[PORT_A] = (int(fw) + int(lr))
        BrickPi.MotorSpeed[PORT_D] = (int(fw) - int(lr))
        BrickPiUpdateValues();
    def on_close(self):
      print 'Connection Closed'



application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(9997)#(8888)
    tornado.ioloop.IOLoop.instance().start()
