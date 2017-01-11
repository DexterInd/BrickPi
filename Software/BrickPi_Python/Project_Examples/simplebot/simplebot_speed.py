#!/usr/bin/env python
'''
########################################################################                                                                 
# Program Name: simplebot_speed.py                                     
# ================================     
# This code is for moving the simplebot with speed control                                     
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
#	t-Increase speed
#	g-Decrease Speed

from BrickPi import *   #import BrickPi.py file to use BrickPi operations
speed=200				#initial speed
cmd='x'		
motor1=PORT_B	# motor1 is on PORT_B
motor2=PORT_C	# motor2 is on PORT_C				#last used command (used when increasing or decreasing speed)

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

#Move the simplebot depending on the command
def move_bot(val):
	global cmd
	if val=='w':
		cmd='w'
		fwd()  
	elif val=='a' :
		cmd='a'
		left()
	elif val=='d':
		cmd='d'
		right()
	elif val=='s':
		cmd='s'
		back()
	elif val=='x':
		stop()

def main():
	global speed
	BrickPiSetup()  # setup the serial port for communication

	BrickPi.MotorEnable[motor1] = 1 #Enable the Motor1
	BrickPi.MotorEnable[motor2] = 1 #Enable the Motor2 

	BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

	BrickPi.Timeout=10000	#Set timeout value for the time till which to run the motors after the last command is pressed
	BrickPiSetTimeout()		#Set the timeout

	while True:
		inp=str(raw_input())	#Take input from the terminal
		move_bot(inp)			#Send command to move the bot
		if inp=='t':			#Increase the speed
			print "Speed: ",speed
			if speed >234:
				speed=255
			else:
				speed=speed+10
			move_bot(cmd)		#call move_bot() to update the motor values
		elif inp=='g':			#Decrease the speed
			print "Speed: ",speed
			if speed<11:
				speed=0
			else:
				speed=speed-10
			move_bot(cmd)
		BrickPiUpdateValues() 	#Update the motor values
		time.sleep(.01)         # sleep for 10 ms
if __name__ == "__main__":
    main()