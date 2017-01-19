#!/usr/bin/env python
###############################################################################################################                                                          
# Program Name: Shooter_Robot_Mouse.py                                     
# ====================================    
# This code is for controlling the BrickPi LEGO Shooter using a mouse
# http://www.dexterindustries.com/                                                                
# History
# ------------------------------------------------
# Author     Comments
# Joshwa     Initial Authoring
#                                                                  
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)           
#
###############################################################################################################
#
# DESCRIPTION:
# Ball Shooter Robot is a stationery robot with two motors - one to rotate and fix a position of the shooter 
# and another to shoot the balls which is controlled by a mouse
#
# CONNECTIONS: 
#	Shooter Motor - Port A
#	Motor for arm movement - Port D 
#
# DIRECTIONS FOR USE
# 	-> Setup battery power source for the RPi & BrickPi and boot.
#	-> Connect the mouse to one of the USB ports of the RaspberryPi
#
# MOUSE CONTROLS
#	-> Move the mouse right to rotate the arm Right
#	-> Move the mouse left to rotate the arm Left
#	-> Left Mouse Button Click to shoot the ball
#	-> Right Mouse Button Click to stop both the motors instantly

from BrickPi import *   #import BrickPi.py file to use BricPi operations
import threading
import struct

file = open( "/dev/input/mice", "rb" );      # reads the /dev/input/mice and converts the hex-input into integers

# function to get the inputs from the mouse and control motors
def getMouseEvent():                         
	buf = file.read(3);                        
	button = ord( buf[0] );
	bLeft = button & 0x1;					# assigns the state of left button to bLeft
	bRight = ( button & 0x2 ) > 0;			# assigns the state of right button to bRight
	x,y = struct.unpack( "bb", buf[1:] );	# assigns the speed of mouse in x and y direction to variables x and y.
	global cr								# variable for keeping track whether the mouse has moved right
	global cl								# variable for keeping track whether the mouse has moved left
	if bRight == 1 :						#If right button is clicked all the motors will stop instantly
		bLeft = 0             
		x = 0								#All the other variables are set to 0 since we want only one motor to be running at a time 
		print "Stop everything"
		BrickPi.MotorSpeed[PORT_A] = 0		#Stop MotorA 
		BrickPi.MotorSpeed[PORT_D] = 0		#Stop MotorB
	elif bLeft == 1 :						#when left mouse mutton is clicked start the shooter motor to shoot the ball
		bRight = 0
		x = 0
		print "Shoot"
		BrickPi.MotorSpeed[PORT_A] = 200	
		BrickPi.MotorSpeed[PORT_D] = 0		
	elif x > 100:							#when speed of mouse is greater than 100 the arm motor rotates right 
		bLeft = 0
		bRight = 0
		print "Turn Right"
		BrickPi.MotorSpeed[PORT_A] = 0
		BrickPi.MotorSpeed[PORT_D] = -200 
	elif x < -100 :							#when speed of mouse is greater than 100 the arm motor rotates left 
		bLeft = 0
		bRight = 0
		print "Turn Left"
		BrickPi.MotorSpeed[PORT_A] = 0         
		BrickPi.MotorSpeed[PORT_D] = 200      
	BrickPiUpdateValues();					# BrickPi updates the values for the motors
	print "Values Updated"

BrickPiSetup()                          #setup the serial port for communication
BrickPi.MotorEnable[PORT_A] = 1         #Enable the Motor A
BrickPi.MotorEnable[PORT_D] = 1         #Enable the Motor D
BrickPiSetupSensors()                   #Send the properties of sensors to BrickPi

while( 1 ):
	running = True
	getMouseEvent();       # Calls the function which gets all the inputs from mouse
	time.sleep(.1)
file.close();				