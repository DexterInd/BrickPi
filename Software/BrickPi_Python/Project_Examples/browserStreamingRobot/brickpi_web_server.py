#! /usr/bin/env python
##############################################################################################################                                                              
# This example is for streaming video and controlling the BrickPiBot from a web browser. It is a port from
# GoPiGo browser streaming robot. The only difference is it uses brickpi specific scripts instead of the
# GoPiGo versions. To make it easier for people to read and understand, the minimum number of changes were.
# This makes it easier to compare and contrast GoPiGo for learning purposes.
#
# http://www.dexterindustries.com/BrickPi                                                          
# History
# ------------------------------------------------
# Author     Date      		Comments
# John Cole  01 Jan 17          Updating for the big code move!
# Peter Lin  27 Dec 14          Simple port for BrickPi
# Karan      24 July 14  	Initial Authoring                                                          
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)           
#
# This example is derived from the Dawn Robotics Raspberry Pi Camera Bot
# https://bitbucket.org/DawnRobotics/raspberry_pi_camera_bot
############################################################################################################

# Copyright (c) 2014, Dawn Robotics Ltd
# All rights reserved.

# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.

# 3. Neither the name of the Dawn Robotics Ltd nor the names of its contributors 
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging

LOG_FILENAME = "/tmp/robot_web_server_log.txt"
logging.basicConfig( filename=LOG_FILENAME, level=logging.DEBUG )

# Also log to stdout
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel( logging.DEBUG )
logging.getLogger( "" ).addHandler( consoleHandler )

import os.path
import math
import time
import signal
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.escape
import sockjs.tornado
import threading
import Queue
import camera_streamer
import brickpi_controller
import json
import subprocess
import sys
import brickpibot
from BrickPi import *
robot = None

cameraStreamer = None
scriptPath = os.path.dirname( __file__ )
# note this expects the www directory to be at the same level as the script. If you want to
# use a different directory, make sure to change this setting
webPath = "./www"
robotConnectionResultQueue = Queue.Queue()
isClosing = False

#--------------------------------------------------------------------------------------------------- 
def createRobot(resultQueue ):
    # Creates the BrickPi controller and puts it in the resultQueue
    robot = brickpi_controller.BrickpiController( )
    resultQueue.put( robot )
            
#---------------------------------------------------------------------------------------------------
# As the name suggests, ConnectionHandler is responsible for reading the commands sent by
# the browser. When the browser sends messages, the on_message function is called. The
# function takes the text command and divides it into chunks. The separator is space. When
# the command is Move, the message has 3 parts: Move, x, y.
class ConnectionHandler( sockjs.tornado.SockJSConnection ):
    
    #-----------------------------------------------------------------------------------------------
    def on_open( self, info ):
        
        pass
        
    #-----------------------------------------------------------------------------------------------
    def on_message( self, message ):
                
        try:
            message = str( message )
            print message
        except Exception:
            logging.warning( "Got a message that couldn't be converted to a string" )
            return

        if isinstance( message, str ):
            
            lineData = message.split( " " )
            if len( lineData ) > 0:
                
                if lineData[ 0 ] == "Centre":
                
                    if robot != None:
                        robot.centreNeck()
                
                elif lineData[ 0 ] == "StartStreaming":
                    cameraStreamer.startStreaming()
                    
                elif lineData[ 0 ] == "Shutdown":
                    cameraStreamer.stopStreaming()
                    brickpibot.stop()
                    robot.disconnect()
                    sys.exit()
                
                elif lineData[ 0 ] == "Move" and len( lineData ) >= 3:
                    
                    motorJoystickX, motorJoystickY = \
                        self.extractJoystickData( lineData[ 1 ], lineData[ 2 ] )
                    
                    if robot != None:
                        robot.setMotorJoystickPos( motorJoystickX, motorJoystickY )     
                elif lineData[ 0 ] == "PanTilt" and len( lineData ) >= 3:
                    
                    neckJoystickX, neckJoystickY = \
                        self.extractJoystickData( lineData[ 1 ], lineData[ 2 ] )
                        
                    if robot != None:
                        robot.setNeckJoystickPos( neckJoystickX, neckJoystickY )
                        
    #-----------------------------------------------------------------------------------------------
    def on_close( self ):
        logging.info( "SockJS connection closed" )

    def extractJoystickData( self, dataX, dataY ):
        
        joystickX = 0.0
        joystickY = 0.0
        
        try:
            joystickX = float( dataX )
        except Exception:
            pass
        
        try:
            joystickY = float( dataY )
        except Exception:
            pass
            
        return ( joystickX, joystickY )

