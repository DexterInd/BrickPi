#!/usr/bin/env python
# BrickPi Hardware Test
############################################
# 
# This can be used to test the hardware on the BrickPi.  
##
# 1. Connect a lego motor to any of the four motor ports.
# 2. Connect a touch sensor, either of these two sensors.  You can connect both or just one sensor:
#		a). NXT Touch sensor to Port 1
#		b). EV3 Touch sensor to Port 2
# 3.  Run the program with sudo python BrickPi_Hardware_Test.py
#
# The motors should run when the touch sensor is pressed.
#
# Original Author: John
# Initial Date: Aug 19, 2015
# Updated: Mar 3, 2015
# http://www.dexterindustries.com/BrickPi
#

from BrickPi import *   								#import BrickPi.py file to use BrickPi operations
BrickPiSetup()  										# setup the serial port for communication
############################################
# !  Set the sensor type on the line below.  
BrickPi.SensorType[PORT_1] = TYPE_SENSOR_TOUCH   	#Set the type of sensor at PORT_1.  NXT Touch Sensor.
BrickPi.SensorType[PORT_2] = TYPE_SENSOR_EV3_TOUCH_0  	#Set the type of sensor at PORT_2.  EV3 Touch sensor.
BrickPi.MotorEnable[PORT_A] = 1 #Enable the Motor A
BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor B
BrickPi.MotorEnable[PORT_C] = 1 #Enable the Motor A
BrickPi.MotorEnable[PORT_D] = 1 #Enable the Motor B

BrickPiSetupSensors()   				#Send the properties of sensors to BrickPi.  Set up the BrickPi.
# There's often a long wait for setup with the EV3 sensors.  Up to 5 seconds.

def run_forward():
    print("Running Forward")
    power = 200
    BrickPi.MotorSpeed[PORT_A] = power  #Set the speed of MotorA (-255 to 255)
    BrickPi.MotorSpeed[PORT_B] = power  #Set the speed of MotorB (-255 to 255)
    BrickPi.MotorSpeed[PORT_C] = power  #Set the speed of MotorA (-255 to 255)
    BrickPi.MotorSpeed[PORT_D] = power  #Set the speed of MotorB (-255 to 255)

    ot = time.time()
    while(time.time() - ot < 3):    #running while loop for 3 seconds
        BrickPiUpdateValues()       # Ask BrickPi to update values for sensors/motors
	time.sleep(.1)

while True:

	result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
	if not result :
		button_value = BrickPi.Sensor[PORT_2]
		if button_value > 1000:
			print( "Button reads: {}".format(button_value))		
			run_forward()
	else:
		time.sleep(0.01)
	time.sleep(.01)     # sleep for 10 ms

