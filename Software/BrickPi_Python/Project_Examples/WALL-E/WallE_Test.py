#!/usr/bin/env python
# WALL-E !  
#
# Dexter Industries
# Initial Date: August 5, 2014
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# Project:  Control a LEGO WALL-E with a PS3 Controller.
#
# See more about the BrickPi:  http://www.dexterindustries.com/BrickPi
# Setup the PS3 Controller Here:  http://booting-rpi.blogspot.ro/2012/08/dualshock-3-and-raspberry-pi.html
# Must be running sudo sixad --start to get the PS3 controller to run.
#
# Move the treads with the two joysticks on the PS3 controller.
# Move WALL-E's head with the left and right gamepad keys.

from BrickPi import *   		#import BrickPi.py file to use BrickPi operations
from ps3 import *				#Import the PS3 library

BrickPiSetup()  				# setup the serial port for communication

BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor B - Right Tread
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor C - Left Tread
BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor D - This is the small motor that controls the arms and head.

BrickPiSetupSensors()   		#Send the properties of sensors to BrickPi

print "Initializing WALL-E Controls!"
p=ps3()							#Create a PS3 object
print "Done Initializing."
print "Running WallE."

while True:

	p.update()			#Read the ps3 values

	# Parse out the head movements.
	z = 0
	if p.right:			#If UP is pressed move the head right
		z = -90
	elif p.left:		#If LEFT is pressed move the head left
		z = 90
	
	# Parse out the motor movements.
	x=((p.a_joystick_left_y+1)*90 - 90)
	y=((p.a_joystick_right_y+1)*90 - 90)
	
	# Set the motor speeds.
	BrickPi.MotorSpeed[PORT_D] = int(z)  	# Turn the head
	BrickPi.MotorSpeed[PORT_B] = int(x)		# Turn the track
	BrickPi.MotorSpeed[PORT_C] = int(y)		# Turn the track

	BrickPiUpdateValues()  
	time.sleep(.01)