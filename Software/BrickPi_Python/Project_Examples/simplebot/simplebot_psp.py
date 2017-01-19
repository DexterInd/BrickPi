#!/usr/bin/env python
'''
########################################################################                                                                 
# Program Name: simplebot_speed.py                                     
# ================================     
# This code is for moving the simplebot usin the MINDSENSORS PSP Controller                                  
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
#Use the joysticks on the PSP controller to control the simplebot, enable the analog mode before using the joysticks

from BrickPi import *   #import BrickPi.py file to use BrickPi operations
speed=200				#initial speed
cmd='x'					#last used command (used when increasing or decreasing speed)

#Move the simplebot depending on the command
def move_bot(m1s,m2s):
	BrickPi.MotorSpeed[motor1] = m1s 
	BrickPi.MotorSpeed[motor2] = m2s
	
b=button()		#Object of button class
I2C_PORT  = PORT_1     # I2C port for the PSP controller
I2C_SPEED = 1         

BrickPi.SensorType       [I2C_PORT]    = TYPE_SENSOR_I2C#Set the type of sensor at PORT_1
BrickPi.SensorI2CSpeed   [I2C_PORT]    = I2C_SPEED      #Set the speed of communication
BrickPi.SensorI2CDevices [I2C_PORT]    = 1              #number of devices in the I2C bus
BrickPiSetup()  # setup the serial port for communication

motor1=PORT_B	# motor1 is on PORT_B
motor2=PORT_C	# motor2 is on PORT_C
BrickPi.MotorEnable[motor1] = 1 #Enable the Motor1
BrickPi.MotorEnable[motor2] = 1 #Enable the Motor2 
BrickPi.SensorSettings   [I2C_PORT][0] = 0
BrickPi.SensorI2CAddr    [I2C_PORT][0] = 0x02     #address for writing
BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

BrickPi.Timeout=10000	#Set timeout value for the time till which to run the motors after the last command is pressed
BrickPiSetTimeout()		#Set the timeout

while True:
	#Send 0x42 to get a response back
	BrickPi.SensorI2CWrite [I2C_PORT][0]    = 1				#number of bytes to write
	BrickPi.SensorI2CRead  [I2C_PORT][0]    = 6				#number of bytes to read
	BrickPi.SensorI2COut   [I2C_PORT][0][0] = 0x42			#byte to write
	BrickPiUpdateValues()               					#writing
		 
	b.upd(I2C_PORT)					#Update the button values
	#print b.ljy,b.rjy
	
	m2speed=(b.ljy+b.ljx)
	m1speed=(b.rjy+b.rjx)
	move_bot(m1speed*2,m2speed*2)			#Send command to move the bot
	BrickPiUpdateValues() 	#Update the motor values
	time.sleep(.01)         # sleep for 10 ms
   