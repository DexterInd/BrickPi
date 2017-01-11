#!/usr/bin/env python
'''
########################################################################                                                                 
# Program Name: simplebot_simple.py                                     
# ================================     
# This code is for moving the simplebot                                    
# http://www.dexterindustries.com/                                                                
# History
# ------------------------------------------------
# Author     Date      Comments
# Karan      04/11/13  Initial Authoring
#                                                                  
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)           
#
########################################################################
'''
#Commands:
#	w-Move forward
#	a-Move left
#	d-Move right
#	s-Move back
#	x-Stop

from BrickPi import *   #import BrickPi.py file to use BrickPi operations

#Move Forward
def fwd():
	BrickPi.MotorSpeed[motor1] = speed  
	BrickPi.MotorSpeed[motor2] = speed  
#Move Left
def left():
	BrickPi.MotorSpeed[motor1] = speed  
	BrickPi.MotorSpeed[motor2] = -speed 
#Move Right
def right():
	BrickPi.MotorSpeed[motor1] = -speed  
	BrickPi.MotorSpeed[motor2] = speed
#Move backward
def back():
	BrickPi.MotorSpeed[motor1] = -speed  
	BrickPi.MotorSpeed[motor2] = -speed
#Stop
def stop():
	BrickPi.MotorSpeed[motor1] = 0  
	BrickPi.MotorSpeed[motor2] = 0
	
BrickPiSetup()  # setup the serial port for communication

motor1=PORT_B
motor2=PORT_C
BrickPi.MotorEnable[motor1] = 1 #Enable the Motor A
BrickPi.MotorEnable[motor2] = 1 #Enable the Motor B 
BrickPiSetupSensors()   #Send the properties of sensors to BrickPi
BrickPi.Timeout=10000	#Set timeout value for the time till which to run the motors after the last command is pressed
BrickPiSetTimeout()		#Set the timeout

speed=200	#Set the speed
while True:
	inp=str(raw_input()) #Take input from the terminal
	#Move the bot
	if inp=='w':
		fwd()  
	elif inp=='a' :
		left()
	elif inp=='d':
		right()
	elif inp=='s':
		back()
	elif inp=='x':
		stop()  
	BrickPiUpdateValues() 	#Update the motor values

	time.sleep(.01)      	# sleep for 10 ms
   