#--------------------------------------------------------------------------------------------------- 
class MainHandler( tornado.web.RequestHandler ):
    
    #------------------------------------------------------------------------------------------------
    def get( self ):
        self.render( webPath + "/index.html" )
        
#--------------------------------------------------------------------------------------------------- 
def robotUpdate():
    
    global robot
    global isClosing
    
    if isClosing:
        tornado.ioloop.IOLoop.instance().stop()
        return
        
    if robot == None:
        
        if not robotConnectionResultQueue.empty():
            
            robot = robotConnectionResultQueue.get()
        
    else:
                
        robot.update()

#--------------------------------------------------------------------------------------------------- 
def signalHandler( signum, frame ):
    
    if signum in [ signal.SIGINT, signal.SIGTERM ]:
        global isClosing
        isClosing = True
        
        
#--------------------------------------------------------------------------------------------------- 
if __name__ == "__main__":

    signal.signal( signal.SIGINT, signalHandler )
    signal.signal( signal.SIGTERM, signalHandler )
    logging.info( webPath )
    
    # Create the configuration for the web server
    router = sockjs.tornado.SockJSRouter( 
        ConnectionHandler, '/robot_control' )
    application = tornado.web.Application( router.urls + [ 
        ( r"/", MainHandler ), 
        ( r"/(.*)", tornado.web.StaticFileHandler, { "path": webPath } ),
        ( r"/css/(.*)", tornado.web.StaticFileHandler, { "path": webPath + "/css" } ),
        ( r"/css/images/(.*)", tornado.web.StaticFileHandler, { "path": webPath + "/css/images" } ),
        ( r"/images/(.*)", tornado.web.StaticFileHandler, { "path": webPath + "/images" } ),
        ( r"/js/(.*)", tornado.web.StaticFileHandler, { "path": webPath + "/js" } ) ] )
    
    #( r"/(.*)", tornado.web.StaticFileHandler, {"path": scriptPath + "/www" } ) ] \
    
    # Create a camera streamer
    cameraStreamer = camera_streamer.CameraStreamer()
    
    # Start connecting to the robot asyncronously
    robotConnectionThread = threading.Thread( target=createRobot, 
        args=[ robotConnectionResultQueue ] )
        #args=[ robotConfig, robotConnectionResultQueue ] )
    robotConnectionThread.start()

    # Now start the web server
    logging.info( "Starting web server..." )
    http_server = tornado.httpserver.HTTPServer( application )
	#The port number on which the robot control works, change in line 106 in www/index.html too
    http_server.listen( 98 )
    
    robotPeriodicCallback = tornado.ioloop.PeriodicCallback( 
        robotUpdate, 100, io_loop=tornado.ioloop.IOLoop.instance() )
    robotPeriodicCallback.start()
    
    cameraStreamerPeriodicCallback = tornado.ioloop.PeriodicCallback( 
        cameraStreamer.update, 1000, io_loop=tornado.ioloop.IOLoop.instance() )
    cameraStreamerPeriodicCallback.start()
    
    tornado.ioloop.IOLoop.instance().start()
    
    # Shut down code
    robotConnectionThread.join()
    
    if robot != None:
        robot.disconnect()
    else:
        if not robotConnectionResultQueue.empty():
            robot = robotConnectionResultQueue.get()
            robot.disconnect()
            
    cameraStreamer.stopStreaming()
